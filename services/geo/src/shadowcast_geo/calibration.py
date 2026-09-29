"""Outage-probability calibration and backtest metrics.

The outage model is a one-feature logistic regression, ``P(outage | wind) = 1 / (1 + exp(-(a + b * wind)))``, fitted
on observed night-light loss after a reference cyclone. It is deliberately simple: two coefficients that a district
officer can read, validated out of sample on other storms and, within the reference storm, on held-out stretches of
coast.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass
from itertools import pairwise
from typing import Any

import numpy as np
from numpy.typing import NDArray

FloatArray = NDArray[np.float64]


@dataclass(frozen=True)
class OutageModel:
    """Calibrated probability that an asset loses grid power given its modelled peak wind.

    Attributes:
        intercept: Logistic intercept ``a``.
        slope: Logistic slope ``b`` per knot.
        trained_on: Scenario id the coefficients were fitted on.
        n: Number of training assets.
        auc: In-sample ROC AUC.
        brier: In-sample Brier score.
    """

    intercept: float
    slope: float
    trained_on: str
    n: int
    auc: float
    brier: float

    def predict(self, wind_kt: FloatArray) -> FloatArray:
        """Outage probability for each wind value.

        Args:
            wind_kt: Modelled peak wind in knots (NaN allowed).

        Returns:
            FloatArray: Probabilities in ``[0, 1]``; NaN wind maps to 0.
        """
        z = np.clip(self.intercept + self.slope * np.nan_to_num(wind_kt, nan=0.0), -60.0, 60.0)
        return 1.0 / (1.0 + np.exp(-z))

    def wind_at_probability(self, probability: float) -> float:
        """Wind speed at which the model reaches a given outage probability.

        Args:
            probability: Target probability strictly between 0 and 1.

        Returns:
            float: Wind in knots.
        """
        return (np.log(probability / (1.0 - probability)) - self.intercept) / self.slope

    def to_dict(self) -> dict[str, Any]:
        """Serialise for the ``models/outage.json`` artifact.

        Returns:
            dict[str, Any]: The model's fields.
        """
        return asdict(self)


def fit_logistic(x: FloatArray, y: FloatArray, *, ridge: float = 1e-6, max_iter: int = 100) -> tuple[float, float]:
    """Fit a one-feature logistic regression by Newton-Raphson (IRLS) with a tiny ridge for stability.

    Args:
        x: Feature values.
        y: Binary labels (0/1).
        ridge: L2 penalty on the slope, keeping perfectly separable data finite.
        max_iter: Iteration cap.

    Returns:
        tuple[float, float]: ``(intercept, slope)``.

    Raises:
        ValueError: If ``x`` is empty or ``y`` contains a single class.
    """
    if x.size == 0 or np.unique(y).size < 2:
        raise ValueError("logistic fit needs at least one positive and one negative example")
    mean, scale = float(x.mean()), float(x.std()) or 1.0
    design = np.column_stack([np.ones_like(x), (x - mean) / scale])
    beta = np.zeros(2)
    penalty = np.diag([0.0, ridge])
    for _ in range(max_iter):
        p = 1.0 / (1.0 + np.exp(-np.clip(design @ beta, -60.0, 60.0)))
        gradient = design.T @ (y - p) - penalty @ beta
        hessian = design.T @ (design * (p * (1.0 - p))[:, None]) + penalty
        step = np.linalg.solve(hessian, gradient)
        beta += step
        if np.abs(step).max() < 1e-10:
            break
    return float(beta[0] - beta[1] * mean / scale), float(beta[1] / scale)


def spearman(a: FloatArray, b: FloatArray) -> float:
    """Spearman rank correlation with average ranks for ties.

    Args:
        a: First sample.
        b: Second sample, same length.

    Returns:
        float: Correlation in ``[-1, 1]``, or NaN for fewer than two points or a constant sample.
    """
    if a.size < 2:
        return float("nan")
    ranks = [_average_ranks(values) for values in (a, b)]
    if ranks[0].std() == 0 or ranks[1].std() == 0:
        return float("nan")
    return float(np.corrcoef(ranks[0], ranks[1])[0, 1])


def roc_auc(y: FloatArray, score: FloatArray) -> float:
    """Area under the ROC curve via the Mann-Whitney U statistic (ties count half).

    Args:
        y: Binary labels (0/1).
        score: Predicted scores; higher means more likely positive.

    Returns:
        float: AUC in ``[0, 1]``, or NaN when only one class is present.
    """
    positives, negatives = int(y.sum()), int(y.size - y.sum())
    if positives == 0 or negatives == 0:
        return float("nan")
    ranks = _average_ranks(score)
    return float((ranks[y == 1].sum() - positives * (positives + 1) / 2) / (positives * negatives))


def fit_outage_model(wind_kt: FloatArray, loss_pct: FloatArray, threshold_pct: float, trained_on: str) -> OutageModel:
    """Fit the outage model on one scenario's backtest and report its in-sample skill.

    Args:
        wind_kt: Modelled peak wind per asset.
        loss_pct: Observed night-light loss per asset (percent).
        threshold_pct: Loss at or above which an asset counts as having lost power.
        trained_on: Scenario id recorded in the model.

    Returns:
        OutageModel: The fitted model.
    """
    y = (loss_pct >= threshold_pct).astype(float)
    intercept, slope = fit_logistic(wind_kt, y)
    model = OutageModel(intercept, slope, trained_on, int(y.size), float("nan"), float("nan"))
    p = model.predict(wind_kt)
    return OutageModel(intercept, slope, trained_on, int(y.size), roc_auc(y, p), float(np.mean((p - y) ** 2)))


def evaluate(model: OutageModel, wind_kt: FloatArray, loss_pct: FloatArray, threshold_pct: float) -> dict[str, float]:
    """Score a model on a (usually out-of-sample) backtest.

    Args:
        model: The outage model.
        wind_kt: Modelled peak wind per asset.
        loss_pct: Observed night-light loss per asset (percent).
        threshold_pct: Loss at or above which an asset counts as having lost power.

    Returns:
        dict[str, float]: ``n``, ``observed_outage_rate``, ``auc``, ``brier`` and ``spearman`` (wind vs loss).
    """
    y = (loss_pct >= threshold_pct).astype(float)
    p = model.predict(wind_kt)
    return {
        "n": float(y.size),
        "observed_outage_rate": float(y.mean()) if y.size else float("nan"),
        "auc": roc_auc(y, p),
        "brier": float(np.mean((p - y) ** 2)) if y.size else float("nan"),
        "spearman": spearman(wind_kt, loss_pct),
    }


def spatial_holdout(
    lat: FloatArray, wind_kt: FloatArray, loss_pct: FloatArray, threshold_pct: float, folds: int
) -> dict[str, Any]:
    """Spatial cross-validation: refit the model with each south-to-north block of the coast held out in turn.

    Blocks are contiguous in latitude and equal in size, so every prediction comes from a model that never saw that
    stretch of coast. The pooled score measures generalisation across the region; the per-block scores (defined only
    where a block holds both outcomes) measure discrimination within one stretch, which is the stricter test.

    Args:
        lat: Latitude per asset.
        wind_kt: Modelled peak wind per asset.
        loss_pct: Observed night-light loss per asset (percent).
        threshold_pct: Loss at or above which an asset counts as having lost power.
        folds: Number of blocks.

    Returns:
        dict[str, Any]: ``folds``, ``n``, pooled out-of-fold ``auc`` and ``brier``, and ``blocks`` (each with
        ``lat_min``, ``lat_max``, ``n``, ``observed_outage_rate`` and ``auc``).

    Raises:
        ValueError: If a training split lacks either outcome.
    """
    y = (loss_pct >= threshold_pct).astype(float)
    p = np.empty_like(wind_kt)
    blocks: list[dict[str, float]] = []
    for held in np.array_split(np.argsort(lat, kind="stable"), folds):
        train = np.ones(y.size, dtype=bool)
        train[held] = False
        intercept, slope = fit_logistic(wind_kt[train], y[train])
        model = OutageModel(intercept, slope, "holdout", int(train.sum()), float("nan"), float("nan"))
        p[held] = model.predict(wind_kt[held])
        blocks.append(
            {
                "lat_min": float(lat[held].min()),
                "lat_max": float(lat[held].max()),
                "n": float(held.size),
                "observed_outage_rate": float(y[held].mean()),
                "auc": roc_auc(y[held], p[held]),
            }
        )
    return {
        "folds": folds,
        "n": float(y.size),
        "auc": roc_auc(y, p),
        "brier": float(np.mean((p - y) ** 2)),
        "blocks": blocks,
    }


def loss_by_band(wind_kt: FloatArray, loss_pct: FloatArray, edges_kt: tuple[int, ...]) -> list[dict[str, float]]:
    """Summarise observed loss per modelled-wind band.

    Args:
        wind_kt: Modelled peak wind per asset.
        loss_pct: Observed night-light loss per asset (percent).
        edges_kt: Band edges; a band is ``(low, high]``.

    Returns:
        list[dict[str, float]]: One entry per non-empty band with ``low_kt``, ``high_kt``, ``n`` and the 25th, 50th
        and 75th percentiles of loss.
    """
    bands: list[dict[str, float]] = []
    for low, high in pairwise(edges_kt):
        values = loss_pct[(wind_kt > low) & (wind_kt <= high)]
        if values.size:
            q25, q50, q75 = np.percentile(values, [25, 50, 75])
            bands.append(
                {
                    "low_kt": low,
                    "high_kt": high,
                    "n": float(values.size),
                    "p25": float(q25),
                    "median": float(q50),
                    "p75": float(q75),
                }
            )
    return bands


def _average_ranks(values: FloatArray) -> FloatArray:
    """Rank values from 1..n, giving tied values the mean of their ranks (the "average" method).

    Args:
        values: Sample to rank.

    Returns:
        FloatArray: Ranks as floats.
    """
    order = np.argsort(values, kind="mergesort")
    ranks = np.empty(values.size)
    ranks[order] = np.arange(1, values.size + 1)
    unique, inverse, counts = np.unique(values, return_inverse=True, return_counts=True)
    if unique.size < values.size:
        sums = np.bincount(inverse, weights=ranks)
        ranks = (sums / counts)[inverse]
    return ranks
