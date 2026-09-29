"use client";

import { REGION_STATE } from "@/lib/advisory";
import { useLive } from "@/lib/api";
import { istStamp } from "@/lib/format";

const SHOWN = 3;

/** "2026/09/27/0615Z" (the archive's run folder) → an ISO instant. */
function runInstant(run: string): string {
  const [year, month, day, hhmm] = run.split("/");
  return `${year}-${month}-${day}T${hhmm.slice(0, 2)}:${hhmm.slice(2, 4)}:00Z`;
}

/**
 * The real world right now, beside the replay: cyclones GDACS is tracking and the official CAP warnings in force from
 * NDMA SACHET, from the feed archiver's newest run (every 6 hours).
 */
export function LiveCard({ regionId }: { regionId: string }) {
  const { data } = useLive();
  if (!data?.run_at) return null;
  const state = REGION_STATE[regionId];
  const runAt = runInstant(data.run_at);
  const inForce = data.warnings.filter((w) => !(Date.parse(w.expires) < Date.parse(runAt))); // as of the archive run
  const local = inForce.filter((w) => state && w.areas.some((area) => area.includes(state)));

  return (
    <section className="rounded-2xl border border-[var(--line)] px-3.5 py-3" aria-labelledby="brief-live">
      <div className="flex items-center gap-2">
        <span className="relative flex size-2" aria-hidden>
          <span className="absolute inline-flex size-full animate-ping rounded-full bg-[var(--accent)] opacity-60" />
          <span className="relative inline-flex size-2 rounded-full bg-[var(--accent)]" />
        </span>
        <h3 id="brief-live" className="label !text-[var(--accent)]">
          Live now · real feeds
        </h3>
        <span className="label ml-auto whitespace-nowrap">{istStamp(runAt)}</span>
      </div>
      <ul className="mt-2 flex flex-col gap-1 text-xs">
        {data.cyclones.length === 0 ? (
          <li className="text-[var(--text-secondary)]">GDACS: no tropical cyclone tracked in the region.</li>
        ) : (
          data.cyclones.map((cyclone) => (
            <li key={cyclone.url} className="text-[var(--text-secondary)]">
              <a href={cyclone.url} target="_blank" rel="noreferrer" className="text-[var(--text-primary)] underline">
                {cyclone.name}
              </a>{" "}
              · GDACS {cyclone.alert} · {cyclone.severity}
              {cyclone.current ? "" : " · ended"}
            </li>
          ))
        )}
        <li className="text-[var(--text-secondary)]">
          NDMA SACHET: {inForce.length} official warnings in force across India
          {state ? `, ${local.length} for ${state}` : ""}.
        </li>
      </ul>
      {local.length > 0 && (
        <ol className="mt-2 flex flex-col gap-1.5">
          {local.slice(0, SHOWN).map((warning) => (
            <li key={warning.identifier} className="text-xs">
              <span className="label !tracking-[0.1em]">
                {warning.event} · {warning.severity} · {warning.sender}
              </span>
              <p className="line-clamp-2 text-[var(--text-primary)]">{warning.headline}</p>
            </li>
          ))}
        </ol>
      )}
    </section>
  );
}
