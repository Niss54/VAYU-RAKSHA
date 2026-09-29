"use client";

import { compactNumber } from "@/lib/format";
import type { ForecastSummary, ReplayMode } from "@/lib/types";

interface ReplayStripProps {
  forecasts: ForecastSummary[];
  mode: ReplayMode;
  onChange: (mode: ReplayMode) => void;
}

/** Switch between the best-track (hindsight) replay and each as-issued ensemble forecast. */
export function ReplayStrip({ forecasts, mode, onChange }: ReplayStripProps) {
  return (
    <div
      className="glass flex max-w-full items-center gap-1 overflow-x-auto rounded-full p-1"
      role="radiogroup"
      aria-label="Replay mode"
    >
      {forecasts.length > 0 && <span className="label shrink-0 pr-1 pl-3">As issued</span>}
      {forecasts.map((forecast) => (
        <button
          key={forecast.key}
          type="button"
          role="radio"
          aria-checked={mode.kind === "forecast" && mode.key === forecast.key}
          title={`${forecast.members} members · ${compactNumber(forecast.assets_likely_gale)} assets likely to get gales`}
          onClick={() => onChange({ kind: "forecast", key: forecast.key })}
          className="segment shrink-0"
        >
          T−{Math.round(forecast.lead_h)}h
        </button>
      ))}
      {forecasts.length > 0 && <span className="mx-1 h-4 w-px shrink-0 bg-[var(--line-strong)]" aria-hidden />}
      <button
        type="button"
        role="radio"
        aria-checked={mode.kind === "best-track"}
        title="Observed track, in hindsight: the backtest"
        onClick={() => onChange({ kind: "best-track" })}
        className="segment shrink-0"
      >
        Best track
      </button>
    </div>
  );
}
