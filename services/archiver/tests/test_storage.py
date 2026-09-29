from unittest.mock import MagicMock

from shadowcast_archiver.storage import GcsStore


async def test_gcs_store_uploads_with_content_type() -> None:
    client = MagicMock()
    store = GcsStore("shadowcast-archive", client=client)

    await store.put("gdacs/2026/09/26/0600Z/events.json", b"{}", "application/json")

    client.bucket.assert_called_once_with("shadowcast-archive")
    client.bucket.return_value.blob.assert_called_once_with("gdacs/2026/09/26/0600Z/events.json")
    client.bucket.return_value.blob.return_value.upload_from_string.assert_called_once_with(
        b"{}", content_type="application/json"
    )
