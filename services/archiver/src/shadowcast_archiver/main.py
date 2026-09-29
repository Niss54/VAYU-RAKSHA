"""Archiver entry point: run every feed source concurrently and persist the results with a run manifest."""

from __future__ import annotations

import asyncio
import json
import logging
import sys
from datetime import UTC, datetime
from typing import Any

import httpx

from shadowcast_archiver.config import USER_AGENT, Settings
from shadowcast_archiver.sources import JSON, SOURCES, Artifact, FetchContext, Source
from shadowcast_archiver.storage import ArtifactStore, GcsStore

logger = logging.getLogger("shadowcast_archiver")


class CloudLoggingFormatter(logging.Formatter):
    """Formats records as single-line JSON that Cloud Logging parses into structured entries with severity."""

    def format(self, record: logging.LogRecord) -> str:
        """Render a log record as JSON.

        Args:
            record: The log record to format.

        Returns:
            str: JSON with ``severity``, ``message``, ``logger`` and, when present, ``exception``.
        """
        entry = {"severity": record.levelname, "message": record.getMessage(), "logger": record.name}
        if record.exc_info:
            entry["exception"] = self.formatException(record.exc_info)
        return json.dumps(entry, ensure_ascii=False)


async def run(settings: Settings, store: ArtifactStore, sources: dict[str, Source] = SOURCES) -> dict[str, Any]:
    """Fetch all sources concurrently, archive their artifacts under a UTC run folder and write a manifest.

    A failing source is recorded in the manifest and never prevents the others from being archived. Objects are
    written to ``{source}/{YYYY}/{MM}/{DD}/{HHMM}Z/{artifact}`` and the manifest to ``manifests/{...}Z.json``.

    Args:
        settings: Run configuration.
        store: Destination for artifacts and the manifest.
        sources: Source coroutines keyed by name (defaults to every registered source).

    Returns:
        dict[str, Any]: The manifest: run timestamp plus per-source status, file count and bytes, or error.
    """
    run_at = datetime.now(UTC).replace(second=0, microsecond=0)
    folder = run_at.strftime("%Y/%m/%d/%H%MZ")
    async with httpx.AsyncClient(
        timeout=settings.http_timeout_s, follow_redirects=True, headers={"User-Agent": USER_AGENT}
    ) as client:
        ctx = FetchContext(client, settings, run_at, asyncio.Semaphore(settings.max_concurrency))
        results = await asyncio.gather(*(source(ctx) for source in sources.values()), return_exceptions=True)

    manifest: dict[str, Any] = {"run_at": run_at.isoformat(), "sources": {}}
    for name, result in zip(sources, results, strict=True):
        if isinstance(result, BaseException):
            logger.error("source %s failed", name, exc_info=result)
            manifest["sources"][name] = {"status": "error", "error": f"{type(result).__name__}: {result}"}
            continue
        artifacts: list[Artifact] = result
        await asyncio.gather(*(store.put(f"{name}/{folder}/{a.name}", a.body, a.content_type) for a in artifacts))
        manifest["sources"][name] = {
            "status": "ok",
            "files": len(artifacts),
            "bytes": sum(len(a.body) for a in artifacts),
        }
        logger.info("source %s archived %d files", name, len(artifacts))
    await store.put(f"manifests/{folder}.json", json.dumps(manifest, indent=2).encode(), JSON)
    return manifest


def main() -> int:
    """CLI entry point used by the container.

    Returns:
        int: ``0`` when at least one source succeeded, ``1`` when every source failed (so Cloud Run marks the
        execution as failed and retries it).
    """
    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(CloudLoggingFormatter())
    logging.basicConfig(level=logging.INFO, handlers=[handler], force=True)
    logging.getLogger("httpx").setLevel(logging.WARNING)  # one INFO line per request would drown the run summary

    settings = Settings.from_env()
    manifest = asyncio.run(run(settings, GcsStore(settings.bucket)))
    succeeded = [name for name, status in manifest["sources"].items() if status["status"] == "ok"]
    logger.info("run %s finished: %d/%d sources ok", manifest["run_at"], len(succeeded), len(manifest["sources"]))
    return 0 if succeeded else 1
