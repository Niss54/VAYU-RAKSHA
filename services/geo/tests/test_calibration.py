import numpy as np
import pytest

from shadowcast_geo.calibration import (
    OutageModel,
    evaluate,
    fit_logistic,
    fit_outage_model,
    loss_by_band,
    roc_auc,
    spatial_holdout,
    spearman,
)


def test_fit_logistic_recovers_known_coefficients() -> None:
    rng = np.random.default_rng(7)
    x = rng.uniform(40, 140, 20_000)
    y = (rng.uniform(size=x.size) < 1 / (1 + np.exp(-(-10.0 + 0.1 * x)))).astype(float)

    intercept, slope = fit_logistic(x, y)

    assert intercept == pytest.approx(-10.0, abs=0.5)
    assert slope == pytest.approx(0.1, abs=0.005)


def test_fit_logistic_stays_finite_on_separable_data() -> None:
    intercept, slope = fit_logistic(np.array([50.0, 60.0, 110.0, 120.0]), np.array([0.0, 0.0, 1.0, 1.0]))

    assert np.isfinite([intercept, slope]).all()
    assert slope > 0


@pytest.mark.parametrize(("x", "y"), [(np.array([]), np.array([])), (np.array([1.0, 2.0]), np.array([1.0, 1.0]))])
def test_fit_logistic_rejects_degenerate_input(x: np.ndarray, y: np.ndarray) -> None:
    with pytest.raises(ValueError, match="positive and one negative"):
        fit_logistic(x, y)


@pytest.mark.parametrize(
    ("a", "b", "expected"),
    [
        ([1, 2, 3, 4], [10, 20, 30, 40], 1.0),
        ([1, 2, 3, 4], [4, 3, 2, 1], -1.0),
        ([1, 2, 2, 3], [1, 2, 2, 3], 1.0),
        ([1], [1], None),
        ([1, 1, 1], [1, 2, 3], None),
    ],
)
def test_spearman(a: list[float], b: list[float], expected: float | None) -> None:
    result = spearman(np.array(a, dtype=float), np.array(b, dtype=float))

    assert np.isnan(result) if expected is None else result == pytest.approx(expected)


@pytest.mark.parametrize(
    ("y", "score", "expected"),
    [
        ([0, 0, 1, 1], [0.1, 0.2, 0.8, 0.9], 1.0),
        ([0, 0, 1, 1], [0.9, 0.8, 0.2, 0.1], 0.0),
        ([0, 1], [0.5, 0.5], 0.5),
        ([1, 1], [0.2, 0.9], None),
    ],
)
def test_roc_auc(y: list[float], score: list[float], expected: float | None) -> None:
    result = roc_auc(np.array(y, dtype=float), np.array(score, dtype=float))

    assert np.isnan(result) if expected is None else result == pytest.approx(expected)


def test_fit_outage_model_and_predictions() -> None:
    wind = np.array([40.0, 60.0, 80.0, 90.0, 105.0, 110.0, 120.0, 95.0])
    loss = np.array([-5.0, 3.0, 10.0, 60.0, 85.0, 90.0, 80.0, 20.0])

    model = fit_outage_model(wind, loss, 50.0, "fani-2019")

    assert model.trained_on == "fani-2019"
    assert model.n == 8
    assert model.auc == pytest.approx(15 / 16)  # one 95 kt negative outranks the 90 kt positive
    assert 0 <= model.brier < 0.25
    p = model.predict(np.array([40.0, 120.0, np.nan]))
    assert p[0] < 0.5 < p[1]
    assert p[2] == pytest.approx(model.predict(np.array([0.0]))[0])
    assert model.predict(np.array([model.wind_at_probability(0.5)]))[0] == pytest.approx(0.5)
    assert model.to_dict()["slope"] == model.slope


def test_evaluate(model: OutageModel) -> None:
    result = evaluate(model, np.array([60.0, 120.0]), np.array([5.0, 90.0]), 50.0)

    assert result["n"] == 2
    assert result["observed_outage_rate"] == 0.5
    assert result["auc"] == 1.0
    assert result["brier"] < 0.05

    empty = evaluate(model, np.array([]), np.array([]), 50.0)
    assert empty["n"] == 0
    assert all(np.isnan(empty[k]) for k in ("observed_outage_rate", "auc", "brier", "spearman"))


def test_loss_by_band_skips_empty_bands() -> None:
    wind = np.array([50.0, 55.0, 105.0, 110.0, 120.0])
    loss = np.array([0.0, 10.0, 70.0, 80.0, 90.0])

    bands = loss_by_band(wind, loss, (0, 60, 80, 100, 130))

    assert [(b["low_kt"], b["high_kt"], b["n"]) for b in bands] == [(0, 60, 2), (100, 130, 3)]
    assert bands[1]["median"] == 80.0
    assert bands[0]["p25"] == 2.5


def test_spatial_holdout_scores_every_block_out_of_fold() -> None:
    lat = np.linspace(19.0, 21.5, 32)
    wind = np.tile([40.0, 60.0, 100.0, 120.0], 8)
    loss = np.where(wind > 80, 90.0, 5.0)

    result = spatial_holdout(lat, wind, loss, 50.0, folds=4)

    assert (result["folds"], result["n"]) == (4, 32.0)
    assert result["auc"] == 1.0
    assert result["brier"] < 0.05
    assert [b["n"] for b in result["blocks"]] == [8.0] * 4
    assert (result["blocks"][0]["lat_min"], result["blocks"][-1]["lat_max"]) == (19.0, 21.5)
    assert all(b["auc"] == 1.0 and b["observed_outage_rate"] == 0.5 for b in result["blocks"])


def test_spatial_holdout_needs_both_outcomes_in_training() -> None:
    lat = np.array([19.0, 19.5, 20.0, 20.5])

    with pytest.raises(ValueError, match="positive and one negative"):
        spatial_holdout(lat, np.array([40.0, 50.0, 110.0, 120.0]), np.array([0.0, 0.0, 90.0, 90.0]), 50.0, folds=2)
