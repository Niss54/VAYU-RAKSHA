"use client";

import React from "react";
import { type ParametricInsuranceTrigger } from "@/lib/vayu-engine";
import { CheckCircle2, Coins, ExternalLink, FileCode, Layers, ShieldCheck, Sparkles, Wind } from "lucide-react";

interface ParametricSmartTriggerProps {
  insurance: ParametricInsuranceTrigger;
}

export function ParametricSmartTrigger({ insurance }: ParametricSmartTriggerProps) {
  const isTriggered = insurance.triggerStatus === "TRIGGER_DISPATCHED";

  return (
    <div className="glass-tactical rounded-2xl p-5 border border-emerald-500/25 flex flex-col gap-4">
      {/* Header */}
      <div className="flex flex-wrap items-center justify-between gap-2 pb-3 border-b border-white/10">
        <div className="flex items-center gap-2.5">
          <div className="p-2 rounded-xl bg-emerald-500/10 text-emerald-400 border border-emerald-500/20">
            <Coins className="w-5 h-5" />
          </div>
          <div>
            <div className="flex items-center gap-2">
              <h3 className="text-sm font-bold tracking-wider font-mono text-emerald-300">
                PARAMETRIC INSURANCE SMART TRIGGER ENGINE
              </h3>
              <span className="px-2 py-0.5 rounded text-[10px] font-mono bg-emerald-500/10 text-emerald-400 border border-emerald-500/30">
                ZERO ADJUSTMENT DELAY
              </span>
            </div>
            <p className="text-xs text-slate-400">
              Autonomous satellite verification triggers immediate emergency liquidity within hours of landfall
            </p>
          </div>
        </div>

        {/* Payout Badge */}
        <div className="bg-emerald-950/60 border border-emerald-500/40 px-3.5 py-1.5 rounded-xl flex items-center gap-2.5">
          <div className="text-right font-mono">
            <div className="text-[10px] text-emerald-400 uppercase font-semibold">Instant Liquidity Release</div>
            <div className="text-lg font-bold text-emerald-300">₹{insurance.payoutLiquidityInrCrores} Crores</div>
          </div>
          <ShieldCheck className="w-6 h-6 text-emerald-400 shrink-0" />
        </div>
      </div>

      {/* Threshold Condition Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
        {/* Wind Speed Condition */}
        <div className="p-3.5 rounded-xl bg-slate-900/80 border border-white/5 space-y-2">
          <div className="flex items-center justify-between text-xs font-mono">
            <span className="flex items-center gap-1.5 text-slate-300">
              <Wind className="w-4 h-4 text-cyan-400" />
              Sustained Wind Threshold
            </span>
            <span className="text-emerald-400 font-bold flex items-center gap-1">
              <CheckCircle2 className="w-3.5 h-3.5" /> MET
            </span>
          </div>

          <div className="flex items-baseline justify-between pt-1">
            <div className="text-xs text-slate-400">Observed vs Trigger:</div>
            <div className="text-sm font-mono font-bold text-slate-100">
              <span className="text-cyan-300">{insurance.observedWindKmh} km/h</span>{" "}
              <span className="text-slate-500">/</span>{" "}
              <span className="text-slate-400">{insurance.windThresholdKmh} km/h</span>
            </div>
          </div>

          <div className="w-full bg-slate-800 h-1.5 rounded-full overflow-hidden">
            <div
              className="bg-cyan-400 h-full rounded-full"
              style={{
                width: `${Math.min(100, (insurance.observedWindKmh / insurance.windThresholdKmh) * 100)}%`,
              }}
            ></div>
          </div>
        </div>

        {/* SAR Flood Extent Condition */}
        <div className="p-3.5 rounded-xl bg-slate-900/80 border border-white/5 space-y-2">
          <div className="flex items-center justify-between text-xs font-mono">
            <span className="flex items-center gap-1.5 text-slate-300">
              <Layers className="w-4 h-4 text-violet-400" />
              ISRO RISAT-1A SAR Flood Extent
            </span>
            <span className="text-emerald-400 font-bold flex items-center gap-1">
              <CheckCircle2 className="w-3.5 h-3.5" /> MET
            </span>
          </div>

          <div className="flex items-baseline justify-between pt-1">
            <div className="text-xs text-slate-400">Observed vs Trigger:</div>
            <div className="text-sm font-mono font-bold text-slate-100">
              <span className="text-violet-300">{insurance.observedFloodPct}%</span>{" "}
              <span className="text-slate-500">/</span>{" "}
              <span className="text-slate-400">{insurance.floodExtentThresholdPct}%</span>
            </div>
          </div>

          <div className="w-full bg-slate-800 h-1.5 rounded-full overflow-hidden">
            <div
              className="bg-violet-400 h-full rounded-full"
              style={{
                width: `${Math.min(100, (insurance.observedFloodPct / insurance.floodExtentThresholdPct) * 100)}%`,
              }}
            ></div>
          </div>
        </div>
      </div>

      {/* Cryptographic Smart Contract Execution Banner */}
      <div className="p-3 rounded-xl bg-slate-950/80 border border-emerald-500/30 flex flex-col md:flex-row items-start md:items-center justify-between gap-2 text-xs font-mono">
        <div className="flex items-center gap-2 text-slate-300">
          <FileCode className="w-4 h-4 text-emerald-400 shrink-0" />
          <span className="text-slate-400">Smart Contract Hash:</span>
          <span className="text-emerald-300 truncate max-w-xs">{insurance.payoutSmartContractHash}</span>
        </div>

        <div className="flex items-center gap-2 text-slate-400 text-[11px]">
          <span>Policy: {insurance.policyId}</span>
          <span className="text-slate-600">|</span>
          <span className="text-cyan-400">{insurance.insuredEntity}</span>
        </div>
      </div>
    </div>
  );
}
