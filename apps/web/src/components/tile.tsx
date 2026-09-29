import { clsx } from "clsx";

interface TileProps {
  label: string;
  value: string;
  hint: string;
  /** Makes the tile a button, e.g. to drill down into what it counts. */
  onClick?: () => void;
}

/** A stat tile inside a panel: tracked label, large readout, one line of context. */
export function Tile({ label, value, hint, onClick }: TileProps) {
  const Element = onClick ? "button" : "div";
  return (
    <Element
      {...(onClick && { type: "button" as const, onClick })}
      className={clsx(
        "min-w-0 rounded-2xl border border-[var(--line)] bg-[var(--surface-2)] px-3.5 py-3 text-left",
        onClick && "transition-colors hover:border-[var(--line-strong)]",
      )}
    >
      <div className="label">{label}</div>
      <div className="readout mt-1 text-2xl text-[var(--text-primary)]">{value}</div>
      <div className="mt-0.5 truncate text-xs text-[var(--text-secondary)]">{hint}</div>
    </Element>
  );
}
