"""Turn per-asset hazard into a ranked, explained priority list.

``score = P(outage) * criticality / 5``. Probability comes from the calibrated outage model; criticality encodes the
consequence of losing that kind of asset. Ties (common for weak storms, where outage risk is ~0 everywhere) are broken
by gale exposure (share of ensemble members bringing 34 kt wind, times criticality), then population. Every rank
carries the plain-language reasons behind it.
"""

from __future__ import annotations

from collections.abc import Hashable, Mapping
from datetime import datetime
from typing import Any

import numpy as np
import pandas as pd

from shadowcast_geo.calibration import OutageModel
from shadowcast_geo.config import CRITICALITY, EXTREME_RAIN_MM, FLOOD_DEPTH_M, LOW_LYING_M

NOTABLE_LOSS_PCT = 10.0  # below this, night-to-night variability dominates the backtest median

KIND_LABELS = {
    "hospital": "hospital",
    "cyclone_shelter": "cyclone shelter",
    "health_centre": "health centre",
    "substation": "power substation",
    "power_plant": "power plant",
    "clinic": "clinic",
    "water_works": "water works",
    "fire_station": "fire station",
    "police": "police station",
    "school": "school",
}


def rank_assets(
    assets: pd.DataFrame,
    model: OutageModel,
    landfall: datetime,
    reference_bands: list[dict[str, float]],
    issued: datetime | None = None,
) -> pd.DataFrame:
    """Score, rank and explain every asset, for a best-track replay or an ensemble forecast.

    Args:
        assets: One row per asset with ``kind``, ``peak_wind_kt``, ``peak_time``, ``min_dist_km``, ``band_kt`` and
            ``band_entry``; optionally ``population``, ``elevation_m``, ``gale_arrival``, a precomputed
            ``p_outage`` and ensemble columns (``p34``, ``p64``, ``wind_p10``, ``wind_p90``, ``members``).
        model: Calibrated outage model (used when ``p_outage`` is not precomputed; always quoted for provenance).
        landfall: Official landfall time, used to express lead time.
        reference_bands: Loss-by-wind-band summary from the reference backtest, quoted in the reasons.
        issued: Forecast issue time for ensemble forecasts; ``None`` for best-track replays.

    Returns:
        pd.DataFrame: ``assets`` plus ``criticality``, ``p_outage``, ``score``, ``rank`` (1 = highest priority) and
        ``reasons`` (list of strings), sorted by rank.
    """
    ranked = assets.copy()
    ranked["criticality"] = ranked["kind"].map(CRITICALITY).fillna(1).astype(int)
    if "p_outage" not in ranked:
        ranked["p_outage"] = model.predict(ranked["peak_wind_kt"].to_numpy(dtype=float))
    ranked["score"] = ranked["p_outage"] * ranked["criticality"] / 5.0
    population = ranked["population"] if "population" in ranked else pd.Series(0.0, index=ranked.index)
    gales = ranked["p34"] * ranked["criticality"] if "p34" in ranked else pd.Series(0.0, index=ranked.index)
    # Scores are compared at 1e-4 resolution so negligible outage probabilities tie and gale exposure decides.
    ranked = ranked.assign(
        _score=ranked["score"].round(4), _gales=gales.round(3), _population=population.fillna(0.0)
    ).sort_values(["_score", "_gales", "_population"], ascending=False, kind="mergesort")
    ranked["rank"] = np.arange(1, len(ranked) + 1)
    ranked["reasons"] = [_reasons(row, model, landfall, reference_bands, issued) for row in ranked.to_dict("records")]
    return ranked.drop(columns=["_score", "_gales", "_population"]).reset_index(drop=True)


def _reasons(
    row: Mapping[Hashable, Any],
    model: OutageModel,
    landfall: datetime,
    reference_bands: list[dict[str, float]],
    issued: datetime | None,
) -> list[str]:
    """Build the plain-language explanation for one asset.

    Args:
        row: Asset record (see :func:`rank_assets`), including ``criticality`` and ``p_outage``.
        model: Calibrated outage model (quoted for provenance).
        landfall: Official landfall time.
        reference_bands: Loss-by-wind-band summary from the reference backtest.
        issued: Forecast issue time for ensemble forecasts, else ``None``.

    Returns:
        list[str]: Reasons, most important first.
    """
    wind = row["peak_wind_kt"]
    if not np.isfinite(wind):
        return ["No modelled wind at this location for this storm"]
    peak_time = pd.Timestamp(row["peak_time"])
    when = f" around {peak_time:%d %b %H:%M} UTC" if pd.notna(peak_time) else ""
    if "p64" in row:
        members = int(row["members"])
        reasons = [
            f"Ensemble median peak wind {wind:.0f} kt (10-90%: {row['wind_p10']:.0f}-{row['wind_p90']:.0f} kt){when}; "
            f"median closest approach {row['min_dist_km']:.0f} km",
            f"{round(row['p64'] * members)} of {members} ECMWF members bring hurricane-force (64 kt) wind; "
            f"{round(row['p34'] * members)} bring gales (34 kt)",
        ]
    else:
        reasons = [f"Modelled peak wind {wind:.0f} kt{when}; storm centre passes {row['min_dist_km']:.0f} km away"]
    reasons.append(
        f"Grid-outage probability {row['p_outage']:.0%} (model fitted on {model.trained_on}, AUC {model.auc:.2f})"
    )
    band = next((b for b in reference_bands if b["low_kt"] < wind <= b["high_kt"]), None)
    if band:
        span = f"In the {model.trained_on} backtest, assets modelled at {band['low_kt']:.0f}-{band['high_kt']:.0f} kt"
        reasons.append(
            f"{span} lost a median {band['median']:.0f}% of their night lights"
            if band["median"] >= NOTABLE_LOSS_PCT
            else f"{span} showed no systematic night-light loss"
        )
    if row["band_kt"]:
        entry = pd.Timestamp(row["band_entry"]).tz_localize("UTC")
        lead_h = (pd.Timestamp(landfall) - entry).total_seconds() / 3600
        reasons.append(
            f"Inside the {row['band_kt']}-kt wind radius from {entry:%d %b %H:%M} UTC ({lead_h:+.0f} h to landfall)"
        )
    arrival = pd.Timestamp(row.get("gale_arrival", pd.NaT))
    if pd.notna(arrival):
        arrival = arrival.tz_localize("UTC")
        before_landfall = (pd.Timestamp(landfall) - arrival).total_seconds() / 3600
        after_issue = (
            f"{(arrival - pd.Timestamp(issued)).total_seconds() / 3600:.0f} h after this forecast, " if issued else ""
        )
        reasons.append(
            f"Gales (34 kt) arrive from {arrival:%d %b %H:%M} UTC ({after_issue}{before_landfall:+.0f} h to landfall)"
        )
    rain, measured = row.get("rain_mm"), row.get("observed_rain_mm")
    if rain is not None and np.isfinite(rain):
        satellite = f"; NASA GPM measured {measured:.0f} mm" if measured is not None and np.isfinite(measured) else ""
        members = (
            f" ({row['p_rain']:.0%} of members bring at least {EXTREME_RAIN_MM:.0f} mm)" if "p_rain" in row else ""
        )
        reasons.append(f"Storm rain modelled at {rain:.0f} mm (R-CLIPER){members}{satellite}")
    population = row.get("population")
    if population is not None and np.isfinite(population) and population > 0:
        reasons.append(f"About {population:,.0f} people live within 2 km")
    elevation, flood = row.get("elevation_m"), row.get("flood_m")
    if flood is not None and np.isfinite(flood) and flood >= FLOOD_DEPTH_M:
        reasons.append(
            f"Storm surge: modelled {row['surge_m']:.1f} m on the coast {row['coast_km']:.0f} km away leaves about "
            f"{flood:.1f} m of water here (ground {elevation:.1f} m)"
        )
    elif elevation is not None and np.isfinite(elevation) and elevation < LOW_LYING_M:
        reasons.append(f"Low-lying: {elevation:.1f} m above sea level (surge and flood exposure)")
    reasons.append(f"Criticality {row['criticality']}/5 as a {KIND_LABELS.get(row['kind'], row['kind'])}")
    return reasons
