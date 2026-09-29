"""Offline scenario build.

For each scenario: storm track and assets → deterministic hazard → Earth Engine enrichment → night-light ground truth
→ outage model (fitted on the reference scenario, evaluated out of sample elsewhere) → ranking → JSON artifacts.
Scenarios with ECMWF forecast issue times are also replayed as-issued: every ensemble member's hazard is aggregated
into impact probabilities per asset.

Usage: ``python -m shadowcast_geo.build [scenario-id ...]`` (default: every registered scenario, reference first).
"""

from __future__ import annotations

import argparse
import logging
import math
import sys
from datetime import UTC, datetime, timedelta
from typing import Any, cast

import httpx
import numpy as np
import pandas as pd

from shadowcast_geo import earth
from shadowcast_geo.artifacts import ArtifactStore, artifact_store
from shadowcast_geo.calibration import (
    OutageModel,
    evaluate,
    fit_outage_model,
    loss_by_band,
    spatial_holdout,
    spearman,
)
from shadowcast_geo.config import (
    EVIDENCE_IMAGES,
    EXTREME_RAIN_MM,
    FLOOD_DEPTH_M,
    HOLDOUT_FOLDS,
    LIT_RADIANCE,
    LOSS_BANDS_KT,
    OUTAGE_LOSS_PCT,
    RAINFALL_WINDOW_DAYS,
    SCENARIOS,
    USER_AGENT,
    Scenario,
    Settings,
)
from shadowcast_geo.ensemble import ensemble_impact, load_ensemble, select_storm
from shadowcast_geo.hazard import Track, exposure, track_position
from shadowcast_geo.inputs import download, fetch_osm_roads, load_assets, load_best_track
from shadowcast_geo.insurance import best_track_triggers, forecast_triggers
from shadowcast_geo.ranking import rank_assets
from shadowcast_geo.roads import nearest_access, road_status, sample_roads
from shadowcast_geo.surge import coast_from_grid, coastal_surge, inundation

logger = logging.getLogger("shadowcast_geo.build")

MODEL_PATH = "models/outage.json"
HAZARD_BLOCK = 2000  # road samples per hazard computation
INDEX_PATH = "scenarios/index.json"
TIME_COLUMNS = ("peak_time", "closest_time", "band_entry", "gale_arrival", "access_closes")
ASSET_FIELDS = [
    "asset_id",
    "rank",
    "kind",
    "name",
    "source",
    "lat",
    "lon",
    "peak_wind_kt",
    "peak_time",
    "min_dist_km",
    "closest_time",
    "band_kt",
    "band_entry",
    "gale_arrival",
    "population",
    "elevation_m",
    "district",
    "coast_km",
    "surge_m",
    "flood_m",
    "rain_mm",
    "observed_rain_mm",
    "road_km",
    "access_road",
    "access_closes",
    "criticality",
    "p_outage",
    "score",
    "observed_loss_pct",
    "reasons",
]
SURGE_FIELDS = ["lat", "lon", "peak_m", "setup_m", "barometer_m", "peak_time"]
# Surge is modelled on the best track only: a forecast replay must not carry hindsight.
HINDSIGHT_FIELDS = ("coast_km", "surge_m", "flood_m", "observed_rain_mm", "road_km", "access_road", "access_closes")
FORECAST_FIELDS = [f for f in ASSET_FIELDS if f not in HINDSIGHT_FIELDS] + [
    "p_rain",
    "p34",
    "p64",
    "wind_p10",
    "wind_p90",
    "members",
]
STATIC_FIELDS = [
    "asset_id",
    "kind",
    "name",
    "source",
    "lat",
    "lon",
    "district",
    "population",
    "elevation_m",
    "observed_loss_pct",
]
ROUNDING = {
    "peak_wind_kt": 1,
    "min_dist_km": 1,
    "population": 0,
    "elevation_m": 1,
    "coast_km": 1,
    "surge_m": 2,
    "flood_m": 2,
    "rain_mm": 0,
    "road_km": 1,
    "observed_rain_mm": 0,
    "p_rain": 3,
    "peak_m": 2,
    "setup_m": 2,
    "barometer_m": 2,
    "p_outage": 4,
    "p34": 3,
    "p64": 3,
    "wind_p10": 1,
    "wind_p90": 1,
    "score": 4,
    "observed_loss_pct": 1,
    "ntl_pre": 3,
    "ntl_post": 3,
    "loss_pct": 1,
}


def json_safe(value: object) -> Any:
    """Recursively convert numpy scalars to Python types and non-finite floats to ``None`` for strict JSON.

    Args:
        value: Any nested structure of dicts, lists, tuples and scalars.

    Returns:
        Any: An equivalent structure that ``json.dumps(..., allow_nan=False)`` accepts.
    """
    if isinstance(value, dict):
        return {str(k): json_safe(v) for k, v in cast("dict[object, object]", value).items()}
    if isinstance(value, list | tuple):
        return [json_safe(v) for v in cast("list[object] | tuple[object, ...]", value)]
    if isinstance(value, np.generic):
        value = cast("object", value.item())
    if isinstance(value, float) and not math.isfinite(value):
        return None
    return value


def frame_records(frame: pd.DataFrame, fields: list[str]) -> list[dict[str, Any]]:
    """Render selected columns as JSON-safe records with rounded floats and ``...Z`` ISO timestamps.

    Args:
        frame: Source frame.
        fields: Columns to keep, in output order (missing columns are skipped).

    Returns:
        list[dict[str, Any]]: One record per row.
    """
    out = frame[[f for f in fields if f in frame]].copy()
    for column in TIME_COLUMNS:
        if column in out:
            stamps = pd.to_datetime(out[column])
            out[column] = stamps.dt.strftime("%Y-%m-%dT%H:%M:%SZ").where(stamps.notna(), None)
    out = out.round({k: v for k, v in ROUNDING.items() if k in out})
    return json_safe(out.to_dict("records"))


def build_forecasts(
    scenario: Scenario,
    client: httpx.Client,
    settings: Settings,
    store: ArtifactStore,
    *,
    assets: pd.DataFrame,
    model: OutageModel,
    reference_bands: list[dict[str, float]],
    target: tuple[float, float],
) -> list[dict[str, Any]]:
    """Replay each as-issued ECMWF ensemble forecast of a scenario and store its ranked, probabilistic assets.

    Args:
        scenario: Scenario whose ``forecasts`` lists the issue times.
        client: HTTP client.
        settings: Settings (cache, retries).
        store: Artifact destination.
        assets: Enriched assets (with ``observed_loss_pct`` where known).
        model: Calibrated outage model applied per member.
        reference_bands: Loss-by-wind-band summary quoted in the reasons.
        target: ``(lat, lon)`` used to pick the right storm from each run (the observed landfall position).

    Returns:
        list[dict[str, Any]]: One summary per issue time, in issue order.
    """
    lat, lon = assets["lat"].to_numpy(dtype=float), assets["lon"].to_numpy(dtype=float)
    static = assets[[column for column in STATIC_FIELDS if column in assets]]
    summaries: list[dict[str, Any]] = []
    for issued in scenario.forecasts:
        storm = select_storm(load_ensemble(client, settings, issued), target)
        impact, member_peak = ensemble_impact(lat, lon, storm, model)
        no_band_entry = pd.Series(pd.NaT, index=static.index, dtype="datetime64[s]")
        frame = static.assign(**impact, band_kt=0, band_entry=no_band_entry, members=len(storm.members))
        ranked = rank_assets(frame, model, scenario.landfall, reference_bands, issued)
        key = issued.strftime("%Y%m%dT%HZ")
        prefix = f"scenarios/{scenario.id}/forecasts/{key}"
        store.write_json(f"{prefix}/assets.json", frame_records(ranked, FORECAST_FIELDS))
        store.write_json(f"{prefix}/tracks.json", [{"member": m, "fixes": f} for m, f in storm.members.items()])
        summaries.append(
            json_safe(
                {
                    "key": key,
                    "issued": issued.strftime("%Y-%m-%dT%H:%M:%SZ"),
                    "lead_h": (scenario.landfall - issued).total_seconds() / 3600,
                    "storm_id": storm.storm_id,
                    "members": len(storm.members),
                    "assets_likely_gale": int((ranked["p34"] >= 0.5).sum()),
                    "assets_likely_hurricane": int((ranked["p64"] >= 0.5).sum()),
                    "max_p_outage": float(ranked["p_outage"].max()),
                    "districts": forecast_triggers(static["district"], member_peak),
                    "source": "ECMWF IFS ensemble tropical-cyclone tracks, as issued (open data, CC BY 4.0)",
                }
            )
        )
        logger.info("forecast %s %s: %s", scenario.id, key, summaries[-1])
    return summaries


def model_surge(
    scenario: Scenario, track: Track, assets: pd.DataFrame
) -> tuple[pd.DataFrame, pd.DataFrame, dict[str, Any]]:
    """Model the storm surge along a scenario's open coast and at every asset, and compare it with IMD's report.

    Args:
        scenario: The scenario (region and IMD surge report).
        track: The best track.
        assets: Assets with ``lat``, ``lon`` and ``elevation_m``.

    Returns:
        tuple[pd.DataFrame, pd.DataFrame, dict[str, Any]]: Assets with ``coast_km``, ``surge_m`` and ``flood_m``;
        the peak surge per coast point; and the surge summary for the scenario index.
    """
    bbox = scenario.region.bbox
    coast = coast_from_grid(earth.relief(bbox), bbox)
    coastal = coastal_surge(coast, track)
    lat, lon = assets["lat"].to_numpy(dtype=float), assets["lon"].to_numpy(dtype=float)
    assets = assets.assign(
        **inundation(
            lat,
            lon,
            assets["elevation_m"].to_numpy(dtype=float),
            coast_lat=coast.lat,
            coast_lon=coast.lon,
            peak_m=coastal["peak_m"],
        )
    )
    crest = int(np.nanargmax(coastal["peak_m"]))
    observed: dict[str, Any] | None = None
    if report := scenario.surge_report:
        south, west, north, east = report.bbox
        stretch = (coast.lat >= south) & (coast.lat <= north) & (coast.lon >= west) & (coast.lon <= east)
        observed = {
            **{k: v for k, v in vars(report).items() if k != "bbox"},
            "modelled_m": round(float(np.nanmax(coastal["peak_m"][stretch])), 2) if stretch.any() else None,
        }
    summary = {
        "peak_m": round(float(coastal["peak_m"][crest]), 2),
        "lat": round(float(coast.lat[crest]), 3),
        "lon": round(float(coast.lon[crest]), 3),
        "time": f"{np.datetime_as_string(coastal['peak_time'][crest], unit='s')}Z",
        "coast_points": int(coast.lat.size),
        "flooded_sites": int((assets["flood_m"] >= FLOOD_DEPTH_M).sum()),
        "method": "1D wind setup over ETOPO1 shelf transects plus inverse barometer; no tide, waves or rivers",
        "observed": observed,
    }
    return assets, pd.DataFrame({"lat": coast.lat, "lon": coast.lon, **coastal}), summary


def score_rain(scenario: Scenario, assets: pd.DataFrame) -> tuple[pd.DataFrame, dict[str, Any]]:
    """Measure storm rain by satellite at every asset and score the modelled rain against it.

    Args:
        scenario: The scenario (landfall sets the measurement window).
        assets: Assets with modelled ``rain_mm``.

    Returns:
        tuple[pd.DataFrame, dict[str, Any]]: Assets with ``observed_rain_mm`` and the rain summary for the index.
    """
    window = timedelta(days=RAINFALL_WINDOW_DAYS)
    assets = assets.assign(
        observed_rain_mm=earth.observed_rain(assets, scenario.landfall - window, scenario.landfall + window)
    )
    modelled_rain, measured_rain = (
        assets["rain_mm"].to_numpy(dtype=float),
        assets["observed_rain_mm"].to_numpy(dtype=float),
    )
    measured = np.isfinite(measured_rain)
    rain = {
        "model": "R-CLIPER parametric rain (Tuleya et al. 2007) along the best track",
        "truth": f"NASA GPM IMERG V07, {RAINFALL_WINDOW_DAYS} days either side of landfall",
        "n": int(measured.sum()),
        "spearman": spearman(modelled_rain[measured], measured_rain[measured]),
        "median_ratio": float(np.median(modelled_rain[measured] / np.maximum(measured_rain[measured], 1.0))),
        "max_modelled_mm": round(float(modelled_rain.max()), 0),
        "max_observed_mm": round(float(np.nanmax(measured_rain)), 0),
        "extreme_sites": int((modelled_rain >= EXTREME_RAIN_MM).sum()),
    }
    return assets, rain


def model_roads(
    roads: list[dict[str, Any]], track: Track, assets: pd.DataFrame, surge_points: pd.DataFrame
) -> tuple[dict[str, Any], dict[str, Any], pd.DataFrame]:
    """Run the hazard along every arterial road, then link each site to its nearest road.

    Args:
        roads: Arterial roads (see :func:`fetch_osm_roads`).
        track: The best track.
        assets: Assets with ``lat`` and ``lon``.
        surge_points: Peak surge per open-coast point (``lat``, ``lon``, ``peak_m``).

    Returns:
        tuple[dict[str, Any], dict[str, Any], pd.DataFrame]: The roads as a GeoJSON FeatureCollection, the road summary
        for the scenario index, and the assets with ``road_km``, ``access_road`` and ``access_closes``.
    """
    samples = sample_roads(roads)
    lat, lon = samples["lat"].to_numpy(dtype=float), samples["lon"].to_numpy(dtype=float)
    # Thousands of samples times a densified track: run the hazard in blocks to bound memory.
    blocks = [
        exposure(lat[i : i + HAZARD_BLOCK], lon[i : i + HAZARD_BLOCK], track) for i in range(0, lat.size, HAZARD_BLOCK)
    ]
    hazard = {key: np.concatenate([block[key] for block in blocks]) for key in blocks[0]}
    samples = samples.assign(**hazard, elevation_m=earth.ground_elevation(samples).to_numpy())
    samples["flood_m"] = inundation(
        lat,
        lon,
        samples["elevation_m"].to_numpy(dtype=float),
        coast_lat=surge_points["lat"].to_numpy(dtype=float),
        coast_lon=surge_points["lon"].to_numpy(dtype=float),
        peak_m=surge_points["peak_m"].to_numpy(dtype=float),
    )["flood_m"]
    statuses = road_status(roads, samples)
    access = nearest_access(assets["lat"].to_numpy(dtype=float), assets["lon"].to_numpy(dtype=float), samples, statuses)
    cut = [s for s in statuses if s["status"] == "cut"]
    closures = sorted(s["closes_at"] for s in cut if s["closes_at"])
    summary = {
        "roads": len(statuses),
        "km": round(sum(s["length_km"] for s in statuses)),
        "km_cut": round(sum(s["length_km"] for s in cut)),
        "km_at_risk": round(sum(s["length_km"] for s in statuses if s["status"] == "at risk")),
        "first_closure": closures[0] if closures else None,
        "cut_by_surge": sum("surge" in s["causes"] for s in statuses),
    }
    geojson = {
        "type": "FeatureCollection",
        "features": [
            {
                "type": "Feature",
                "geometry": {"type": "LineString", "coordinates": s["path"]},
                "properties": {k: v for k, v in s.items() if k != "path"},
            }
            for s in statuses
        ],
    }
    linked = assets.assign(
        road_km=access["road_km"].to_numpy(),
        access_road=access["access_road"].to_numpy(),
        access_closes=access["access_closes"].to_numpy(),
    )
    return geojson, summary, linked


def build_scenario(
    scenario: Scenario, client: httpx.Client, settings: Settings, store: ArtifactStore, model: OutageModel | None
) -> tuple[OutageModel, dict[str, Any]]:
    """Build and store every artifact for one scenario.

    Args:
        scenario: Scenario to build.
        client: HTTP client for build inputs.
        settings: Settings (cache, retries).
        store: Artifact destination.
        model: Outage model from the reference scenario; ignored (and refitted) when ``scenario.reference``.

    Returns:
        tuple[OutageModel, dict[str, Any]]: The model used and the scenario summary written to the index.

    Raises:
        ValueError: If a non-reference scenario is built without a model.
    """
    logger.info("building %s", scenario.id)
    fixes = load_best_track(client, settings, scenario.storm, scenario.season)
    track = Track.from_records(fixes)
    assets = load_assets(client, settings, scenario.region)
    lat, lon = assets["lat"].to_numpy(dtype=float), assets["lon"].to_numpy(dtype=float)
    assets = earth.enrich(assets.assign(**exposure(lat, lon, track), district=earth.districts(assets)))
    assets, surge_points, surge = model_surge(scenario, track, assets)
    roads, road_summary, assets = model_roads(
        fetch_osm_roads(client, settings, scenario.region), track, assets, surge_points
    )
    assets, rain = score_rain(scenario, assets)

    substations = assets[assets["kind"] == "substation"]
    truth = substations[["asset_id", "lat", "lon", "district", "peak_wind_kt"]].join(
        earth.nightlight_loss(substations, scenario.truth_pre, scenario.truth_post)
    )
    truth["lit"] = truth["ntl_pre"] >= LIT_RADIANCE
    lit = truth[truth["lit"] & truth["loss_pct"].notna() & truth["peak_wind_kt"].notna()]
    wind, loss = lit["peak_wind_kt"].to_numpy(dtype=float), lit["loss_pct"].to_numpy(dtype=float)
    bands = loss_by_band(wind, loss, LOSS_BANDS_KT)

    if scenario.reference:
        model = fit_outage_model(wind, loss, OUTAGE_LOSS_PCT, scenario.id)
        store.write_json(MODEL_PATH, json_safe({"model": model.to_dict(), "bands": bands}))
    elif model is None:
        raise ValueError(f"{scenario.id} needs the reference outage model; build the reference scenario first")
    reference_bands = bands if scenario.reference else store.read_json(MODEL_PATH)["bands"]
    skill: dict[str, Any] = {**evaluate(model, wind, loss, OUTAGE_LOSS_PCT), "out_of_sample": not scenario.reference}
    if scenario.reference:
        lat = lit["lat"].to_numpy(dtype=float)
        skill["spatial_holdout"] = spatial_holdout(lat, wind, loss, OUTAGE_LOSS_PCT, HOLDOUT_FOLDS)

    assets = assets.merge(
        truth[["asset_id", "loss_pct"]].rename(columns={"loss_pct": "observed_loss_pct"}), on="asset_id", how="left"
    )
    ranked = rank_assets(assets, model, scenario.landfall, reference_bands)
    backtest = truth.merge(ranked[["asset_id", "name", "p_outage"]], on="asset_id")
    forecasts: list[dict[str, Any]] = []
    if scenario.forecasts:
        landfall_at = track_position(track, scenario.landfall)
        if landfall_at is None:
            raise ValueError(f"{scenario.id}: landfall time is outside the best track")
        target = (landfall_at["lat"], landfall_at["lon"])
        forecasts = build_forecasts(
            scenario,
            client,
            settings,
            store,
            assets=assets,
            model=model,
            reference_bands=reference_bands,
            target=target,
        )

    summary = json_safe(
        {
            "id": scenario.id,
            "storm": scenario.storm.title(),
            "season": scenario.season,
            "region": {"id": scenario.region.id, "name": scenario.region.name, "bbox": list(scenario.region.bbox)},
            "landfall": scenario.landfall.strftime("%Y-%m-%dT%H:%M:%SZ"),
            "track_source": "IBTrACS best track (JTWC intensity and wind radii)",
            "peak_vmax_kt": float(track.vmax_kt.max()),
            "asset_counts": ranked["kind"].value_counts().to_dict(),
            "model": model.to_dict(),
            "skill": skill,
            "loss_by_band": bands,
            "surge": surge,
            "rain": rain,
            "roads": road_summary,
            "insurance": {
                "terms": "Illustrative: index = wind reached at 25% of a district's sites; "
                "pays 25/50/100% at 64/83/96 kt",
                "districts": best_track_triggers(assets, lit, pd.Timestamp(scenario.landfall)),
            },
            "forecasts": forecasts,
            "built_at": datetime.now(UTC).strftime("%Y-%m-%dT%H:%M:%SZ"),
        }
    )
    prefix = f"scenarios/{scenario.id}"
    store.write_json(f"{prefix}/scenario.json", summary)
    store.write_json(f"{prefix}/track.json", fixes)
    store.write_json(f"{prefix}/assets.json", frame_records(ranked, ASSET_FIELDS))
    store.write_json(f"{prefix}/surge.json", frame_records(surge_points, SURGE_FIELDS))
    store.write_json(f"{prefix}/roads.json", roads)
    urls = earth.nightlight_image_urls(scenario.region.bbox, scenario.truth_pre, scenario.truth_post)
    for name, url in zip(EVIDENCE_IMAGES, urls, strict=True):
        image = download(client, settings, f"{scenario.id}-{name}.png", (url,))
        store.write_bytes(f"{prefix}/evidence/{name}.png", image, "image/png")
    store.write_json(
        f"{prefix}/backtest.json",
        {
            "skill": summary["skill"],  # JSON-safe: block AUCs are NaN where a block has one outcome
            "loss_by_band": bands,
            "substations": frame_records(
                backtest,
                [
                    "asset_id",
                    "name",
                    "lat",
                    "lon",
                    "peak_wind_kt",
                    "p_outage",
                    "ntl_pre",
                    "ntl_post",
                    "loss_pct",
                    "lit",
                ],
            ),
        },
    )
    logger.info("built %s: %d assets, skill %s", scenario.id, len(ranked), skill)
    return model, summary


def main(argv: list[str] | None = None) -> int:
    """CLI entry point: build the requested scenarios (reference first) and refresh the scenario index.

    Args:
        argv: Command-line arguments (defaults to ``sys.argv[1:]``).

    Returns:
        int: Process exit code (0 on success).
    """
    parser = argparse.ArgumentParser(description="Build ShadowCast scenario artifacts.")
    parser.add_argument("scenarios", nargs="*", metavar="scenario", help=f"scenario ids: {', '.join(SCENARIOS)}")
    args = parser.parse_args(argv)
    if unknown := sorted(set(args.scenarios) - set(SCENARIOS)):
        parser.error(f"unknown scenario(s): {', '.join(unknown)}")
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s: %(message)s")

    settings = Settings.from_env()
    store = artifact_store(settings)
    earth.initialize(settings.ee_project)
    selected = sorted((SCENARIOS[s] for s in (args.scenarios or SCENARIOS)), key=lambda s: not s.reference)
    model = None
    if not any(s.reference for s in selected) and store.exists(MODEL_PATH):
        model = OutageModel(**store.read_json(MODEL_PATH)["model"])

    existing: list[dict[str, Any]] = store.read_json(INDEX_PATH) if store.exists(INDEX_PATH) else []
    index = {entry["id"]: entry for entry in existing}
    with httpx.Client(
        timeout=settings.http_timeout_s, follow_redirects=True, headers={"User-Agent": USER_AGENT}
    ) as client:
        for scenario in selected:
            model, summary = build_scenario(scenario, client, settings, store, model)
            index[scenario.id] = {
                k: summary[k] for k in ("id", "storm", "season", "region", "landfall", "peak_vmax_kt")
            }
    store.write_json(INDEX_PATH, [index[s] for s in SCENARIOS if s in index])
    return 0


if __name__ == "__main__":  # pragma: no cover
    sys.exit(main())
