"use client";

import type { ReactNode } from "react";

import { useBulletin } from "@/lib/api";
import { istStamp } from "@/lib/format";
import type { ScenarioDetail } from "@/lib/types";

interface BulletinCardProps {
  scenario: ScenarioDetail;
  /** Issue time of the forecast being replayed; a bulletin issued after it is not shown (no hindsight). */
  forecastIssued: string | null;
}

function Row({ label, children }: { label: string; children: ReactNode }) {
  return (
    <div className="grid grid-cols-[4.5rem_1fr] gap-2 text-xs">
      <dt className="label !tracking-[0.1em]">{label}</dt>
      <dd className="text-[var(--text-primary)]">{children}</dd>
    </div>
  );
}

/** The official IMD bulletin as Gemini read it from the PDF, next to ShadowCast's own numbers. IMD is the authority. */
export function BulletinCard({ scenario, forecastIssued }: BulletinCardProps) {
  const { data, error, isLoading } = useBulletin(scenario.id);
  const heading = (
    <div className="flex items-center gap-2">
      <span className="label !text-[var(--accent)]">IMD {data?.kind ?? "bulletin"} · read by Gemini</span>
      {data && (
        <a
          href={data.source}
          target="_blank"
          rel="noreferrer"
          className="label ml-auto hover:!text-[var(--text-primary)]"
        >
          PDF ↗
        </a>
      )}
    </div>
  );

  if (error) return null; // no archived document for this storm, or IMD's site is down: the brief stands alone
  if (isLoading || !data) {
    return (
      <section className="rounded-2xl border border-[var(--line)] px-3.5 py-3" aria-busy>
        {heading}
        <p className="mt-2 animate-pulse text-xs text-[var(--text-secondary)]">
          Gemini is reading IMD&apos;s bulletin…
        </p>
      </section>
    );
  }

  const { reading } = data;
  const issuedMs = Date.parse(reading.issued);
  if (forecastIssued && !(issuedMs <= Date.parse(forecastIssued))) {
    return (
      <section className="rounded-2xl border border-[var(--line)] px-3.5 py-3">
        {heading}
        <p className="mt-2 text-xs text-[var(--text-secondary)]">
          {reading.title} is issued later ({Number.isNaN(issuedMs) ? reading.issued : istStamp(reading.issued)}), after
          this forecast.
        </p>
      </section>
    );
  }

  const { surge } = reading;
  return (
    <section className="rounded-2xl border border-[var(--accent)]/30 px-3.5 py-3">
      {heading}
      <div className="mt-1.5 text-sm font-medium text-[var(--text-primary)]">
        {reading.title} · {Number.isNaN(issuedMs) ? reading.issued : istStamp(reading.issued)}
      </div>
      <p className="mt-1 text-xs leading-relaxed text-[var(--text-secondary)]">{reading.summary}</p>
      <dl className="mt-2.5 flex flex-col gap-1.5">
        <Row label="Storm">{reading.system}</Row>
        {reading.landfall && (
          <Row label="Landfall">
            {reading.landfall.place} · {reading.landfall.time}
          </Row>
        )}
        {reading.windKmh && (
          <Row label="Wind">
            {reading.windKmh.low}–{reading.windKmh.high} km/h{reading.gustKmh ? `, gusts ${reading.gustKmh}` : ""}
          </Row>
        )}
        {surge && (
          <Row label="Surge">
            IMD {surge.low === surge.high ? surge.low : `${surge.low}–${surge.high}`} m
            {!forecastIssued &&
              (scenario.surge.observed?.modelled_m != null ? (
                <>
                  {" "}
                  · ShadowCast {scenario.surge.observed.modelled_m.toFixed(1)} m on the {scenario.surge.observed.place}
                </>
              ) : (
                <> · ShadowCast crest {scenario.surge.peak_m.toFixed(1)} m</>
              ))}
            {surge.areas.length > 0 && (
              <span className="text-[var(--text-secondary)]"> · {surge.areas.join(", ")}</span>
            )}
          </Row>
        )}
      </dl>
    </section>
  );
}
