from collections.abc import Iterator
from datetime import UTC, datetime
from pathlib import Path
from typing import Any
from unittest.mock import MagicMock

import httpx
import numpy as np
import pytest

from shadowcast_geo import ensemble
from shadowcast_geo.calibration import OutageModel
from shadowcast_geo.config import Settings
from shadowcast_geo.ensemble import (
    StormForecast,
    ensemble_impact,
    load_ensemble,
    select_storm,
    track_file_urls,
)
from tests.conftest import make_fixes

ISSUED = datetime(2024, 10, 23, 0, tzinfo=UTC)
MISSING = -1e100


class FakeEccodes:
    """Stands in for the ecCodes module: messages are dicts of BUFR key -> value."""

    CODES_MISSING_DOUBLE = MISSING

    class CodesInternalError(Exception):
        """Raised for unknown keys, like ecCodes."""

    def __init__(self, messages: list[dict[str, Any]]) -> None:
        self.messages: Iterator[dict[str, Any]] = iter(messages)
        self.released: list[dict[str, Any]] = []

    def codes_bufr_new_from_file(self, handle: object) -> dict[str, Any] | None:
        return next(self.messages, None)

    def codes_set(self, message: dict[str, Any], key: str, value: int) -> None:
        assert (key, value) == ("unpack", 1)

    def codes_get(self, message: dict[str, Any], key: str) -> Any:
        return message[key]

    def codes_get_array(self, message: dict[str, Any], key: str) -> Any:
        if key not in message:
            raise self.CodesInternalError(key)
        return message[key]

    def codes_release(self, message: dict[str, Any]) -> None:
        self.released.append(message)


def _message(storm_id: str) -> dict[str, Any]:
    """Two members, analysis + two 6-hourly periods; member 2 has missing data after the analysis."""
    return {
        "stormIdentifier": f"{storm_id} ",
        "year": 2024, "month": 10, "day": 23, "hour": 0,
        "ensembleMemberNumber": [1, 2],
        "#2#latitude": [18.0, 18.1], "#2#longitude": [87.0, 87.1], "#1#windSpeedAt10M": [20.0, 21.0],
        "#1#timePeriod": [6], "#4#latitude": [18.5, MISSING], "#4#longitude": [86.8, MISSING],
        "#2#windSpeedAt10M": [22.0, MISSING],
        "#2#timePeriod": 12, "#6#latitude": [19.0, MISSING], "#6#longitude": 86.6, "#3#windSpeedAt10M": [25.0, 25.0],
    }  # fmt: skip


@pytest.fixture
def cache(tmp_path: Path) -> Settings:
    settings = Settings(cache_dir=tmp_path, max_attempts=1, retry_backoff_s=0)
    (tmp_path / "ecmwf_enfo_tf_2024102300.bufr").write_bytes(b"BUFR")  # cached, so no download happens
    return settings


def test_track_file_urls() -> None:
    assert track_file_urls(ISSUED) == (
        "https://storage.googleapis.com/ecmwf-open-data/20241023/00z/ifs/0p25/enfo/20241023000000-360h-enfo-tf.bufr",
        "https://storage.googleapis.com/ecmwf-open-data/20241023/00z/ifs/0p25/enfo/20241023000000-240h-enfo-tf.bufr",
    )


def test_load_ensemble_decodes_members(cache: Settings, monkeypatch: pytest.MonkeyPatch) -> None:
    fake = FakeEccodes([_message("70B"), _message("03B")])
    monkeypatch.setattr(ensemble, "eccodes", fake)

    with httpx.Client() as client:
        storms = load_ensemble(client, cache, ISSUED)

    assert [s.storm_id for s in storms] == ["70B", "03B"]
    assert len(fake.released) == 2
    storm = storms[0]
    assert storm.issued == ISSUED
    assert list(storm.members) == [1]  # member 2 keeps only its analysis fix, fewer than two
    fixes = storm.members[1]
    assert [f["time"] for f in fixes] == ["2024-10-23T00:00:00Z", "2024-10-23T06:00:00Z", "2024-10-23T12:00:00Z"]
    assert fixes[2]["lon"] == 86.6  # compressed single value broadcast to every member
    assert fixes[1]["vmax_kt"] == pytest.approx(42.8, abs=0.1)
    assert fixes[0]["rmw_km"] > fixes[2]["rmw_km"]  # stronger storms have tighter cores
    assert fixes[0]["r64_km"] == [None, None, None, None]


def test_load_ensemble_releases_message_on_error(cache: Settings, monkeypatch: pytest.MonkeyPatch) -> None:
    broken = {**_message("70B")}
    del broken["ensembleMemberNumber"]
    fake = FakeEccodes([broken])
    monkeypatch.setattr(ensemble, "eccodes", fake)

    with httpx.Client() as client, pytest.raises(FakeEccodes.CodesInternalError):
        load_ensemble(client, cache, ISSUED)

    assert fake.released == [broken]


def test_select_storm_prefers_member_agreement() -> None:
    lone_close = StormForecast("71B", ISSUED, {1: make_fixes(lon=86.0)})
    many_near = StormForecast("70B", ISSUED, {m: make_fixes(lon=86.5 + 0.1 * m) for m in range(1, 5)})
    far = StormForecast("72B", ISSUED, {m: make_fixes(lon=92.0) for m in range(1, 9)})

    assert select_storm([lone_close, many_near, far, StormForecast("00X", ISSUED, {})], (19.5, 86.0)) is many_near
    with pytest.raises(ValueError, match="no storm"):
        select_storm([StormForecast("00X", ISSUED, {})], (19.5, 86.0))


def test_ensemble_impact_aggregates_members(model: OutageModel) -> None:
    members = {1: make_fixes(vmax=120.0), 2: make_fixes(vmax=70.0), 3: make_fixes(vmax=30.0), 4: make_fixes(lon=95.0)}
    storm = StormForecast("70B", ISSUED, members)
    lat, lon = np.array([19.5, 19.5]), np.array([86.4, 89.5])

    impact, member_peak = ensemble_impact(lat, lon, storm, model)

    assert impact["p34"].tolist() == [0.5, 0.0]
    assert member_peak.shape == (4, 2)
    assert impact["p64"].tolist() == [0.5, 0.0]
    assert impact["rain_mm"][0] > impact["rain_mm"][1]
    assert 0.0 <= impact["p_rain"][0] <= 1.0
    assert 0.2 < impact["p_outage"][0] < 0.3
    assert impact["wind_p10"][0] < impact["peak_wind_kt"][0] < impact["wind_p90"][0]
    # Median over the members that reach gales: 12:00 (120 kt member) and 13:45 (70 kt member).
    assert impact["gale_arrival"][0] == np.datetime64("2019-05-02T12:52:30")
    assert np.isnat(impact["gale_arrival"][1])
    assert impact["peak_time"][0] == np.datetime64("2019-05-02T21:00:00")
    assert impact["closest_time"][0] == np.datetime64("2019-05-02T21:00:00")


def test_load_ensemble_downloads_when_not_cached(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    def write_cache(_client: object, _settings: object, name: str, _urls: object) -> None:
        (tmp_path / name).write_bytes(b"x")

    download = MagicMock(side_effect=write_cache)
    monkeypatch.setattr(ensemble, "download", download)
    monkeypatch.setattr(ensemble, "eccodes", FakeEccodes([]))

    with httpx.Client() as client:
        assert load_ensemble(client, Settings(cache_dir=tmp_path), ISSUED) == []

    assert download.call_args.args[2] == "ecmwf_enfo_tf_2024102300.bufr"
