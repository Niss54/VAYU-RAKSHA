import json

from shadowcast_geo.live import digest, parse_cap
from tests.conftest import MemoryArtifacts

RUN = "2026/09/27/0615Z"


def cap(identifier: str, sent: str, *, language: str = "en-IN", info: bool = True) -> bytes:
    block = f"""<cap:info><cap:language>hi-IN</cap:language><cap:event>भारी वर्षा</cap:event></cap:info>
    <cap:info><cap:language>{language}</cap:language><cap:event>Heavy Rain</cap:event>
    <cap:severity>Severe</cap:severity><cap:urgency>Expected</cap:urgency><cap:certainty>Likely</cap:certainty>
    <cap:headline> Heavy rain likely over Puri </cap:headline>
    <cap:onset>{sent}</cap:onset><cap:expires>{sent}</cap:expires>
    <cap:area><cap:areaDesc>Puri district of Odisha</cap:areaDesc></cap:area></cap:info>"""
    return f"""<cap:alert xmlns:cap="urn:oasis:names:tc:emergency:cap:1.2"><cap:identifier>{identifier}</cap:identifier>
    <cap:sender>IMD-Bhubaneswar</cap:sender><cap:sent>{sent}</cap:sent>{block if info else ""}</cap:alert>""".encode()


def test_parse_cap_prefers_the_english_block() -> None:
    alert = parse_cap(cap("IN-1", "2026-09-27T09:00:00+05:30"))

    assert alert == {
        "identifier": "IN-1",
        "sender": "IMD-Bhubaneswar",
        "sent": "2026-09-27T09:00:00+05:30",
        "event": "Heavy Rain",
        "severity": "Severe",
        "urgency": "Expected",
        "certainty": "Likely",
        "headline": "Heavy rain likely over Puri",
        "onset": "2026-09-27T09:00:00+05:30",
        "expires": "2026-09-27T09:00:00+05:30",
        "areas": ["Puri district of Odisha"],
    }
    fallback = parse_cap(cap("IN-2", "x", language="or-IN"))
    assert fallback is not None and fallback["event"] == "भारी वर्षा"  # no English: the first block
    assert parse_cap(cap("IN-3", "x", info=False)) is None


def test_digest_reads_the_newest_run() -> None:
    archive = MemoryArtifacts()
    archive.write_json("manifests/2026/09/27/0015Z.json", {})
    archive.write_json(f"manifests/{RUN}.json", {})
    event = {"eventid": 1001326, "name": "Tropical Cyclone ONE-26", "alertlevel": "Orange", "country": "India",
             "fromdate": "2026-09-22T18:00:00", "todate": "2026-09-24T00:00:00", "iscurrent": "true",
             "severitydata": {"severitytext": "Tropical Storm (maximum wind speed of 83 km/h)"}}  # fmt: skip
    archive.write_json(f"gdacs/{RUN}/events.json", {"type": "FeatureCollection", "features": [{"properties": event}]})
    archive.write_bytes(f"sachet/{RUN}/cap/1.xml", cap("IN-old", "2026-09-26T09:00:00+05:30"), "application/xml")
    archive.write_bytes(f"sachet/{RUN}/cap/2.xml", cap("IN-new", "2026-09-27T09:00:00+05:30"), "application/xml")
    archive.write_bytes(f"sachet/{RUN}/cap/3.xml", cap("IN-empty", "x", info=False), "application/xml")

    live = digest(archive)

    assert live["run_at"] == RUN
    assert live["cyclones"] == [
        {
            "name": "Tropical Cyclone ONE-26",
            "alert": "Orange",
            "severity": "Tropical Storm (maximum wind speed of 83 km/h)",
            "country": "India",
            "from": "2026-09-22T18:00:00",
            "to": "2026-09-24T00:00:00",
            "current": True,
            "url": "https://www.gdacs.org/report.aspx?eventtype=TC&eventid=1001326",
        }
    ]
    assert [w["identifier"] for w in live["warnings"]] == ["IN-new", "IN-old"]


def test_digest_without_gdacs_events() -> None:
    archive = MemoryArtifacts()
    archive.write_bytes(f"manifests/{RUN}.json", json.dumps({}).encode(), "application/json")

    assert digest(archive) == {"run_at": RUN, "cyclones": [], "warnings": []}
