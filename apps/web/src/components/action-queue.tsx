"use client";
/**
 * ActionQueue — ranked pre-landfall hardening actions from counterfactual optimizer.
 * Shows: rank, timing, action text, benefit-cost ratio, cascade victims prevented.
 */
import type { ActionItem } from "@/lib/types";

export interface ActionQueueProps {
  actions?: ActionItem[];
  landfallTime?: string;
}

const PRIORITY_COLORS = [
  "bg-red-700/90 border-red-600",
  "bg-orange-700/90 border-orange-600",
  "bg-amber-700/90 border-amber-600",
  "bg-yellow-700/90 border-yellow-600",
  "bg-lime-700/90 border-lime-600",
];

export function ActionQueue({ actions = [], landfallTime }: ActionQueueProps) {
  if (!actions || actions.length === 0) {
    return (
      <div className="flex items-center justify-center h-24 text-zinc-500 text-sm border border-dashed border-zinc-800 rounded-lg">
        No counterfactual pre-landfall actions computed yet.
      </div>
    );
  }

  return (
    <div className="space-y-3">
      <div className="flex items-center justify-between text-xs text-zinc-400">
        <span className="font-mono text-cyan-400">
          {actions.length} PRE-LANDFALL DIRECTIVES
        </span>
        <span className="text-zinc-500">
          Ranked by Population Benefit ÷ Operational Disruption
        </span>
      </div>
      <div className="space-y-3">
        {actions.map((action) => (
          <div
            key={action.rank}
            className="bg-zinc-900/90 border border-zinc-800 rounded-lg overflow-hidden shadow-sm"
          >
            <div
              className={`flex items-center gap-3 px-3.5 py-2 text-white border-b ${
                PRIORITY_COLORS[action.rank - 1] ?? "bg-zinc-800 border-zinc-700"
              }`}
            >
              <span className="font-black text-sm">#{action.rank}</span>
              <span className="text-sm font-semibold tracking-wide">
                T-{action.timing_hours_before_landfall}h · {action.asset_kind.replace("_", " ").toUpperCase()}
              </span>
              <span className="ml-auto font-mono text-xs bg-black/30 px-2 py-0.5 rounded border border-white/20">
                BCR {action.benefit_cost_ratio.toFixed(1)}
              </span>
            </div>
            <div className="px-3.5 py-2.5 space-y-2">
              <p className="text-zinc-200 text-xs leading-relaxed font-medium">
                {action.hardening_action}
              </p>
              <div className="flex flex-wrap items-center gap-4 text-[11px] text-zinc-400 pt-1 border-t border-zinc-800/60">
                <span className="flex items-center gap-1 text-emerald-400 font-mono">
                  🔗 {action.cascade_victims_prevented} cascade assets prevented
                </span>
                <span className="flex items-center gap-1 text-blue-400 font-mono">
                  👥 ~{Math.round(action.cascade_population_protected).toLocaleString()} people protected
                </span>
                <span className="flex items-center gap-1 text-amber-400 font-mono ml-auto font-bold">
                  P(outage) {(action.direct_p_outage * 100).toFixed(0)}%
                </span>
              </div>
            </div>
          </div>
        ))}
      </div>
      <p className="text-[11px] text-zinc-500 pt-1">
        VAYU-RAKSHA Counterfactual Engine · Benefit-cost ratio (BCR) = $\Delta$ Population benefit ÷ operational disruption proxy
      </p>
    </div>
  );
}
