from datetime import UTC, date, datetime
from unittest.mock import MagicMock

import numpy as np
import pandas as pd
import pytest

from shadowcast_geo import earth

POINTS = pd.DataFrame({"lat": [19.8, 20.1], "lon": [85.8, 86.0]}, index=[10, 11])


@pytest.fixture
def ee(monkeypatch: pytest.MonkeyPatch) -> MagicMock:
    mock = MagicMock(name="ee")
    monkeypatch.setattr(earth, "ee", mock)
    return mock


def _features(*properties: dict[str, float | None]) -> dict[str, list[dict[str, dict[str, float | None]]]]:
    return {"features": [{"properties": {"i": i, **p}} for i, p in enumerate(properties)]}


def test_initialize(ee: MagicMock) -> None:
    earth.initialize("argmax-cyclone-2026")

    ee.Initialize.assert_called_once_with(project="argmax-cyclone-2026")


def test_enrich_adds_population_and_elevation(ee: MagicMock) -> None:
    population = ee.ImageCollection.return_value.filter.return_value.mosaic.return_value.select.return_value
    elevation = ee.Image.return_value.rename.return_value.unmask.return_value
    population.reduceRegions.return_value.getInfo.return_value = _features({"sum": 1200.0}, {"sum": None})
    elevation.reduceRegions.return_value.getInfo.return_value = _features({"mean": 3.5})

    enriched = earth.enrich(POINTS)

    assert enriched["population"].iloc[0] == 1200.0
    assert np.isnan(enriched["population"].iloc[1])
    assert enriched["elevation_m"].tolist()[0] == 3.5
    assert np.isnan(enriched["elevation_m"].iloc[1])
    ee.Geometry.Point.return_value.buffer.assert_called_with(2000)


def test_nightlight_images_share_one_scale(ee: MagicMock) -> None:
    median = ee.ImageCollection.return_value.map.return_value.filterDate.return_value.median.return_value
    median.visualize.return_value.getThumbURL.return_value = "https://earthengine.test/thumb.png"

    urls = earth.nightlight_image_urls(
        (19.0, 84.4, 21.7, 87.6), (date(2019, 4, 20), date(2019, 5, 2)), (date(2019, 5, 4), date(2019, 5, 11))
    )

    assert urls == ("https://earthengine.test/thumb.png", "https://earthengine.test/thumb.png")
    ee.Geometry.Rectangle.assert_called_once_with([84.4, 19.0, 87.6, 21.7])
    assert median.visualize.call_args.kwargs["max"] == 30.0


def test_nightlight_loss(ee: MagicMock) -> None:
    window = ee.ImageCollection.return_value.map.return_value.filterDate.return_value.median.return_value
    stacked = window.rename.return_value.addBands.return_value
    stacked.reduceRegions.return_value.getInfo.return_value = _features(
        {"pre": 10.0, "post": 1.0}, {"pre": 2.0, "post": 2.0}
    )

    result = earth.nightlight_loss(POINTS, (date(2019, 4, 20), date(2019, 5, 2)), (date(2019, 5, 4), date(2019, 5, 11)))

    assert result.index.tolist() == [10, 11]
    assert result["loss_pct"].tolist() == [90.0, 0.0]
    window_calls = ee.ImageCollection.return_value.map.return_value.filterDate.call_args_list
    assert [c.args for c in window_calls] == [("2019-04-20", "2019-05-02"), ("2019-05-04", "2019-05-11")]

    high_quality = ee.ImageCollection.return_value.map.call_args.args[0]
    image = MagicMock(name="image")
    high_quality(image)
    image.select.assert_any_call("Mandatory_Quality_Flag")
    image.select.return_value.lte.assert_called_once_with(1)


def test_districts_joins_each_point_to_its_adm2(ee: MagicMock) -> None:
    joined = ee.Join.saveFirst.return_value.apply.return_value
    joined.getInfo.return_value = {
        "features": [{"properties": {"i": 0, "district": {"properties": {"shapeName": "Puri"}}}}]
    }

    names = earth.districts(POINTS)

    ee.Join.saveFirst.assert_called_once_with("district")
    assert names.tolist() == ["Puri", None] and names.index.tolist() == [10, 11]


def test_observed_rain_sums_half_hourly_imerg(ee: MagicMock) -> None:
    total = ee.ImageCollection.return_value.filterDate.return_value.select.return_value.sum.return_value
    image = total.multiply.return_value.rename.return_value
    image.reduceRegions.return_value.getInfo.return_value = _features({"mean": 212.0}, {"mean": None})

    rain = earth.observed_rain(POINTS, datetime(2019, 4, 30, tzinfo=UTC), datetime(2019, 5, 6, tzinfo=UTC))

    total.multiply.assert_called_once_with(0.5)
    assert rain.index.tolist() == [10, 11]
    assert rain.iloc[0] == 212.0 and np.isnan(rain.iloc[1])


def test_relief_requests_the_region_plus_a_seaward_margin(ee: MagicMock) -> None:
    ee.data.computePixels.return_value = {"bedrock": np.array([[5, -20], [-40, -80]], dtype=np.int16)}

    grid = earth.relief((19.0, 84.4, 21.7, 87.6))

    request = ee.data.computePixels.call_args.args[0]
    assert request["grid"]["affineTransform"]["translateX"] == pytest.approx(84.4 - 2.5)
    assert request["grid"]["affineTransform"]["translateY"] == pytest.approx(21.7 + 2.5)
    assert request["grid"]["dimensions"] == {"width": 492, "height": 462}
    assert grid.cells.dtype == np.float64 and grid.cells[1, 1] == -80.0
    assert grid.cell_deg == pytest.approx(1 / 60)


def test_reductions_are_batched_under_the_earth_engine_limit(ee: MagicMock, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(earth, "EE_POINTS_PER_REQUEST", 1)
    elevation = ee.Image.return_value.rename.return_value.unmask.return_value
    elevation.reduceRegions.return_value.getInfo.side_effect = [
        {"features": [{"properties": {"i": 0, "mean": 2.0}}]},
        {"features": [{"properties": {"i": 1, "mean": 7.0}}]},
    ]

    heights = earth.ground_elevation(POINTS)

    assert heights.tolist() == [2.0, 7.0]
    assert elevation.reduceRegions.call_count == 2
