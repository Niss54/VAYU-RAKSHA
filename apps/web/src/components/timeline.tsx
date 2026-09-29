"use client";

import { Pause, Play } from "lucide-react";
import { useEffect } from "react";

import { istStamp, leadLabel, utcAndIst } from "@/lib/format";

interface TimelineProps {
  start: number;
  end: number;
  value: number;
  landfall: string;
  playing: boolean;
  onChange: (ms: number) => void;
  onPlayingChange: (playing: boolean) => void;
}

const STEP_MS = 15 * 60 * 1000; // matches the hazard model's densified track
const TICK_MS = 120; // playback advances one 15-minute step per tick
const DAY_MS = 24 * 60 * 60 * 1000;

export function Timeline({ start, end, value, landfall, playing, onChange, onPlayingChange }: TimelineProps) {
  useEffect(() => {
    if (!playing) return;
    const timer = setInterval(() => {
      const next = value + STEP_MS;
      if (next > end) onPlayingChange(false);
      else onChange(next);
    }, TICK_MS);
    return () => clearInterval(timer);
  }, [playing, value, end, onChange, onPlayingChange]);

  const iso = new Date(value).toISOString();
  const pct = (ms: number) => ((ms - start) / (end - start)) * 100;
  const landfallPct = pct(Date.parse(landfall));
  const days = Array.from(
    { length: Math.floor((end - start) / DAY_MS) + 1 },
    (_, i) => Math.ceil(start / DAY_MS) * DAY_MS + i * DAY_MS,
  ).filter((ms) => ms <= end && Math.abs(pct(ms) - pct(Date.parse(landfall))) > 6); // keep clear of the landfall label
  const utc = utcAndIst(iso).split(" · ")[0];

  return (
    <div className="glass flex items-center gap-4 rounded-3xl py-3 pr-5 pl-3">
      <button
        type="button"
        onClick={() => onPlayingChange(!playing)}
        className="btn-primary grid size-11 shrink-0 place-items-center"
        aria-label={playing ? "Pause replay" : "Play replay"}
      >
        {playing ? <Pause className="size-4" /> : <Play className="ml-0.5 size-4" />}
      </button>
      <div className="min-w-0 flex-1">
        <div className="relative hidden h-5 sm:block">
          {days.map((ms) => (
            <span
              key={ms}
              className="label absolute top-0 -translate-x-1/2 whitespace-nowrap"
              style={{ left: `${pct(ms)}%` }}
            >
              {new Date(ms).toUTCString().slice(5, 11)}
            </span>
          ))}
          {landfallPct >= 0 && landfallPct <= 100 && (
            <span
              className="label absolute top-0 -translate-x-1/2 !text-[var(--accent)]"
              style={{ left: `${landfallPct}%` }}
            >
              landfall
            </span>
          )}
        </div>
        <div className="relative">
          {landfallPct >= 0 && landfallPct <= 100 && (
            <span
              className="pointer-events-none absolute top-1/2 h-3 w-px -translate-y-1/2 bg-[var(--accent)]"
              style={{ left: `${landfallPct}%` }}
              aria-hidden
            />
          )}
          <input
            type="range"
            min={start}
            max={end}
            step={STEP_MS}
            value={value}
            onChange={(event) => onChange(Number(event.target.value))}
            className="scrub w-full cursor-pointer"
            aria-label="Replay time"
          />
        </div>
      </div>
      <div className="hidden w-52 shrink-0 text-right sm:block">
        <div className="readout text-xl font-medium text-[var(--text-primary)]">{istStamp(iso)}</div>
        <div className="label mt-0.5">
          {utc} · {leadLabel(iso, landfall)}
        </div>
      </div>
    </div>
  );
}
