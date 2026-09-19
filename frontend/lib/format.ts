import type { EventType, StockStatus } from "./types";

// Canonical event presentation, per the mapping table in docs/04-ui-ux-design-system.md.
// The UI never renders a raw enum string.
export const EVENT_META: Record<EventType, { label: string; icon: string; tone: "up" | "down" | "loss" | "credit" | "neutral" }> = {
  STOCK_IN: { label: "Stock In", icon: "↑", tone: "up" },
  PURCHASE: { label: "Purchase", icon: "⊕", tone: "up" },
  RETURN: { label: "Return", icon: "↩", tone: "up" },
  SALE: { label: "Sale", icon: "→", tone: "down" },
  STOCK_OUT: { label: "Stock Out", icon: "↓", tone: "down" },
  CREDIT_SALE: { label: "Credit Sale", icon: "◷", tone: "credit" },
  DAMAGE: { label: "Damage", icon: "✕", tone: "loss" },
  LOSS: { label: "Loss", icon: "!", tone: "loss" },
  ADJUSTMENT: { label: "Adjustment", icon: "±", tone: "neutral" },
};

/**
 * Event tones. Direction stays semantic — arriving stock is not a brand
 * moment — while rose red is kept for A.R.I.A.'s own activity and for loss.
 */
export const TONE_TEXT: Record<string, string> = {
  up: "text-emerald-500",
  down: "text-ink-300",
  loss: "text-red-400",
  credit: "text-amber-400",
  neutral: "text-ink-500",
};

/**
 * Stock status.
 *
 * Deliberately not all red: a shelf where most products are merely low would
 * otherwise render as a wall of red and stop meaning anything. Amber is the
 * warning step and deep red is reserved for genuinely critical, so the two
 * are told apart at a glance. Rose red stays on the alert surfaces, where it
 * marks something A.R.I.A. wants the owner to act on.
 *
 * Chips are tinted rather than filled, so a list of them reads as status
 * without lighting up the whole panel.
 */
export const STATUS_META: Record<StockStatus, { label: string; dot: string; chip: string }> = {
  healthy: {
    label: "Healthy",
    dot: "bg-emerald-500",
    chip: "border-emerald-500/25 bg-emerald-500/10 text-emerald-600",
  },
  low: {
    label: "Low",
    dot: "bg-amber-500",
    chip: "border-amber-500/30 bg-amber-500/10 text-amber-300",
  },
  critical: {
    label: "Critical",
    dot: "bg-red-500",
    chip: "border-red-500/30 bg-red-500/10 text-red-300",
  },
  out_of_stock: {
    label: "Out of stock",
    dot: "bg-ink-500",
    chip: "border-ink-850 bg-ink-900 text-ink-400",
  },
};

export function formatQty(value: number): string {
  const rounded = Math.round(value * 10) / 10;
  return Number.isInteger(rounded) ? String(rounded) : rounded.toFixed(1);
}

export function formatSigned(value: number): string {
  return `${value > 0 ? "+" : value < 0 ? "−" : ""}${formatQty(Math.abs(value))}`;
}

export function formatRupees(value: number | null): string {
  if (value === null || value === undefined) return "—";
  return `₹${value.toLocaleString("en-IN", { maximumFractionDigits: 0 })}`;
}

/** Shorthand used throughout the command surfaces. */
export const rupees = formatRupees;

/**
 * Kept as a named export because the command surfaces import it, but the
 * tokens are now theme-aware, so the same meanings hold in both themes.
 */
export const TONE_TEXT_DARK: Record<string, string> = TONE_TEXT;

export const SOURCE_META: Record<string, { label: string; chip: string }> = {
  // Voice is A.R.I.A.'s own doing, so it carries the brand colour.
  voice: { label: "Voice", chip: "border-aria-500/30 bg-aria-500/10 text-aria-400" },
  text: { label: "Typed", chip: "border-ink-850 bg-ink-900 text-ink-400" },
  manual: { label: "Manual", chip: "border-ink-850 bg-ink-900 text-ink-400" },
  opening: { label: "Opening", chip: "border-ink-850 bg-ink-900 text-ink-400" },
  // Demo rows are always labelled as demo. Real trading is never dressed up as
  // demo data, and demo data is never passed off as real.
  demo: { label: "Demo", chip: "border-amber-500/30 bg-amber-500/10 text-amber-300" },
};

export function relativeTime(iso: string | null): string {
  if (!iso) return "No activity yet";
  const then = new Date(iso.endsWith("Z") ? iso : `${iso}Z`).getTime();
  const mins = Math.round((Date.now() - then) / 60000);
  if (mins < 1) return "just now";
  if (mins < 60) return `${mins} min ago`;
  const hours = Math.round(mins / 60);
  if (hours < 24) return `${hours} hr ago`;
  const days = Math.round(hours / 24);
  return days === 1 ? "yesterday" : `${days} days ago`;
}

export function clockTime(iso: string): string {
  return new Date(iso.endsWith("Z") ? iso : `${iso}Z`).toLocaleTimeString("en-IN", {
    hour: "2-digit",
    minute: "2-digit",
    hour12: false,
  });
}

export function dayLabel(iso: string): string {
  const d = new Date(iso.endsWith("Z") ? iso : `${iso}Z`);
  const today = new Date();
  const yesterday = new Date(today);
  yesterday.setDate(today.getDate() - 1);

  const same = (a: Date, b: Date) => a.toDateString() === b.toDateString();
  if (same(d, today)) return "Today";
  if (same(d, yesterday)) return "Yesterday";
  return d.toLocaleDateString("en-IN", { day: "numeric", month: "short" });
}

export function stockoutPhrase(days: number | null): string {
  if (days === null) return "No usage recorded yet";
  if (days < 1) return "Running out today";
  if (days < 2) return "About a day left";
  return `About ${Math.round(days)} days left`;
}
