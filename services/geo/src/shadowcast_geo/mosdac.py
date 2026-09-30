"""ISRO MOSDAC API client.

MOSDAC (Meteorological and Oceanographic Satellite Data Archival Centre) is
operated by ISRO SAC and provides free real-time satellite data for disaster
management. URL: https://mosdac.gov.in

Data used:
- INSAT-3DS: 10-minute cloud-top temperature (Dvorak technique for cyclone intensity)
- Cyclone forecast bulletins: RSMC New Delhi format
- Ocean state: Bay of Bengal SST anomaly (warm water = rapid intensification risk)

NOTE: MOSDAC requires free registration at https://www.mosdac.gov.in/registration
      Store credentials as MOSDAC_TOKEN environment variable.
      If MOSDAC_TOKEN is not set, all methods return gracefully with demo data.
"""
from __future__ import annotations

import logging
import os
from dataclasses import dataclass
from datetime import datetime
from typing import Any

logger = logging.getLogger("shadowcast_geo.mosdac")

MOSDAC_BASE = "https://www.mosdac.gov.in/live/api"
MOSDAC_TOKEN_ENV = "MOSDAC_TOKEN"
BHOONIDHI_BASE = "https://bhoonidhi.nrsc.gov.in"


@dataclass
class MOSDACCycloneProduct:
    """INSAT-3DS derived cyclone intensity estimate."""

    storm_name: str
    valid_time: datetime
    lat: float
    lon: float
    dvt_intensity_kt: float  # Dvorak technique wind estimate
    cloud_top_temp_c: float  # minimum cloud-top temperature
    rapid_intensification_risk: bool  # SST anomaly > 1°C in 24h
    source: str = "ISRO MOSDAC INSAT-3DS"
    citation: str = "ISRO SAC, MOSDAC (https://mosdac.gov.in)"


def get_mosdac_token() -> str | None:
    """Return the MOSDAC API token from environment, or None if not set."""
    return os.environ.get(MOSDAC_TOKEN_ENV)


def fetch_cyclone_intensity(storm_name: str) -> MOSDACCycloneProduct | None:
    """Fetch latest INSAT-3DS cyclone intensity for a named storm.

    Falls back gracefully if MOSDAC token is not configured.
    In demo/hackathon mode, returns a mock product for Cyclone FANI.

    Args:
        storm_name: Storm name as reported by IMD (e.g., "FANI", "DANA").

    Returns:
        MOSDACCycloneProduct or None if unavailable.
    """
    token = get_mosdac_token()
    if not token:
        logger.info("MOSDAC_TOKEN not set — using demo INSAT-3DS product for %s", storm_name)
        return _demo_product(storm_name)

    try:
        import httpx

        resp = httpx.get(
            f"{MOSDAC_BASE}/cyclone/latest",
            params={"storm": storm_name},
            headers={"Authorization": f"Bearer {token}"},
            timeout=10.0,
        )
        resp.raise_for_status()
        data = resp.json()
        return _parse_mosdac_response(data)
    except Exception as exc:
        logger.warning("MOSDAC fetch failed for %s: %s — using demo product", storm_name, exc)
        return _demo_product(storm_name)


def fetch_bof_sst_anomaly(lat: float, lon: float) -> dict[str, Any] | None:
    """Fetch Bay of Bengal SST anomaly at cyclone position (rapid intensification proxy).

    Args:
        lat: Cyclone centre latitude.
        lon: Cyclone centre longitude.

    Returns:
        dict with 'sst_c', 'sst_anomaly_c', 'ri_risk' or None.
    """
    token = get_mosdac_token()
    if not token:
        # Demo: Fani crossed 29°C SST water — moderate RI risk
        return {"sst_c": 29.2, "sst_anomaly_c": 1.1, "ri_risk": True, "source": "demo"}

    try:
        import httpx

        resp = httpx.get(
            f"{MOSDAC_BASE}/oceansat/sst",
            params={"lat": lat, "lon": lon},
            headers={"Authorization": f"Bearer {token}"},
            timeout=10.0,
        )
        resp.raise_for_status()
        d = resp.json()
        return {
            "sst_c": float(d.get("sst", 0)),
            "sst_anomaly_c": float(d.get("anomaly", 0)),
            "ri_risk": float(d.get("anomaly", 0)) > 1.0,
            "source": "ISRO MOSDAC / Oceansat-3",
        }
    except Exception as exc:
        logger.warning("MOSDAC SST fetch failed: %s", exc)
        return None


def build_isro_data_citation() -> dict[str, str]:
    """Return the ISRO data citation block for the judge submission."""
    return {
        "INSAT-3DS": (
            "ISRO Space Applications Centre, MOSDAC. "
            "Meteorological and Oceanographic Satellite Data Archival Centre. "
            "https://mosdac.gov.in"
        ),
        "Oceansat-3": (
            "ISRO NRSC/SAC. Oceansat-3 OCM-3 / OSCAT-3 data products. "
            "https://mosdac.gov.in/oceansat3"
        ),
        "RISAT-1A": (
            "ISRO NRSC. RISAT-1A C-band SAR data. Disaster Management Support. "
            "https://bhoonidhi.nrsc.gov.in"
        ),
        "Bhuvan": (
            "ISRO NRSC. National Remote Sensing Centre Bhuvan Geoportal. "
            "https://bhuvan.nrsc.gov.in"
        ),
        "Access": (
            "All ISRO data used in VAYU-RAKSHA is free and open for disaster management. "
            "Registration at https://www.mosdac.gov.in/registration"
        ),
    }


def _demo_product(storm_name: str) -> MOSDACCycloneProduct:
    """Return a demo INSAT-3DS product for the hackathon presentation."""
    # Based on published MOSDAC products for Cyclone FANI (May 2-3, 2019)
    name = (storm_name or "FANI").upper()
    return MOSDACCycloneProduct(
        storm_name=name,
        valid_time=datetime(2019, 5, 2, 18, 0),
        lat=16.5,
        lon=86.8,
        dvt_intensity_kt=140.0,  # Dvorak T-number 6.5 → ~140 kt
        cloud_top_temp_c=-82.0,  # Deep convection
        rapid_intensification_risk=True,
        source="ISRO MOSDAC INSAT-3DS (demo/hackathon mode)",
    )


def _parse_mosdac_response(data: dict[str, Any]) -> MOSDACCycloneProduct:
    """Parse MOSDAC API response into MOSDACCycloneProduct."""
    return MOSDACCycloneProduct(
        storm_name=data.get("name", ""),
        valid_time=datetime.fromisoformat(data["valid_time"].replace("Z", "+00:00")),
        lat=float(data["lat"]),
        lon=float(data["lon"]),
        dvt_intensity_kt=float(data.get("dvorak_kt", 0)),
        cloud_top_temp_c=float(data.get("cloud_top_temp_c", 0)),
        rapid_intensification_risk=bool(data.get("ri_risk", False)),
    )
