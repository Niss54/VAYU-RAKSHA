"""ETH Zürich CLIMADA fragility curves as a second outage model.

CLIMADA (CLIMate ADAptation) is published in Geoscientific Model Development
(Aznar-Siguan & Bresch 2019) and provides validated physical vulnerability
functions for tropical cyclone damage.

We use CLIMADA's Emanuel (2011) wind-damage function alongside ShadowCast's
VIIRS-fitted logistic model. When the two models agree, confidence is high.
When they diverge, the Prove tab explains why (grid topology vs wind speed).

Reference:
    Aznar-Siguan, G. & Bresch, D.N. (2019). CLIMADA v1: a global weather and
    climate risk assessment platform. Geoscientific Model Development, 12(7).
    https://doi.org/10.5194/gmd-12-3085-2019

GitHub: https://github.com/CLIMADA-project/climada_python (GPL-3.0)
"""
from __future__ import annotations

from typing import Any

import numpy as np
from numpy.typing import NDArray

# Emanuel (2011) wind-power damage function parameters
# Used in CLIMADA for tropical cyclone impact
VHALF: float = 74.7  # wind speed at 50% damage (m/s) — CLIMADA default for residential
VTHRESH: float = 25.7  # threshold wind speed for damage onset (m/s)
EXPONENT: float = 3.0  # damage curve exponent

# Conversion
KT_TO_MS: float = 0.514444  # 1 knot = 0.514444 m/s


def climada_damage_fraction(wind_kt: NDArray[np.float64]) -> NDArray[np.float64]:
    """Emanuel (2011) wind-damage fraction, as implemented in CLIMADA.

    This is a normalized mean damage ratio (MDR) in [0, 1]:
        D(v) = 1 / (1 + (Vhalf / max(v - Vthresh, 0))^n)

    Adapted for infrastructure outage probability by treating damage fraction
    as outage probability at the asset level.

    Args:
        wind_kt: Peak wind speed in knots (NaN allowed → returns 0).

    Returns:
        NDArray: Damage fraction in [0, 1], same shape as wind_kt.
    """
    v_ms = np.nan_to_num(wind_kt, nan=0.0) * KT_TO_MS
    excess = np.maximum(v_ms - VTHRESH, 0.0)
    # Avoid division by zero when excess = 0
    with np.errstate(divide="ignore", invalid="ignore"):
        p = np.where(excess > 0, 1.0 / (1.0 + (VHALF / excess) ** EXPONENT), 0.0)
    return np.clip(p, 0.0, 1.0)


def compare_models(
    wind_kt: NDArray[np.float64],
    viirs_model_p: NDArray[np.float64],
) -> dict[str, Any]:
    """Compare VIIRS-fitted logistic model with CLIMADA Emanuel curve.

    Args:
        wind_kt: Modelled peak wind in knots.
        viirs_model_p: P(outage) from ShadowCast's VIIRS-fitted logistic model.

    Returns:
        dict with 'climada_p', 'viirs_p', 'mean_absolute_difference',
        'agreement_rate' (fraction where both agree within 0.2), 'divergence_cases'.
    """
    climada_p = climada_damage_fraction(wind_kt)
    diff = np.abs(climada_p - viirs_model_p)
    valid = np.isfinite(wind_kt) & np.isfinite(viirs_model_p)

    agreement = float(np.mean(diff[valid] < 0.2)) if valid.any() else float("nan")
    mad = float(np.mean(diff[valid])) if valid.any() else float("nan")

    # Cases where models diverge by > 0.3: note them for the Prove tab
    divergence = np.where(valid & (diff > 0.3))[0]

    return {
        "climada_p": climada_p,
        "viirs_p": viirs_model_p,
        "mean_absolute_difference": mad,
        "agreement_rate": agreement,
        "divergence_indices": divergence.tolist(),
        "citation": (
            "CLIMADA Emanuel (2011) wind-damage function: "
            "Aznar-Siguan & Bresch (2019) GMD 12:3085. "
            "https://github.com/CLIMADA-project/climada_python"
        ),
    }
