"""Parametric insurance triggers per district: a transparent wind index, tiered payouts, and the forecast odds.

A district's index is the peak wind reached at ``TRIGGER_SHARE`` of its sites (the upper quantile of site peak winds),
so one exposed headland cannot trigger a whole district. Payout tiers follow the Saffir-Simpson category thresholds.
On the best track the trigger time is when that share of sites entered the 64-kt wind radius; on an as-issued ensemble
forecast every member is scored, giving the probability of a payout days before landfall (forecast-based financing).
The terms are illustrative: a real product would be priced and agreed with an insurer.
"""

from __future__ import annotations

import math
from typing import Any

import numpy as np
import pandas as pd
from numpy.typing import NDArray

from shadowcast_geo.config import OUTAGE_LOSS_PCT, PAYOUT_TIERS_KT, TRIGGER_SHARE


def payout_share(index_kt: NDArray[np.float64]) -> NDArray[np.float64]:
    """Payout as a share of the sum insured for each wind index, from the tier table.

    Args:
        index_kt: District wind indices (knots), any shape.

    Returns:
        NDArray[np.float64]: Payout share in [0, 1], same shape.
    """
    share = np.zeros_like(index_kt, dtype=float)
    for threshold, payout in PAYOUT_TIERS_KT:  # ascending, so higher tiers overwrite
        share = np.where(index_kt >= threshold, payout, share)
    return share


def district_index(districts: pd.Series, peak_kt: NDArray[np.float64]) -> pd.DataFrame:
    """Wind index per district for one or more storm realisations.

    Args:
        districts: District name per asset (``None`` for assets outside every district).
        peak_kt: Peak wind per asset, shape ``(n_assets,)`` or ``(n_members, n_assets)``; NaN counts as calm.

    Returns:
        pd.DataFrame: One row per district, one column per realisation: the wind reached at ``TRIGGER_SHARE`` of the
        district's sites.
    """
    winds = np.atleast_2d(np.nan_to_num(peak_kt, nan=0.0))
    frame = pd.DataFrame(winds.T, index=districts.to_numpy())
    frame = frame[frame.index.notna()]
    return frame.groupby(level=0).quantile(1.0 - TRIGGER_SHARE)


def best_track_triggers(assets: pd.DataFrame, truth: pd.DataFrame, landfall: pd.Timestamp) -> list[dict[str, Any]]:
    """Trigger outcome per district on the observed track, with the outages satellites saw there (basis risk).

    Args:
        assets: Assets with ``district``, ``peak_wind_kt``, ``band_kt`` and ``band_entry``.
        truth: Lit substations with ``district`` and ``loss_pct`` (night-light truth).
        landfall: Official landfall time (UTC).

    Returns:
        list[dict[str, Any]]: Per district, strongest first: ``district``, ``lat``/``lon`` (mean of its sites),
        ``sites``, ``index_kt``, ``payout_share``,
        ``trigger_time`` (when ``TRIGGER_SHARE`` of the sites were inside the 64-kt radius; ``None`` if never),
        ``lead_h`` (hours from trigger to landfall), ``lit_substations`` and ``observed_outage_rate``.
    """
    index = district_index(assets["district"], assets["peak_wind_kt"].to_numpy(dtype=float))[0]
    rows: list[dict[str, Any]] = []
    for district, group in assets[assets["district"].notna()].groupby("district"):
        entries = pd.to_datetime(group.loc[group["band_kt"] == 64, "band_entry"]).sort_values()
        needed = math.ceil(TRIGGER_SHARE * len(group))
        trigger = entries.iloc[needed - 1] if len(entries) >= needed else None
        lit = truth[truth["district"] == district]
        rows.append(
            {
                "district": district,
                "lat": round(float(group["lat"].mean()), 3),
                "lon": round(float(group["lon"].mean()), 3),
                "sites": len(group),
                "index_kt": float(index[district]),
                "payout_share": float(payout_share(np.array([index[district]]))[0]),
                "trigger_time": None if trigger is None else f"{trigger:%Y-%m-%dT%H:%M:%S}Z",
                "lead_h": None if trigger is None else (landfall.tz_localize(None) - trigger).total_seconds() / 3600,
                "lit_substations": len(lit),
                "observed_outage_rate": float((lit["loss_pct"] >= OUTAGE_LOSS_PCT).mean()) if len(lit) else None,
            }
        )
    return sorted(rows, key=lambda r: -r["index_kt"])


def forecast_triggers(districts: pd.Series, member_peak_kt: NDArray[np.float64]) -> list[dict[str, Any]]:
    """Probability of a payout per district from every ensemble member of an as-issued forecast.

    Args:
        districts: District name per asset.
        member_peak_kt: Peak wind per member and asset, shape ``(n_members, n_assets)``.

    Returns:
        list[dict[str, Any]]: Per district, most likely first: ``district``, ``p_trigger`` (share of members reaching
        the first tier), ``expected_payout_share`` (member mean) and the median ``index_kt``.
    """
    index = district_index(districts, member_peak_kt)
    members = index.to_numpy(dtype=float)  # (districts, members)
    payouts = payout_share(members)
    rows = [
        {
            "district": str(district),
            "p_trigger": float((members[i] >= PAYOUT_TIERS_KT[0][0]).mean()),
            "expected_payout_share": float(payouts[i].mean()),
            "index_kt": float(np.median(members[i])),
        }
        for i, district in enumerate(index.index)
    ]
    return sorted(rows, key=lambda r: (-r["p_trigger"], -r["index_kt"]))
