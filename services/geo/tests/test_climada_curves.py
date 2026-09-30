"""Tests for CLIMADA ETH Zürich fragility curves."""
import numpy as np

from shadowcast_geo.climada_curves import (
    KT_TO_MS,
    VHALF,
    VTHRESH,
    climada_damage_fraction,
    compare_models,
)


def test_no_damage_below_threshold():
    threshold_kt = VTHRESH / KT_TO_MS
    wind = np.array([0.0, threshold_kt * 0.9])
    assert np.allclose(climada_damage_fraction(wind), [0.0, 0.0], atol=1e-3)


def test_half_damage_at_vhalf():
    vhalf_kt = (VHALF + VTHRESH) / KT_TO_MS  # approximate
    wind = np.array([vhalf_kt])
    result = climada_damage_fraction(wind)
    assert 0.3 < float(result[0]) < 0.7  # roughly 0.5


def test_nan_input_returns_zero():
    wind = np.array([np.nan, 100.0])
    result = climada_damage_fraction(wind)
    assert result[0] == 0.0
    assert result[1] > 0.0


def test_damage_monotonically_increasing():
    wind = np.linspace(0, 200, 50)
    result = climada_damage_fraction(wind)
    assert np.all(np.diff(result) >= 0)


def test_compare_models_fields():
    wind = np.array([50.0, 100.0, 150.0, 80.0])
    viirs_p = np.array([0.1, 0.7, 0.9, 0.4])
    result = compare_models(wind, viirs_p)
    assert "mean_absolute_difference" in result
    assert "agreement_rate" in result
    assert "citation" in result
    assert 0.0 <= result["agreement_rate"] <= 1.0
    assert result["mean_absolute_difference"] >= 0.0
