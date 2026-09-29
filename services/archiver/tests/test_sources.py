import json

import httpx
import pytest
import respx

from shadowcast_archiver.config import COASTAL_POINTS, GDACS_API, IBTRACS_ACTIVE_CSV, OPEN_METEO_ENSEMBLE
from shadowcast_archiver.sources import (
    SOURCES,
    FetchContext,
    fetch,
    gdacs_cyclones,
    ibtracs_active,
    sachet_alerts,
    weathernext2_ensemble,
)

URL = "https://example.test/feed"


@pytest.mark.parametrize(
    ("responses", "allow_missing", "expected_status", "expected_calls"),
    [
        ([httpx.Response(200, text="ok")], False, 200, 1),
        ([httpx.Response(503), httpx.Response(429), httpx.Response(200, text="ok")], False, 200, 3),
        ([httpx.ConnectError("boom"), httpx.Response(200, text="ok")], False, 200, 2),
        ([httpx.Response(404)], True, None, 1),
    ],
)
async def test_fetch_success_paths(
    ctx: FetchContext,
    respx_mock: respx.MockRouter,
    responses: list[httpx.Response | Exception],
    allow_missing: bool,
    expected_status: int | None,
    expected_calls: int,
) -> None:
    route = respx_mock.get(URL).mock(side_effect=responses)

    response = await fetch(ctx, URL, allow_missing=allow_missing)  # type: ignore[call-overload]

    assert (response.status_code if response else None) == expected_status
    assert route.call_count == expected_calls


@pytest.mark.parametrize(
    ("responses", "error", "expected_calls"),
    [
        ([httpx.Response(404)], httpx.HTTPStatusError, 1),
        ([httpx.Response(400)], httpx.HTTPStatusError, 1),
        ([httpx.Response(502)] * 3, httpx.HTTPStatusError, 3),
        ([httpx.ReadTimeout("slow")] * 3, httpx.ReadTimeout, 3),
    ],
)
async def test_fetch_failure_paths(
    ctx: FetchContext,
    respx_mock: respx.MockRouter,
    responses: list[httpx.Response | Exception],
    error: type[Exception],
    expected_calls: int,
) -> None:
    route = respx_mock.get(URL).mock(side_effect=responses)

    with pytest.raises(error):
        await fetch(ctx, URL)

    assert route.call_count == expected_calls


def _tc_feature(eventid: int, lon: float, lat: float) -> dict[str, object]:
    return {
        "type": "Feature",
        "geometry": {"type": "Point", "coordinates": [lon, lat]},
        "properties": {"eventid": eventid, "episodeid": 6},
    }


async def test_gdacs_cyclones_keeps_north_indian_events(ctx: FetchContext, respx_mock: respx.MockRouter) -> None:
    listing = {"features": [_tc_feature(1001326, 83.7, 18.1), _tc_feature(1001400, -75.0, 25.0)]}
    search = respx_mock.get(f"{GDACS_API}/events/geteventlist/SEARCH").mock(
        return_value=httpx.Response(200, json=listing)
    )
    respx_mock.get(f"{GDACS_API}/events/geteventdata").mock(return_value=httpx.Response(200, json={"id": "d"}))
    respx_mock.get(f"{GDACS_API}/polygons/getgeometry").mock(return_value=httpx.Response(200, json={"id": "g"}))

    artifacts = await gdacs_cyclones(ctx)

    assert [a.name for a in artifacts] == ["events.json", "1001326-6/details.json", "1001326-6/geometry.json"]
    assert [f["properties"]["eventid"] for f in json.loads(artifacts[0].body)["features"]] == [1001326]
    assert search.calls.last.request.url.params["fromDate"] == "2026-09-16"


async def test_gdacs_cyclones_handles_no_events(ctx: FetchContext, respx_mock: respx.MockRouter) -> None:
    respx_mock.get(f"{GDACS_API}/events/geteventlist/SEARCH").mock(return_value=httpx.Response(404))

    artifacts = await gdacs_cyclones(ctx)

    assert [a.name for a in artifacts] == ["events.json"]
    assert json.loads(artifacts[0].body)["features"] == []


def _rss(*items: tuple[str, str]) -> str:
    entries = "".join(f"<item><guid>{guid}</guid><link>{link}</link></item>" for guid, link in items)
    return f"<?xml version='1.0' encoding='UTF-8'?><rss><channel>{entries}</channel></rss>"


async def test_sachet_alerts_archives_feeds_and_coastal_cap_documents(
    ctx: FetchContext, respx_mock: respx.MockRouter
) -> None:
    cap = "https://sachet.ndma.gov.in/cap_public_website/FetchXMLFile?identifier="
    feeds = {
        "india": _rss(("999", f"{cap}999")),
        "odisha": _rss(("111", f"{cap}111"), ("not-an-id", f"{cap}x")),
        "andhra": _rss(("111", f"{cap}111"), ("222", f"{cap}222")),
    }

    def serve_feed(request: httpx.Request) -> httpx.Response:
        slug = request.url.path.rsplit("rss_", 1)[1].removesuffix(".xml")
        return httpx.Response(200, text=feeds[slug]) if slug in feeds else httpx.Response(404)

    respx_mock.get(url__regex=r".*/rss/rss_\w+\.xml").mock(side_effect=serve_feed)
    documents = respx_mock.get(url__startswith=cap).mock(return_value=httpx.Response(200, text="<alert/>"))

    artifacts = await sachet_alerts(ctx)

    assert sorted(a.name for a in artifacts) == [
        "cap/111.xml",
        "cap/222.xml",
        "rss/andhra.xml",
        "rss/india.xml",
        "rss/odisha.xml",
    ]
    assert documents.call_count == 2


async def test_ibtracs_active(ctx: FetchContext, respx_mock: respx.MockRouter) -> None:
    respx_mock.get(IBTRACS_ACTIVE_CSV).mock(return_value=httpx.Response(200, text="SID,NAME\n"))

    artifacts = await ibtracs_active(ctx)

    assert [(a.name, a.body, a.content_type) for a in artifacts] == [("ibtracs_active.csv", b"SID,NAME\n", "text/csv")]


async def test_weathernext2_ensemble(ctx: FetchContext, respx_mock: respx.MockRouter) -> None:
    route = respx_mock.get(OPEN_METEO_ENSEMBLE).mock(return_value=httpx.Response(200, json=[{"hourly": {}}]))

    artifacts = await weathernext2_ensemble(ctx)

    params = route.calls.last.request.url.params
    body = json.loads(artifacts[0].body)
    assert params["models"] == "google_weathernext2_ensemble"
    assert params["forecast_days"] == "2"
    assert len(params["latitude"].split(",")) == len(COASTAL_POINTS)
    assert body["points"][0] == {"name": COASTAL_POINTS[0][0], "lat": COASTAL_POINTS[0][1], "lon": COASTAL_POINTS[0][2]}
    assert body["forecasts"] == [{"hourly": {}}]


def test_sources_registry() -> None:
    assert set(SOURCES) == {"gdacs", "sachet", "ibtracs", "weathernext2"}
