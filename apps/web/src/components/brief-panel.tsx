"use client";

import { clsx } from "clsx";

import { BulletinCard } from "@/components/bulletin-card";
import { LiveCard } from "@/components/live-card";
import { ParametricCard } from "@/components/parametric-card";
import { Tile } from "@/components/tile";
import { useAdvisories } from "@/lib/api";
import type { Brief } from "@/lib/brief";
import { compactNumber, istStamp } from "@/lib/format";
import type { ForecastSummary, ScenarioDetail } from "@/lib/types";

interface BriefPanelProps {
  scenario: ScenarioDetail;
  /** The forecast being replayed, or undefined on the best track. */
  forecast: ForecastSummary | undefined;
  brief: Brief;
  onOpenAsset: (assetId: string) => void;
  onShowPriorities: () => void;
  /** Colours the map by surge water. */
  onShowFlood: () => void;
  onDraftAdvisory: () => void;
}

/**
 * The duty brief: the situation, the exceptions that need attention, recommended actions per agency and the
 * advisory audit trail. Everything is re-derived as the replay moves; every item drills down into the map and list.
 */
export function BriefPanel({
  scenario,
  forecast,
  brief,
  onOpenAsset,
  onShowPriorities,
  onShowFlood,
  onDraftAdvisory,
}: BriefPanelProps) {
  const { data: advisories, error } = useAdvisories(scenario.id);
  const { next } = brief;

  return (
    <div className="flex min-h-0 flex-1 flex-col gap-5 overflow-y-auto px-4 pb-4">
      <p className="text-[15px] leading-relaxed text-[var(--text-primary)]">{brief.summary}</p>

      <BulletinCard scenario={scenario} forecastIssued={forecast?.issued ?? null} />

      <LiveCard regionId={scenario.region.id} />

      <section aria-label="Exceptions" className="grid grid-cols-2 gap-2">
        <Tile
          label="At risk"
          value={compactNumber(brief.likely)}
          hint={brief.hazard === "lose power" ? "outage likely" : "gales likely"}
          onClick={onShowPriorities}
        />
        <Tile label="Gales in" value={compactNumber(brief.reached)} hint={`of ${compactNumber(brief.likely)}`} />
        <Tile
          label="Next gales"
          value={next ? `${next.hours} h` : "–"}
          hint={next?.name ?? "none due"}
          onClick={next ? () => onOpenAsset(next.assetId) : undefined}
        />
        {brief.flooded != null && (
          <Tile
            label="Surge flood"
            value={compactNumber(brief.flooded)}
            hint="sites in the surge zone"
            onClick={onShowFlood}
          />
        )}
      </section>

      <section aria-labelledby="brief-actions">
        <h3 id="brief-actions" className="label mb-2">
          Recommended actions · before gales arrive
        </h3>
        {brief.actions.length === 0 ? (
          <p className="rounded-2xl border border-[var(--line)] px-3.5 py-3 text-sm text-[var(--text-secondary)]">
            All clear: no site needs action.
          </p>
        ) : (
          <ol className="flex flex-col gap-2">
            {brief.actions.map((action) => (
              <li key={action.agency}>
                <button
                  type="button"
                  onClick={() => action.leadId && onOpenAsset(action.leadId)}
                  className="w-full rounded-2xl border border-[var(--line)] bg-[var(--surface-2)] px-3.5 py-3 text-left transition-colors hover:border-[var(--line-strong)]"
                >
                  <div className="flex items-center gap-2">
                    <span className="label whitespace-nowrap">{action.agency}</span>
                    <span
                      className={clsx(
                        "label ml-auto whitespace-nowrap",
                        action.deadline && !action.late && "!text-[var(--accent)]",
                      )}
                    >
                      {action.deadline == null
                        ? "No gales"
                        : action.late
                          ? `Gales ${action.hours} h ago`
                          : `In ${action.hours} h`}
                    </span>
                  </div>
                  <div className="mt-1 text-sm font-medium text-[var(--text-primary)]">{action.task}</div>
                  <div className="mt-0.5 text-xs text-[var(--text-secondary)]">
                    {action.sites} {action.sites === 1 ? "site" : "sites"}, led by {action.leadName}
                    {action.deadline && ` · gales ${istStamp(action.deadline)}`}
                  </div>
                </button>
              </li>
            ))}
          </ol>
        )}
      </section>

      <ParametricCard scenario={scenario} forecast={forecast} />

      <section aria-labelledby="brief-advisories">
        <div className="mb-2 flex items-center gap-2">
          <h3 id="brief-advisories" className="label">
            Advisories · audit log
          </h3>
          <button type="button" onClick={onDraftAdvisory} className="btn-primary ml-auto px-3 py-1 text-xs">
            Draft advisory
          </button>
        </div>
        {error ? (
          <p className="text-sm text-[var(--text-secondary)]">The audit log is unavailable right now.</p>
        ) : !advisories ? (
          <div className="h-14 animate-pulse rounded-2xl bg-white/[0.04]" />
        ) : advisories.length === 0 ? (
          <p className="text-sm text-[var(--text-secondary)]">No advisory decided for this storm yet.</p>
        ) : (
          <ul className="flex flex-col gap-2">
            {advisories.map((advisory) => (
              <li key={advisory.id} className="rounded-2xl border border-[var(--line)] px-3.5 py-3">
                <div className="flex items-center gap-2">
                  <span
                    className={clsx(
                      "label rounded-full border px-2 py-0.5",
                      advisory.status === "issued"
                        ? "border-[var(--accent)]/50 !text-[var(--accent)]"
                        : "border-[var(--line-strong)]",
                    )}
                  >
                    {advisory.status === "issued" ? "Issued" : "Rejected"}
                  </span>
                  <span className="label ml-auto whitespace-nowrap">{istStamp(advisory.decidedAt)}</span>
                </div>
                <div className="mt-1.5 text-sm leading-snug text-[var(--text-primary)]">{advisory.headline}</div>
                <div className="mt-0.5 text-xs text-[var(--text-muted)]">
                  {advisory.replay === "best-track" ? "Best-track replay" : `Forecast issued ${advisory.replay}`}
                </div>
              </li>
            ))}
          </ul>
        )}
      </section>
    </div>
  );
}
