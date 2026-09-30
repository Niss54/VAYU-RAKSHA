"use client";

import { clsx } from "clsx";
import type { CSSProperties } from "react";

import type { LiveAlert } from "@/lib/alerts";
import { istStamp } from "@/lib/format";

const TILTS = [-1.2, 0.9, -0.5]; // slight scatter, like notifications landing on the map
const LABELS: Record<LiveAlert["kind"], string> = {
  landfall: "Landfall",
  "hurricane-now": "Hurricane force",
  "gales-now": "Gales now",
  "hurricane-soon": "Incoming",
  "gales-soon": "Incoming",
};

interface LiveAlertsProps {
  alerts: LiveAlert[];
  onSelect: (assetId: string) => void;
}

/** Floating alert cards over the map, re-derived as the replay moves; new ones animate in. */
export function LiveAlerts({ alerts, onSelect }: LiveAlertsProps) {
  return (
    <ol className="flex w-[340px] flex-col items-stretch gap-2.5" aria-live="polite" aria-label="Live alerts">
      {alerts.map((alert, i) => {
        const urgent = !alert.kind.endsWith("-soon");
        return (
          <li
            key={alert.id}
            className="alert-card transition-transform duration-300 hover:scale-[1.02]"
            style={{ "--tilt": `${TILTS[i % TILTS.length]}deg` } as CSSProperties}
          >
            <button
              type="button"
              disabled={!alert.assetId}
              onClick={() => alert.assetId && onSelect(alert.assetId)}
              className={clsx(
                "group relative w-full rounded-2xl px-4 py-3.5 text-left transition-all duration-200 cursor-pointer",
                "bg-[#15171b]/92 backdrop-blur-xl border",
                urgent
                  ? "border-[#f28a2e]/45 hover:border-[#f28a2e] shadow-[0_10px_30px_rgba(0,0,0,0.8),0_0_18px_rgba(242,138,46,0.2)] hover:shadow-[0_12px_36px_rgba(0,0,0,0.9),0_0_24px_rgba(242,138,46,0.35)]"
                  : "border-white/12 hover:border-white/25 shadow-[0_8px_25px_rgba(0,0,0,0.7)]",
              )}
              style={{
                background: urgent
                  ? "linear-gradient(135deg, rgba(28, 23, 20, 0.95) 0%, rgba(21, 23, 27, 0.92) 100%)"
                  : "rgba(21, 23, 27, 0.9)",
              }}
            >
              <div className="flex items-center gap-2">
                <span className="relative flex size-2.5" aria-hidden>
                  {urgent && (
                    <span className="absolute inline-flex size-full animate-ping rounded-full bg-[#f28a2e] opacity-75" />
                  )}
                  <span
                    className={clsx(
                      "relative inline-flex size-2.5 rounded-full",
                      urgent ? "bg-[#f28a2e] shadow-[0_0_8px_#f28a2e]" : "bg-zinc-500",
                    )}
                  />
                </span>
                <span
                  className={clsx(
                    "text-[10.5px] font-mono tracking-widest uppercase font-bold whitespace-nowrap",
                    urgent ? "text-[#f28a2e]" : "text-zinc-400",
                  )}
                >
                  {LABELS[alert.kind]}
                </span>
                <span className="text-[11px] font-mono tracking-wider text-zinc-400 ml-auto whitespace-nowrap">
                  {istStamp(alert.at)}
                </span>
              </div>
              <div className="mt-2 text-[14px] leading-snug font-semibold text-white tracking-tight group-hover:text-amber-100 transition-colors">
                {alert.title}
              </div>
              <div className="mt-1 text-xs text-zinc-400 leading-relaxed font-sans">
                {alert.detail}
              </div>
            </button>
          </li>
        );
      })}
    </ol>
  );
}
