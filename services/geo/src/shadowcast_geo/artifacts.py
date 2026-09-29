"""Built scenario artifacts: JSON documents in Google Cloud Storage, the service's only store.

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
from typing import Any, Protocol

from google.cloud import storage

from shadowcast_geo.config import Settings


class ArtifactStore(Protocol):
    """Reads and writes artifacts (JSON documents and images) by relative path."""

    def read_bytes(self, path: str) -> bytes:
        """Read one object.

        Args:
            path: Artifact path relative to the store root.

        Returns:
            bytes: The object's bytes.
        """
        ...

    def write_bytes(self, path: str, body: bytes, content_type: str) -> None:
        """Write one object.

        Args:
            path: Artifact path relative to the store root.
            body: Object bytes.
            content_type: MIME type.
        """
        ...

    def read_json(self, path: str) -> Any:
        """Read one JSON document.

        Args:
            path: Artifact path relative to the store root.

        Returns:
            Any: The decoded JSON value.
        """
        ...

    def write_json(self, path: str, data: Any) -> None:
        """Write one JSON document.

        Args:
            path: Artifact path relative to the store root.
            data: JSON-serialisable value.
        """
        ...

    def exists(self, path: str) -> bool:
        """Whether an artifact exists.

        Args:
            path: Artifact path relative to the store root.

        Returns:
            bool: ``True`` when the artifact exists.
        """
        ...


class GcsArtifacts:
    """Artifacts in a Google Cloud Storage bucket, via Application Default Credentials."""

    def __init__(self, bucket: str, client: storage.Client | None = None) -> None:
        """Bind to a bucket.

        Args:
            bucket: Bucket name (without ``gs://``).
            client: Optional pre-built client.
        """
        self._bucket = (client or storage.Client()).bucket(bucket)

    def read_bytes(self, path: str) -> bytes:
        """Download one object.

        Args:
            path: Object name.

        Returns:
            bytes: The object's bytes.
        """
        return self._bucket.blob(path).download_as_bytes()

    def write_bytes(self, path: str, body: bytes, content_type: str) -> None:
        """Upload one object.

        Args:
            path: Object name.
            body: Object bytes.
            content_type: MIME type stored with the object.
        """
        # google-cloud-storage ships incomplete type hints for upload_from_string's optional parameters.
        self._bucket.blob(path).upload_from_string(body, content_type=content_type)  # pyright: ignore[reportUnknownMemberType]

    def names(self, prefix: str) -> list[str]:
        """Object names under a prefix.

        Args:
            prefix: Name prefix.

        Returns:
            list[str]: Matching object names.
        """
        # google-cloud-storage leaves list_blobs untyped.
        return [str(blob.name) for blob in self._bucket.list_blobs(prefix=prefix)]  # pyright: ignore[reportUnknownVariableType, reportUnknownArgumentType]

    def read_json(self, path: str) -> Any:
        """Download and decode one JSON object.

        Args:
            path: Object name.

        Returns:
            Any: The decoded JSON value.
        """
        return json.loads(self.read_bytes(path))

    def write_json(self, path: str, data: Any) -> None:
        """Encode (strict JSON, UTF-8) and upload one JSON object.

        Args:
            path: Object name.
            data: JSON-serialisable value.
        """
        self.write_bytes(path, json.dumps(data, ensure_ascii=False, allow_nan=False).encode(), "application/json")

    def exists(self, path: str) -> bool:
        """Whether an object exists in the bucket.

        Args:
            path: Object name.

        Returns:
            bool: ``True`` when the object exists.
        """
        return bool(self._bucket.blob(path).exists())


def artifact_store(settings: Settings) -> ArtifactStore:
    """The artifact store for these settings.

    Args:
        settings: Resolved settings.

    Returns:
        ArtifactStore: The scenario bucket.
    """
    return GcsArtifacts(settings.bucket)
