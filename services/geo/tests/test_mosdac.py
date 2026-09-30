"""Tests for ISRO MOSDAC client (no real API calls)."""
import os
from datetime import datetime

from shadowcast_geo.mosdac import (
    MOSDACCycloneProduct,
    build_isro_data_citation,
    fetch_bof_sst_anomaly,
    fetch_cyclone_intensity,
)


def test_fetch_intensity_no_token():
    """Without token, should return demo product (not None)."""
    os.environ.pop("MOSDAC_TOKEN", None)
    product = fetch_cyclone_intensity("FANI")
    assert product is not None
    assert isinstance(product, MOSDACCycloneProduct)
    assert product.dvt_intensity_kt > 0


def test_demo_product_fields():
    product = fetch_cyclone_intensity("FANI")
    assert product is not None
    assert product.storm_name in ("FANI", "fani")
    assert isinstance(product.valid_time, datetime)
    assert -90 <= product.lat <= 90
    assert 0 <= product.lon <= 180


def test_sst_anomaly_no_token():
    result = fetch_bof_sst_anomaly(16.5, 86.8)
    assert result is not None
    assert "sst_c" in result
    assert "ri_risk" in result


def test_citation_dict():
    citation = build_isro_data_citation()
    assert "INSAT-3DS" in citation
    assert "RISAT-1A" in citation
    assert "Bhuvan" in citation
    assert "mosdac.gov.in" in citation["INSAT-3DS"]


def test_ri_risk_flag():
    result = fetch_bof_sst_anomaly(16.5, 86.8)
    assert result is not None
    assert isinstance(result["ri_risk"], bool)
