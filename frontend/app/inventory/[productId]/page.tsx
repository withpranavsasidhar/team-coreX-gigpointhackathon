"use client";

import Link from "next/link";
import { useParams } from "next/navigation";
import { useCallback, useEffect, useMemo, useState } from "react";

import { Button, Card, Field, SectionLabel, inputClass } from "@/components/ui/Primitives";
import { ErrorState, LoadingRows, Toast } from "@/components/ui/States";
import { api } from "@/lib/api";
import { useBusiness } from "@/lib/BusinessContext";
import {
  EVENT_META,
  TONE_TEXT,
  clockTime,
  dayLabel,
  formatQty,
  formatRupees,
  formatSigned,
  STATUS_META,
  stockoutPhrase,
} from "@/lib/format";
import type { EventType, InventoryEvent, ProductHistory } from "@/lib/types";

const MOVEMENT_OPTIONS: { value: EventType; label: string }[] = [
  { value: "STOCK_IN", label: "Stock In" },
  { value: "PURCHASE", label: "Purchase" },
  { value: "SALE", label: "Sale" },
  { value: "STOCK_OUT", label: "Stock Out" },
  { value: "CREDIT_SALE", label: "Credit Sale" },
  { value: "DAMAGE", label: "Damage" },
  { value: "RETURN", label: "Return" },
  { value: "LOSS", label: "Loss" },
];

function groupByDay(events: InventoryEvent[]) {
  const groups: { label: string; events: InventoryEvent[] }[] = [];
  for (const event of events) {
    const label = dayLabel(event.occurred_at);
    const last = groups[groups.length - 1];
    if (last && last.label === label) last.events.push(event);
    else groups.push({ label, events: [event] });
  }
  return groups;
}

export default function ProductDetailPage() {
  const { productId } = useParams<{ productId: string }>();
  const { business } = useBusiness();

  const [data, setData] = useState<ProductHistory | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [toast, setToast] = useState<{ message: string; tone: "success" | "error" } | null>(null);

  const [formOpen, setFormOpen] = useState(false);
  const [eventType, setEventType] = useState<EventType>("STOCK_IN");
  const [quantity, setQuantity] = useState("");
  const [unit, setUnit] = useState("");
  const [customer, setCustomer] = useState("");
  const [submitting, setSubmitting] = useState(false);
  const [formError, setFormError] = useState<string | null>(null);

  const load = useCallback(() => {
    if (!business) return;
    setLoading(true);
    setError(null);
    api
      .productHistory(business.id, productId)
      .then((d) => {
        setData(d);
        setUnit((u) => u || d.product.base_unit);
      })
      .catch((e: Error) => setError(e.message))
      .finally(() => setLoading(false));
  }, [business, productId]);

  useEffect(load, [load]);

  useEffect(() => {
    if (!toast) return;
    const t = setTimeout(() => setToast(null), 2600);
    return () => clearTimeout(t);
  }, [toast]);

  const grouped = useMemo(() => groupByDay(data?.events ?? []), [data]);

  const unitOptions = useMemo(() => {
    if (!data) return [];
    return [data.product.base_unit, ...data.product.conversions.map((c) => c.unit_name)];
  }, [data]);

  async function submitMovement() {
    if (!business || !data) return;
    const qty = Number(quantity);
    if (!qty || qty <= 0) {
      setFormError("Enter a quantity greater than zero.");
      return;
    }
    if (eventType === "CREDIT_SALE" && !customer.trim()) {
      setFormError("A credit sale needs a customer name.");
      return;
    }

    setSubmitting(true);
    setFormError(null);
    try {
      await api.createEvent(business.id, {
        product_id: productId,
        event_type: eventType,
        quantity: qty,
        unit,
        customer_name: customer.trim() || undefined,
        source: "manual",
      });
      setQuantity("");
      setCustomer("");
      setFormOpen(false);
      setToast({ message: "Movement recorded", tone: "success" });
      load();
    } catch (e) {
      setFormError((e as Error).message);
    } finally {
      setSubmitting(false);
    }
  }

  if (loading && !data) return <LoadingRows count={4} />;
  if (error) return <ErrorState message={error} onRetry={load} />;
  if (!data) return null;

  const { product } = data;
  const meta = STATUS_META[product.status];

  return (
    <div className="space-y-7">
      <Link href="/inventory" className="inline-flex items-center gap-1.5 text-sm text-ink-400 hover:text-warm-50">
        ‹ Inventory
      </Link>

      <header className="text-center">
        <SectionLabel>Current stock</SectionLabel>
        <p className="mt-2 text-5xl font-semibold tabular-nums tracking-tight text-warm-50">
          {formatQty(product.current_quantity)}
        </p>
        <p className="mt-1 text-base text-ink-400">
          {product.base_unit} of {product.name}
        </p>
        <div className="mt-4 flex items-center justify-center gap-2">
          <span className={`inline-flex items-center gap-1.5 rounded-full border px-3 py-1 text-xs font-semibold uppercase tracking-wide ${meta.chip}`}>
            <span className={`h-1.5 w-1.5 rounded-full ${meta.dot}`} />
            {meta.label}
          </span>
          <span className="text-xs text-ink-400">{stockoutPhrase(product.estimated_days_to_stockout)}</span>
        </div>
      </header>

      <div className="grid grid-cols-3 gap-3">
        {[
          { label: "Used daily", value: `${formatQty(product.avg_daily_usage)} ${product.base_unit}` },
          { label: "Minimum", value: `${formatQty(product.minimum_quantity)} ${product.base_unit}` },
          { label: "Unit price", value: formatRupees(product.price) },
        ].map((stat) => (
          <Card key={stat.label} className="px-3 py-4 text-center">
            <p className="text-[10px] font-semibold uppercase tracking-wide text-ink-400">{stat.label}</p>
            <p className="mt-1.5 text-sm font-semibold text-warm-50">{stat.value}</p>
          </Card>
        ))}
      </div>

      <section className="space-y-3">
        <div className="flex items-baseline justify-between">
          <h2 className="text-lg font-semibold text-warm-50">Why did it change?</h2>
          <span className="text-xs text-ink-400">Last {data.window_days} days</span>
        </div>

        <Card className="p-5">
          <div className="flex items-center justify-between text-sm">
            <span className="text-ink-400">Started at</span>
            <span className="font-medium tabular-nums text-warm-50">
              {formatQty(data.opening_balance)} {product.base_unit}
            </span>
          </div>

          <div className="my-4 space-y-2.5 border-y border-ink-850 py-4">
            {data.breakdown.length === 0 ? (
              <p className="text-sm text-ink-400">No movements recorded in this window.</p>
            ) : (
              data.breakdown
                .slice()
                .sort((a, b) => a.net_change - b.net_change)
                .map((row) => {
                  const rowMeta = EVENT_META[row.event_type];
                  return (
                    <div key={row.event_type} className="flex items-center justify-between gap-3 text-sm">
                      <span className="flex items-center gap-2.5 text-ink-600">
                        <span className={TONE_TEXT[rowMeta.tone]}>{rowMeta.icon}</span>
                        {rowMeta.label}
                        <span className="text-xs text-ink-500">×{row.count}</span>
                      </span>
                      <span
                        className={`font-semibold tabular-nums ${
                          row.net_change > 0 ? "text-aria-400" : "text-warm-50"
                        }`}
                      >
                        {formatSigned(row.net_change)}
                      </span>
                    </div>
                  );
                })
            )}
          </div>

          <div className="flex items-center justify-between text-sm">
            <span className="font-medium text-warm-50">Now</span>
            <span className="font-semibold tabular-nums text-warm-50">
              {formatQty(product.current_quantity)} {product.base_unit}
            </span>
          </div>
        </Card>
      </section>

      <section className="space-y-3">
        <div className="flex items-center justify-between">
          <h2 className="text-lg font-semibold text-warm-50">Record a movement</h2>
          {!formOpen && (
            <Button variant="secondary" onClick={() => setFormOpen(true)}>
              + Record
            </Button>
          )}
        </div>

        {formOpen && (
          <Card className="animate-slide-up space-y-4 p-5">
            <Field label="What happened?">
              <select
                value={eventType}
                onChange={(e) => setEventType(e.target.value as EventType)}
                className={inputClass}
              >
                {MOVEMENT_OPTIONS.map((o) => (
                  <option key={o.value} value={o.value}>
                    {o.label}
                  </option>
                ))}
              </select>
            </Field>

            <div className="grid grid-cols-2 gap-3">
              <Field label="Quantity">
                <input
                  type="number"
                  inputMode="decimal"
                  min="0"
                  step="0.1"
                  value={quantity}
                  onChange={(e) => setQuantity(e.target.value)}
                  placeholder="0"
                  className={inputClass}
                />
              </Field>
              <Field label="Unit">
                <select value={unit} onChange={(e) => setUnit(e.target.value)} className={inputClass}>
                  {unitOptions.map((u) => (
                    <option key={u} value={u}>
                      {u}
                    </option>
                  ))}
                </select>
              </Field>
            </div>

            {eventType === "CREDIT_SALE" && (
              <Field label="Customer" hint="Credit sales are tracked against a person.">
                <input
                  value={customer}
                  onChange={(e) => setCustomer(e.target.value)}
                  placeholder="e.g. Ramesh"
                  className={inputClass}
                />
              </Field>
            )}

            {formError && (
              <p className="rounded-xl bg-red-950 px-4 py-3 text-sm text-red-300">{formError}</p>
            )}

            <div className="flex gap-3">
              <Button onClick={submitMovement} disabled={submitting} fullWidth>
                {submitting ? "Recording…" : "Record movement"}
              </Button>
              <Button variant="secondary" onClick={() => setFormOpen(false)}>
                Cancel
              </Button>
            </div>
          </Card>
        )}
      </section>

      <section className="space-y-3">
        <h2 className="text-lg font-semibold text-warm-50">Movement history</h2>
        {grouped.length === 0 ? (
          <Card className="px-5 py-8 text-center text-sm text-ink-400">
            No movements recorded for this product yet.
          </Card>
        ) : (
          <div className="space-y-5">
            {grouped.map((group) => (
              <div key={group.label}>
                <p className="mb-2 text-[11px] font-semibold uppercase tracking-[0.08em] text-ink-400">
                  {group.label}
                </p>
                <Card className="divide-y divide-ink-850">
                  {group.events.map((e) => {
                    const eventMeta = EVENT_META[e.event_type];
                    return (
                      <div key={e.id} className="flex items-center justify-between gap-3 px-5 py-3.5">
                        <div className="flex min-w-0 items-center gap-3">
                          <span className={`w-4 text-center text-sm ${TONE_TEXT[eventMeta.tone]}`}>
                            {eventMeta.icon}
                          </span>
                          <div className="min-w-0">
                            <p className="text-sm text-warm-50">{eventMeta.label}</p>
                            <p className="text-xs text-ink-400">
                              {clockTime(e.occurred_at)}
                              {e.customer_name ? ` · ${e.customer_name}` : ""}
                              {e.unit !== product.base_unit ? ` · ${formatQty(e.quantity)} ${e.unit}` : ""}
                            </p>
                          </div>
                        </div>
                        <span
                          className={`shrink-0 text-sm font-semibold tabular-nums ${
                            e.delta > 0 ? "text-aria-400" : "text-warm-50"
                          }`}
                        >
                          {formatSigned(e.delta)}
                        </span>
                      </div>
                    );
                  })}
                </Card>
              </div>
            ))}
          </div>
        )}
      </section>

      {toast && <Toast message={toast.message} tone={toast.tone} />}
    </div>
  );
}
