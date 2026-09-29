"use client";

import React, { useState } from "react";
import { type AgentTelemetry } from "@/lib/vayu-engine";
import { Activity, Brain, CheckCircle2, ChevronDown, ChevronUp, Cpu, Eye, Radio, Shield, Waves, Zap } from "lucide-react";

interface AgentBrainHudProps {
  telemetry: Record<string, AgentTelemetry>;
}

const AGENT_CONFIGS: Record<
  string,
  {
    icon: React.ComponentType<{ className?: string }>;
    title: string;
    subtitle: string;
    color: string;
    glowClass: string;
  }
> = {
  NIRNAY: {
    icon: Brain,
    title: "NIRNAY",
    subtitle: "Supervisor · Counterfactual Optimizer",
    color: "#00F5FF",
    glowClass: "glow-cyan",
  },
  BHUMI: {
    icon: Eye,
    title: "BHUMI",
    subtitle: "Earth Intel · ISRO RISAT-1A SAR",
    color: "#A855F7",
    glowClass: "glow-amber",
  },
  VAYU: {
    icon: Waves,
    title: "VAYU",
    subtitle: "Atmospheric · Holland Vortex Model",
    color: "#38BDF8",
    glowClass: "glow-cyan",
  },
  SETU: {
    icon: Zap,
    title: "SETU",
    subtitle: "Cascade Graph · NetworkX 5-Tier",
    color: "#FF9F1C",
    glowClass: "glow-amber",
  },
  SANCHAR: {
    icon: Radio,
    title: "SANCHAR",
    subtitle: "6-Lang Comms · Parametric Insurance",
    color: "#10B981",
    glowClass: "glow-emerald",
  },
};

export function AgentBrainHud({ telemetry }: AgentBrainHudProps) {
  const [expandedAgent, setExpandedAgent] = useState<string | null>("NIRNAY");

  const agents = ["NIRNAY", "BHUMI", "VAYU", "SETU", "SANCHAR"];

  return (
    <div className="glass-tactical rounded-2xl p-4 w-full border border-cyan-500/20">
      {/* Header bar */}
      <div className="flex items-center justify-between pb-3 border-b border-white/10">
        <div className="flex items-center gap-2.5">
          <div className="relative flex h-3 w-3">
            <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-cyan-400 opacity-75"></span>
            <span className="relative inline-flex rounded-full h-3 w-3 bg-cyan-500"></span>
          </div>
          <div>
            <div className="flex items-center gap-2">
              <span className="label-tactical text-cyan-400 font-bold tracking-widest">
                5-AGENT LANGGRAPH BRAIN HUD
              </span>
              <span className="px-1.5 py-0.5 rounded text-[10px] font-mono bg-cyan-500/10 text-cyan-300 border border-cyan-500/30">
                ACTIVE STATEGRAPH
              </span>
            </div>
            <p className="text-xs text-slate-400 mt-0.5">
              Deterministic multi-agent pipeline executing parallel satellite ingestion & cascade simulation
            </p>
          </div>
        </div>

        <div className="flex items-center gap-3">
          <div className="text-right hidden sm:block">
            <div className="label-tactical text-slate-400">Total Pipeline Latency</div>
            <div className="readout-tactical text-sm font-semibold text-cyan-300">
              {Object.values(telemetry).reduce((acc, t) => acc + (t?.latencyMs || 0), 0).toFixed(1)} ms
            </div>
          </div>
          <Cpu className="w-5 h-5 text-cyan-400/80 animate-pulse" />
        </div>
      </div>

      {/* Grid of Agent Nodes */}
      <div className="grid grid-cols-1 md:grid-cols-5 gap-2.5 mt-3">
        {agents.map((name) => {
          const cfg = AGENT_CONFIGS[name];
          const data = telemetry[name];
          const Icon = cfg.icon;
          const isSelected = expandedAgent === name;

          return (
            <div
              key={name}
              onClick={() => setExpandedAgent(isSelected ? null : name)}
              className={`p-3 rounded-xl cursor-pointer transition-all border ${
                isSelected
                  ? "bg-slate-800/80 border-cyan-400/50 shadow-lg shadow-cyan-950/50"
                  : "bg-slate-900/50 border-white/5 hover:border-cyan-500/30 hover:bg-slate-900/80"
              }`}
            >
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-2">
                  <div
                    className="p-1.5 rounded-lg"
                    style={{ backgroundColor: `${cfg.color}15`, color: cfg.color }}
                  >
                    <Icon className="w-4 h-4" />
                  </div>
                  <div>
                    <div className="text-xs font-bold tracking-wide font-mono" style={{ color: cfg.color }}>
                      {cfg.title}
                    </div>
                    <div className="text-[10px] text-slate-400 truncate max-w-[110px]">
                      {cfg.subtitle.split("·")[0]}
                    </div>
                  </div>
                </div>

                <div className="flex items-center gap-1">
                  <span className="inline-block w-2 h-2 rounded-full bg-emerald-400 animate-pulse"></span>
                  {isSelected ? (
                    <ChevronUp className="w-3.5 h-3.5 text-slate-400" />
                  ) : (
                    <ChevronDown className="w-3.5 h-3.5 text-slate-500" />
                  )}
                </div>
              </div>

              {/* Quick mini-stat */}
              <div className="mt-2.5 flex items-center justify-between text-[11px] font-mono text-slate-400 border-t border-white/5 pt-2">
                <span>{data?.latencyMs ? `${data.latencyMs}ms` : "Active"}</span>
                <span className="text-emerald-400 flex items-center gap-0.5">
                  <CheckCircle2 className="w-3 h-3" />
                  {(data?.confidenceScore ? data.confidenceScore * 100 : 98).toFixed(0)}%
                </span>
              </div>
            </div>
          );
        })}
      </div>

      {/* Expanded Agent Thought Trace Console */}
      {expandedAgent && telemetry[expandedAgent] && (
        <div className="mt-3 p-3.5 rounded-xl bg-slate-950/70 border border-cyan-500/30 text-xs">
          <div className="flex items-center justify-between text-slate-400 font-mono text-[11px] mb-1.5">
            <span className="flex items-center gap-1.5 text-cyan-300 font-bold">
              <Activity className="w-3.5 h-3.5 text-cyan-400" />
              {expandedAgent} AGENT THOUGHT TRACE & EXECUTION SUMMARY
            </span>
            <span>Step: {telemetry[expandedAgent].activeStep}</span>
          </div>
          <p className="text-slate-200 leading-relaxed font-sans pl-2 border-l-2 border-cyan-400/60">
            {telemetry[expandedAgent].lastThought}
          </p>
        </div>
      )}
    </div>
  );
}
