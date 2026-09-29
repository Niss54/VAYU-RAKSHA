"use client";

import type { PickingInfo } from "@deck.gl/core";
import { GoogleMapsOverlay } from "@deck.gl/google-maps";
import { PathLayer, ScatterplotLayer } from "@deck.gl/layers";
import { APIProvider, Map as GoogleMap, useMap } from "@vis.gl/react-google-maps";
import { useEffect, useMemo, useRef } from "react";

import {
  assetValue,
  type ColorBy,
  istStamp,
  kindLabel,
  percent,
  rampColor,
  type Rgb,
  SURGE_FULL_M,
} from "@/lib/format";
import type {
  Asset,
  ForecastAsset,
  Region,
  RoadCollection,
  RoadProperties,
  StormPosition,
  SurgePoint,
  TrackFeatureCollection,
} from "@/lib/types";

type Path = { id: string; path: [number, number][] };

interface MapViewProps {
  apiKey: string;
  region: Region;
  assets: (Asset | ForecastAsset)[];
  colorBy: ColorBy;
  windById: Map<string, number> | null;
  track: TrackFeatureCollection | undefined;
  members: TrackFeatureCollection | undefined;
  storm: StormPosition | null;
  /** Peak modelled surge along the coast (best track only). */
  surge: SurgePoint[] | undefined;
  /** Arterial roads with their status (best track only); a cut road turns amber once the replay passes its closure. */
  roads: RoadCollection | undefined;
  timeMs: number | null;
  selectedId: string | null;
  onSelect: (assetId: string | null) => void;
}

const WHITE: Rgb = [255, 255, 255];
const VOID: Rgb = [14, 16, 18];
const MEMBER: [number, number, number, number] = [127, 167, 217, 95]; // --member: cool and recessive under the risk dots
const AMBER: Rgb = [242, 138, 46]; // --accent
const PULSE_MS = 2400;

/** Two rings expanding from the radius of maximum wind and fading, half a cycle apart: the storm's heartbeat. */
function pulseLayers(storm: StormPosition, phase: number) {
  return [0, 0.5].map((offset) => {
    const p = (phase + offset) % 1;
    return new ScatterplotLayer<StormPosition>({
      id: `storm-pulse-${offset}`,
      data: [storm],
      getPosition: (s) => [s.lon, s.lat],
      getRadius: (s) => s.rmw_km * 1000 * (1 + 2.2 * p),
      radiusUnits: "meters",
      stroked: true,
      filled: false,
      getLineColor: [...AMBER, Math.round(230 * (1 - p))] as [number, number, number, number],
      lineWidthUnits: "pixels",
      getLineWidth: 1.5,
      updateTriggers: { getRadius: p, getLineColor: p },
    });
  });
}

// Near-black cartography: land in the panel tone, water in the void, faint boundaries and town names only, so the
// storm and the risk dots are the only light on the map.
const MAP_STYLE: google.maps.MapTypeStyle[] = [
  { elementType: "geometry", stylers: [{ color: "#16191d" }] },
  { elementType: "labels.icon", stylers: [{ visibility: "off" }] },
  { elementType: "labels.text.fill", stylers: [{ color: "#7d8797" }] },
  { elementType: "labels.text.stroke", stylers: [{ color: "#0e1012" }] },
  { featureType: "water", elementType: "geometry", stylers: [{ color: "#0a0c0e" }] },
  { featureType: "water", elementType: "labels", stylers: [{ visibility: "off" }] },
  { featureType: "poi", stylers: [{ visibility: "off" }] },
  { featureType: "transit", stylers: [{ visibility: "off" }] },
  { featureType: "road", stylers: [{ visibility: "off" }] },
  { featureType: "road.highway", elementType: "geometry", stylers: [{ visibility: "on" }, { color: "#20242a" }] },
  { featureType: "administrative", elementType: "geometry.stroke", stylers: [{ color: "#2b3038" }] },
  { featureType: "administrative.province", elementType: "geometry.stroke", stylers: [{ color: "#3a414c" }] },
  { featureType: "administrative.neighborhood", stylers: [{ visibility: "off" }] },
  { featureType: "administrative.land_parcel", stylers: [{ visibility: "off" }] },
  { featureType: "landscape.natural.terrain", stylers: [{ visibility: "off" }] },
];

function lines(collection: TrackFeatureCollection | undefined): Path[] {
  return (collection?.features ?? [])
    .filter((f) => f.geometry.type === "LineString")
    .map((f, i) => ({ id: String(f.properties.member ?? i), path: f.geometry.coordinates as [number, number][] }));
}

interface DeckOverlayProps {
  layers: unknown[];
  tooltip: (info: PickingInfo) => string | null;
  pulse: StormPosition | null;
}

function DeckOverlay({ layers, tooltip, pulse }: DeckOverlayProps) {
  const map = useMap();
  const overlay = useRef<GoogleMapsOverlay | null>(null);
  const latest = useRef({ layers, tooltip });

  // Attach only once the map knows its rendering type. Given an UNINITIALIZED map, deck.gl registers a
  // `renderingtype_changed` listener it never removes, so after an unmount (React's dev double-mount) that listener
  // builds an overlay on the finalized instance. Our own listener is removed on cleanup, and each mount owns one
  // overlay that finalize() fully tears down.
  useEffect(() => {
    if (!map) return;
    let instance: GoogleMapsOverlay | null = null;
    const attach = () => {
      instance = new GoogleMapsOverlay({ interleaved: false }); // the styled basemap is a raster map
      instance.setProps({ layers: latest.current.layers as never[], getTooltip: latest.current.tooltip });
      instance.setMap(map);
      overlay.current = instance;
    };
    let listener: google.maps.MapsEventListener | null = null;
    if (map.getRenderingType() !== google.maps.RenderingType.UNINITIALIZED) attach();
    else listener = map.addListener("renderingtype_changed", attach);
    return () => {
      listener?.remove();
      instance?.finalize();
      overlay.current = null;
    };
  }, [map]);

  // Animate the storm pulse on the overlay directly (no React re-render per frame); hold it still for reduced motion.
  useEffect(() => {
    latest.current = { layers, tooltip };
    if (!pulse) {
      overlay.current?.setProps({ layers: layers as never[], getTooltip: tooltip });
      return;
    }
    const still = window.matchMedia("(prefers-reduced-motion: reduce)").matches;
    let frame = 0;
    const draw = (now: number) => {
      const phase = still ? 0.35 : (now % PULSE_MS) / PULSE_MS;
      overlay.current?.setProps({ layers: [...layers, ...pulseLayers(pulse, phase)] as never[], getTooltip: tooltip });
      if (!still) frame = requestAnimationFrame(draw);
    };
    frame = requestAnimationFrame(draw);
    return () => cancelAnimationFrame(frame);
  }, [layers, tooltip, pulse]);
  return null;
}

function FitRegion({ region }: { region: Region }) {
  const map = useMap();
  useEffect(() => {
    const [south, west, north, east] = region.bbox;
    map?.fitBounds({ south, west, north, east }, 24);
  }, [map, region]);
  return null;
}

export function MapView(props: MapViewProps) {
  const {
    apiKey,
    region,
    assets,
    colorBy,
    windById,
    track,
    members,
    storm,
    surge,
    roads,
    timeMs,
    selectedId,
    onSelect,
  } = props;

  const layers = useMemo(() => {
    const assetLayer = new ScatterplotLayer<Asset | ForecastAsset>({
      id: "assets",
      data: [...assets].reverse(), // draw highest priority last so it sits on top
      getPosition: (a) => [a.lon, a.lat],
      getFillColor: (a) =>
        [...rampColor(assetValue(a, colorBy, windById), colorBy), 200] as [number, number, number, number],
      getRadius: (a) => 2 + 3.5 * assetValue(a, colorBy, windById), // small enough that dense clusters stay legible
      getLineColor: (a) =>
        (a.asset_id === selectedId ? [...WHITE, 255] : [...VOID, 200]) as [number, number, number, number],
      getLineWidth: (a) => (a.asset_id === selectedId ? 3 : 0.6),
      radiusUnits: "pixels",
      lineWidthUnits: "pixels",
      stroked: true,
      pickable: true,
      onClick: (info) => onSelect(info.object ? info.object.asset_id : null),
      updateTriggers: {
        getFillColor: [colorBy, windById],
        getRadius: [colorBy, windById],
        getLineColor: selectedId,
        getLineWidth: selectedId,
      },
    });
    const memberLayer = new PathLayer<Path>({
      id: "ensemble",
      data: lines(members),
      getPath: (p) => p.path,
      getColor: MEMBER,
      widthUnits: "pixels",
      getWidth: 1.5,
    });
    const trackLayer = new PathLayer<Path>({
      id: "best-track",
      data: members ? [] : lines(track),
      getPath: (p) => p.path,
      getColor: [...WHITE, 220] as [number, number, number, number],
      widthUnits: "pixels",
      getWidth: 2.5,
    });
    const stormLayer = new ScatterplotLayer<StormPosition>({
      id: "storm",
      data: storm ? [storm] : [],
      getPosition: (s) => [s.lon, s.lat],
      getRadius: (s) => s.rmw_km * 1000,
      radiusUnits: "meters",
      stroked: true,
      filled: true,
      getFillColor: [...AMBER, 45] as [number, number, number, number],
      getLineColor: [...WHITE, 235] as [number, number, number, number],
      lineWidthUnits: "pixels",
      getLineWidth: 1.5,
    });
    // The surge crest as a band of light along the shore, blue like the water encoding.
    const surgeLayer = new ScatterplotLayer<SurgePoint>({
      id: "surge",
      data: surge ?? [],
      getPosition: (p) => [p.lon, p.lat],
      getFillColor: (p) =>
        [...rampColor((p.peak_m ?? 0) / SURGE_FULL_M, "flood"), 230] as [number, number, number, number],
      getRadius: (p) => 1.5 + (4 * Math.min(p.peak_m ?? 0, SURGE_FULL_M)) / SURGE_FULL_M,
      radiusUnits: "pixels",
      pickable: true,
    });
    const closed = (road: RoadProperties) =>
      road.status === "cut" && (road.closes_at == null || (timeMs ?? 0) >= Date.parse(road.closes_at));
    const roadLayer = new PathLayer<RoadCollection["features"][number]>({
      id: "roads",
      data: roads?.features ?? [],
      getPath: (f) => f.geometry.coordinates,
      getColor: (f) =>
        (closed(f.properties)
          ? [...AMBER, 235]
          : f.properties.status === "open"
            ? [...WHITE, 40]
            : [...WHITE, 110]) as [number, number, number, number],
      getWidth: (f) => (closed(f.properties) ? 2.5 : 1.2),
      widthUnits: "pixels",
      pickable: true,
      updateTriggers: { getColor: timeMs, getWidth: timeMs },
    });
    return [memberLayer, trackLayer, roadLayer, surgeLayer, assetLayer, stormLayer];
  }, [assets, colorBy, windById, members, track, storm, surge, roads, timeMs, selectedId, onSelect]);

  const tooltip = useMemo(
    () => (info: PickingInfo) => {
      if (info.object && info.layer?.id === "roads") {
        const road = (info.object as RoadCollection["features"][number]).properties;
        const causes = road.causes.length ? ` (${road.causes.join(", ")})` : "";
        return `${road.name ?? road.ref ?? "Arterial road"} · ${road.status}${causes}\n${road.closes_at ? `closes ${istStamp(road.closes_at)}` : `peak wind ${Math.round(road.peak_wind_kt)} kt`}`;
      }
      if (info.object && info.layer?.id === "surge") {
        const point = info.object as SurgePoint;
        return `Storm surge ${point.peak_m?.toFixed(1)} m · ${istStamp(point.peak_time)}
wind setup ${point.setup_m?.toFixed(1)} m + low pressure ${point.barometer_m?.toFixed(1)} m`;
      }
      const asset = info.object as Asset | ForecastAsset | undefined;
      if (!asset || info.layer?.id !== "assets") return null;
      const gales = "p34" in asset ? ` · gales ${percent(asset.p34)}` : "";
      return `#${asset.rank} ${asset.name ?? kindLabel(asset.kind)}\n${kindLabel(asset.kind)} · outage ${percent(asset.p_outage)}${gales}`;
    },
    [],
  );

  return (
    <APIProvider apiKey={apiKey}>
      <GoogleMap
        className="absolute inset-0" // size from the positioned parent: % heights collapse inside grid-stretched items
        styles={MAP_STYLE}
        backgroundColor="#0e1012"
        defaultCenter={{ lat: 20.3, lng: 86.0 }}
        defaultZoom={7}
        gestureHandling="greedy"
        disableDefaultUI
        zoomControl
      >
        <FitRegion region={region} />
        <DeckOverlay layers={layers} tooltip={tooltip} pulse={storm} />
      </GoogleMap>
    </APIProvider>
  );
}
