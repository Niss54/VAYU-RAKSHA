"use client";

import { clsx } from "clsx";
import dynamic from "next/dynamic";
import Image from "next/image";
import { useCallback, useMemo, useState } from "react";

import { AssetDetail } from "@/components/asset-detail";
import { AssetList } from "@/components/asset-list";
import { BacktestPanel } from "@/components/backtest-panel";
import { BriefPanel } from "@/components/brief-panel";
import { LiveAlerts } from "@/components/live-alerts";
import { PreparePanel } from "@/components/prepare-panel";
import { ReplayStrip } from "@/components/replay-strip";
import { Timeline } from "@/components/timeline";
import { useAssets, useForecastTracks, useHazard, useRoads, useScenario, useSurge, useTrack } from "@/lib/api";
import { LANGUAGES, REGION_LANGUAGE } from "@/lib/advisory";
import { liveAlerts } from "@/lib/alerts";
import { dutyBrief } from "@/lib/brief";
import { type ColorBy, compactNumber, FLOOD_FULL_M, kindLabel, RAIN_FULL_MM, rampColor, rgbCss } from "@/lib/format";
import type { ReplayMode, ScenarioSummary } from "@/lib/types";

// deck.gl and the Maps JS API need the browser: never render the map on the server.
const MapView = dynamic(() => import("@/components/map-view").then((m) => m.MapView), {
  ssr: false,
  loading: () => <div className="absolute inset-0 animate-pulse bg-white/[0.03]" />,
});

const QUANTUM_MS = 15 * 60 * 1000;
const LEGENDS: Record<ColorBy, string> = {
  risk: "Grid-outage probability",
  gales: "Members bringing gales (34 kt)",
  wind: "Modelled wind now",
  flood: "Storm-surge water at the site",
  rain: "Storm-total rain (R-CLIPER)",
};
const COLOR_LABELS: Record<ColorBy, string> = {
  risk: "Outage",
  gales: "Gales",
  wind: "Wind",
  flood: "Surge",
  rain: "Rain",
};
const LEGEND_ENDS: Record<ColorBy, [string, string]> = {
  risk: ["0%", "100%"],
  gales: ["0%", "100%"],
  wind: ["0 kt", "120 kt"],
  flood: ["0 m", `${FLOOD_FULL_M} m`],
  rain: ["0 mm", `${RAIN_FULL_MM} mm`],
};
const TABS = ["brief", "prioritise", "prepare", "prove"] as const;

interface ConsoleProps {
  scenarios: ScenarioSummary[];
  mapsApiKey: string;
}

function Readout({ label, value, unit }: { label: string; value: string; unit?: string }) {
  return (
    <div className="glass min-w-28 rounded-2xl px-4 py-2.5">
      <div className="label">{label}</div>
      <div className="readout mt-0.5 text-2xl font-medium text-[var(--text-primary)]">
        {value}
        {unit && <span className="ml-1 text-sm text-[var(--text-muted)]">{unit}</span>}
      </div>
    </div>
  );
}

export function Console({ scenarios, mapsApiKey }: ConsoleProps) {
  const [scenarioId, setScenarioId] = useState(scenarios[0].id);
  const [mode, setMode] = useState<ReplayMode>({ kind: "best-track" });
  const [tab, setTab] = useState<(typeof TABS)[number]>("brief");
  const [selectedId, setSelectedId] = useState<string | null>(null);
  const [colorBy, setColorBy] = useState<ColorBy>("risk");
  const [scrub, setScrub] = useState<{ scenarioId: string; ms: number } | null>(null);
  const [playing, setPlaying] = useState(false);

  const { data: scenario, error: scenarioError } = useScenario(scenarioId);
  const { data: track } = useTrack(scenarioId);
  const { data: page, isLoading: assetsLoading } = useAssets(scenarioId, mode);
  const { data: members } = useForecastTracks(scenarioId, mode);
  const { data: surge } = useSurge(scenarioId, mode);
  const { data: roads } = useRoads(scenarioId, mode);

  const span = useMemo(() => {
    const times = (track?.features ?? [])
      .map((f) => f.properties.time)
      .filter((t): t is string => typeof t === "string")
      .map(Date.parse);
    return times.length ? { start: Math.min(...times), end: Math.max(...times) } : null;
  }, [track]);

  // Each scenario opens at landfall; once the user scrubs, their position wins until the scenario changes.
  const landfallMs = scenario && span ? Math.min(span.end, Math.max(span.start, Date.parse(scenario.landfall))) : null;
  const timeMs = scrub?.scenarioId === scenarioId ? scrub.ms : landfallMs;
  const setTimeMs = useCallback((ms: number) => setScrub({ scenarioId, ms }), [scenarioId]);

  const quantised = timeMs == null ? null : new Date(Math.round(timeMs / QUANTUM_MS) * QUANTUM_MS).toISOString();
  const { data: hazard } = useHazard(scenarioId, mode.kind === "best-track" ? quantised : null);
  const windById = useMemo(
    () => (hazard ? new Map(hazard.asset_ids.map((id, i) => [id, hazard.wind_kt[i]] as [string, number])) : null),
    [hazard],
  );

  const assets = useMemo(() => page?.items ?? [], [page]);
  const selected = assets.find((a) => a.asset_id === selectedId) ?? null;
  const atRisk = useMemo(() => assets.filter((a) => a.p_outage >= 0.5).length, [assets]);
  const alerts = useMemo(
    () =>
      scenario && timeMs != null
        ? liveAlerts({
            assets,
            timeMs,
            landfall: scenario.landfall,
            storm: scenario.storm,
            stormVmaxKt: hazard?.storm?.vmax_kt ?? null,
          })
        : [],
    [assets, timeMs, scenario, hazard],
  );
  const brief = useMemo(
    () =>
      scenario && timeMs != null
        ? dutyBrief({
            assets,
            timeMs,
            storm: scenario.storm,
            region: scenario.region.name,
            landfall: scenario.landfall,
            roads,
          })
        : null,
    [assets, timeMs, scenario, roads],
  );

  const changeScenario = (id: string) => {
    setScenarioId(id);
    setMode({ kind: "best-track" });
    setColorBy("risk");
    setSelectedId(null);
    setPlaying(false);
  };
  const changeMode = (next: ReplayMode) => {
    setMode(next);
    setColorBy(next.kind === "forecast" ? "gales" : "risk");
    setSelectedId(null);
  };
  // Selecting on the map opens the asset, except while talking to the analyst, where it sets "this asset".
  const select = useCallback((id: string | null) => {
    setSelectedId(id);
    if (id) setTab((current) => (current === "prepare" ? current : "prioritise"));
  }, []);
  const openAsset = useCallback((id: string) => {
    setSelectedId(id);
    setTab("prioritise");
  }, []);

  if (scenarioError) {
    return (
      <div className="grid h-dvh place-items-center text-[var(--text-secondary)]">
        Could not load the scenario: {String(scenarioError.message)}
      </div>
    );
  }

  const colorOptions: ColorBy[] =
    mode.kind === "forecast" ? ["gales", "risk", "rain"] : ["risk", "wind", "flood", "rain"];
  const forecastKey = mode.kind === "forecast" ? mode.key : null;
  const forecast = scenario?.forecasts.find((f) => f.key === forecastKey);
  const local = scenario && REGION_LANGUAGE[scenario.region.id];
  const suggestions = [
    selected
      ? `Why is ${selected.name ?? kindLabel(selected.kind)} ranked #${selected.rank}?`
      : "Which hospitals and cyclone shelters are most at risk?",
    forecastKey
      ? "How far do the ensemble members agree, and what could still change?"
      : "How well did the model predict where the lights went out?",
    `Draft an advisory for the five highest-priority assets in English, Hindi${local ? ` and ${LANGUAGES[local].name}` : ""}`,
  ];

  return (
    <div className="relative flex min-h-dvh flex-col bg-[var(--surface-0)] text-[var(--text-primary)] lg:block lg:h-dvh lg:overflow-hidden">
      <section
        className="relative h-[48dvh] shrink-0 lg:absolute lg:inset-0 lg:h-auto"
        aria-label="Map of assets and storm"
      >
        {scenario && (
          <MapView
            apiKey={mapsApiKey}
            region={scenario.region}
            assets={assets}
            colorBy={colorBy}
            windById={windById}
            track={track}
            members={members}
            storm={mode.kind === "best-track" ? (hazard?.storm ?? null) : null}
            surge={surge}
            roads={roads}
            timeMs={timeMs}
            selectedId={selectedId}
            onSelect={select}
          />
        )}
        {/* Dissolve the map's edges into the void so the floating panels read cleanly. */}
        <div
          className="pointer-events-none absolute inset-0 bg-[linear-gradient(to_bottom,rgb(14_16_18/0.9),transparent_24%,transparent_76%,rgb(14_16_18/0.92))]"
          aria-hidden
        />
      </section>

      {/* Mission header: brand, storm, replay, live readouts. */}
      <header className="relative flex flex-col items-start gap-3 p-4 lg:pointer-events-none lg:absolute lg:top-0 lg:right-[432px] lg:left-0">
        <div className="glass flex max-w-full items-center gap-3 rounded-full py-1.5 pr-2 pl-2.5 lg:pointer-events-auto">
          <Image src="/logo.svg" alt="" width={30} height={30} priority />
          <div className="shrink-0 leading-none">
            <div className="text-[15px] font-semibold tracking-tight">ShadowCast</div>
            <div className="label mt-1 hidden sm:block">impact forecast · proven by satellite</div>
          </div>
          <select
            value={scenarioId}
            onChange={(event) => changeScenario(event.target.value)}
            aria-label="Storm"
            className="min-w-0 flex-1 cursor-pointer truncate rounded-full border lg:max-w-80 border-[var(--line-strong)] bg-[var(--surface-2)] px-3 py-1.5 text-sm text-[var(--text-primary)] hover:bg-[var(--surface-3)]"
          >
            {scenarios.map((s) => (
              <option key={s.id} value={s.id}>
                {s.storm} {s.season} · {s.region.name}
              </option>
            ))}
          </select>
        </div>

        <div className="lg:pointer-events-auto">
          <ReplayStrip forecasts={scenario?.forecasts ?? []} mode={mode} onChange={changeMode} />
        </div>

        {scenario && (
          <div className="flex flex-wrap gap-2 lg:pointer-events-auto">
            {forecast ? (
              <>
                <Readout label="Members" value={String(forecast.members)} />
                <Readout label="Likely gales" value={compactNumber(forecast.assets_likely_gale)} unit="assets" />
              </>
            ) : (
              <>
                <Readout
                  label="Storm now"
                  value={hazard?.storm ? String(Math.round(hazard.storm.vmax_kt)) : "—"}
                  unit="kt"
                />
                <Readout label="Backtest AUC" value={scenario.skill.auc?.toFixed(2) ?? "—"} />
                <Readout label="Surge crest" value={scenario.surge.peak_m.toFixed(1)} unit="m" />
              </>
            )}
            <Readout label="≥50% outage" value={compactNumber(atRisk)} unit="assets" />
          </div>
        )}
      </header>

      {/* Live alerts float over the map's top-right, clear of the readouts and the panel. */}
      <div className="pointer-events-none absolute top-[84px] right-[432px] hidden lg:block">
        <div className="pointer-events-auto">
          <LiveAlerts alerts={alerts} onSelect={openAsset} />
        </div>
      </div>

      {/* Legend and encoding switch. */}
      <div className="glass relative mx-4 mb-3 rounded-2xl p-3 lg:absolute lg:bottom-[116px] lg:left-4 lg:m-0 lg:w-80">
        <div className="mb-2.5 flex gap-1" role="radiogroup" aria-label="Colour assets by">
          {colorOptions.map((option) => (
            <button
              key={option}
              type="button"
              role="radio"
              aria-checked={colorBy === option}
              onClick={() => setColorBy(option)}
              className="segment"
            >
              {COLOR_LABELS[option]}
            </button>
          ))}
        </div>
        <div className="text-xs text-[var(--text-secondary)]">{LEGENDS[colorBy]}</div>
        <div
          className="mt-2 h-1.5 rounded-full"
          style={{
            background: `linear-gradient(90deg, ${[0, 0.25, 0.5, 0.75, 1].map((t) => rgbCss(rampColor(t, colorBy))).join(", ")})`,
          }}
          aria-hidden
        />
        <div className="label mt-1.5 flex justify-between">
          <span>{LEGEND_ENDS[colorBy][0]}</span>
          <span>{LEGEND_ENDS[colorBy][1]}</span>
        </div>
        {roads && (
          <div className="mt-2 flex items-center gap-2 text-xs text-[var(--text-secondary)]">
            <span className="h-0.5 w-5 bg-[var(--accent)]" aria-hidden /> Arterial road closed
            <span className="ml-2 h-0.5 w-5 bg-[var(--text-muted)]" aria-hidden /> at risk
          </div>
        )}
        {surge && (
          <div className="mt-2 flex items-center gap-2 text-xs text-[var(--text-secondary)]">
            <span className="size-2 rounded-full" style={{ background: rgbCss(rampColor(0.8, "flood")) }} aria-hidden />{" "}
            Coast: modelled surge crest
          </div>
        )}
        {mode.kind === "forecast" && (
          <div className="mt-2 flex items-center gap-2 text-xs text-[var(--text-secondary)]">
            <span className="h-0.5 w-5 bg-[var(--member)]" aria-hidden /> ECMWF ensemble members
          </div>
        )}
      </div>

      {scenario && span && timeMs != null && (
        <div className="relative mx-4 mb-3 lg:absolute lg:right-[432px] lg:bottom-4 lg:left-4 lg:m-0">
          <Timeline
            start={span.start}
            end={span.end}
            value={timeMs}
            landfall={scenario.landfall}
            playing={playing}
            onChange={setTimeMs}
            onPlayingChange={setPlaying}
          />
        </div>
      )}

      <aside className="glass relative mx-4 mb-4 flex h-[75dvh] min-h-0 flex-col rounded-3xl lg:absolute lg:top-4 lg:right-4 lg:bottom-4 lg:m-0 lg:h-auto lg:w-[400px]">
        <div className="flex gap-1 p-2" role="tablist" aria-label="Panels">
          {TABS.map((name) => (
            <button
              key={name}
              type="button"
              role="tab"
              aria-selected={tab === name}
              onClick={() => setTab(name)}
              className="segment flex-1 !px-1 !py-2 !tracking-[0.08em]"
            >
              {name}
            </button>
          ))}
        </div>
        {/* Kept mounted while hidden so the conversation survives tab switches; a new replay starts a new one. */}
        <div className={clsx("min-h-0 flex-1 flex-col pt-2", tab === "prepare" ? "flex" : "hidden")}>
          <PreparePanel
            key={`${scenarioId}:${forecastKey ?? "best-track"}`}
            context={{ scenarioId, forecastKey, selectedAssetId: selectedId }}
            suggestions={suggestions}
            onSelectAsset={openAsset}
          />
        </div>
        <div className={clsx("min-h-0 flex-1 flex-col pt-2", tab === "prepare" ? "hidden" : "flex")}>
          {tab === "brief" && brief && scenario ? (
            <BriefPanel
              scenario={scenario}
              forecast={forecast}
              brief={brief}
              onOpenAsset={openAsset}
              onShowPriorities={() => setTab("prioritise")}
              onShowFlood={() => setColorBy("flood")}
              onDraftAdvisory={() => setTab("prepare")}
            />
          ) : tab === "prove" && scenario ? (
            <BacktestPanel scenario={scenario} />
          ) : selected ? (
            <AssetDetail scenarioId={scenarioId} asset={selected} onBack={() => setSelectedId(null)} />
          ) : assetsLoading && !page ? (
            <div className="space-y-2 px-4">
              {Array.from({ length: 8 }, (_, i) => (
                <div key={i} className="h-12 animate-pulse rounded-xl bg-white/[0.04]" />
              ))}
            </div>
          ) : (
            <>
              <p className="label px-4 pb-2">
                {compactNumber(page?.total ?? 0)} assets ·{" "}
                {mode.kind === "forecast"
                  ? "outage, then gale chance × criticality"
                  : "outage probability × criticality"}
              </p>
              <AssetList assets={assets} colorBy={colorBy} selectedId={selectedId} onSelect={select} />
            </>
          )}
        </div>
      </aside>
    </div>
  );
}
