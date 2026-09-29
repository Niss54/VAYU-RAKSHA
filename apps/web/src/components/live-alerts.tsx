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
    <ol className="flex w-80 flex-col items-stretch gap-2" aria-live="polite" aria-label="Live alerts">
      {alerts.map((alert, i) => {
        const urgent = !alert.kind.endsWith("-soon");
        return (
          <li
            key={alert.id}
            className="alert-card"
            style={{ "--tilt": `${TILTS[i % TILTS.length]}deg` } as CSSProperties}
          >
            <button
              type="button"
              disabled={!alert.assetId}
              onClick={() => alert.assetId && onSelect(alert.assetId)}
              className={clsx(
                "glass w-full rounded-2xl px-3.5 py-3 text-left transition-colors enabled:hover:border-[var(--line-strong)]",
                urgent && "border-[var(--accent)]/40",
              )}
            >
              <div className="flex items-center gap-2">
                <span className="relative flex size-2" aria-hidden>
                  {urgent && (
                    <span className="absolute inline-flex size-full animate-ping rounded-full bg-[var(--accent)] opacity-60" />
                  )}
                  <span
                    className={clsx(
                      "relative inline-flex size-2 rounded-full",
                      urgent ? "bg-[var(--accent)]" : "border border-[var(--text-muted)]",
                    )}
                  />
                </span>
                <span className={clsx("label whitespace-nowrap", urgent && "!text-[var(--accent)]")}>
                  {LABELS[alert.kind]}
                </span>
                <span className="label ml-auto whitespace-nowrap">{istStamp(alert.at)}</span>
              </div>
              <div className="mt-1.5 text-sm leading-snug font-medium text-[var(--text-primary)]">{alert.title}</div>
              <div className="mt-0.5 text-xs text-[var(--text-secondary)]">{alert.detail}</div>
            </button>
          </li>
        );
      })}
    </ol>
  );
}
