import json
import logging
import re
import sys
from typing import Any
from unittest.mock import MagicMock

import pytest

from shadowcast_archiver import main as archiver_main
from shadowcast_archiver.config import Settings
from shadowcast_archiver.sources import Artifact, FetchContext


class MemoryStore:
    """In-memory stand-in for the archive bucket."""

    def __init__(self) -> None:
        self.objects: dict[str, bytes] = {}

    async def put(self, path: str, body: bytes, content_type: str) -> None:
        self.objects[path] = body


async def _ok_source(ctx: FetchContext) -> list[Artifact]:
    return [Artifact("a.json", b"{}", "application/json"), Artifact("nested/b.xml", b"<b/>", "application/xml")]


async def _failing_source(ctx: FetchContext) -> list[Artifact]:
    raise RuntimeError("upstream down")


async def test_run_archives_successes_and_records_failures(settings: Settings) -> None:
    store = MemoryStore()
    manifest = await archiver_main.run(settings, store, {"good": _ok_source, "bad": _failing_source})

    folder = re.sub(r"(\d{4})-(\d{2})-(\d{2})T(\d{2}):(\d{2}).*", r"\1/\2/\3/\4\5Z", manifest["run_at"])
    assert manifest["sources"]["good"] == {"status": "ok", "files": 2, "bytes": 6}
    assert manifest["sources"]["bad"] == {"status": "error", "error": "RuntimeError: upstream down"}
    assert store.objects[f"good/{folder}/nested/b.xml"] == b"<b/>"
    assert json.loads(store.objects[f"manifests/{folder}.json"]) == manifest
    assert not any(path.startswith("bad/") for path in store.objects)


@pytest.mark.parametrize(
    ("statuses", "expected_exit"),
    [({"gdacs": "ok", "sachet": "error"}, 0), ({"gdacs": "ok"}, 0), ({"gdacs": "error", "sachet": "error"}, 1)],
)
def test_main_writes_to_the_bucket_and_sets_the_exit_code(
    monkeypatch: pytest.MonkeyPatch, statuses: dict[str, str], expected_exit: int
) -> None:
    captured: dict[str, Any] = {}

    async def fake_run(settings: Settings, store: object) -> dict[str, Any]:
        captured["store"] = store
        return {"run_at": "2026-09-26T06:00:00+00:00", "sources": {k: {"status": v} for k, v in statuses.items()}}

    gcs_store = MagicMock(name="GcsStore")
    monkeypatch.setattr(archiver_main, "run", fake_run)
    monkeypatch.setattr(archiver_main, "GcsStore", gcs_store)
    monkeypatch.setattr(archiver_main.Settings, "from_env", lambda: Settings(bucket="shadowcast-archive"))

    assert archiver_main.main() == expected_exit
    gcs_store.assert_called_once_with("shadowcast-archive")
    assert captured["store"] is gcs_store.return_value


@pytest.mark.parametrize("with_exception", [False, True])
def test_cloud_logging_formatter(with_exception: bool) -> None:
    exc_info = None
    if with_exception:
        try:
            raise ValueError("bad feed")
        except ValueError:
            exc_info = sys.exc_info()
    record = logging.LogRecord(
        "shadowcast_archiver", logging.ERROR, __file__, 1, "source %s failed", ("gdacs",), exc_info
    )

    entry = json.loads(archiver_main.CloudLoggingFormatter().format(record))

    assert entry["severity"] == "ERROR"
    assert entry["message"] == "source gdacs failed"
    assert ("exception" in entry) is with_exception
    if with_exception:
        assert "ValueError: bad feed" in entry["exception"]
