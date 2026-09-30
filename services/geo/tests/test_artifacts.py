import json
from pathlib import Path
from unittest.mock import MagicMock

import pytest

from shadowcast_geo.artifacts import GcsArtifacts, LocalArtifacts, artifact_store
from shadowcast_geo.config import Settings


def test_gcs_read_write_exists() -> None:
    client = MagicMock()
    blob = client.bucket.return_value.blob.return_value
    blob.download_as_bytes.return_value = b'{"id": "dana-2024"}'
    blob.exists.return_value = True
    store = GcsArtifacts("scenarios-bucket", client=client)

    store.write_json("scenarios/index.json", [{"id": "dana-2024", "storm": "Dana ବାତ୍ୟା"}])

    client.bucket.assert_called_once_with("scenarios-bucket")
    blob.upload_from_string.assert_called_once_with(
        json.dumps([{"id": "dana-2024", "storm": "Dana ବାତ୍ୟା"}], ensure_ascii=False).encode(),
        content_type="application/json",
    )
    assert store.read_json("scenarios/index.json") == {"id": "dana-2024"}
    assert store.exists("scenarios/index.json") is True
    listed = MagicMock()
    listed.name = "manifests/2026/09/27/0615Z.json"
    client.bucket.return_value.list_blobs.return_value = [listed]
    assert store.names("manifests/") == ["manifests/2026/09/27/0615Z.json"]
    client.bucket.return_value.list_blobs.assert_called_once_with(prefix="manifests/")


def test_gcs_rejects_non_finite_numbers() -> None:
    with pytest.raises(ValueError, match="Out of range float"):
        GcsArtifacts("b", client=MagicMock()).write_json("x.json", {"auc": float("nan")})


def test_local_artifacts(tmp_path: Path) -> None:
    store = LocalArtifacts(tmp_path)
    store.write_json("scenarios/index.json", [{"id": "fani-2019"}])
    assert store.exists("scenarios/index.json") is True
    assert store.read_json("scenarios/index.json") == [{"id": "fani-2019"}]
    assert store.names("scenarios/") == ["scenarios/index.json"]


def test_artifact_store_resolves() -> None:
    store = artifact_store(Settings(bucket="b"))
    assert store.exists("scenarios/index.json") is True
