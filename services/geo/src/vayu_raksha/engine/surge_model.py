"""VAYU-RAKSHA Physics-Informed Storm Surge Model.

Computes coastal storm surge crest and overland water inundation depth
combining inverted barometer effect, wind stress on shallow shelf, and coastal bathymetry.
"""

from typing import Dict
import math


class StormSurgeModel:
    """Hydrodynamic proxy for coastal storm surge calculation."""

    G_ACCEL: float = 9.80665  # m/s^2
    RHO_WATER: float = 1025.0  # kg/m^3 (seawater)
    RHO_AIR: float = 1.15
    DRAG_COEFF: float = 0.0026  # Wind drag coefficient under gale/cyclone conditions

    @classmethod
    def compute_coastal_surge(
        cls,
        p_cen_hpa: float,
        v_max_kt: float,
        coastal_distance_km: float,
        shelf_width_km: float = 45.0,
        mean_shelf_depth_m: float = 25.0,
        astronomical_tide_m: float = 0.8,
    ) -> Dict[str, float]:
        """Calculates peak storm surge height (meters above mean sea level).

        Args:
            p_cen_hpa: Storm central pressure.
            v_max_kt: Maximum sustained 10-meter wind speed.
            coastal_distance_km: Distance of storm eye from coastline (negative if inland).
            shelf_width_km: Width of continental shelf.
            mean_shelf_depth_m: Average depth of coastal shelf.
            astronomical_tide_m: Predicted astronomical high tide.

        Returns:
            Dictionary with surge_crest_m, total_water_level_m, inverted_barometer_m,
            wind_setup_m.
        """
        # 1. Inverted Barometer Effect (IBE) ~ 1 cm per 1 hPa pressure drop below 1010 hPa
        p_drop_hpa = max(0.0, 1010.0 - p_cen_hpa)
        ibe_m = 0.010 * p_drop_hpa

        # 2. Wind Setup on Continental Shelf
        # Attenuation based on distance of eye from coast
        # Surge is maximized right near landfall (distance ~ 0 to 40km offshore)
        dist_factor = math.exp(-((max(0.0, coastal_distance_km - 15.0) / 75.0) ** 2))

        v_max_ms = v_max_kt * 0.514444
        wind_stress = cls.RHO_AIR * cls.DRAG_COEFF * (v_max_ms**2)
        wind_setup_raw = (wind_stress * (shelf_width_km * 1000.0)) / (
            cls.RHO_WATER * cls.G_ACCEL * max(5.0, mean_shelf_depth_m)
        )
        wind_setup_m = wind_setup_raw * dist_factor

        surge_crest_m = round(max(0.0, ibe_m + wind_setup_m), 2)
        total_water_level_m = round(surge_crest_m + astronomical_tide_m, 2)

        return {
            "inverted_barometer_m": round(ibe_m, 2),
            "wind_setup_m": round(wind_setup_m, 2),
            "surge_crest_m": surge_crest_m,
            "astronomical_tide_m": round(astronomical_tide_m, 2),
            "total_water_level_m": total_water_level_m,
        }

    @classmethod
    def get_site_flood_depth(
        cls,
        site_elevation_m: float,
        total_water_level_m: float,
        dist_from_coastline_km: float,
    ) -> float:
        """Estimates overland inundation depth at a specific site elevation."""
        if dist_from_coastline_km > 25.0:
            return 0.0

        # Surge attenuates inland at roughly 0.15m to 0.35m per kilometer inland depending on vegetation/terrain
        attenuation_rate = 0.18  # meters per km inland
        inland_water_head = max(0.0, total_water_level_m - (dist_from_coastline_km * attenuation_rate))
        depth_m = max(0.0, inland_water_head - site_elevation_m)
        return round(depth_m, 2)
