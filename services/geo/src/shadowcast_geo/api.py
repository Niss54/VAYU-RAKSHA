"""ShadowCast geo API: serves built scenarios and forecast replays, and computes hazard on demand.

All built artifacts are loaded into memory at startup (a few MB per scenario), so request handlers never block on
storage; on-demand hazard is a small vectorised numpy computation.
"""

from __future__ import annotations

import asyncio
import time
from collections.abc import AsyncGenerator, Sequence
from contextlib import asynccontextmanager
from dataclasses import dataclass
from datetime import UTC, datetime
from typing import Annotated, Any, cast

import numpy as np
from fastapi import APIRouter, Depends, FastAPI, HTTPException, Query, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from numpy.typing import NDArray
from pydantic import BaseModel, Field

from shadowcast_geo.artifacts import ArtifactStore, GcsArtifacts, artifact_store
from shadowcast_geo.config import EVIDENCE_IMAGES, Settings
from shadowcast_geo.hazard import Track, track_position, wind_at, wind_timeline
from shadowcast_geo.live import ArchiveReader, digest
from shadowcast_geo.models import (
    Asset,
    AssetDetail,
    AssetPage,
    ForecastAsset,
    ForecastAssetPage,
    ForecastSummary,
    HazardSnapshot,
    LiveFeed,
    ScenarioDetail,
    ScenarioSummary,
    StormPosition,
    SurgePoint,
    TimelinePoint,
)


@dataclass(frozen=True)
class LoadedForecast:
    """An as-issued ensemble forecast replay held in memory.

    Attributes:
        summary: Forecast metadata.
        assets: Assets in forecast rank order.
        tracks: Member tracks (``member`` and ``fixes``).
    """

    summary: ForecastSummary
    assets: list[ForecastAsset]
    tracks: list[dict[str, Any]]


@dataclass(frozen=True)
class LoadedScenario:
    """A built scenario held in memory.

    Attributes:
        detail: Scenario metadata, model and skill.
        fixes: Raw track fix records (for GeoJSON output).
        track: Parsed track for on-demand hazard.
        assets: Assets in rank order.
        by_id: Asset lookup by id.
        lat: Asset latitudes in rank order.
        lon: Asset longitudes in rank order.
        backtest: Backtest artifact.
        surge: Peak modelled surge along the open coast.
        roads: Arterial roads with their status, as GeoJSON.
        evidence: Before/after satellite images (PNG) by name.
        forecasts: Ensemble forecast replays keyed by forecast key.
    """

    detail: ScenarioDetail
    fixes: list[dict[str, Any]]
    track: Track
    assets: list[Asset]
    by_id: dict[str, Asset]
    lat: NDArray[np.float64]
    lon: NDArray[np.float64]
    backtest: dict[str, Any]
    surge: list[SurgePoint]
    roads: dict[str, Any]
    evidence: dict[str, bytes]
    forecasts: dict[str, LoadedForecast]


class AssetQuery(BaseModel):
    """Filters shared by the asset listing endpoints."""

    kind: list[str] | None = Field(default=None, description="Filter by asset kind (repeatable)")
    q: str | None = Field(default=None, min_length=2, description="Case-insensitive substring of the name or id")
    min_score: float = Field(default=0.0, ge=0, le=1, description="Minimum priority score")
    limit: int = Field(default=100, ge=1, le=5000)
    offset: int = Field(default=0, ge=0)


def paginate[AssetT: Asset](items: Sequence[AssetT], query: AssetQuery) -> tuple[int, list[AssetT]]:
    """Filter rank-ordered assets by kind, name/id search and minimum score, then slice a page.

    Args:
        items: Assets in rank order.
        query: Filters and paging.

    Returns:
        tuple[int, list[AssetT]]: Total matches and the requested page.
    """
    needle = query.q.casefold() if query.q else None
    selected = [
        a
        for a in items
        if (not query.kind or a.kind in query.kind)
        and a.score >= query.min_score
        and (needle is None or needle in f"{a.name or ''} {a.asset_id}".casefold())
    ]
    return len(selected), selected[query.offset : query.offset + query.limit]


def load_scenarios(store: ArtifactStore) -> dict[str, LoadedScenario]:
    """Load every scenario listed in the artifact index, with its forecast replays.

    Args:
        store: Artifact store.

    Returns:
        dict[str, LoadedScenario]: Scenarios keyed by id (empty when nothing has been built yet).
    """
    if not store.exists("scenarios/index.json"):
        return {}
    loaded: dict[str, LoadedScenario] = {}
    for entry in store.read_json("scenarios/index.json"):
        prefix = f"scenarios/{entry['id']}"
        fixes = store.read_json(f"{prefix}/track.json")
        assets = [Asset.model_validate(record) for record in store.read_json(f"{prefix}/assets.json")]
        detail = ScenarioDetail.model_validate(store.read_json(f"{prefix}/scenario.json"))
        forecasts = {
            summary.key: LoadedForecast(
                summary=summary,
                assets=[
                    ForecastAsset.model_validate(record)
                    for record in store.read_json(f"{prefix}/forecasts/{summary.key}/assets.json")
                ],
                tracks=store.read_json(f"{prefix}/forecasts/{summary.key}/tracks.json"),
            )
            for summary in detail.forecasts
        }
        loaded[entry["id"]] = LoadedScenario(
            detail=detail,
            fixes=fixes,
            track=Track.from_records(fixes),
            assets=assets,
            by_id={asset.asset_id: asset for asset in assets},
            lat=np.array([asset.lat for asset in assets]),
            lon=np.array([asset.lon for asset in assets]),
            backtest=store.read_json(f"{prefix}/backtest.json"),
            surge=[SurgePoint.model_validate(point) for point in store.read_json(f"{prefix}/surge.json")],
            roads=store.read_json(f"{prefix}/roads.json"),
            evidence={name: store.read_bytes(f"{prefix}/evidence/{name}.png") for name in EVIDENCE_IMAGES},
            forecasts=forecasts,
        )
    return loaded


def loaded_scenarios(request: Request) -> dict[str, LoadedScenario]:
    """Scenarios loaded at startup (dependency).

    Args:
        request: Current request.

    Returns:
        dict[str, LoadedScenario]: Scenarios keyed by id.
    """
    return cast("dict[str, LoadedScenario]", request.app.state.scenarios)


def get_scenario(
    scenario_id: str, scenarios: Annotated[dict[str, LoadedScenario], Depends(loaded_scenarios)]
) -> LoadedScenario:
    """Resolve the ``scenario_id`` path parameter (dependency).

    Args:
        scenario_id: Scenario id from the URL.
        scenarios: Loaded scenarios.

    Returns:
        LoadedScenario: The scenario.

    Raises:
        HTTPException: 404 when the scenario is unknown.
    """
    if scenario_id not in scenarios:
        raise HTTPException(status_code=404, detail=f"unknown scenario {scenario_id!r}")
    return scenarios[scenario_id]


ScenarioDep = Annotated[LoadedScenario, Depends(get_scenario)]


def get_forecast(scenario: ScenarioDep, key: str) -> LoadedForecast:
    """Resolve the ``key`` path parameter of a scenario's forecast replay (dependency).

    Args:
        scenario: Resolved scenario.
        key: Forecast key from the URL, e.g. ``20241023T00Z``.

    Returns:
        LoadedForecast: The forecast replay.

    Raises:
        HTTPException: 404 when the forecast is unknown.
    """
    if key not in scenario.forecasts:
        raise HTTPException(status_code=404, detail=f"unknown forecast {key!r} for {scenario.detail.id!r}")
    return scenario.forecasts[key]


ForecastDep = Annotated[LoadedForecast, Depends(get_forecast)]
AssetQueryDep = Annotated[AssetQuery, Query()]
router = APIRouter()


@router.get("/health")
async def health(scenarios: Annotated[dict[str, LoadedScenario], Depends(loaded_scenarios)]) -> dict[str, Any]:
    """Liveness probe listing the scenarios loaded in memory."""
    return {"status": "ok", "scenarios": sorted(scenarios)}


@dataclass
class LiveCache:
    """The live digest and when it was read; one reader at a time refreshes it."""

    archive: ArchiveReader
    ttl_s: float
    feed: LiveFeed | None = None
    read_at: float = 0.0
    lock: asyncio.Lock | None = None


@router.get("/live")
async def live(request: Request) -> LiveFeed:
    """Active cyclones (GDACS) and official warnings (NDMA SACHET), from the feed archiver's newest run."""
    cache = cast("LiveCache", request.app.state.live)
    cache.lock = cache.lock or asyncio.Lock()
    async with cache.lock:
        if cache.feed is None or time.monotonic() - cache.read_at > cache.ttl_s:
            cache.feed = LiveFeed.model_validate(await asyncio.to_thread(digest, cache.archive))
            cache.read_at = time.monotonic()
    return cache.feed


@router.get("/scenarios")
async def list_scenarios(
    scenarios: Annotated[dict[str, LoadedScenario], Depends(loaded_scenarios)],
) -> list[ScenarioSummary]:
    """Every built scenario."""
    return [ScenarioSummary.model_validate(s.detail.model_dump()) for s in scenarios.values()]


@router.get("/scenarios/{scenario_id}")
async def scenario_detail(scenario: ScenarioDep) -> ScenarioDetail:
    """Scenario metadata, calibrated outage model, backtest skill and forecast replays."""
    return scenario.detail


@router.get("/scenarios/{scenario_id}/track")
async def track_geojson(scenario: ScenarioDep) -> dict[str, Any]:
    """Storm track as a GeoJSON FeatureCollection: the path as a LineString plus one Point per fix."""
    line = {
        "type": "Feature",
        "geometry": {"type": "LineString", "coordinates": [[f["lon"], f["lat"]] for f in scenario.fixes]},
        "properties": {"kind": "path"},
    }
    points = [
        {
            "type": "Feature",
            "geometry": {"type": "Point", "coordinates": [f["lon"], f["lat"]]},
            "properties": {"kind": "fix", **{k: v for k, v in f.items() if k not in ("lat", "lon")}},
        }
        for f in scenario.fixes
    ]
    return {"type": "FeatureCollection", "features": [line, *points]}


@router.get("/scenarios/{scenario_id}/assets")
async def assets(scenario: ScenarioDep, query: AssetQueryDep) -> AssetPage:
    """Assets in priority order (best-track replay), optionally filtered by kind, name/id search and minimum score."""
    total, items = paginate(scenario.assets, query)
    return AssetPage(total=total, items=items)


@router.get("/scenarios/{scenario_id}/assets/{asset_id:path}")
async def asset_detail(scenario: ScenarioDep, asset_id: str) -> AssetDetail:
    """One asset with its modelled wind through the storm's life (15-minute steps)."""
    asset = scenario.by_id.get(asset_id)
    if asset is None:
        raise HTTPException(status_code=404, detail=f"unknown asset {asset_id!r}")
    times, winds = wind_timeline(asset.lat, asset.lon, scenario.track)
    timeline = [
        TimelinePoint(
            time=f"{np.datetime_as_string(t, unit='s')}Z", wind_kt=None if np.isnan(w) else round(float(w), 1)
        )
        for t, w in zip(times, winds, strict=True)
    ]
    return AssetDetail(asset=asset, timeline=timeline)


@router.get("/scenarios/{scenario_id}/hazard")
async def hazard(scenario: ScenarioDep, at: Annotated[datetime, Query(description="ISO 8601 time")]) -> HazardSnapshot:
    """Modelled wind at every asset (rank order) at one moment, plus the interpolated storm position."""
    at_utc = at.astimezone(UTC) if at.tzinfo else at.replace(tzinfo=UTC)
    position = track_position(scenario.track, at_utc)
    return HazardSnapshot(
        at=at_utc.strftime("%Y-%m-%dT%H:%M:%SZ"),
        storm=StormPosition.model_validate(position) if position else None,
        asset_ids=[a.asset_id for a in scenario.assets],
        wind_kt=np.round(wind_at(scenario.lat, scenario.lon, scenario.track, at_utc), 1).tolist(),
    )


@router.get("/scenarios/{scenario_id}/backtest")
async def backtest(scenario: ScenarioDep) -> dict[str, Any]:
    """Predicted outage probability vs observed night-light loss per substation, with skill metrics."""
    return scenario.backtest


@router.get("/scenarios/{scenario_id}/surge")
async def surge(scenario: ScenarioDep) -> list[SurgePoint]:
    """Peak modelled storm surge at every open-coast point of the region (best track)."""
    return scenario.surge


@router.get("/scenarios/{scenario_id}/roads")
async def roads(scenario: ScenarioDep) -> dict[str, Any]:
    """Arterial roads as GeoJSON LineStrings: status (cut, at risk, open), causes and when each closes (best track)."""
    return scenario.roads


@router.get("/scenarios/{scenario_id}/evidence/{name}.png", response_class=Response)
async def evidence(scenario: ScenarioDep, name: str) -> Response:
    """Satellite night lights over the region before (``night-lights-pre``) or after (``night-lights-post``)."""
    if name not in scenario.evidence:
        raise HTTPException(status_code=404, detail=f"unknown image {name!r}")
    return Response(scenario.evidence[name], media_type="image/png", headers={"Cache-Control": "public, max-age=86400"})


@router.get("/scenarios/{scenario_id}/forecasts")
async def forecasts(scenario: ScenarioDep) -> list[ForecastSummary]:
    """As-issued ECMWF ensemble forecasts replayed for this scenario, in issue order."""
    return [forecast.summary for forecast in scenario.forecasts.values()]


@router.get("/scenarios/{scenario_id}/forecasts/{key}/tracks")
async def forecast_tracks(forecast: ForecastDep) -> dict[str, Any]:
    """Ensemble member tracks as a GeoJSON FeatureCollection of LineStrings (the "spaghetti plot")."""
    features = [
        {
            "type": "Feature",
            "geometry": {"type": "LineString", "coordinates": [[f["lon"], f["lat"]] for f in member["fixes"]]},
            "properties": {
                "member": member["member"],
                "max_vmax_kt": max(f["vmax_kt"] for f in member["fixes"]),
                "times": [f["time"] for f in member["fixes"]],
            },
        }
        for member in forecast.tracks
    ]
    return {"type": "FeatureCollection", "features": features}


@router.get("/scenarios/{scenario_id}/forecasts/{key}/assets")
async def forecast_assets(forecast: ForecastDep, query: AssetQueryDep) -> ForecastAssetPage:
    """Assets ranked under one ensemble forecast, with member-agreement probabilities and gale arrival."""
    total, items = paginate(forecast.assets, query)
    return ForecastAssetPage(total=total, items=items)


def create_app(
    settings: Settings | None = None, store: ArtifactStore | None = None, archive: ArchiveReader | None = None
) -> FastAPI:
    """Build the FastAPI application.

    Args:
        settings: Settings (defaults to the environment).
        store: Artifact store (defaults to the one selected by ``settings``).
        archive: Feed archive for the live picture (defaults to ``settings.archive_bucket``).

    Returns:
        FastAPI: The configured application.
    """
    settings = settings or Settings.from_env()

    @asynccontextmanager
    async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
        app.state.scenarios = load_scenarios(store or artifact_store(settings))
        app.state.live = LiveCache(archive or GcsArtifacts(settings.archive_bucket), settings.live_ttl_s)
        yield

    app = FastAPI(
        title="ShadowCast geo API",
        version="0.2.0",
        summary="Impact-based cyclone forecasting per asset, verified against satellite ground truth.",
        lifespan=lifespan,
    )
    app.add_middleware(GZipMiddleware, minimum_size=1024)
    app.add_middleware(CORSMiddleware, allow_origins=list(settings.allowed_origins), allow_methods=["GET"])
    app.include_router(router)
    return app
