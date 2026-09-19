"use client";

import Link from "next/link";
import { useParams } from "next/navigation";
import { useCallback, useEffect, useState } from "react";

import { Button, Card, SectionLabel, Stat, inputClass } from "@/components/ui/Primitives";
import { ErrorState, LoadingRows, Toast } from "@/components/ui/States";
import { api } from "@/lib/api";
import { useBusiness } from "@/lib/BusinessContext";
import {
  EVENT_META,
  TONE_TEXT_DARK,
  clockTime,
  dayLabel,
  formatQty,
  rupees,
} from "@/lib/format";
import type { CustomerDetail, EventType } from "@/lib/types";

/**
 * Customer 360 — the answer to "show me everything related to Ramesh".
 * What they took, what they owe, and the settle-up action, in one place.
 */
export default function CustomerPage() {
  const { customerId } = useParams<{ customerId: string }>();
  const { business } = useBusiness();
  const [data, setData] = useState<CustomerDetail | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [toast, setToast] = useState<string | null>(null);

  const load = useCallback(() => {
    if (!business || !customerId) return;
    setLoading(true);
    setError(null);
    api
      .customerDetail(business.id, customerId)
      .then(setData)
      .catch((e: Error) => setError(e.message))
      .finally(() => setLoading(false));
  }, [business, customerId]);

  useEffect(load, [load]);

  useEffect(() => {
    if (!toast) return;
    const id = setTimeout(() => setToast(null), 3000);
    return () => clearTimeout(id);
  }, [toast]);

  if (error) return <ErrorState message={error} onRetry={load} />;
  if (loading && !data) return <LoadingRows count={4} />;
  if (!data) return null;

  const { customer, totals, events, payments } = data;

  return (
    <div className="space-y-7">
      <div>
        <Link href="/customers" className="text-xs font-medium text-ink-400 hover:text-warm-50">
          ← People
        </Link>
        <div className="mt-3 flex items-center gap-3.5">
          <span className="grid h-12 w-12 place-items-center rounded-full border border-ink-850 bg-ink-900 text-lg font-medium text-ink-300">
            {customer.name.slice(0, 1).toUpperCase()}
          </span>
          <div>
            <h1 className="text-2xl font-semibold tracking-tight text-warm-50">{customer.name}</h1>
            <p className="text-sm text-ink-400">
              {data.transaction_count} transactions
              {customer.phone ? ` · ${customer.phone}` : ""}
            </p>
          </div>
        </div>
      </div>

      <div className="grid grid-cols-2 gap-3 lg:grid-cols-4">
        <Stat
          label="Outstanding"
          value={rupees(customer.outstanding_credit)}
          tone={customer.outstanding_credit > 0 ? "warn" : "good"}
        />
        <Stat label="Lifetime value" value={rupees(data.lifetime_value)} />
        <Stat label="Paid back" value={rupees(data.total_paid)} tone="good" />
        <Stat label="Products taken" value={totals.length} />
      </div>

      {customer.outstanding_credit > 0 && (
        <SettleUp
          businessId={business!.id}
          customerId={customer.id}
          outstanding={customer.outstanding_credit}
          onDone={(amount) => {
            setToast(`Recorded ${rupees(amount)} from ${customer.name}`);
            load();
          }}
        />
      )}

      {totals.length > 0 && (
        <section className="space-y-3">
          <SectionLabel>What they take</SectionLabel>
          <Card className="divide-y divide-ink-850">
            {totals.slice(0, 8).map((t) => (
              <div key={t.product_name} className="flex items-center justify-between px-5 py-3.5">
                <div>
                  <p className="text-sm text-warm-50">{t.product_name}</p>
                  <p className="text-xs text-ink-500">
                    {t.count} {t.count === 1 ? "time" : "times"}
                  </p>
                </div>
                <span className="text-sm font-semibold tabular-nums text-warm-50">
                  {formatQty(t.quantity)}
                  <span className="ml-1 text-xs font-normal text-ink-500">{t.base_unit}</span>
                </span>
              </div>
            ))}
          </Card>
        </section>
      )}

      {payments.length > 0 && (
        <section className="space-y-3">
          <SectionLabel>Payments received</SectionLabel>
          <Card className="divide-y divide-ink-850">
            {payments.map((p) => (
              <div key={p.id} className="flex items-center justify-between px-5 py-3">
                <div>
                  <p className="text-sm text-warm-50">{dayLabel(p.occurred_at)}</p>
                  {p.note && <p className="text-xs text-ink-500">{p.note}</p>}
                </div>
                <span className="text-sm font-semibold tabular-nums text-aria-400">
                  {rupees(p.amount)}
                </span>
              </div>
            ))}
          </Card>
        </section>
      )}

      <section className="space-y-3">
        <SectionLabel>History</SectionLabel>
        <Card className="divide-y divide-ink-850">
          {events.slice(0, 25).map((e) => {
            const meta = EVENT_META[e.event_type as EventType];
            return (
              <div key={e.id} className="flex items-center justify-between gap-3 px-5 py-3.5">
                <div className="flex min-w-0 items-center gap-3">
                  <span className={`w-4 text-center text-sm ${TONE_TEXT_DARK[meta.tone]}`}>
                    {meta.icon}
                  </span>
                  <div className="min-w-0">
                    <Link
                      href={`/inventory/${e.product_id}`}
                      className="truncate text-sm text-warm-50 hover:text-aria-400"
                    >
                      {e.product_name}
                    </Link>
                    <p className="text-xs text-ink-500">
                      {meta.label} · {dayLabel(e.occurred_at)} {clockTime(e.occurred_at)}
                    </p>
                  </div>
                </div>
                <div className="shrink-0 text-right">
                  <p className="text-sm font-semibold tabular-nums text-warm-50">
                    {formatQty(e.quantity)} {e.unit}
                  </p>
                  {e.price != null && <p className="text-xs text-ink-500">{rupees(e.price)}</p>}
                </div>
              </div>
            );
          })}
        </Card>
      </section>

      {toast && <Toast message={toast} />}
    </div>
  );
}

function SettleUp({
  businessId,
  customerId,
  outstanding,
  onDone,
}: {
  businessId: string;
  customerId: string;
  outstanding: number;
  onDone: (amount: number) => void;
}) {
  const [amount, setAmount] = useState("");
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const submit = async (value: number) => {
    if (!value || value <= 0) return;
    setSaving(true);
    setError(null);
    try {
      await api.recordPayment(businessId, customerId, value);
      setAmount("");
      onDone(value);
    } catch (e) {
      setError((e as Error).message);
    } finally {
      setSaving(false);
    }
  };

  return (
    <Card tone="raised" className="space-y-3 p-4">
      <div className="flex items-baseline justify-between">
        <p className="text-sm font-medium text-warm-50">Record a payment</p>
        <p className="text-xs text-ink-400">
          Owes <span className="font-semibold text-amber-300">{rupees(outstanding)}</span>
        </p>
      </div>
      <div className="flex gap-2">
        <input
          type="number"
          inputMode="decimal"
          value={amount}
          onChange={(e) => setAmount(e.target.value)}
          onKeyDown={(e) => e.key === "Enter" && void submit(Number(amount))}
          placeholder="Amount"
          aria-label="Payment amount"
          className={inputClass}
        />
        <Button onClick={() => void submit(Number(amount))} disabled={!amount || saving}>
          {saving ? "…" : "Record"}
        </Button>
      </div>
      <div className="flex gap-1.5">
        <button
          onClick={() => void submit(outstanding)}
          disabled={saving}
          className="rounded-full border border-ink-850 bg-ink-950 px-3 py-1.5 text-xs text-ink-300 transition-colors hover:text-warm-50"
        >
          Settle in full ({rupees(outstanding)})
        </button>
      </div>
      {error && <p className="text-xs text-red-300">{error}</p>}
    </Card>
  );
}
