"use client";

import { istStamp, leadLabel, percent } from "@/lib/format";
import type { ForecastSummary, ScenarioDetail } from "@/lib/types";

const SHOWN = 5;

interface ParametricCardProps {
  scenario: ScenarioDetail;
  /** The as-issued forecast being replayed, or undefined on the best track. */
  forecast: ForecastSummary | undefined;
}

/**
 * Anticipatory finance: an illustrative parametric cover per district. In a forecast replay it shows the chance each
 * district triggers a payout (money that could move before landfall); on the best track, what triggered and when, and
 * whether the satellites saw outages there (basis risk).
 */
export function ParametricCard({ scenario, forecast }: ParametricCardProps) {
  const { terms, districts } = scenario.insurance;
  const triggered = districts.filter((d) => d.payout_share > 0 && d.observed_outage_rate != null);
  const spared = districts.filter((d) => d.payout_share === 0 && d.observed_outage_rate != null);
  const mean = (rows: typeof districts) =>
    rows.reduce((sum, d) => sum + (d.observed_outage_rate ?? 0), 0) / Math.max(rows.length, 1);

  return (
    <section aria-labelledby="brief-parametric">
      <h3 id="brief-parametric" className="label mb-2">
        Anticipatory finance · parametric cover
      </h3>
      <ol className="flex flex-col divide-y divide-[var(--line)] rounded-2xl border border-[var(--line)]">
        {forecast
          ? forecast.districts.slice(0, SHOWN).map((d) => (
              <li key={d.district} className="flex items-center gap-2 px-3.5 py-2 text-xs">
                <span className="text-[var(--text-primary)]">{d.district}</span>
                <span className="label ml-auto whitespace-nowrap">index {Math.round(d.index_kt)} kt</span>
                <span className="readout w-24 text-right text-[var(--text-primary)]">
                  {percent(d.p_trigger)} <span className="text-[var(--text-muted)]">trigger</span>
                </span>
              </li>
            ))
          : districts.slice(0, SHOWN).map((d) => (
              <li key={d.district} className="flex items-center gap-2 px-3.5 py-2 text-xs">
                <span className="text-[var(--text-primary)]">{d.district}</span>
                <span className="label ml-auto whitespace-nowrap">
                  {d.trigger_time
                    ? `${istStamp(d.trigger_time)} · ${leadLabel(d.trigger_time, scenario.landfall)}`
                    : "not triggered"}
                </span>
                <span
                  className={
                    d.payout_share > 0 ? "readout w-12 text-right !text-[var(--accent)]" : "readout w-12 text-right"
                  }
                >
                  {percent(d.payout_share)}
                </span>
              </li>
            ))}
      </ol>
      <p className="mt-2 text-xs leading-relaxed text-[var(--text-muted)]">
        {forecast
          ? `Share of the ${forecast.members} ECMWF members that trigger a payout: funds could be released before landfall. `
          : triggered.length > 0 && spared.length > 0
            ? `Satellite check: triggered districts lost power at ${percent(mean(triggered))} of lit substations, others at ${percent(mean(spared))}. `
            : ""}
        {terms}.
      </p>
    </section>
  );
}
