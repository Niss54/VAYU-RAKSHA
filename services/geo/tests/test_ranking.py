from datetime import UTC, datetime

import numpy as np
import pandas as pd

from shadowcast_geo.calibration import OutageModel
from shadowcast_geo.ranking import rank_assets

LANDFALL = datetime(2019, 5, 3, 3, 30, tzinfo=UTC)
BANDS = [
    {"low_kt": 0.0, "high_kt": 60.0, "n": 47.0, "p25": -15.0, "median": -9.0, "p75": -3.0},
    {"low_kt": 100.0, "high_kt": 130.0, "n": 36.0, "p25": 70.0, "median": 82.0, "p75": 90.0},
]
ISSUED = datetime(2019, 5, 1, 12, tzinfo=UTC)


def _frame(**overrides: list[object]) -> pd.DataFrame:
    base: dict[str, list[object]] = {
        "asset_id": ["a", "b", "c", "d"],
        "kind": ["school", "hospital", "hospital", "unknown_kind"],
        "peak_wind_kt": [115.0, 115.0, 115.0, np.nan],
        "peak_time": [pd.Timestamp("2019-05-03T03:00:00")] * 4,
        "min_dist_km": [20.0, 20.0, 20.0, 400.0],
        "band_kt": [64, 64, 0, 0],
        "band_entry": [pd.Timestamp("2019-05-02T21:00:00"), pd.Timestamp("2019-05-02T21:00:00"), pd.NaT, pd.NaT],
        "population": [1000.0, 500.0, 9000.0, np.nan],
        "elevation_m": [3.2, 12.0, np.nan, 1.0],
    }
    return pd.DataFrame({**base, **overrides})


def test_rank_orders_by_score_then_population(model: OutageModel) -> None:
    ranked = rank_assets(_frame(), model, LANDFALL, BANDS)

    assert ranked["asset_id"].tolist() == ["c", "b", "a", "d"]
    assert ranked["rank"].tolist() == [1, 2, 3, 4]
    assert ranked.loc[0, "criticality"] == 5
    assert ranked.loc[3, "criticality"] == 1
    assert ranked.loc[0, "score"] == ranked.loc[0, "p_outage"]


def test_reasons_cover_every_signal(model: OutageModel) -> None:
    ranked = rank_assets(_frame(), model, LANDFALL, BANDS)
    reasons: dict[str, list[str]] = dict(zip(ranked["asset_id"], ranked["reasons"], strict=True))

    school = reasons["a"]
    assert school[0].startswith("Modelled peak wind 115 kt around 03 May 03:00 UTC")
    assert "model fitted on fani-2019" in school[1]
    assert "lost a median 82% of their night lights" in school[2]
    assert "Inside the 64-kt wind radius from 02 May 21:00 UTC (+6 h to landfall)" in school
    assert "About 1,000 people live within 2 km" in school
    assert any(r.startswith("Low-lying: 3.2 m") for r in school)
    assert school[-1] == "Criticality 2/5 as a school"
    assert not any("wind radius" in r for r in reasons["c"])
    assert reasons["d"] == ["No modelled wind at this location for this storm"]


def test_surge_reason_replaces_low_lying(model: OutageModel) -> None:
    frame = _frame(
        elevation_m=[0.4, 12.0, np.nan, 1.0], coast_km=[2.0] * 4, surge_m=[1.8] * 4, flood_m=[1.1, 0.0, np.nan, 0.0]
    ).assign(rain_mm=[240.0, 0.0, 0.0, 0.0], observed_rain_mm=[310.0, np.nan, np.nan, np.nan])

    ranked = rank_assets(frame, model, LANDFALL, BANDS)
    school = ranked.loc[ranked["asset_id"] == "a", "reasons"].iloc[0]

    assert (
        "Storm surge: modelled 1.8 m on the coast 2 km away leaves about 1.1 m of water here (ground 0.4 m)" in school
    )
    assert not any(r.startswith("Low-lying") for r in school)
    assert "Storm rain modelled at 240 mm (R-CLIPER); NASA GPM measured 310 mm" in school


def test_rank_without_population_or_band_match(model: OutageModel) -> None:
    frame = _frame(peak_wind_kt=[70.0, 70.0, 70.0, 70.0]).drop(columns=["population", "elevation_m"])

    ranked = rank_assets(frame, model, LANDFALL, BANDS)

    assert len(ranked) == 4
    assert not any("lost a median" in r for reasons in ranked["reasons"] for r in reasons)
    assert not any("people live" in r for reasons in ranked["reasons"] for r in reasons)


def test_ensemble_forecast_ranking_and_reasons(model: OutageModel) -> None:
    frame = _frame(
        kind=["school", "cyclone_shelter", "cyclone_shelter", "school"],
        peak_wind_kt=[45.0, 45.0, 45.0, 45.0],
        band_kt=[0, 0, 0, 0],
        band_entry=[pd.NaT] * 4,
        peak_time=[pd.Timestamp("2019-05-03T03:00:00"), pd.NaT, pd.NaT, pd.NaT],
        population=[1.0, 10.0, 5.0, 1.0],
    ).assign(
        p_outage=[3e-7, 1e-7, 2e-7, 0.0],  # negligible: must not override gale exposure
        p34=[0.9, 0.2, 0.8, 0.0],
        p64=[0.0, 0.0, 0.0, 0.0],
        wind_p10=[30.0] * 4,
        wind_p90=[55.0] * 4,
        members=[52] * 4,
        gale_arrival=np.array(["2019-05-02T21:00:00", "NaT", "NaT", "NaT"], dtype="datetime64[s]"),
        rain_mm=[120.0] * 4,
        p_rain=[0.25] * 4,
    )

    ranked = rank_assets(frame, model, LANDFALL, BANDS, issued=ISSUED)

    # No outage risk anywhere: gale exposure x criticality decides, not population alone.
    assert ranked["asset_id"].tolist() == ["c", "a", "b", "d"]
    assert (ranked["p_outage"] < 1e-6).all()
    school = dict(zip(ranked["asset_id"], ranked["reasons"], strict=True))["a"]
    assert school[0] == (
        "Ensemble median peak wind 45 kt (10-90%: 30-55 kt) around 03 May 03:00 UTC; median closest approach 20 km"
    )
    assert school[1] == "0 of 52 ECMWF members bring hurricane-force (64 kt) wind; 47 bring gales (34 kt)"
    assert school[3] == "In the fani-2019 backtest, assets modelled at 0-60 kt showed no systematic night-light loss"
    assert "Gales (34 kt) arrive from 02 May 21:00 UTC (33 h after this forecast, +6 h to landfall)" in school
    shelter = dict(zip(ranked["asset_id"], ranked["reasons"], strict=True))["c"]
    assert "around" not in shelter[0]  # no peak time known
