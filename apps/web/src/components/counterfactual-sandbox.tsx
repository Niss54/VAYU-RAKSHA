"use client";

import React, { useState } from "react";
import { type CounterfactualAction, formatInt } from "@/lib/vayu-engine";
import { Check, CheckCircle2, ChevronRight, FileCheck, Play, ShieldAlert, Sparkles, TrendingUp, Users, Zap } from "lucide-react";

interface CounterfactualSandboxProps {
  actions: CounterfactualAction[];
  onToggleAction?: (actionId: string, approved: boolean) => void;
  onRunSimulation?: () => void;
}

export function CounterfactualSandbox({
  actions,
  onToggleAction,
  onRunSimulation,
}: CounterfactualSandboxProps) {
  const [authorizedActions, setAuthorizedActions] = useState<Record<string, boolean>>({
    ACT_DE_ENERGIZE_COASTAL_SUBSTATIONS: true,
    ACT_PREPOSITION_HOSPITAL_FUEL: true,
  });

  const handleToggle = (actionId: string) => {
    const nextState = !authorizedActions[actionId];
    setAuthorizedActions((prev) => ({ ...prev, [actionId]: nextState }));
    onToggleAction?.(actionId, nextState);
  };

  const totalProtected = actions
    .filter((a) => authorizedActions[a.actionId])
    .reduce((sum, a) => sum + a.deltaPopulationProtected, 0);

  const totalSavedNodes = actions
    .filter((a) => authorizedActions[a.actionId])
    .reduce((sum, a) => sum + a.cascadeNodesSaved, 0);

  return (
    <div className="glass-tactical rounded-2xl p-5 border border-amber-500/20 flex flex-col gap-4">
      {/* Header */}
      <div className="flex flex-wrap items-center justify-between gap-3 pb-3 border-b border-white/10">
        <div className="flex items-center gap-2.5">
          <div className="p-2 rounded-xl bg-amber-500/10 text-amber-400 border border-amber-500/20">
            <Sparkles className="w-5 h-5" />
          </div>
          <div>
            <div className="flex items-center gap-2">
              <h3 className="text-sm font-bold tracking-wider font-mono text-amber-300">
                COUNTERFACTUAL PRE-LANDFALL ACTION OPTIMIZER
              </h3>
              <span className="px-2 py-0.5 rounded text-[10px] font-mono bg-amber-500/10 text-amber-400 border border-amber-500/30">
                WHAT-IF ENGINE
              </span>
            </div>
            <p className="text-xs text-slate-400">
              Simulate pre-landfall interventions and optimize lives saved vs economic disruption cost
            </p>
          </div>
        </div>

        {/* Live Impact Scoreboard */}
        <div className="flex items-center gap-4 bg-slate-950/70 px-4 py-2 rounded-xl border border-amber-500/30">
          <div className="text-left font-mono">
            <div className="text-[10px] uppercase text-slate-400 flex items-center gap-1">
              <Users className="w-3 h-3 text-cyan-400" />
              Protected Citizens
            </div>
            <div className="text-base font-bold text-cyan-300" suppressHydrationWarning>
              +{formatInt(totalProtected)}
            </div>
          </div>

          <div className="h-6 w-px bg-white/10"></div>

          <div className="text-left font-mono">
            <div className="text-[10px] uppercase text-slate-400 flex items-center gap-1">
              <Zap className="w-3 h-3 text-amber-400" />
              Saved Nodes
            </div>
            <div className="text-base font-bold text-amber-300">
              +{totalSavedNodes} Downstream
            </div>
          </div>
        </div>
      </div>

      {/* Action Queue List */}
      <div className="space-y-3">
        {actions.map((action, idx) => {
          const isApproved = !!authorizedActions[action.actionId];

          return (
            <div
              key={action.actionId}
              className={`p-4 rounded-xl border transition-all ${
                isApproved
                  ? "bg-slate-900/90 border-cyan-500/50 shadow-md shadow-cyan-950/40 ring-1 ring-cyan-500/30"
                  : "bg-slate-900/40 border-white/5 opacity-80 hover:opacity-100"
              }`}
            >
              <div className="flex flex-col md:flex-row md:items-center justify-between gap-3">
                <div className="space-y-1">
                  <div className="flex items-center gap-2">
                    <span className="font-mono text-xs font-bold text-slate-400">
                      RANK #{idx + 1}
                    </span>
                    <span
                      className={`px-2 py-0.5 rounded text-[10px] font-mono font-bold ${
                        action.priority === "CRITICAL"
                          ? "bg-rose-500/20 text-rose-300 border border-rose-500/40"
                          : "bg-amber-500/20 text-amber-300 border border-amber-500/40"
                      }`}
                    >
                      {action.priority}
                    </span>
                    <span className="text-xs font-mono text-slate-400">
                      Deadline: <strong className="text-slate-200">{action.windowDeadline}</strong>
                    </span>
                  </div>

                  <h4 className="text-sm font-semibold text-slate-100">{action.actionTitle}</h4>
                  <p className="text-xs text-slate-400 max-w-2xl">{action.description}</p>
                </div>

                {/* Metrics & Authorization Toggle */}
                <div className="flex items-center gap-4 shrink-0 justify-between md:justify-end">
                  <div className="text-right font-mono hidden sm:block">
                    <div className="text-[10px] text-slate-400">ROI SCORE</div>
                    <div className="text-sm font-bold text-emerald-400">{action.roiScore}</div>
                  </div>

                  <button
                    onClick={() => handleToggle(action.actionId)}
                    className={`px-3.5 py-2 rounded-xl text-xs font-mono font-bold flex items-center gap-2 transition-all cursor-pointer ${
                      isApproved
                        ? "bg-cyan-500 text-slate-950 hover:bg-cyan-400 shadow-md shadow-cyan-500/30"
                        : "bg-slate-800 text-slate-300 hover:bg-slate-700 border border-white/10"
                    }`}
                  >
                    {isApproved ? (
                      <>
                        <Check className="w-4 h-4 stroke-[3]" />
                        ORDER AUTHORIZED
                      </>
                    ) : (
                      <>
                        <FileCheck className="w-4 h-4" />
                        AUTHORIZE ORDER
                      </>
                    )}
                  </button>
                </div>
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}
