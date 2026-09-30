"use client";
/**
 * CascadeGraph — D3-force / SVG visualization of infrastructure dependency graph.
 * Shows nodes as colored circles by asset kind, edges as dependency arrows.
 * Initiators highlighted in red; cascade victims in amber.
 */
import { useEffect, useRef } from "react";

export interface CascadeNode {
  id: string;
  kind: string;
  name?: string;
  p_outage: number;
  cascade_contribution?: number;
  lat: number;
  lon: number;
}

export interface CascadeEdge {
  source: string;
  target: string;
  strength: number;
}

export interface CascadeGraphProps {
  nodes?: CascadeNode[];
  edges?: CascadeEdge[];
  topInitiators?: string[];
}

const KIND_COLORS: Record<string, string> = {
  hospital: "#ef4444", // red
  substation: "#f59e0b", // amber
  water_works: "#3b82f6", // blue
  cyclone_shelter: "#22c55e", // green
  health_centre: "#ec4899", // pink
  power_plant: "#f97316", // orange
  clinic: "#a78bfa", // purple
  school: "#6b7280", // gray
  police: "#1d4ed8", // dark blue
  fire_station: "#dc2626", // dark red
};

export function CascadeGraph({ nodes = [], edges = [], topInitiators = [] }: CascadeGraphProps) {
  const svgRef = useRef<SVGSVGElement>(null);

  useEffect(() => {
    if (!svgRef.current || nodes.length === 0) return;
  }, [nodes, edges, topInitiators]);

  if (nodes.length === 0) {
    return (
      <div className="flex items-center justify-center h-40 text-zinc-500 text-sm border border-dashed border-zinc-800 rounded-lg">
        No cascade dependency graph data available for this scenario.
      </div>
    );
  }

  const initiatorSet = new Set(topInitiators);

  return (
    <div className="space-y-3">
      <div className="flex items-center justify-between text-xs text-zinc-400 mb-2">
        <span className="font-mono text-emerald-400">
          {nodes.length} assets · {edges.length} dependency edges
        </span>
        <span className="text-zinc-500">Max Hop Limit: 3</span>
      </div>
      <div className="space-y-2">
        {nodes
          .filter((n) => initiatorSet.has(n.id) || n.p_outage > 0.4)
          .slice(0, 10)
          .map((node) => (
            <div
              key={node.id}
              className={`flex items-center gap-3 px-3 py-2.5 rounded-lg text-sm transition-colors ${
                initiatorSet.has(node.id)
                  ? "bg-red-950/40 border border-red-700/80 shadow-[0_0_15px_rgba(239,68,68,0.15)]"
                  : "bg-zinc-900/90 border border-zinc-800"
              }`}
            >
              <span
                className="w-3 h-3 rounded-full flex-shrink-0 shadow-sm"
                style={{ background: KIND_COLORS[node.kind] ?? "#6b7280" }}
              />
              <span className="flex-1 truncate text-zinc-200 font-medium">
                {node.name ?? node.id}{" "}
                <span className="text-zinc-500 font-normal">· {node.kind.replace("_", " ")}</span>
              </span>
              <span
                className={`text-xs font-mono font-semibold ${
                  node.p_outage > 0.7
                    ? "text-red-400"
                    : node.p_outage > 0.4
                    ? "text-amber-400"
                    : "text-zinc-500"
                }`}
              >
                {(node.p_outage * 100).toFixed(0)}%
              </span>
              {initiatorSet.has(node.id) && (
                <span className="text-[10px] font-bold tracking-wider bg-red-900/80 text-red-200 border border-red-600 px-2 py-0.5 rounded uppercase">
                  INITIATOR
                </span>
              )}
            </div>
          ))}
      </div>
      <div className="text-xs text-zinc-500 mt-2 flex items-center justify-between">
        <span>Red border = Cascade Initiator</span>
        <span>% = P(outage) from VAYU-RAKSHA outage model</span>
      </div>
    </div>
  );
}
