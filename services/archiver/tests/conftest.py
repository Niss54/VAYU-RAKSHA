"""Shared fixtures: deterministic settings and a fetch context backed by a real client routed through respx."""

from __future__ import annotations

import asyncio
from collections.abc import AsyncIterator
from datetime import UTC, datetime

import httpx
import pytest

from shadowcast_archiver.config import Settings
from shadowcast_archiver.sources import FetchContext

RUN_AT = datetime(2026, 9, 26, 6, 0, tzinfo=UTC)


@pytest.fixture
def settings() -> Settings:
    """Settings with fast retries and short horizons for tests."""
    return Settings(max_attempts=3, retry_backoff_s=0.0, gdacs_lookback_days=10, forecast_days=2)


@pytest.fixture
async def ctx(settings: Settings) -> AsyncIterator[FetchContext]:
    """A fetch context at a fixed run time; HTTP calls are intercepted by the test's respx mock."""
    async with httpx.AsyncClient() as client:
        yield FetchContext(client, settings, RUN_AT, asyncio.Semaphore(settings.max_concurrency))
