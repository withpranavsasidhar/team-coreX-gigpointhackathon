"use client";

import Link from "next/link";
import { EVENT_META, STATUS_META, TONE_TEXT, formatQty, formatSigned, clockTime, rupees } from "@/lib/format";
import type { EventType, QueryAnswer, StockStatus } from "@/lib/types";

/**
 * Renders the verified rows behind an answer, so a reply never looks like raw
 * data. Works on both the light pages and the dark command surfaces, because
 * the same answer is shown in both places.
 */

type Tone = "light" | "dark";

const SURFACE: Record<Tone, string> = {
  light: "rounded-2xl border border-ink-850 bg-ink-950 shadow-soft",
  dark: "rounded-xl border border-ink-850 bg-ink-950 shadow-soft",
};
const DIVIDE: Record<Tone, string> = {
  light: "divide-y divide-ink-850",
  dark: "divide-y divide-ink-850",
};
const TEXT_STRONG: Record<Tone, string> = { light: "text-warm-50", dark: "text-warm-50" };
const TEXT_SOFT: Record<Tone, string> = { light: "text-ink-500", dark: "text-ink-500" };
const TEXT_MID: Record<Tone, string> = { light: "text-ink-300", dark: "text-ink-300" };
const TRACK: Record<Tone, string> = { light: "bg-ink-900", dark: "bg-ink-900" };

export function AnswerVisual({ result, tone = "light" }: { result: QueryAnswer; tone?: Tone }) {
  if (!result.items?.length || result.visual === "none") return null;

  if (result.visual === "stock") {
    const item = result.items[0];
    const status = STATUS_META[(item.status as StockStatus) ?? "healthy"];
    return (
      <Link href={`/inventory/${item.id}`} className="focus-ring block">
        <div className={`${SURFACE[tone]} p-5 transition-shadow hover:shadow-lift`}>
          <div className="flex items-end justify-between gap-4">
            <div>
              <p className={`text-sm ${TEXT_SOFT[tone]}`}>{item.name}</p>
              <p
                className={`mt-1 font-display text-[40px] font-semibold leading-none tabular-nums ${TEXT_STRONG[tone]}`}
              >
                {formatQty(item.current_quantity)}
                <span className={`ml-2 text-base font-normal ${TEXT_SOFT[tone]}`}>{item.base_unit}</span>
              </p>
            </div>
            <span className={`rounded-full border px-2.5 py-1 text-[10.5px] font-bold uppercase tracking-wide ${status.chip}`}>
              {status.label}
            </span>
          </div>
          <div
            className={`mt-4 grid grid-cols-2 gap-3 border-t border-ink-850 pt-3 text-xs ${TEXT_SOFT[tone]}`}
          >
            <span>
              Uses {formatQty(item.avg_daily_usage)} {item.base_unit}/day
            </span>
            <span className="text-right">Minimum {formatQty(item.minimum_quantity)}</span>
          </div>
        </div>
      </Link>
    );
  }

  if (result.visual === "breakdown") {
    const rows = result.items as { event_type: EventType; net_change: number; count: number }[];
    const peak = Math.max(...rows.map((r) => Math.abs(r.net_change)), 1);
    return (
      <div className={`${SURFACE[tone]} space-y-3 p-5`}>
        {rows
          .slice()
          .sort((a, b) => a.net_change - b.net_change)
          .map((row) => {
            const meta = EVENT_META[row.event_type];
            const positive = row.net_change > 0;
            return (
              <div key={row.event_type}>
                <div className="flex items-center justify-between text-sm">
                  <span className={`flex items-center gap-2 ${TEXT_MID[tone]}`}>
                    <span className={TONE_TEXT[meta.tone]}>{meta.icon}</span>
                    {meta.label}
                    <span className="text-xs text-ink-500">×{row.count}</span>
                  </span>
                  <span
                    className={`font-semibold tabular-nums ${
                      positive ? "text-emerald-500" : TEXT_STRONG[tone]
                    }`}
                  >
                    {formatSigned(row.net_change)}
                  </span>
                </div>
                <div className={`mt-1.5 h-1 overflow-hidden rounded-full ${TRACK[tone]}`}>
                  <div
                    className={`h-full rounded-full transition-all duration-500 ${positive ? "bg-emerald-500" : "bg-aria-500"}`}
                    style={{ width: `${(Math.abs(row.net_change) / peak) * 100}%` }}
                  />
                </div>
              </div>
            );
          })}
      </div>
    );
  }

  if (result.visual === "timeline") {
    return (
      <div className={`${SURFACE[tone]} ${DIVIDE[tone]}`}>
        {result.items.slice(0, 8).map((item, i) => {
          const meta = EVENT_META[item.event_type as EventType];
          return (
            <div key={i} className="flex items-center justify-between gap-3 px-5 py-3">
              <div className="flex min-w-0 items-center gap-3">
                <span className={`w-4 text-center text-sm ${TONE_TEXT[meta.tone]}`}>{meta.icon}</span>
                <div className="min-w-0">
                  <p className={`truncate text-sm ${TEXT_STRONG[tone]}`}>{item.product_name}</p>
                  <p className={`text-xs ${TEXT_SOFT[tone]}`}>
                    {meta.label} · {clockTime(item.occurred_at)}
                    {item.customer_name ? ` · ${item.customer_name}` : ""}
                  </p>
                </div>
              </div>
              <span className={`shrink-0 text-sm font-semibold tabular-nums ${TEXT_STRONG[tone]}`}>
                {formatQty(item.quantity)} {item.unit}
              </span>
            </div>
          );
        })}
      </div>
    );
  }

  // Generic list: alerts, reorder suggestions, period totals, movers, credit book.
  return (
    <div className={`${SURFACE[tone]} ${DIVIDE[tone]}`}>
      {result.items.slice(0, 8).map((item, i) => {
        // The credit book lists people, not products.
        const isCredit = item.outstanding_credit != null;
        const title = isCredit ? item.customer_name : item.product_name;

        const headline = isCredit
          ? rupees(item.outstanding_credit)
          : item.suggested_quantity != null
            ? `${formatQty(item.suggested_quantity)} ${item.base_unit}`
            : item.quantity != null
              ? `${formatQty(item.quantity)} ${item.base_unit}`
              : item.current_quantity != null
                ? `${formatQty(item.current_quantity)} ${item.base_unit}`
                : "";

        const sub =
          item.message ??
          item.reason ??
          (isCredit && item.phone ? item.phone : null) ??
          (item.event_count ? `${item.event_count} transactions` : null);
        const severity = item.severity as "critical" | "warning" | undefined;

        return (
          <div
            key={item.product_id ?? item.customer_id ?? i}
            className="flex items-start justify-between gap-3 px-5 py-3.5"
          >
            <div className="flex min-w-0 items-start gap-3">
              {severity && (
                <span
                  className={`mt-1.5 h-2 w-2 shrink-0 rounded-full ${
                    severity === "critical" ? "bg-red-500" : "bg-amber-500"
                  }`}
                />
              )}
              <div className="min-w-0">
                <p className={`text-sm font-medium ${TEXT_STRONG[tone]}`}>{title}</p>
                {sub && <p className={`mt-0.5 text-xs leading-relaxed ${TEXT_SOFT[tone]}`}>{sub}</p>}
              </div>
            </div>
            {headline && (
              <span className={`shrink-0 text-sm font-semibold tabular-nums ${TEXT_STRONG[tone]}`}>
                {headline}
              </span>
            )}
          </div>
        );
      })}
    </div>
  );
}
