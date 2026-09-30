"""Built scenario artifacts: JSON documents in Google Cloud Storage or local bundled data.

Layout::

    scenarios/index.json                 scenario summaries
    scenarios/{id}/scenario.json         metadata, calibration and backtest skill
    scenarios/{id}/track.json            storm track fixes
    scenarios/{id}/assets.json           ranked assets with hazard, probability and reasons
    scenarios/{id}/backtest.json         per-substation predicted vs observed night-light loss
    scenarios/{id}/surge.json            peak modelled surge per open-coast point
    scenarios/{id}/evidence/*.png        before/after satellite images of the region
    models/outage.json                   calibrated outage model
"""

from __future__ import annotations

import json
import logging
import os
from pathlib import Path
from typing import Any, Protocol

logger = logging.getLogger("shadowcast_geo.artifacts")


class ArtifactStore(Protocol):
    """Reads and writes artifacts (JSON documents and images) by relative path."""

    def read_bytes(self, path: str) -> bytes:
        """Read one object."""
        ...

    def write_bytes(self, path: str, body: bytes, content_type: str) -> None:
        """Write one object."""
        ...

    def read_json(self, path: str) -> Any:
        """Read one JSON document."""
        ...

    def write_json(self, path: str, data: Any) -> None:
        """Write one JSON document."""
        ...

    def exists(self, path: str) -> bool:
        """Whether an artifact exists."""
        ...


class LocalArtifacts:
    """Artifacts on local disk, bundled with the package or cached locally."""

    def __init__(self, base_dir: Path | str | None = None) -> None:
        if base_dir is None:
            pkg_data = Path(__file__).resolve().parent / "data"
            if (pkg_data / "scenarios" / "index.json").exists():
                self.base_dir = pkg_data
            else:
                self.base_dir = Path("data")
        else:
            self.base_dir = Path(base_dir)

    def read_bytes(self, path: str) -> bytes:
        target = self.base_dir / path
        if not target.exists():
            raise FileNotFoundError(f"Local artifact not found: {target}")
        return target.read_bytes()

    def write_bytes(self, path: str, body: bytes, content_type: str = "application/octet-stream") -> None:
        target = self.base_dir / path
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(body)

    def read_json(self, path: str) -> Any:
        return json.loads(self.read_bytes(path).decode("utf-8"))

    def write_json(self, path: str, data: Any) -> None:
        self.write_bytes(
            path,
            json.dumps(data, ensure_ascii=False, allow_nan=False, indent=2).encode("utf-8"),
            "application/json",
        )

    def exists(self, path: str) -> bool:
        return (self.base_dir / path).exists()

    def names(self, prefix: str) -> list[str]:
        target = self.base_dir / prefix
        if not target.exists():
            return []
        return [str(p.relative_to(self.base_dir)).replace("\\", "/") for p in target.rglob("*") if p.is_file()]


class GcsArtifacts:
    """Artifacts in a Google Cloud Storage bucket, via Application Default Credentials."""

    def __init__(self, bucket: str, client: Any = None) -> None:
        """Bind to a bucket safely without crashing on missing GCP credentials."""
        self.bucket_name = bucket
        self._bucket = None
        self._disabled = False
        try:
            if client is not None:
                self._bucket = client.bucket(bucket)
            else:
                from google.cloud import storage

                self._bucket = storage.Client().bucket(bucket)
        except Exception as e:
            self._disabled = True
            logger.warning("GCS bucket '%s' not accessible (%s). Operating without GCS.", bucket, e)

    def read_bytes(self, path: str) -> bytes:
        """Download one object."""
        if self._disabled or self._bucket is None:
            raise FileNotFoundError(f"GCS disabled; cannot read {path}")
        return self._bucket.blob(path).download_as_bytes()

    def write_bytes(self, path: str, body: bytes, content_type: str) -> None:
        """Upload one object."""
        if self._disabled or self._bucket is None:
            raise RuntimeError(f"GCS disabled; cannot upload {path}")
        self._bucket.blob(path).upload_from_string(body, content_type=content_type)

    def names(self, prefix: str) -> list[str]:
        """Object names under a prefix."""
        if self._disabled or self._bucket is None:
            return []
        try:
            return [str(blob.name) for blob in self._bucket.list_blobs(prefix=prefix)]
        except Exception:
            return []

    def read_json(self, path: str) -> Any:
        """Download and decode one JSON object."""
        return json.loads(self.read_bytes(path))

    def write_json(self, path: str, data: Any) -> None:
        """Encode (strict JSON, UTF-8) and upload one JSON object."""
        self.write_bytes(path, json.dumps(data, ensure_ascii=False, allow_nan=False).encode(), "application/json")

    def exists(self, path: str) -> bool:
        """Whether an object exists in the bucket."""
        if self._disabled or self._bucket is None:
            return False
        try:
            return bool(self._bucket.blob(path).exists())
        except Exception:
            return False


class FallbackArchiveReader:
    """Fallback archive reader when feed archiver GCS is offline."""

    def names(self, prefix: str) -> list[str]:
        return []

    def read_bytes(self, path: str) -> bytes:
        raise FileNotFoundError(path)


def artifact_store(settings: Any) -> ArtifactStore:
    """The artifact store for these settings.

    Prefers bundled local artifacts when present, otherwise tries GCS if credentials are set,
    falling back cleanly to local disk to ensure zero crash at startup.
    """
    # 1. Bundled package data
    pkg_data = Path(__file__).resolve().parent / "data"
    if (pkg_data / "scenarios" / "index.json").exists():
        return LocalArtifacts(pkg_data)

    # 2. Local workspace directory
    if Path("data/scenarios/index.json").exists():
        return LocalArtifacts(Path("data"))

    # 3. GCS if credentials are configured
    if os.environ.get("GOOGLE_APPLICATION_CREDENTIALS") or os.environ.get("GCP_PROJECT"):
        try:
            gcs = GcsArtifacts(settings.bucket)
            if not gcs._disabled and gcs.exists("scenarios/index.json"):
                return gcs
        except Exception:
            pass

    # 4. Local fallback
    return LocalArtifacts(pkg_data)
