"use client";

import React, { useState } from "react";
import { type DependencyEdge, type InfrastructureNode, formatInt } from "@/lib/vayu-engine";
import {
  AlertTriangle,
  Building2,
  CheckCircle2,
  Droplets,
  Network,
  Radio,
  Shield,
  Truck,
  Zap,
} from "lucide-react";

interface CascadeTopologyCanvasProps {
  nodes: InfrastructureNode[];
  edges: DependencyEdge[];
  onNodeSelect?: (node: InfrastructureNode) => void;
}

const TIER_META = {
  L1: { label: "L1: High-Voltage Transmission", color: "#38BDF8", icon: Zap },
  L2: { label: "L2: Hospitals & Shelters", color: "#F43F5E", icon: Building2 },
  L3: { label: "L3: Arterial Bridges & Roads", color: "#F59E0B", icon: Truck },
  L4: { label: "L4: Telecom & VHF Relays", color: "#A855F7", icon: Radio },
  L5: { label: "L5: Water Treatment & Headworks", color: "#06B6D4", icon: Droplets },
};

export function CascadeTopologyCanvas({ nodes, edges, onNodeSelect }: CascadeTopologyCanvasProps) {
  const [selectedNodeId, setSelectedNodeId] = useState<string>("H_PURI_DISTRICT");

  const selectedNode = nodes.find((n) => n.id === selectedNodeId) || nodes[0];

  // Group nodes by tier
  const tiers = ["L1", "L2", "L3", "L4", "L5"] as const;
  const nodesByTier: Record<string, InfrastructureNode[]> = {
    L1: nodes.filter((n) => n.tier === "L1"),
    L2: nodes.filter((n) => n.tier === "L2"),
    L3: nodes.filter((n) => n.tier === "L3"),
    L4: nodes.filter((n) => n.tier === "L4"),
    L5: nodes.filter((n) => n.tier === "L5"),
  };

  const getStatusBadge = (status: InfrastructureNode["status"]) => {
    switch (status) {
      case "FAILED":
        return {
          bg: "bg-rose-500/15 text-rose-300 border-rose-500/40",
          dot: "bg-rose-500 animate-pulse",
          text: "CASCADE FAILED",
        };
      case "AT_RISK":
        return {
          bg: "bg-amber-500/15 text-amber-300 border-amber-500/40",
          dot: "bg-amber-400",
          text: "HIGH RISK",
        };
      case "HARDENED":
        return {
          bg: "bg-cyan-500/15 text-cyan-300 border-cyan-500/40",
          dot: "bg-cyan-400",
          text: "HARDENED PRE-LANDFALL",
        };
      default:
        return {
          bg: "bg-emerald-500/15 text-emerald-300 border-emerald-500/40",
          dot: "bg-emerald-400",
          text: "OPERATIONAL",
        };
    }
  };

  return (
    <div className="glass-tactical rounded-2xl p-5 border border-cyan-500/20 flex flex-col gap-4">
      {/* Topology Header */}
      <div className="flex flex-wrap items-center justify-between gap-2 pb-3 border-b border-white/10">
        <div className="flex items-center gap-2">
          <Network className="w-5 h-5 text-cyan-400" />
          <div>
            <h3 className="text-sm font-bold tracking-wider font-mono text-cyan-300">
              NETWORKX 5-TIER CASCADE FAILURE TOPOLOGY
            </h3>
            <p className="text-xs text-slate-400">
              Visualizing cross-infrastructure dependency chain and ripple failure propagation
            </p>
          </div>
        </div>

        <div className="flex items-center gap-2 text-xs font-mono">
          <span className="flex items-center gap-1.5 px-2 py-0.5 rounded bg-rose-500/10 text-rose-300 border border-rose-500/20">
            <span className="w-2 h-2 rounded-full bg-rose-500 animate-pulse"></span>
            Failed ({nodes.filter((n) => n.status === "FAILED").length})
          </span>
          <span className="flex items-center gap-1.5 px-2 py-0.5 rounded bg-amber-500/10 text-amber-300 border border-amber-500/20">
            <span className="w-2 h-2 rounded-full bg-amber-400"></span>
            At Risk ({nodes.filter((n) => n.status === "AT_RISK").length})
          </span>
          <span className="flex items-center gap-1.5 px-2 py-0.5 rounded bg-emerald-500/10 text-emerald-300 border border-emerald-500/20">
            <span className="w-2 h-2 rounded-full bg-emerald-400"></span>
            Normal ({nodes.filter((n) => n.status === "OPERATIONAL").length})
          </span>
        </div>
      </div>

      {/* Main Graph Grid by Tiers */}
      <div className="grid grid-cols-1 md:grid-cols-5 gap-3 bg-slate-950/60 p-4 rounded-xl border border-white/5">
        {tiers.map((tierKey) => {
          const tierInfo = TIER_META[tierKey];
          const tierNodes = nodesByTier[tierKey] || [];
          const Icon = tierInfo.icon;

          return (
            <div key={tierKey} className="flex flex-col gap-2.5">
              <div className="flex items-center gap-1.5 text-[11px] font-mono font-bold text-slate-300 pb-1.5 border-b border-white/10">
                <Icon className="w-3.5 h-3.5" style={{ color: tierInfo.color }} />
                <span className="truncate">{tierInfo.label.split(":")[0]}</span>
              </div>

              <div className="flex flex-col gap-2">
                {tierNodes.map((node) => {
                  const badge = getStatusBadge(node.status);
                  const isSelected = selectedNodeId === node.id;

                  return (
                    <div
                      key={node.id}
                      onClick={() => {
                        setSelectedNodeId(node.id);
                        onNodeSelect?.(node);
                      }}
                      className={`p-2.5 rounded-lg border text-left cursor-pointer transition-all ${
                        isSelected
                          ? "bg-slate-800 border-cyan-400 shadow-md shadow-cyan-950/60 ring-1 ring-cyan-400/50"
                          : "bg-slate-900/60 border-white/5 hover:border-white/20 hover:bg-slate-900"
                      }`}
                    >
                      <div className="flex items-start justify-between gap-1">
                        <span className="text-xs font-semibold text-slate-100 line-clamp-1">
                          {node.name.replace(/\(.*?\)/g, "").trim()}
                        </span>
                        <span className={`w-2 h-2 rounded-full shrink-0 mt-1 ${badge.dot}`}></span>
                      </div>

                      <div className="flex items-center justify-between text-[10px] font-mono text-slate-400 mt-2">
                        <span>P(fail): {(node.failureProbability * 100).toFixed(0)}%</span>
                        {node.cascadeDepth > 0 && (
                          <span className="text-rose-400 font-bold">Hop {node.cascadeDepth}</span>
                        )}
                      </div>
                    </div>
                  );
                })}
              </div>
            </div>
          );
        })}
      </div>

      {/* Selected Node Inspector Detail Card */}
      {selectedNode && (
        <div className="p-4 rounded-xl bg-slate-900/90 border border-cyan-500/30 flex flex-col md:flex-row gap-4 justify-between items-start">
          <div className="space-y-1.5 max-w-xl">
            <div className="flex items-center gap-2">
              <h4 className="text-sm font-bold text-slate-100">{selectedNode.name}</h4>
              <span
                className={`text-[10px] font-mono px-2 py-0.5 rounded border ${
                  getStatusBadge(selectedNode.status).bg
                }`}
              >
                {getStatusBadge(selectedNode.status).text}
              </span>
            </div>
            <p className="text-xs text-slate-300">
              <strong className="text-slate-400">Capacity & Role:</strong> {selectedNode.capacity} · District:{" "}
              {selectedNode.district} · Elevation: {selectedNode.elevationM}m
            </p>

            {/* Plain language reasons list */}
            {selectedNode.plainLanguageReasons.length > 0 && (
              <div className="mt-2 space-y-1">
                <span className="text-[11px] font-mono text-rose-300 font-semibold block">
                  Root Hazard & Cascade Diagnostics:
                </span>
                {selectedNode.plainLanguageReasons.map((r, i) => (
                  <div key={i} className="text-xs text-slate-300 flex items-start gap-1.5 pl-1">
                    <span className="text-rose-400 font-bold">•</span>
                    <span>{r}</span>
                  </div>
                ))}
              </div>
            )}
          </div>

          <div className="flex flex-row md:flex-col gap-3 shrink-0 text-right font-mono">
            <div>
              <div className="text-[10px] uppercase text-slate-400">Population Served</div>
              <div className="text-sm font-bold text-cyan-300" suppressHydrationWarning>
                {formatInt(selectedNode.populationServed)}
              </div>
            </div>
            <div>
              <div className="text-[10px] uppercase text-slate-400">Generator Reserve</div>
              <div className="text-sm font-bold text-amber-300">
                {selectedNode.backupPowerHrs} Hours
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
