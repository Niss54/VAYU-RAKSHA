"use client";

import {
  Bar,
  BarChart,
  CartesianGrid,
  ResponsiveContainer,
  Scatter,
  ScatterChart,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";

import { EvidenceCard } from "@/components/evidence-card";
import { Tile } from "@/components/tile";
import { useBacktest } from "@/lib/api";
import { istStamp, percent } from "@/lib/format";
import type { ScenarioDetail } from "@/lib/types";

const TOOLTIP_STYLE = {
  background: "var(--surface-1)",
  border: "1px solid var(--line-strong)",
  borderRadius: 10,
  fontSize: 12,
};
const AXIS_TICK = { fontSize: 11, fill: "var(--text-muted)", fontFamily: "var(--font-geist-mono)" };

/** "Prove": how well modelled wind predicted observed night-light loss after landfall. */
export function BacktestPanel({ scenario }: { scenario: ScenarioDetail }) {
  const { data } = useBacktest(scenario.id);
  const { skill, surge, rain } = scenario;
  const observed = surge.observed;
  const holdout = skill.spatial_holdout;
  const blockAucs = (holdout?.blocks ?? []).flatMap((b) => (b.auc == null ? [] : [b.auc]));
  const lit = (data?.substations ?? []).filter((s) => s.lit && s.loss_pct != null && s.peak_wind_kt != null);
  const bands = scenario.loss_by_band.map((b) => ({
    band: `${b.low_kt}–${b.high_kt}`,
    median: Math.max(0, b.median),
    raw: b.median,
    n: b.n,
  }));

  return (
    <div className="flex min-h-0 flex-1 flex-col gap-4 overflow-y-auto px-4 pb-4">
      <span className="label self-start rounded-full border border-[var(--line-strong)] px-2.5 py-1 !text-[var(--text-primary)]">
        {skill.out_of_sample ? "Held-out storm" : "Reference storm"}
      </span>
      <p className="-mt-1 text-sm text-[var(--text-secondary)]">
        {skill.out_of_sample
          ? `Held-out storm: the outage model was fitted on ${scenario.model.trained_on} and is scored here without refitting.`
          : "Reference storm: the outage model is fitted here, then tested on other storms."}{" "}
        Truth is VIIRS night-light loss around {skill.n} lit substations.
      </p>
      <div className="grid grid-cols-2 gap-2">
        <Tile label="ROC AUC" value={skill.auc == null ? "–" : skill.auc.toFixed(2)} hint="separates dark from lit" />
        <Tile label="Brier score" value={skill.brier == null ? "–" : skill.brier.toFixed(3)} hint="lower is better" />
        <Tile
          label="Spearman"
          value={skill.spearman == null ? "–" : skill.spearman.toFixed(2)}
          hint="wind vs light loss"
        />
        <Tile label="Went dark" value={percent(skill.observed_outage_rate)} hint="≥ 50% light loss" />
      </div>

      {holdout && (
        <p className="rounded-2xl border border-[var(--line)] px-3.5 py-3 text-xs leading-relaxed text-[var(--text-secondary)]">
          <span className="font-medium text-[var(--text-primary)]">Spatial holdout.</span> Refitted {holdout.folds}{" "}
          times, each time hiding one stretch of coast from south to north: out-of-fold AUC{" "}
          <span className="font-mono text-[var(--text-primary)]">{holdout.auc?.toFixed(2) ?? "–"}</span>, Brier{" "}
          <span className="font-mono text-[var(--text-primary)]">{holdout.brier?.toFixed(3) ?? "–"}</span>.
          {blockAucs.length > 0 &&
            ` Within the held-out stretches that had outages, AUC ${Math.min(...blockAucs).toFixed(2)}–${Math.max(...blockAucs).toFixed(2)}.`}
        </p>
      )}

      <section aria-label="Median night-light loss by modelled wind band">
        <h3 className="label mb-2">Median light loss by modelled wind</h3>
        <div className="h-44">
          <ResponsiveContainer>
            <BarChart data={bands} margin={{ top: 8, right: 8, bottom: 0, left: -18 }}>
              <CartesianGrid stroke="var(--line)" vertical={false} />
              <XAxis dataKey="band" unit=" kt" tick={AXIS_TICK} stroke="transparent" />
              <YAxis unit="%" domain={[0, 100]} tick={AXIS_TICK} stroke="transparent" width={52} />
              <Tooltip
                cursor={{ fill: "rgb(255 255 255 / 0.04)" }}
                contentStyle={TOOLTIP_STYLE}
                formatter={(_value, _name, item) => [
                  `${Math.round(item.payload.raw)}% (n=${item.payload.n})`,
                  "median loss",
                ]}
              />
              <Bar
                dataKey="median"
                fill="var(--accent)"
                radius={[4, 4, 0, 0]}
                maxBarSize={36}
                isAnimationActive={false}
              />
            </BarChart>
          </ResponsiveContainer>
        </div>
      </section>

      <section aria-label="Predicted outage probability against observed light loss per substation">
        <h3 className="label mb-2">Predicted vs observed, per substation</h3>
        <div className="h-52">
          <ResponsiveContainer>
            <ScatterChart margin={{ top: 8, right: 8, bottom: 0, left: -18 }}>
              <CartesianGrid stroke="var(--line)" />
              <XAxis
                dataKey="p"
                type="number"
                domain={[0, 1]}
                tickFormatter={(v: number) => percent(v)}
                tick={AXIS_TICK}
                stroke="transparent"
                name="predicted"
              />
              <YAxis
                dataKey="loss"
                type="number"
                domain={[-50, 100]}
                unit="%"
                tick={AXIS_TICK}
                stroke="transparent"
                width={52}
                name="observed"
              />
              <Tooltip
                contentStyle={TOOLTIP_STYLE}
                formatter={(value, name) =>
                  name === "predicted"
                    ? [percent(Number(value)), "predicted outage"]
                    : [`${Math.round(Number(value))}%`, "observed light loss"]
                }
              />
              <Scatter
                data={lit.map((s) => ({ p: s.p_outage, loss: Math.max(-50, s.loss_pct ?? 0), name: s.name }))}
                fill="var(--accent)"
                fillOpacity={0.75}
                isAnimationActive={false}
              />
            </ScatterChart>
          </ResponsiveContainer>
        </div>
      </section>

      <EvidenceCard scenarioId={scenario.id} />

      <section aria-labelledby="prove-rain">
        <h3 id="prove-rain" className="label mb-2">
          Storm rain vs NASA GPM
        </h3>
        <div className="grid grid-cols-2 gap-2">
          <Tile
            label="Rank correlation"
            value={rain.spearman == null ? "–" : rain.spearman.toFixed(2)}
            hint={`modelled vs measured, ${rain.n} sites`}
          />
          <Tile label="Model ÷ satellite" value={`${rain.median_ratio.toFixed(2)}×`} hint="median storm total" />
        </div>
        <p className="mt-2 text-xs leading-relaxed text-[var(--text-secondary)]">
          {rain.model}, scored against {rain.truth}. Wettest site: {Math.round(rain.max_modelled_mm)} mm modelled,{" "}
          {Math.round(rain.max_observed_mm)} mm measured.
        </p>
      </section>

      <section aria-labelledby="prove-surge">
        <h3 id="prove-surge" className="label mb-2">
          Storm surge vs IMD
        </h3>
        {observed && (
          <div className="grid grid-cols-2 gap-2">
            <Tile
              label="Modelled"
              value={observed.modelled_m == null ? "–" : `${observed.modelled_m.toFixed(1)} m`}
              hint={observed.place}
            />
            <Tile
              label="IMD reported"
              value={
                observed.low_m === observed.high_m ? `${observed.low_m} m` : `${observed.low_m}–${observed.high_m} m`
              }
              hint={observed.kind}
            />
          </div>
        )}
        <p className="mt-2 text-xs leading-relaxed text-[var(--text-secondary)]">
          Modelled crest {surge.peak_m.toFixed(1)} m at {surge.lat.toFixed(2)}°N {surge.lon.toFixed(2)}°E,{" "}
          {istStamp(surge.time)}; {surge.flooded_sites} sites get at least 0.3 m of water. Method: {surge.method}.
          {observed && (
            <>
              {" "}
              <a
                href={observed.source}
                target="_blank"
                rel="noreferrer"
                className="underline hover:text-[var(--text-primary)]"
              >
                IMD report
              </a>
              .
            </>
          )}
        </p>
      </section>
    </div>
  );
}
