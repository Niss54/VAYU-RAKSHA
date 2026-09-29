"use client";

import { ArrowLeft } from "lucide-react";
import { Area, AreaChart, ReferenceLine, ResponsiveContainer, Tooltip, XAxis, YAxis } from "recharts";

import { useAssetDetail } from "@/lib/api";
import { assetName, compactNumber, istStamp, kindLabel, knots, percent, utcAndIst } from "@/lib/format";
import type { Asset, ForecastAsset } from "@/lib/types";

interface AssetDetailProps {
  scenarioId: string;
  asset: Asset | ForecastAsset;
  onBack: () => void;
}

const AXIS_TICK = { fontSize: 11, fill: "var(--text-muted)", fontFamily: "var(--font-geist-mono)" };

function Stat({ label, value, hint }: { label: string; value: string; hint?: string }) {
  return (
    <div className="rounded-2xl border border-[var(--line)] bg-[var(--surface-2)] px-3.5 py-3">
      <div className="label">{label}</div>
      <div className="readout mt-1 text-lg text-[var(--text-primary)]">{value}</div>
      {hint && <div className="mt-0.5 text-xs text-[var(--text-secondary)]">{hint}</div>}
    </div>
  );
}

/** Wind at the asset through the storm's life (best-track replay), with gale and hurricane-force references. */
function WindChart({ scenarioId, assetId }: { scenarioId: string; assetId: string }) {
  const { data, isLoading } = useAssetDetail(scenarioId, assetId);
  if (isLoading || !data) return <div className="h-40 animate-pulse rounded-2xl bg-white/[0.04]" />;
  const points = data.timeline.map((p) => ({ t: Date.parse(p.time), wind: p.wind_kt }));
  const hours = (ms: number) => new Date(ms).toISOString().slice(8, 13).replace("T", " ") + "Z";
  return (
    <div className="h-44" aria-label="Modelled wind at this asset over time">
      <ResponsiveContainer>
        <AreaChart data={points} margin={{ top: 8, right: 4, bottom: 0, left: -18 }}>
          <defs>
            <linearGradient id="wind-fill" x1="0" y1="0" x2="0" y2="1">
              <stop offset="0%" stopColor="var(--accent)" stopOpacity={0.35} />
              <stop offset="100%" stopColor="var(--accent)" stopOpacity={0} />
            </linearGradient>
          </defs>
          <XAxis
            dataKey="t"
            type="number"
            domain={["dataMin", "dataMax"]}
            tickFormatter={hours}
            tick={AXIS_TICK}
            stroke="transparent"
            minTickGap={48}
          />
          <YAxis unit=" kt" tick={AXIS_TICK} stroke="transparent" width={58} />
          {[
            [34, "gale"],
            [64, "hurricane force"],
          ].map(([y, name]) => (
            <ReferenceLine
              key={y}
              y={y}
              stroke="var(--line-strong)"
              strokeDasharray="3 4"
              label={{ value: name, fill: "var(--text-muted)", fontSize: 11, position: "insideTopLeft" }}
            />
          ))}
          <Tooltip
            cursor={{ stroke: "var(--line-strong)" }}
            contentStyle={{
              background: "var(--surface-1)",
              border: "1px solid var(--line-strong)",
              borderRadius: 10,
              fontSize: 12,
            }}
            labelFormatter={(value) => utcAndIst(new Date(Number(value)).toISOString())}
            formatter={(value) => [knots(Number(value)), "wind"]}
          />
          <Area
            dataKey="wind"
            stroke="var(--accent)"
            strokeWidth={2}
            fill="url(#wind-fill)"
            dot={false}
            isAnimationActive={false}
          />
        </AreaChart>
      </ResponsiveContainer>
    </div>
  );
}

export function AssetDetail({ scenarioId, asset, onBack }: AssetDetailProps) {
  const forecast = "p34" in asset ? (asset as ForecastAsset) : null;
  return (
    <div className="flex min-h-0 flex-1 flex-col overflow-y-auto px-4 pb-5">
      <button
        type="button"
        onClick={onBack}
        className="label mb-4 flex items-center gap-1.5 self-start hover:!text-[var(--text-primary)]"
      >
        <ArrowLeft className="size-3.5" /> Priorities
      </button>

      <div className="label">
        Rank {String(asset.rank).padStart(2, "0")} · {kindLabel(asset.kind)}
      </div>
      <h2 className="mt-1 text-xl leading-tight font-semibold tracking-tight text-[var(--text-primary)]">
        {assetName(asset)}
      </h2>
      <div className="mt-0.5 text-xs text-[var(--text-muted)]">{asset.source}</div>

      {/* The headline number is the replay's question: gales in a forecast, grid outage in the best track. */}
      <div className="mt-4 flex items-end gap-3">
        <div className="readout text-5xl leading-none font-medium text-[var(--accent)]">
          {percent(forecast ? forecast.p34 : asset.p_outage)}
        </div>
        <div className="pb-1 text-sm leading-snug text-[var(--text-secondary)]">
          {forecast ? `of ${forecast.members} members bring gales` : "chance of losing grid power"}
          <br />
          <span className="text-[var(--text-muted)]">criticality {asset.criticality}/5</span>
        </div>
      </div>

      <div className="mt-4 grid grid-cols-2 gap-2">
        {forecast ? (
          <Stat
            label="Grid outage"
            value={percent(asset.p_outage)}
            hint={`hurricane-force winds ${percent(forecast.p64)}`}
          />
        ) : (
          <Stat
            label="Peak wind"
            value={knots(asset.peak_wind_kt)}
            hint={`${Math.round(asset.min_dist_km)} km from the centre`}
          />
        )}
        <Stat label="Gales arrive" value={istStamp(asset.gale_arrival)} />
        <Stat label="People · 2 km" value={compactNumber(asset.population)} />
        {asset.access_road != null && (
          <Stat
            label="Access road"
            value={asset.access_closes ? istStamp(asset.access_closes) : "Stays open"}
            hint={`${asset.access_road}, ${(asset.road_km ?? 0).toFixed(1)} km away${asset.access_closes ? ", closes then" : ""}`}
          />
        )}
        {asset.rain_mm != null && (
          <Stat
            label="Storm rain"
            value={`${Math.round(asset.rain_mm)} mm`}
            hint={
              asset.observed_rain_mm != null
                ? `NASA GPM measured ${Math.round(asset.observed_rain_mm)} mm`
                : forecast
                  ? `${percent(forecast.p_rain)} of members ≥ 204.5 mm`
                  : "R-CLIPER model"
            }
          />
        )}
        {asset.flood_m != null && (
          <Stat
            label="Surge water"
            value={`${asset.flood_m.toFixed(1)} m`}
            hint={`${(asset.surge_m ?? 0).toFixed(1)} m on the coast ${Math.round(asset.coast_km ?? 0)} km away`}
          />
        )}
        <Stat
          label="Elevation"
          value={asset.elevation_m != null ? `${asset.elevation_m.toFixed(1)} m` : "–"}
          hint="above sea level"
        />
      </div>

      {forecast ? (
        <p className="mt-4 text-sm text-[var(--text-secondary)]">
          Ensemble peak wind {knots(forecast.wind_p10)}–{knots(forecast.wind_p90)} (10–90%), median{" "}
          {knots(forecast.peak_wind_kt)}, across {forecast.members} members.
        </p>
      ) : (
        <div className="mt-5">
          <div className="label mb-2">Modelled wind at this asset</div>
          <WindChart scenarioId={scenarioId} assetId={asset.asset_id} />
        </div>
      )}

      {asset.observed_loss_pct != null && (
        <div className="mt-4 rounded-2xl border border-[var(--line)] px-3.5 py-3">
          <div className="label">Satellite check · VIIRS night lights</div>
          <p className="mt-1 text-sm text-[var(--text-secondary)]">
            {asset.observed_loss_pct >= 0 ? (
              <>
                Lights around this substation fell{" "}
                <span className="readout text-[var(--text-primary)]">{Math.round(asset.observed_loss_pct)}%</span> after
                landfall.
              </>
            ) : (
              <>No loss: {Math.round(-asset.observed_loss_pct)}% brighter after landfall.</>
            )}
          </p>
        </div>
      )}

      <div className="label mt-5">Why it ranks here</div>
      <ul className="mt-2 space-y-2">
        {asset.reasons.map((reason) => (
          <li key={reason} className="flex gap-2.5 text-sm leading-snug text-[var(--text-secondary)]">
            <span className="mt-[7px] size-1 shrink-0 rounded-full bg-[var(--accent)]" aria-hidden />
            {reason}
          </li>
        ))}
      </ul>
    </div>
  );
}
