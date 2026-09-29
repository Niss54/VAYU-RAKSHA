"use client";

import { clsx } from "clsx";
import { useMemo, useState } from "react";

import { assetName, assetValue, type ColorBy, kindLabel, percent, rampColor, rgbCss } from "@/lib/format";
import type { Asset, ForecastAsset } from "@/lib/types";

interface AssetListProps {
  assets: (Asset | ForecastAsset)[];
  colorBy: ColorBy;
  selectedId: string | null;
  onSelect: (assetId: string) => void;
}

const PAGE = 50;

export function AssetList({ assets, colorBy, selectedId, onSelect }: AssetListProps) {
  const [kinds, setKinds] = useState<string[]>([]);
  const [visible, setVisible] = useState(PAGE);

  const counts = useMemo(() => {
    const byKind = new Map<string, number>();
    for (const asset of assets) byKind.set(asset.kind, (byKind.get(asset.kind) ?? 0) + 1);
    return [...byKind.entries()].sort((a, b) => b[1] - a[1]);
  }, [assets]);
  const filtered = useMemo(
    () => (kinds.length ? assets.filter((a) => kinds.includes(a.kind)) : assets),
    [assets, kinds],
  );

  const toggle = (kind: string) => {
    setVisible(PAGE);
    setKinds((current) => (current.includes(kind) ? current.filter((k) => k !== kind) : [...current, kind]));
  };

  return (
    <div className="flex min-h-0 flex-1 flex-col">
      <div className="flex flex-wrap gap-1 px-3 pb-3" aria-label="Filter by asset kind">
        {counts.map(([kind, count]) => (
          <button
            key={kind}
            type="button"
            aria-pressed={kinds.includes(kind)}
            onClick={() => toggle(kind)}
            className="segment border border-[var(--line)] !px-2.5 !tracking-[0.08em]"
          >
            {kindLabel(kind)} <span className="opacity-60">{count}</span>
          </button>
        ))}
      </div>
      <ol className="min-h-0 flex-1 overflow-y-auto border-t border-[var(--line)] px-2 py-1">
        {filtered.slice(0, visible).map((asset) => {
          const value = assetValue(asset, colorBy, null);
          const forecast = "p34" in asset;
          const shown =
            colorBy === "flood"
              ? `${(asset.flood_m ?? 0).toFixed(1)} m`
              : colorBy === "rain"
                ? `${Math.round(asset.rain_mm ?? 0)} mm`
                : percent(colorBy === "gales" && forecast ? (asset as ForecastAsset).p34 : asset.p_outage);
          return (
            <li key={asset.asset_id}>
              <button
                type="button"
                onClick={() => onSelect(asset.asset_id)}
                className={clsx(
                  "grid w-full grid-cols-[2.25rem_1fr_4.5rem] items-center gap-3 rounded-xl px-2.5 py-2.5 text-left transition-colors hover:bg-[var(--surface-3)]",
                  asset.asset_id === selectedId && "bg-[var(--surface-3)]",
                )}
              >
                <span className="readout text-xs text-[var(--text-muted)]">{String(asset.rank).padStart(2, "0")}</span>
                <span className="min-w-0">
                  <span className="block truncate text-sm text-[var(--text-primary)]">{assetName(asset)}</span>
                  <span className="label mt-0.5 block !tracking-[0.1em]">
                    {kindLabel(asset.kind)}
                    {forecast ? ` · gales ${percent((asset as ForecastAsset).p34)}` : ""}
                  </span>
                </span>
                <span className="text-right">
                  <span className="readout block text-sm text-[var(--text-primary)]">{shown}</span>
                  <span className="mt-1.5 block h-[3px] rounded-full bg-[var(--surface-3)]" aria-hidden>
                    <span
                      className="block h-full rounded-full"
                      style={{ width: `${Math.max(4, value * 100)}%`, background: rgbCss(rampColor(value, colorBy)) }}
                    />
                  </span>
                </span>
              </button>
            </li>
          );
        })}
        {visible < filtered.length && (
          <li className="p-3 text-center">
            <button type="button" onClick={() => setVisible((v) => v + PAGE)} className="btn-ghost px-4 py-1.5 text-xs">
              Show {Math.min(PAGE, filtered.length - visible)} more of {filtered.length - visible}
            </button>
          </li>
        )}
      </ol>
    </div>
  );
}
