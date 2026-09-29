"use client";

import { clsx } from "clsx";

import { GEO_PREFIX, useEvidence } from "@/lib/api";

const AGREEMENT_STYLE = {
  agrees: "border-[var(--accent)]/50 !text-[var(--accent)]",
  "partly agrees": "border-[var(--line-strong)] !text-[var(--text-primary)]",
  disagrees: "border-[var(--line-strong)]",
} as const;

/** The before/after satellite night lights, and what Gemini sees in them compared with ShadowCast's forecast. */
export function EvidenceCard({ scenarioId }: { scenarioId: string }) {
  const { data, error } = useEvidence(scenarioId);
  const image = (name: string) => `${GEO_PREFIX}/scenarios/${scenarioId}/evidence/${name}.png`;

  return (
    <section aria-labelledby="prove-evidence">
      <h3 id="prove-evidence" className="label mb-2">
        Satellite evidence · read by Gemini
      </h3>
      <div className="grid grid-cols-2 gap-2">
        {(["before", "after"] as const).map((when) => (
          <figure key={when} className="overflow-hidden rounded-xl border border-[var(--line)]">
            {/* Served same-origin through the geo rewrite; next/image adds nothing for a fixed-size PNG. */}
            {/* eslint-disable-next-line @next/next/no-img-element */}
            <img
              src={image(when === "before" ? "night-lights-pre" : "night-lights-post")}
              alt={`VIIRS night lights over the region ${when} the storm`}
              className="aspect-square w-full object-cover"
            />
            <figcaption className="label px-2 py-1">{when} · VIIRS</figcaption>
          </figure>
        ))}
      </div>
      {error ? (
        <p className="mt-2 text-xs text-[var(--text-secondary)]">Gemini&apos;s reading is unavailable right now.</p>
      ) : !data ? (
        <p className="mt-2 animate-pulse text-xs text-[var(--text-secondary)]">Gemini is comparing the images…</p>
      ) : (
        <div className="mt-2 flex flex-col gap-2 text-xs">
          <div className="flex items-center gap-2">
            <span className={clsx("label rounded-full border px-2 py-0.5", AGREEMENT_STYLE[data.reading.agreement])}>
              {data.reading.agreement} with ShadowCast
            </span>
          </div>
          <p className="leading-relaxed text-[var(--text-primary)]">{data.reading.summary}</p>
          {data.reading.darkened.length > 0 && (
            <ul className="flex flex-col gap-1">
              {data.reading.darkened.map((area) => (
                <li key={area.place} className="text-[var(--text-secondary)]">
                  <span className="text-[var(--text-primary)]">{area.place}</span> · {area.severity} blackout ·{" "}
                  {area.note}
                </li>
              ))}
            </ul>
          )}
          {data.reading.caveats.length > 0 && (
            <p className="text-[var(--text-muted)]">Caveats: {data.reading.caveats.join("; ")}</p>
          )}
        </div>
      )}
    </section>
  );
}
