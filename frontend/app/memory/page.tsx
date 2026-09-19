"use client";

import Link from "next/link";
import { useCallback, useEffect, useState } from "react";

import { Card, PageHeader, inputClass } from "@/components/ui/Primitives";
import { EmptyState, ErrorState, LoadingRows } from "@/components/ui/States";
import { api } from "@/lib/api";
import { useBusiness } from "@/lib/BusinessContext";
import {
  EVENT_META,
  SOURCE_META,
  TONE_TEXT_DARK,
  clockTime,
  dayLabel,
  formatQty,
  formatSigned,
  rupees,
} from "@/lib/format";
import type { EventType, MemoryEvent } from "@/lib/types";

const EVENT_FILTERS: { value: string; label: string }[] = [
  { value: "", label: "Everything" },
  { value: "SALE", label: "Sales" },
  { value: "CREDIT_SALE", label: "Credit" },
  { value: "STOCK_IN", label: "Stock in" },
  { value: "PURCHASE", label: "Purchases" },
  { value: "DAMAGE", label: "Damage" },
  { value: "LOSS", label: "Loss" },
  { value: "ADJUSTMENT", label: "Corrections" },
];

const RANGES = [
  { value: 1, label: "Today" },
  { value: 7, label: "7 days" },
  { value: 30, label: "30 days" },
  { value: 0, label: "All time" },
];

/**
 * Business memory: the shop's timeline.
 *
 * Each entry keeps what was actually said, in which language, and how sure the
 * system was — so any number can be traced back to the sentence that produced
 * it.
 */
export default function MemoryPage() {
  const { business } = useBusiness();
  const [events, setEvents] = useState<MemoryEvent[]>([]);
  const [q, setQ] = useState("");
  const [eventType, setEventType] = useState("");
  const [days, setDays] = useState(7);
  const [expanded, setExpanded] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const load = useCallback(() => {
    if (!business) return;
    setLoading(true);
    setError(null);
    api
      .memory(business.id, {
        q: q || undefined,
        event_type: eventType || undefined,
        days: days || undefined,
        limit: 150,
      })
      .then((r) => setEvents(r.events))
      .catch((e: Error) => setError(e.message))
      .finally(() => setLoading(false));
  }, [business, q, eventType, days]);

  // Debounced so typing doesn't fire a request per keystroke.
  useEffect(() => {
    const id = setTimeout(load, q ? 280 : 0);
    return () => clearTimeout(id);
  }, [load, q]);

  const grouped = events.reduce<Record<string, MemoryEvent[]>>((acc, e) => {
    const key = dayLabel(e.occurred_at);
    (acc[key] ||= []).push(e);
    return acc;
  }, {});

  return (
    <div className="space-y-6">
      <PageHeader
        title="Memory"
        subtitle="Everything that has happened, and what was said to record it."
      />

      {/* Filters */}
      <div className="space-y-3">
        <input
          value={q}
          onChange={(e) => setQ(e.target.value)}
          placeholder="Search products, people, or what was said…"
          aria-label="Search memory"
          className={inputClass}
        />
        <div className="flex flex-wrap gap-1.5">
          {EVENT_FILTERS.map((f) => (
            <FilterChip
              key={f.value}
              active={eventType === f.value}
              onClick={() => setEventType(f.value)}
            >
              {f.label}
            </FilterChip>
          ))}
        </div>
        <div className="flex flex-wrap gap-1.5">
          {RANGES.map((r) => (
            <FilterChip key={r.value} active={days === r.value} onClick={() => setDays(r.value)}>
              {r.label}
            </FilterChip>
          ))}
        </div>
      </div>

      {error ? (
        <ErrorState message={error} onRetry={load} />
      ) : loading && !events.length ? (
        <LoadingRows count={4} />
      ) : events.length === 0 ? (
        <EmptyState
          title="Your business memory is still quiet here"
          description="Nothing matches these filters yet. Try a wider date range, or start talking to A.R.I.A. and your activity will appear."
        />
      ) : (
        <div className="space-y-6">
          {Object.entries(grouped).map(([day, rows]) => (
            <section key={day} className="space-y-2.5">
              <div className="flex items-center justify-between gap-3">
                <h2 className="flex items-center gap-2.5 text-[11px] font-bold uppercase tracking-[0.12em] text-warm-50">
                  <span className="h-1.5 w-1.5 rounded-full bg-aria-500" />
                  {day}
                </h2>
                <span className="text-[11px] text-ink-500">{rows.length} entries</span>
              </div>
              <Card className="divide-y divide-ink-850">
                {rows.map((e) => (
                  <MemoryRow
                    key={e.id}
                    event={e}
                    open={expanded === e.id}
                    onToggle={() => setExpanded(expanded === e.id ? null : e.id)}
                  />
                ))}
              </Card>
            </section>
          ))}
        </div>
      )}
    </div>
  );
}

function MemoryRow({
  event,
  open,
  onToggle,
}: {
  event: MemoryEvent;
  open: boolean;
  onToggle: () => void;
}) {
  const meta = EVENT_META[event.event_type as EventType];
  const source = SOURCE_META[event.source] ?? SOURCE_META.manual;
  const hasDetail = !!(event.original_text || event.normalized_text);

  return (
    <div>
      <button
        onClick={onToggle}
        disabled={!hasDetail}
        className={`flex w-full items-center justify-between gap-3 px-5 py-3.5 text-left transition-colors ${
          hasDetail ? "hover:bg-ink-900" : "cursor-default"
        }`}
      >
        <div className="flex min-w-0 items-center gap-3.5">
          <span className="relative grid h-7 w-7 shrink-0 place-items-center rounded-full border border-aria-500/25">
            <span className={`text-xs ${TONE_TEXT_DARK[meta.tone]}`}>{meta.icon}</span>
          </span>
          <div className="min-w-0">
            <p className="truncate text-[14px] font-medium text-warm-50">
              {meta.label} · {event.product_name}
            </p>
            <p className="mt-0.5 truncate text-[11.5px] text-ink-500">
              {clockTime(event.occurred_at)}
              {event.customer_name ? ` · ${event.customer_name}` : ""}
              {event.price != null ? ` · ${rupees(event.price)}` : ""}
            </p>
          </div>
        </div>
        <div className="flex shrink-0 items-center gap-2.5">
          {event.source === "demo" && (
            <span className={`rounded border px-1.5 py-0.5 text-[10px] font-medium ${source.chip}`}>
              {source.label}
            </span>
          )}
          <span
            className={`text-[14px] font-semibold tabular-nums ${
              event.delta > 0 ? "text-emerald-500" : "text-ink-300"
            }`}
          >
            {formatSigned(event.delta)}
          </span>
        </div>
      </button>

      {open && hasDetail && (
        <div className="animate-slide-up space-y-3 border-t border-ink-850 bg-ink-900 px-5 py-4">
          {event.original_text && (
            <Detail label="What was said">
              <span className="text-warm-50">&ldquo;{event.original_text}&rdquo;</span>
            </Detail>
          )}
          {event.normalized_text && (
            <Detail label="Understood as">{event.normalized_text}</Detail>
          )}
          <div className="grid grid-cols-2 gap-3 sm:grid-cols-4">
            <Detail label="Quantity">
              {formatQty(event.quantity)} {event.unit}
            </Detail>
            <Detail label="Applied">
              {formatSigned(event.delta)} {event.base_unit}
            </Detail>
            {event.detected_language && (
              <Detail label="Language">{event.detected_language}</Detail>
            )}
            <Detail label="Confidence">{Math.round(event.confidence * 100)}%</Detail>
          </div>
          <div className="flex items-center gap-2 pt-1">
            <span className={`rounded border px-1.5 py-0.5 text-[10px] font-medium ${source.chip}`}>
              {source.label}
            </span>
            <Link
              href={`/inventory/${event.product_id}`}
              className="text-xs font-semibold text-aria-400 transition-colors hover:text-aria-400"
            >
              View {event.product_name} →
            </Link>
          </div>
        </div>
      )}
    </div>
  );
}

function Detail({ label, children }: { label: string; children: React.ReactNode }) {
  return (
    <div>
      <p className="text-[10px] font-medium uppercase tracking-wider text-ink-600">{label}</p>
      <p className="mt-0.5 text-xs leading-relaxed text-ink-300">{children}</p>
    </div>
  );
}

function FilterChip({
  active,
  onClick,
  children,
}: {
  active: boolean;
  onClick: () => void;
  children: React.ReactNode;
}) {
  return (
    <button
      onClick={onClick}
      className={`press rounded-full border px-3.5 py-1.5 text-xs font-semibold transition-all ${
        active
          ? "border-aria-500/40 bg-aria-500/10 text-aria-400"
          : "border-ink-850 bg-ink-950 text-ink-400 hover:border-aria-500/25 hover:text-warm-50"
      }`}
    >
      {children}
    </button>
  );
}
