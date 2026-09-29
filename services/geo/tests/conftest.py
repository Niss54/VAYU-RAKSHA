"""Shared fixtures: a synthetic northbound cyclone, a small asset table and fast-retry settings."""

from __future__ import annotations

import json
from datetime import UTC, datetime, timedelta
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd
import pytest

from shadowcast_geo.calibration import OutageModel
from shadowcast_geo.config import Settings
from shadowcast_geo.hazard import Track
from shadowcast_geo.surge import Grid

START = datetime(2019, 5, 2, 12, tzinfo=UTC)


class MemoryArtifacts:
    """In-memory stand-in for the scenario bucket, with the same strict-JSON round trip."""

    def __init__(self) -> None:
        self.objects: dict[str, bytes] = {}

    def read_bytes(self, path: str) -> bytes:
        return self.objects[path]

    def write_bytes(self, path: str, body: bytes, content_type: str) -> None:
        self.objects[path] = body

    def names(self, prefix: str) -> list[str]:
        return sorted(name for name in self.objects if name.startswith(prefix))

    def read_json(self, path: str) -> Any:
        return json.loads(self.objects[path])

    def write_json(self, path: str, data: Any) -> None:
        self.objects[path] = json.dumps(data, ensure_ascii=False, allow_nan=False).encode()

    def exists(self, path: str) -> bool:
        return path in self.objects


CELL_DEG = 1.0 / 60.0


def east_facing_coast(coast_lon: float = 86.0, slope_m_per_km: float = 1.0, lagoon: bool = False) -> Grid:
    """Relief with land west of ``coast_lon`` (10 m) and sea east of it deepening linearly offshore, 17-23N.

    ``lagoon`` adds a closed body of water on land, whose shore is not open coast.
    """
    lon = 83.0 + (np.arange(420) + 0.5) * CELL_DEG
    offshore_km = (lon - coast_lon) * 111.0 * np.cos(np.radians(19.5))
    values = np.tile(np.where(lon < coast_lon, 10.0, -np.maximum(offshore_km, 0.5) * slope_m_per_km), (360, 1))
    if lagoon:
        values[150:160, 100:120] = -2.0
    return Grid(cells=values, north=23.0, west=83.0, cell_deg=CELL_DEG)


def make_fixes(n: int = 7, lon: float = 86.0, vmax: float = 100.0, start: datetime = START) -> list[dict[str, Any]]:
    """A storm moving due north along ``lon`` from 18N, one fix every 3 hours from ``start``."""
    return [
        {
            "time": (start + timedelta(hours=3 * i)).strftime("%Y-%m-%dT%H:%M:%SZ"),
            "lat": 18.0 + 0.5 * i,
            "lon": lon,
            "vmax_kt": vmax,
            "rmw_km": 30.0,
            "r34_km": [200.0, 200.0, 200.0, 200.0],
            "r50_km": [120.0, 120.0, 120.0, 120.0],
            "r64_km": [60.0, None, 60.0, 60.0],
        }
        for i in range(n)
    ]


@pytest.fixture
def fixes() -> list[dict[str, Any]]:
    return make_fixes()


@pytest.fixture
def track(fixes: list[dict[str, Any]]) -> Track:
    return Track.from_records(fixes)


@pytest.fixture
def settings(tmp_path: Path) -> Settings:
    return Settings(bucket="test-bucket", cache_dir=tmp_path / "cache", max_attempts=2, retry_backoff_s=0.0)


@pytest.fixture
def model() -> OutageModel:
    return OutageModel(intercept=-12.8, slope=0.128, trained_on="fani-2019", n=200, auc=0.91, brier=0.09)


@pytest.fixture
def assets() -> pd.DataFrame:
    """Four assets at increasing distance east of the synthetic track."""
    return pd.DataFrame(
        {
            "asset_id": ["osm:node/1", "osm:node/2", "osdma:PURI:19.5,86.2", "osm:way/4"],
            "kind": ["substation", "hospital", "cyclone_shelter", "school"],
            "name": ["Near substation", "Mid hospital", "Shelter", None],
            "source": ["OpenStreetMap", "OpenStreetMap", "OSDMA (MCS)", "OpenStreetMap"],
            "lat": [19.5, 19.5, 19.5, 19.5],
            "lon": [86.05, 86.4, 86.2, 88.5],
        }
    )
