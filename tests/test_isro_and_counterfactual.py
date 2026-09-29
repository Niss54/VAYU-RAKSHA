"""Test suite for ISRO clients and Counterfactual Engine."""

import sys
from pathlib import Path

src_dir = Path(__file__).resolve().parent.parent / "services" / "geo" / "src"
sys.path.insert(0, str(src_dir))

from vayu_raksha.data.mosdac_client import IsroMosdacClient
from vayu_raksha.data.risat_client import IsroRisatClient
from vayu_raksha.engine.holland_wind import HollandWindModel
from vayu_raksha.engine.surge_model import StormSurgeModel


def test_isro_mosdac_and_risat():
    mosdac = IsroMosdacClient()
    insat_data = mosdac.fetch_insat3ds_cyclone_telemetry("FANI_2019")
    assert insat_data["satellite"] == "INSAT-3DS (Geostationary 82.0°E)"
    assert insat_data["dvorak_current_intensity_ci"] == 6.0
    assert insat_data["cloud_top_temperature_celsius"] < -70.0

    risat = IsroRisatClient()
    sar_data = risat.fetch_disaster_pass_flood_mask("OD_PURI")
    assert sar_data["satellite"] == "ISRO EOS-04 (RISAT-1A)"
    assert sar_data["spatial_resolution_meters"] == 3.0
    assert sar_data["total_sar_water_extent_sqkm"] > 300.0


def test_holland_and_surge_physics():
    wind = HollandWindModel.get_surface_wind_at_point(
        point_lat=19.8,
        point_lon=85.8,
        center_lat=19.45,
        center_lon=85.58,
        p_cen_hpa=932.0,
        v_max_kt=115.0,
    )
    assert wind["wind_kt"] > 50.0
    assert wind["radial_distance_km"] > 0.0

    surge = StormSurgeModel.compute_coastal_surge(
        p_cen_hpa=932.0,
        v_max_kt=115.0,
        coastal_distance_km=15.0,
    )
    assert surge["surge_crest_m"] > 1.5
    assert surge["total_water_level_m"] > surge["surge_crest_m"]


if __name__ == "__main__":
    test_isro_mosdac_and_risat()
    test_holland_and_surge_physics()
    print("=== ISRO & PHYSICS TESTS PASSED ===")
