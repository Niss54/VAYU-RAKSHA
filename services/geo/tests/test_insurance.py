import numpy as np
import pandas as pd
import pytest

from shadowcast_geo.insurance import best_track_triggers, district_index, forecast_triggers, payout_share

LANDFALL = pd.Timestamp("2019-05-03T03:30:00Z")


def test_payout_share_steps_at_the_category_thresholds() -> None:
    assert payout_share(np.array([50.0, 64.0, 90.0, 96.0, 140.0])).tolist() == [0.0, 0.25, 0.5, 1.0, 1.0]


def test_district_index_is_the_wind_reached_at_a_quarter_of_the_sites() -> None:
    districts = pd.Series(["Puri", "Puri", "Puri", "Puri", "Khurda", None])
    winds = np.array([[120.0, 80.0, 60.0, 40.0, np.nan, 150.0], [70.0, 70.0, 70.0, 70.0, 30.0, 150.0]])

    index = district_index(districts, winds)

    assert sorted(index.index) == ["Khurda", "Puri"]  # sites outside every district are ignored
    assert index.loc["Puri", 0] == pytest.approx(90.0)  # 75th percentile of 40, 60, 80, 120
    assert index.loc["Khurda", 0] == 0.0  # calm where the member never arrives
    assert index.loc["Puri", 1] == 70.0


def test_best_track_triggers_time_the_trigger_and_check_it_against_outages() -> None:
    entries = pd.to_datetime(pd.Series(["2019-05-02T22:00:00", "2019-05-02T23:30:00", None, None]))
    assets = pd.DataFrame(
        {
            "district": ["Puri", "Puri", "Puri", "Ganjam"],
            "lat": [19.8, 19.9, 20.0, 19.3],
            "lon": [85.8, 85.9, 86.0, 84.8],
            "peak_wind_kt": [120.0, 110.0, 70.0, 50.0],
            "band_kt": [64, 64, 50, 34],
            "band_entry": entries,
        }
    )
    truth = pd.DataFrame({"district": ["Puri", "Puri", "Ganjam"], "loss_pct": [80.0, 20.0, 5.0]})

    puri, ganjam = best_track_triggers(assets, truth, LANDFALL)

    assert puri["district"] == "Puri" and puri["sites"] == 3
    assert (puri["lat"], puri["lon"]) == (19.9, 85.9)
    assert puri["payout_share"] == 1.0
    assert puri["trigger_time"] == "2019-05-02T22:00:00Z"  # one of three sites (25% rounds up to 1)
    assert puri["lead_h"] == pytest.approx(5.5)
    assert (puri["lit_substations"], puri["observed_outage_rate"]) == (2, 0.5)
    assert ganjam["payout_share"] == 0.0 and ganjam["trigger_time"] is None and ganjam["lead_h"] is None
    no_truth = best_track_triggers(assets, truth.iloc[:0], LANDFALL)[0]
    assert no_truth["observed_outage_rate"] is None


def test_forecast_triggers_give_the_odds_of_a_payout() -> None:
    districts = pd.Series(["Puri", "Puri", "Kendrapara"])
    members = np.array([[100.0, 90.0, 40.0], [60.0, 50.0, 40.0], [70.0, 70.0, 66.0], [30.0, 30.0, 30.0]])

    puri, kendrapara = forecast_triggers(districts, members)

    assert puri["district"] == "Puri"
    assert puri["p_trigger"] == 0.5  # two of four members reach 64 kt at a quarter of Puri's sites
    assert puri["expected_payout_share"] == pytest.approx((1.0 + 0 + 0.25 + 0) / 4)
    assert kendrapara["p_trigger"] == 0.25
