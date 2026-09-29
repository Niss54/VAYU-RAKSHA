"use client";

import React, { useEffect, useRef, useState } from "react";
import { type EvacuationCorridor, type InfrastructureNode } from "@/lib/vayu-engine";
import {
  AlertCircle,
  Eye,
  Layers,
  MapPin,
  Maximize2,
  Navigation,
  Pause,
  Play,
  RotateCcw,
  Shield,
  Sliders,
  Waves,
  Wind,
  Zap,
} from "lucide-react";

interface TacticalCommandMapProps {
  nodes: InfrastructureNode[];
  corridors: EvacuationCorridor[];
  centerLat: number;
  centerLon: number;
  maxWindKmh: number;
  surgeCrestM: number;
  stormName: string;
  leadTimeHours: number;
  onNodeClick?: (node: InfrastructureNode) => void;
}

export function TacticalCommandMap({
  nodes,
  corridors,
  centerLat,
  centerLon,
  maxWindKmh,
  surgeCrestM,
  stormName,
  leadTimeHours,
  onNodeClick,
}: TacticalCommandMapProps) {
  const [activeLayers, setActiveLayers] = useState({
    sarFlood: true,
    windVortex: true,
    stormSurge: true,
    evacuationRoutes: true,
    assets: true,
  });

  const [isPlaying, setIsPlaying] = useState(false);
  const [timeStepHours, setTimeStepHours] = useState(leadTimeHours); // e.g. T-36h down to T-0 (Landfall)
  const [selectedAsset, setSelectedAsset] = useState<InfrastructureNode | null>(nodes[0] || null);

  // Auto-play timeline simulation
  useEffect(() => {
    let interval: NodeJS.Timeout;
    if (isPlaying) {
      interval = setInterval(() => {
        setTimeStepHours((prev) => {
          if (prev <= 0) return 48; // Loop back
          return Math.max(0, prev - 2);
        });
      }, 1000);
    }
    return () => clearInterval(interval);
  }, [isPlaying]);

  // Coordinate projections for the SVG canvas (Bounding box around Odisha Coast: Lat 19.4-20.6, Lon 85.0-87.2)
  const mapWidth = 900;
  const mapHeight = 520;
  const minLat = 19.3;
  const maxLat = 20.6;
  const minLon = 85.0;
  const maxLon = 87.2;

  const projectToSvg = (lat: number, lon: number) => {
    const x = ((lon - minLon) / (maxLon - minLon)) * mapWidth;
    const y = mapHeight - ((lat - minLat) / (maxLat - minLat)) * mapHeight;
    return { x: Math.max(20, Math.min(mapWidth - 20, x)), y: Math.max(20, Math.min(mapHeight - 20, y)) };
  };

  // Interpolated storm center based on current timeline scrubber
  const stormProgress = 1 - timeStepHours / 48.0; // 0 (T-48h offshore) -> 1 (Landfall on coast)
  const currentEyeLat = 18.2 + stormProgress * (19.8 - 18.2);
  const currentEyeLon = 87.8 - stormProgress * (87.8 - 85.8);
  const eyePos = projectToSvg(currentEyeLat, currentEyeLon);

  return (
    <div className="glass-tactical rounded-2xl border border-cyan-500/25 overflow-hidden flex flex-col">
      {/* Map Control HUD Bar */}
      <div className="p-4 border-b border-white/10 bg-slate-950/70 flex flex-wrap items-center justify-between gap-3">
        <div className="flex items-center gap-2.5">
          <div className="p-2 rounded-xl bg-cyan-500/10 text-cyan-400 border border-cyan-500/20">
            <Navigation className="w-5 h-5" />
          </div>
          <div>
            <div className="flex items-center gap-2">
              <h3 className="text-xs font-bold font-mono tracking-widest text-cyan-300">
                4D TACTICAL GEOSPATIAL COMMAND MAP
              </h3>
              <span className="px-2 py-0.5 rounded text-[10px] font-mono bg-cyan-500/10 text-cyan-300 border border-cyan-500/30">
                ISRO SAR + HOLLAND RADAR FUSION
              </span>
            </div>
            <p className="text-[11px] text-slate-400">
              High-resolution radar flood mask (RISAT-1A) & 51-member ensemble storm envelope
            </p>
          </div>
        </div>

        {/* Layer Toggles */}
        <div className="flex items-center gap-2 flex-wrap">
          <button
            onClick={() => setActiveLayers((p) => ({ ...p, sarFlood: !p.sarFlood }))}
            className={`px-2.5 py-1 rounded-lg text-xs font-mono flex items-center gap-1.5 transition-all cursor-pointer ${
              activeLayers.sarFlood
                ? "bg-violet-500/20 text-violet-300 border border-violet-500/40"
                : "bg-slate-900 text-slate-500 border border-white/5"
            }`}
          >
            <span
              className={`w-2 h-2 rounded-full ${activeLayers.sarFlood ? "bg-violet-400" : "bg-slate-600"}`}
            ></span>
            ISRO SAR Flood
          </button>

          <button
            onClick={() => setActiveLayers((p) => ({ ...p, windVortex: !p.windVortex }))}
            className={`px-2.5 py-1 rounded-lg text-xs font-mono flex items-center gap-1.5 transition-all cursor-pointer ${
              activeLayers.windVortex
                ? "bg-cyan-500/20 text-cyan-300 border border-cyan-500/40"
                : "bg-slate-900 text-slate-500 border border-white/5"
            }`}
          >
            <span
              className={`w-2 h-2 rounded-full ${activeLayers.windVortex ? "bg-cyan-400" : "bg-slate-600"}`}
            ></span>
            Holland Wind
          </button>

          <button
            onClick={() => setActiveLayers((p) => ({ ...p, stormSurge: !p.stormSurge }))}
            className={`px-2.5 py-1 rounded-lg text-xs font-mono flex items-center gap-1.5 transition-all cursor-pointer ${
              activeLayers.stormSurge
                ? "bg-blue-500/20 text-blue-300 border border-blue-500/40"
                : "bg-slate-900 text-slate-500 border border-white/5"
            }`}
          >
            <span
              className={`w-2 h-2 rounded-full ${activeLayers.stormSurge ? "bg-blue-400" : "bg-slate-600"}`}
            ></span>
            Surge Crest
          </button>

          <button
            onClick={() => setActiveLayers((p) => ({ ...p, evacuationRoutes: !p.evacuationRoutes }))}
            className={`px-2.5 py-1 rounded-lg text-xs font-mono flex items-center gap-1.5 transition-all cursor-pointer ${
              activeLayers.evacuationRoutes
                ? "bg-amber-500/20 text-amber-300 border border-amber-500/40"
                : "bg-slate-900 text-slate-500 border border-white/5"
            }`}
          >
            <span
              className={`w-2 h-2 rounded-full ${activeLayers.evacuationRoutes ? "bg-amber-400" : "bg-slate-600"}`}
            ></span>
            Road Corridors
          </button>
        </div>
      </div>

      {/* SVG Tactical Map Canvas */}
      <div className="relative w-full bg-[#05070B] overflow-hidden" style={{ minHeight: "480px" }}>
        <svg
          viewBox={`0 0 ${mapWidth} ${mapHeight}`}
          className="w-full h-full select-none"
          style={{ filter: "drop-shadow(0 0 10px rgba(0,0,0,0.8))" }}
        >
          {/* Tactical Background Grid */}
          <defs>
            <pattern id="tacticalGrid" width="40" height="40" patternUnits="userSpaceOnUse">
              <path d="M 40 0 L 0 0 0 40" fill="none" stroke="rgba(0, 245, 255, 0.04)" strokeWidth="1" />
            </pattern>
            {/* Radial Gradient for Cyclone Eye */}
            <radialGradient id="cycloneEyeGrad" cx="50%" cy="50%" r="50%">
              <stop offset="0%" stopColor="#FF3366" stopOpacity="0.8" />
              <stop offset="40%" stopColor="#FF9F1C" stopOpacity="0.4" />
              <stop offset="80%" stopColor="#00F5FF" stopOpacity="0.15" />
              <stop offset="100%" stopColor="#00F5FF" stopOpacity="0" />
            </radialGradient>
            {/* Flood Inundation Gradient */}
            <radialGradient id="sarFloodGrad" cx="50%" cy="50%" r="50%">
              <stop offset="0%" stopColor="#8B5CF6" stopOpacity="0.6" />
              <stop offset="60%" stopColor="#3B82F6" stopOpacity="0.3" />
              <stop offset="100%" stopColor="#3B82F6" stopOpacity="0" />
            </radialGradient>
          </defs>

          <rect width={mapWidth} height={mapHeight} fill="url(#tacticalGrid)" />

          {/* Bay of Bengal Water Area */}
          <path
            d="M 380 520 Q 420 380 480 300 Q 560 220 720 180 L 900 180 L 900 520 Z"
            fill="rgba(8, 20, 38, 0.55)"
            stroke="rgba(0, 245, 255, 0.15)"
            strokeWidth="1.5"
          />

          {/* Odisha Coastline Path */}
          <path
            d="M 120 520 Q 240 440 340 370 Q 420 310 470 270 Q 550 200 680 150 Q 780 110 900 80"
            fill="none"
            stroke="rgba(0, 245, 255, 0.4)"
            strokeWidth="2.5"
            strokeDasharray="4 2"
          />

          {/* Chilika Lake Lagoon */}
          <ellipse
            cx="260"
            cy="420"
            rx="55"
            ry="25"
            fill="rgba(14, 165, 233, 0.15)"
            stroke="rgba(14, 165, 233, 0.4)"
            strokeWidth="1.5"
          />
          <text x="235" y="424" fill="#38BDF8" fontSize="10" fontFamily="monospace">
            Chilika Lagoon
          </text>

          {/* 1. LAYER: ISRO RISAT-1A C-band SAR Flood Inundation Mask */}
          {activeLayers.sarFlood && (
            <g id="sarFloodLayer">
              <ellipse cx="380" cy="330" rx="90" ry="45" fill="url(#sarFloodGrad)" />
              <ellipse cx="510" cy="240" rx="75" ry="38" fill="url(#sarFloodGrad)" />
              <text x="320" y="325" fill="#C084FC" fontSize="10" fontFamily="monospace" fontWeight="bold">
                RISAT-1A SAR INUNDATION (348.6 km²)
              </text>
            </g>
          )}

          {/* 2. LAYER: Storm Surge Crest Corridor */}
          {activeLayers.stormSurge && (
            <path
              d="M 320 370 Q 440 290 530 240 Q 640 180 750 140"
              fill="none"
              stroke="#38BDF8"
              strokeWidth="12"
              strokeOpacity="0.3"
            />
          )}

          {/* 3. LAYER: Evacuation Road Corridors */}
          {activeLayers.evacuationRoutes && (
            <g id="roadCorridors">
              {/* NH-316 Puri to Bhubaneswar: At Risk */}
              <line
                x1="360"
                y1="340"
                x2="320"
                y2="210"
                stroke="#F59E0B"
                strokeWidth="3.5"
                strokeDasharray="6 3"
              />
              {/* Balikuda Causeway: Severed */}
              <line x1="490" y1="280" x2="540" y2="240" stroke="#F43F5E" strokeWidth="4" />
              {/* Inland SH-60: Clear */}
              <line x1="310" y1="220" x2="250" y2="170" stroke="#10B981" strokeWidth="3" />
            </g>
          )}

          {/* 4. LAYER: Holland Wind Vortex & Eyewall */}
          {activeLayers.windVortex && (
            <g id="windVortexLayer" transform={`translate(${eyePos.x}, ${eyePos.y})`}>
              {/* Eyewall radius circles */}
              <circle r="140" fill="url(#cycloneEyeGrad)" />
              <circle
                r="95"
                fill="none"
                stroke="#FF9F1C"
                strokeWidth="1.5"
                strokeDasharray="8 4"
                className="animate-spin"
                style={{ transformOrigin: "0px 0px", animationDuration: "20s" }}
              />
              <circle
                r="45"
                fill="none"
                stroke="#FF3366"
                strokeWidth="2.5"
                className="animate-spin"
                style={{ transformOrigin: "0px 0px", animationDuration: "10s" }}
              />
              {/* Eye center */}
              <circle r="6" fill="#FFFFFF" />
              <text x="12" y="4" fill="#FFFFFF" fontSize="11" fontFamily="monospace" fontWeight="bold">
                EYE: {stormName} ({maxWindKmh} km/h)
              </text>
            </g>
          )}

          {/* 5. LAYER: Infrastructure Asset Pins */}
          {activeLayers.assets &&
            nodes.map((node) => {
              const pos = projectToSvg(node.lat, node.lon);
              const isFailed = node.status === "FAILED";
              const isAtRisk = node.status === "AT_RISK";
              const isHardened = node.status === "HARDENED";
              const isSelected = selectedAsset?.id === node.id;

              const pinColor = isFailed
                ? "#F43F5E"
                : isAtRisk
                ? "#F59E0B"
                : isHardened
                ? "#00F5FF"
                : "#10B981";

              return (
                <g
                  key={node.id}
                  transform={`translate(${pos.x}, ${pos.y})`}
                  className="cursor-pointer"
                  onClick={() => {
                    setSelectedAsset(node);
                    onNodeClick?.(node);
                  }}
                >
                  {/* Pulsing ring if failed or selected */}
                  {(isFailed || isSelected) && (
                    <circle
                      r="16"
                      fill="none"
                      stroke={pinColor}
                      strokeWidth="2"
                      className="animate-ping"
                      opacity="0.6"
                    />
                  )}
                  <circle
                    r={isSelected ? "9" : "7"}
                    fill={pinColor}
                    stroke="#0B132B"
                    strokeWidth="2"
                  />
                  <text
                    x="11"
                    y="4"
                    fill={isSelected ? "#00F5FF" : "#CBD5E1"}
                    fontSize="9.5"
                    fontFamily="monospace"
                    fontWeight={isSelected ? "bold" : "normal"}
                  >
                    {node.name.replace(/\(.*?\)/g, "").trim().slice(0, 18)}
                  </text>
                </g>
              );
            })}
        </svg>

        {/* Selected Asset Floating Quick-Inspector Card */}
        {selectedAsset && (
          <div className="absolute bottom-4 left-4 p-3.5 rounded-xl glass-elevated border border-cyan-400/40 text-xs font-mono max-w-sm">
            <div className="flex items-center justify-between gap-2 border-b border-white/10 pb-1.5 mb-1.5">
              <span className="font-bold text-cyan-300 truncate">{selectedAsset.name}</span>
              <span
                className={`px-1.5 py-0.5 rounded text-[10px] font-bold ${
                  selectedAsset.status === "FAILED"
                    ? "bg-rose-500/20 text-rose-300"
                    : selectedAsset.status === "AT_RISK"
                    ? "bg-amber-500/20 text-amber-300"
                    : "bg-emerald-500/20 text-emerald-300"
                }`}
              >
                {selectedAsset.status}
              </span>
            </div>
            <div className="text-[11px] text-slate-300 space-y-1">
              <div>
                Elevation: {selectedAsset.elevationM}m · Pop:{" "}
                {selectedAsset.populationServed.toLocaleString()}
              </div>
              <div className="text-slate-400">
                Fragility Prob: {(selectedAsset.failureProbability * 100).toFixed(0)}%
              </div>
              {selectedAsset.directHazardCause && (
                <div className="text-rose-400 font-sans">
                  <strong>Trigger:</strong> {selectedAsset.directHazardCause}
                </div>
              )}
            </div>
          </div>
        )}
      </div>

      {/* 72-Hour Scrubbable Ensemble Time Bar */}
      <div className="p-4 bg-slate-950/90 border-t border-white/10 flex flex-col sm:flex-row items-center justify-between gap-4 font-mono text-xs">
        <div className="flex items-center gap-3 w-full sm:w-auto">
          <button
            onClick={() => setIsPlaying(!isPlaying)}
            className="p-2 rounded-xl bg-cyan-500 text-slate-950 hover:bg-cyan-400 cursor-pointer transition-all shadow-md shadow-cyan-500/30"
          >
            {isPlaying ? <Pause className="w-4 h-4" /> : <Play className="w-4 h-4 fill-current" />}
          </button>

          <button
            onClick={() => setTimeStepHours(48)}
            className="p-2 rounded-xl bg-slate-900 text-slate-300 hover:bg-slate-800 border border-white/10 cursor-pointer"
          >
            <RotateCcw className="w-4 h-4" />
          </button>

          <div>
            <div className="text-[10px] uppercase text-slate-400">Timeline Scrubber</div>
            <div className="font-bold text-cyan-300">
              {timeStepHours === 0 ? "LANDFALL CROSSING COAST" : `T-${timeStepHours} HOURS TO LANDFALL`}
            </div>
          </div>
        </div>

        {/* Range Slider */}
        <div className="flex-1 max-w-md w-full flex items-center gap-3">
          <span className="text-[10px] text-slate-500">T-48h</span>
          <input
            type="range"
            min="0"
            max="48"
            step="2"
            value={48 - timeStepHours}
            onChange={(e) => setTimeStepHours(48 - parseInt(e.target.value))}
            className="w-full accent-cyan-400 cursor-pointer"
          />
          <span className="text-[10px] text-rose-400 font-bold">Landfall</span>
        </div>
      </div>
    </div>
  );
}
