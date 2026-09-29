import json
from collections.abc import Iterator, Mapping, Sequence

import httpx
import pytest
import respx

from shadowcast_geo.config import IBTRACS_NI_CSV, OSDMA_SHELTERS_URL, OVERPASS_URLS, Region, Settings
from shadowcast_geo.inputs import (
    download,
    fetch_osdma_shelters,
    fetch_osm_assets,
    fetch_osm_roads,
    load_assets,
    load_best_track,
)

REGION = Region("test", "Test coast", (19.0, 85.0, 21.0, 87.0), osdma_districts=("PURI", "GANJAM"))
MIRRORS = ("https://mirror-a.test/x", "https://mirror-b.test/x")


@pytest.fixture
def client() -> Iterator[httpx.Client]:
    with httpx.Client() as http:
        yield http


def test_download_caches_after_success(client: httpx.Client, settings: Settings, respx_mock: respx.MockRouter) -> None:
    route = respx_mock.get(MIRRORS[0]).mock(side_effect=[httpx.Response(503), httpx.Response(200, content=b"data")])

    assert download(client, settings, "x.bin", MIRRORS) == b"data"
    assert download(client, settings, "x.bin", MIRRORS) == b"data"

    assert route.call_count == 2
    assert (settings.cache_dir / "x.bin").read_bytes() == b"data"


def test_download_falls_back_to_next_mirror(
    client: httpx.Client, settings: Settings, respx_mock: respx.MockRouter
) -> None:
    respx_mock.post(MIRRORS[0]).mock(side_effect=httpx.ConnectError("down"))
    mirror_b = respx_mock.post(MIRRORS[1]).mock(return_value=httpx.Response(200, content=b"ok"))

    assert download(client, settings, "y.bin", MIRRORS, method="POST", data={"q": "1"}) == b"ok"
    assert mirror_b.calls.last.request.content == b"q=1"


def test_download_skips_missing_url_without_retrying(
    client: httpx.Client, settings: Settings, respx_mock: respx.MockRouter
) -> None:
    missing = respx_mock.get(MIRRORS[0]).mock(return_value=httpx.Response(404))
    respx_mock.get(MIRRORS[1]).mock(return_value=httpx.Response(200, content=b"renamed"))

    assert download(client, settings, "w.bin", MIRRORS) == b"renamed"
    assert missing.call_count == 1


@pytest.mark.parametrize(
    ("status", "error"), [(502, httpx.HTTPStatusError), (400, httpx.HTTPStatusError), (404, httpx.HTTPStatusError)]
)
def test_download_raises_after_all_attempts(
    client: httpx.Client, settings: Settings, respx_mock: respx.MockRouter, status: int, error: type[Exception]
) -> None:
    respx_mock.get(url__startswith="https://mirror-").mock(return_value=httpx.Response(status))

    with pytest.raises(error):
        download(client, settings, "z.bin", MIRRORS)

    assert not (settings.cache_dir / "z.bin").exists()


IBTRACS = (
    "SID,SEASON,NAME,ISO_TIME,LAT,LON,USA_WIND,USA_RMW,"
    + ",".join(f"USA_R{b}_{q}" for b in (34, 50, 64) for q in ("NE", "SE", "SW", "NW"))
    + "\n"
    + ",".join(["", "Year", "", "", "deg", "deg", "kts", "nmile"] + ["nmile"] * 12)
    + "\n"
    + "1,2019,FANI,2019-05-02 12:00:00,17.6,84.8,150,12,"
    + ",".join(["155"] * 4 + ["80"] * 4 + ["50", " ", "45", "40"])
    + "\n"
    + "1,2019,FANI,2019-05-02 15:00:00,17.9,84.9, ,12,"
    + ",".join([" "] * 12)
    + "\n"
)


def test_load_best_track(client: httpx.Client, settings: Settings, respx_mock: respx.MockRouter) -> None:
    respx_mock.get(IBTRACS_NI_CSV).mock(return_value=httpx.Response(200, text=IBTRACS))

    fixes = load_best_track(client, settings, "FANI", 2019)

    assert fixes == [
        {
            "time": "2019-05-02T12:00:00Z",
            "lat": 17.6,
            "lon": 84.8,
            "vmax_kt": 150.0,
            "rmw_km": 22.2,
            "r34_km": [287.1, 287.1, 287.1, 287.1],
            "r50_km": [148.2, 148.2, 148.2, 148.2],
            "r64_km": [92.6, None, 83.3, 74.1],
        }
    ]
    with pytest.raises(ValueError, match="AMPHAN 2020 not found"):
        load_best_track(client, settings, "AMPHAN", 2020)


def test_fetch_osm_assets(client: httpx.Client, settings: Settings, respx_mock: respx.MockRouter) -> None:
    elements = [
        {"type": "node", "id": 1, "lat": 19.8, "lon": 85.8, "tags": {"power": "substation", "name": "Puri"}},
        {
            "type": "way",
            "id": 2,
            "center": {"lat": 19.9, "lon": 85.9},
            "tags": {"amenity": "hospital", "name:en": "DHH"},
        },
        {"type": "node", "id": 3, "lat": 19.7, "lon": 85.7, "tags": {"amenity": "cafe"}},
        {"type": "relation", "id": 4, "tags": {"amenity": "school"}},
    ]
    route = respx_mock.post(OVERPASS_URLS[0]).mock(return_value=httpx.Response(200, json={"elements": elements}))

    assets = fetch_osm_assets(client, settings, REGION)

    assert assets.to_dict("records") == [
        {
            "asset_id": "osm:node/1",
            "kind": "substation",
            "name": "Puri",
            "source": "OpenStreetMap",
            "lat": 19.8,
            "lon": 85.8,
        },
        {
            "asset_id": "osm:way/2",
            "kind": "hospital",
            "name": "DHH",
            "source": "OpenStreetMap",
            "lat": 19.9,
            "lon": 85.9,
        },
    ]
    assert b"19.0%2C85.0%2C21.0%2C87.0" in route.calls.last.request.content


def _osdma_page(shelters: Sequence[Mapping[str, object]]) -> str:
    body = ",\n".join(json.dumps(s) for s in shelters)
    return f"<script>\n  var shelters1 = [\n{body},\n  ];\n</script>"


def test_fetch_osdma_shelters(client: httpx.Client, settings: Settings, respx_mock: respx.MockRouter) -> None:
    shelter = {"name": "TONDAHAR", "lat": 19.904438, "lon": 86.221331, "village": "ASTARANGA", "shelter": "NCRMP"}
    outside = {**shelter, "lat": 0, "lon": 0}

    def serve(request: httpx.Request) -> httpx.Response:
        page = _osdma_page([shelter, outside]) if request.url.params["district"] == "PURI" else "<html></html>"
        return httpx.Response(200, text=page)

    respx_mock.get(url__startswith=OSDMA_SHELTERS_URL).mock(side_effect=serve)

    shelters = fetch_osdma_shelters(client, settings, REGION)

    assert shelters.to_dict("records") == [
        {
            "asset_id": "osdma:PURI:19.90444,86.22133",
            "kind": "cyclone_shelter",
            "name": "Tondahar shelter (Astaranga)",
            "source": "OSDMA (NCRMP)",
            "lat": 19.904438,
            "lon": 86.221331,
        }
    ]


def test_load_assets_merges_and_deduplicates(
    client: httpx.Client, settings: Settings, respx_mock: respx.MockRouter
) -> None:
    node = {"type": "node", "id": 1, "lat": 19.8, "lon": 85.8, "tags": {"power": "substation"}}
    respx_mock.post(OVERPASS_URLS[0]).mock(return_value=httpx.Response(200, json={"elements": [node, node]}))
    respx_mock.get(url__startswith=OSDMA_SHELTERS_URL).mock(return_value=httpx.Response(200, text="<html></html>"))

    assets = load_assets(client, settings, REGION)

    assert assets["asset_id"].tolist() == ["osm:node/1"]
    assert assets.loc[0, "name"] is None


def test_load_assets_empty_region(client: httpx.Client, settings: Settings, respx_mock: respx.MockRouter) -> None:
    respx_mock.post(OVERPASS_URLS[0]).mock(return_value=httpx.Response(200, json={"elements": []}))
    empty_region = Region("none", "Nowhere", (0.0, 0.0, 0.1, 0.1))

    assets = load_assets(client, settings, empty_region)

    assert assets.empty
    assert list(assets.columns) == ["asset_id", "kind", "name", "source", "lat", "lon"]


def test_fetch_osm_roads_keeps_ways_with_geometry(
    client: httpx.Client, settings: Settings, respx_mock: respx.MockRouter
) -> None:
    elements = [
        {"type": "way", "id": 7, "tags": {"highway": "trunk", "ref": "NH316", "name": "Puri-Konark Marine Drive"},
         "geometry": [{"lat": 19.8, "lon": 85.8}, {"lat": 19.85, "lon": 85.9}]},
        {"type": "way", "id": 8, "tags": {"highway": "primary", "name:en": "SH 13"},
         "geometry": [{"lat": 20.0, "lon": 86.0}]},
    ]  # fmt: skip
    route = respx_mock.post(OVERPASS_URLS[0]).mock(return_value=httpx.Response(200, json={"elements": elements}))

    roads = fetch_osm_roads(client, settings, REGION)

    assert roads == [
        {"road_id": "osm:way/7", "name": "Puri-Konark Marine Drive", "ref": "NH316", "highway": "trunk",
         "coords": [[19.8, 85.8], [19.85, 85.9]]},
    ]  # fmt: skip
    assert "motorway%7Ctrunk%7Cprimary" in route.calls.last.request.content.decode()
