"""VAYU-RAKSHA Holland (1980) Parametric Wind Field Model.

Provides numerical wind velocity and radial pressure profiles around the cyclone center,
including forward storm translation asymmetry and surface boundary layer reduction.
"""

from typing import Dict, Tuple
import math


class HollandWindModel:
    """Holland (1980) parametric vortex engine."""

    RHO_AIR: float = 1.15  # kg/m^3
    P_ENV: float = 1010.0  # Ambient sea-level pressure in hPa
    OMEGA: float = 7.2921e-5  # Earth rotation rate in rad/s

    @staticmethod
    def haversine_km(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
        """Calculates great-circle distance in kilometers."""
        r = 6371.0
        phi1 = math.radians(lat1)
        phi2 = math.radians(lat2)
        dphi = math.radians(lat2 - lat1)
        dlam = math.radians(lon2 - lon1)

        a = math.sin(dphi / 2.0) ** 2 + math.cos(phi1) * math.cos(phi2) * math.sin(dlam / 2.0) ** 2
        return 2.0 * r * math.asin(math.sqrt(max(0.0, min(1.0, a))))

    @staticmethod
    def bearing_deg(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
        """Calculates initial compass bearing from (lat1, lon1) to (lat2, lon2)."""
        phi1 = math.radians(lat1)
        phi2 = math.radians(lat2)
        dlam = math.radians(lon2 - lon1)

        x = math.sin(dlam) * math.cos(phi2)
        y = math.cos(phi1) * math.sin(phi2) - math.sin(phi1) * math.cos(phi2) * math.cos(dlam)
        initial_bearing = math.atan2(x, y)
        return (math.degrees(initial_bearing) + 360.0) % 360.0

    @classmethod
    def compute_holland_b(cls, p_cen: float, v_max_ms: float, r_max_km: float) -> float:
        """Calculates Holland shape parameter B, clamped to meteorological limits [1.0, 2.5]."""
        delta_p = max(5.0, cls.P_ENV - p_cen) * 100.0  # Pascals
        # Empirical Holland relation: B = (v_max^2 * rho * e) / delta_p
        b_est = (v_max_ms**2 * cls.RHO_AIR * math.e) / delta_p
        return max(1.0, min(2.5, b_est))

    @classmethod
    def get_surface_wind_at_point(
        cls,
        point_lat: float,
        point_lon: float,
        center_lat: float,
        center_lon: float,
        p_cen_hpa: float,
        v_max_kt: float,
        r_max_km: float = 35.0,
        forward_speed_kmh: float = 18.0,
        forward_heading_deg: float = 330.0,
    ) -> Dict[str, float]:
        """Calculates surface 10-meter 10-minute sustained wind at a target coordinate.

        Returns:
            Dictionary with wind_kt, wind_kmh, radial_dist_km, gale_exceeded (34kt),
            hurricane_exceeded (64kt).
        """
        r_km = cls.haversine_km(center_lat, center_lon, point_lat, point_lon)
        # Avoid singularity at exact center
        r_clamped = max(0.5, r_km)

        v_max_ms = v_max_kt * 0.514444
        b_param = cls.compute_holland_b(p_cen_hpa, v_max_ms, r_max_km)

        # Coriolis parameter f at center latitude
        f_coriolis = 2.0 * cls.OMEGA * math.sin(math.radians(center_lat))

        # Radial scale ratio
        ratio = (r_max_km / r_clamped) ** b_param
        delta_p_pa = max(5.0, cls.P_ENV - p_cen_hpa) * 100.0

        # Holland gradient wind equation
        term1 = (b_param / cls.RHO_AIR) * ratio * delta_p_pa * math.exp(-ratio)
        term2 = ((r_clamped * 1000.0 * f_coriolis) / 2.0) ** 2

        radicand = max(0.0, term1 + term2)
        v_gradient_ms = math.sqrt(radicand) - ((r_clamped * 1000.0 * f_coriolis) / 2.0)
        v_gradient_ms = max(0.0, v_gradient_ms)

        # Surface reduction (typically 0.80 to 0.85 over coastal waters / low roughness land)
        surface_reduction = 0.82
        v_surface_ms = v_gradient_ms * surface_reduction

        # Add forward speed asymmetry (right-front quadrant enhancement in Northern Hemisphere)
        point_bearing = cls.bearing_deg(center_lat, center_lon, point_lat, point_lon)
        relative_angle = math.radians(point_bearing - forward_heading_deg)
        # Asymmetric translation component: forward speed projected perpendicularly to radius
        v_forward_ms = (forward_speed_kmh / 3.6) * 0.5 * math.sin(relative_angle)

        total_v_ms = max(0.0, v_surface_ms + v_forward_ms)
        total_v_kt = total_v_ms / 0.514444
        total_v_kmh = total_v_ms * 3.6

        return {
            "wind_kt": round(total_v_kt, 1),
            "wind_kmh": round(total_v_kmh, 1),
            "radial_distance_km": round(r_km, 2),
            "gale_exceeded": total_v_kt >= 34.0,
            "storm_force_exceeded": total_v_kt >= 48.0,
            "hurricane_force_exceeded": total_v_kt >= 64.0,
        }
