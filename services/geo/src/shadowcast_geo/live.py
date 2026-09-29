"""The live picture: active cyclones and official warnings from the feed archiver's newest run.

Cyclones come from GDACS; warnings are NDMA SACHET CAP 1.2 alerts, as issued by IMD and the state disaster authorities.

The archiver snapshots the feeds every 6 hours into its own bucket; this module reads the newest run and turns it into
one small document for the console. Reading is blocking I/O, so the API runs it in a worker thread and caches it.
"""

from __future__ import annotations

import json
import xml.etree.ElementTree as ET
from typing import Any, Protocol, cast

CAP = {"cap": "urn:oasis:names:tc:emergency:cap:1.2"}
WARNINGS_KEPT = 200


class ArchiveReader(Protocol):
    """Read access to the feed archive bucket."""

    def names(self, prefix: str) -> list[str]:
        """Object names under a prefix.

        Args:
            prefix: Name prefix.

        Returns:
            list[str]: Matching object names.
        """
        ...

    def read_bytes(self, path: str) -> bytes:
        """Read one object.

        Args:
            path: Object name.

        Returns:
            bytes: The object's bytes.
        """
        ...


def parse_cap(document: bytes) -> dict[str, Any] | None:
    """The English ``info`` block of one CAP 1.2 alert, flattened.

    Args:
        document: CAP XML.

    Returns:
        dict[str, Any] | None: ``identifier``, ``sender``, ``sent``, ``event``, ``severity``, ``urgency``,
        ``certainty``, ``headline``, ``areas``, ``onset`` and ``expires``; None when the alert has no info block.
    """
    alert = ET.fromstring(document)
    infos = alert.findall("cap:info", CAP)
    info = next((i for i in infos if (i.findtext("cap:language", "", CAP) or "").startswith("en")), None)
    info = info if info is not None else next(iter(infos), None)
    if info is None:
        return None
    fields = ("event", "severity", "urgency", "certainty", "headline", "onset", "expires")
    return {
        "identifier": (alert.findtext("cap:identifier", "", CAP) or "").strip(),
        "sender": (alert.findtext("cap:sender", "", CAP) or "").strip(),
        "sent": (alert.findtext("cap:sent", "", CAP) or "").strip(),
        **{name: (info.findtext(f"cap:{name}", "", CAP) or "").strip() for name in fields},
        "areas": [a.findtext("cap:areaDesc", "", CAP) or "" for a in info.findall("cap:area", CAP)],
    }


def digest(archive: ArchiveReader) -> dict[str, Any]:
    """Digest the archiver's newest run.

    Args:
        archive: The feed archive.

    Returns:
        dict[str, Any]: ``run_at`` (the run's folder, e.g. ``2026/09/27/0615Z``), ``cyclones`` (GDACS events: name,
        alert level, severity text, country, dates, whether current) and ``warnings`` (SACHET alerts, newest first).
        Empty lists when the archive has no run yet.
    """
    manifests = sorted(n for n in archive.names("manifests/") if n.endswith(".json"))
    if not manifests:
        return {"run_at": None, "cyclones": [], "warnings": []}
    run = manifests[-1].removeprefix("manifests/").removesuffix(".json")
    gdacs = f"gdacs/{run}/events.json"
    listing: dict[str, Any] = json.loads(archive.read_bytes(gdacs)) if gdacs in archive.names(gdacs) else {}
    events = cast("list[dict[str, Any]]", listing.get("features", []))  # GDACS serves a GeoJSON FeatureCollection
    cyclones: list[dict[str, Any]] = [
        {
            "name": p.get("name"),
            "alert": p.get("alertlevel"),
            "severity": (p.get("severitydata") or {}).get("severitytext"),
            "country": p.get("country"),
            "from": p.get("fromdate"),
            "to": p.get("todate"),
            "current": str(p.get("iscurrent")).lower() == "true",
            "url": f"https://www.gdacs.org/report.aspx?eventtype=TC&eventid={p.get('eventid')}",
        }
        for p in (cast("dict[str, Any]", event.get("properties", {})) for event in events)
    ]
    alerts = [parse_cap(archive.read_bytes(name)) for name in archive.names(f"sachet/{run}/cap/")]
    warnings = sorted((a for a in alerts if a), key=lambda a: a["sent"], reverse=True)[:WARNINGS_KEPT]
    return {"run_at": run, "cyclones": cyclones, "warnings": warnings}
