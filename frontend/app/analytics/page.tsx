"use client";

import Link from "next/link";
import { useCallback, useEffect, useState } from "react";

import { Card, EstimateTag, PageHeader, SectionLabel, Stat } from "@/components/ui/Primitives";
import { EmptyState, ErrorState, LoadingRows } from "@/components/ui/States";
import { api } from "@/lib/api";
import { useBusiness } from "@/lib/BusinessContext";
import { formatQty, rupees } from "@/lib/format";
import type { Customer, Insights, MoneySummary, Mover } from "@/lib/types";

/**
 * Analytics as intelligence cards, not a wall of charts.
 *
 * Each card answers one of: what happened, why, what is changing, what may
 * happen next, what to do. Anything forward-looking is marked as an estimate,
 * because a prediction presented as a fact is a lie with a number on it.
 */
export default function AnalyticsPage() {
  const { business } = useBusiness();
  const [data, setData] = useState<Insights | null>(null);
  const [money, setMoney] = useState<MoneySummary | null>(null);
  const [customers, setCustomers] = useState<Customer[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const load = useCallback(() => {
    if (!business) return;
    setLoading(true);
    setError(null);
    Promise.all([
      api.insights(business.id),
      api.money(business.id, 30).catch(() => null),
      api.customers(business.id).catch(() => []),
    ])
      .then(([insights, moneyRows, people]) => {
        setData(insights);
        setMoney(moneyRows);
        setCustomers(people);
      })
      .catch((e: Error) => setError(e.message))
      .finally(() => setLoading(false));
  }, [business]);

  useEffect(load, [load]);

  if (error) return <ErrorState message={error} onRetry={load} />;
  if (loading && !data) return <LoadingRows count={5} />;
  if (!data) return null;

  const outstanding = customers.reduce((s, c) => s + c.outstanding_credit, 0);
  const atRisk = data.alerts.filter((a) => a.severity === "critical").length;

  return (
    <div className="space-y-8">
      <PageHeader title="Analytics" subtitle="What happened, why, and what it means for tomorrow." />

      {/* Headline state */}
      <div className="grid grid-cols-2 gap-3 lg:grid-cols-4">
        <Stat
          label="Stockout risk"
          value={atRisk}
          tone={atRisk ? "bad" : "good"}
          hint={atRisk ? "Products running out soon" : "Nothing critical"}
        />
        <Stat
          label="To reorder"
          value={data.reorder_recommendations.length}
          tone={data.reorder_recommendations.length ? "warn" : "good"}
          hint="Below lead-time cover"
        />
        <Stat
          label="Credit out"
          value={rupees(outstanding)}
          tone={outstanding ? "warn" : "good"}
          hint={`${customers.filter((c) => c.outstanding_credit > 0).length} customers`}
        />
        <Stat
          label="Expenses (30d)"
          value={money ? rupees(money.expenses_total) : "₹0"}
          hint={money?.expenses_by_category[0]?.category ?? "None recorded"}
        />
      </div>

      {/* Needs attention */}
      <section className="space-y-3">
        <SectionLabel>Needs attention</SectionLabel>
        {data.alerts.length === 0 ? (
          <Card className="px-5 py-6">
            <p className="text-sm text-ink-400">Every product is comfortably stocked.</p>
          </Card>
        ) : (
          <div className="space-y-2.5">
            {data.alerts.map((a) => (
              <Link
                key={a.product_id}
                href={`/inventory/${a.product_id}`}
                className={`focus-ring relative block overflow-hidden rounded-2xl border p-4 pl-5 shadow-soft transition-all duration-200 hover:shadow-lift ${
                  a.severity === "critical"
                    ? "border-red-500/25 bg-red-950"
                    : "border-ink-850 bg-ink-950 hover:border-aria-500/30"
                }`}
              >
                <span
                  className={`absolute inset-y-0 left-0 w-[3px] ${
                    a.severity === "critical" ? "bg-red-500" : "bg-aria-500"
                  }`}
                />
                <div className="flex items-start justify-between gap-3">
                  <div className="min-w-0">
                    <p className="text-[15px] font-semibold tracking-tight text-warm-50">
                      {a.product_name}
                    </p>
                    <p className="mt-1 text-xs leading-relaxed text-ink-400">{a.message}</p>
                  </div>
                  <span className="shrink-0 font-display text-[17px] font-semibold tabular-nums text-warm-50">
                    {formatQty(a.current_quantity)}
                    <span className="ml-1 text-xs font-normal text-ink-500">{a.base_unit}</span>
                  </span>
                </div>
              </Link>
            ))}
          </div>
        )}
      </section>

      {/* Unusual movement */}
      {data.unusual_movement.length > 0 && (
        <section className="space-y-3">
          <SectionLabel action={<EstimateTag>Compared to prior period</EstimateTag>}>
            What is changing
          </SectionLabel>
          <div className="space-y-2.5">
            {data.unusual_movement.map((u) => (
              <Card key={u.product_id} className="flex items-start gap-3 p-4">
                <span
                  className={`text-lg ${u.direction === "spike" ? "text-aria-500" : "text-ink-500"}`}
                >
                  {u.direction === "spike" ? "▲" : "▼"}
                </span>
                <div className="min-w-0">
                  <p className="text-sm leading-relaxed text-ink-300">{u.message}</p>
                  <Link
                    href={`/inventory/${u.product_id}`}
                    className="mt-1.5 inline-block text-xs font-semibold text-aria-400 transition-colors hover:text-aria-400"
                  >
                    Investigate →
                  </Link>
                </div>
              </Card>
            ))}
          </div>
        </section>
      )}

      {/* Reorder */}
      <section className="space-y-3">
        <SectionLabel
          action={
            data.reorder_recommendations.length > 0 ? (
              <EstimateTag>Suggested — based on 14-day usage</EstimateTag>
            ) : undefined
          }
        >
          What to order
        </SectionLabel>
        {data.reorder_recommendations.length === 0 ? (
          <EmptyState
            title="Nothing to reorder"
            description="Every product covers its lead time at the current rate of sale. A.R.I.A. will say so the moment that changes."
          />
        ) : (
          <Card className="divide-y divide-ink-850">
            {data.reorder_recommendations.map((r) => (
              <div key={r.product_id} className="px-5 py-4">
                <div className="flex items-baseline justify-between gap-3">
                  <Link
                    href={`/inventory/${r.product_id}`}
                    className="text-sm font-semibold text-warm-50 transition-colors hover:text-aria-400"
                  >
                    {r.product_name}
                  </Link>
                  <span className="font-display text-[17px] font-semibold tabular-nums text-aria-400">
                    +{formatQty(r.suggested_quantity)}
                    <span className="ml-1 text-xs font-normal text-ink-500">{r.base_unit}</span>
                  </span>
                </div>
                <p className="mt-1.5 text-xs leading-relaxed text-ink-500">{r.reason}</p>
              </div>
            ))}
          </Card>
        )}
      </section>

      {/* Velocity */}
      <div className="grid gap-6 lg:grid-cols-2">
        {data.fast_moving.length > 0 && (
          <section className="space-y-3">
            <SectionLabel>Fast moving</SectionLabel>
            <VelocityBars rows={data.fast_moving} tone="fast" />
          </section>
        )}
        {data.slow_moving.length > 0 && (
          <section className="space-y-3">
            <SectionLabel>Slow moving</SectionLabel>
            <VelocityBars rows={data.slow_moving} tone="slow" />
          </section>
        )}
      </div>

      {/* Credit */}
      {customers.some((c) => c.outstanding_credit > 0) && (
        <section className="space-y-3">
          <SectionLabel
            action={
              <Link href="/customers" className="text-xs font-semibold text-aria-400 transition-colors hover:text-aria-400">
                All people
              </Link>
            }
          >
            Who owes you
          </SectionLabel>
          <Card className="divide-y divide-ink-850">
            {customers
              .filter((c) => c.outstanding_credit > 0)
              .sort((a, b) => b.outstanding_credit - a.outstanding_credit)
              .slice(0, 6)
              .map((c) => (
                <Link
                  key={c.id}
                  href={`/customers/${c.id}`}
                  className="flex items-center justify-between px-5 py-3.5 transition-colors hover:bg-ink-900"
                >
                  <span className="text-sm text-warm-50">{c.name}</span>
                  <span className="font-display text-[15px] font-semibold tabular-nums text-amber-300">
                    {rupees(c.outstanding_credit)}
                  </span>
                </Link>
              ))}
          </Card>
        </section>
      )}
    </div>
  );
}

function VelocityBars({ rows, tone }: { rows: Mover[]; tone: "fast" | "slow" }) {
  const peak = Math.max(...rows.map((r) => r.avg_daily_usage), 0.1);
  return (
    <Card className="divide-y divide-ink-850">
      {rows.map((row) => (
        <Link
          key={row.product_id}
          href={`/inventory/${row.product_id}`}
          className="focus-ring block px-5 py-3.5 transition-colors hover:bg-ink-900"
        >
          <div className="flex items-center justify-between text-sm">
            <span className="font-medium text-warm-50">{row.product_name}</span>
            <span className="tabular-nums text-ink-400">
              {formatQty(row.avg_daily_usage)} {row.base_unit}/day
            </span>
          </div>
          <div className="mt-2 h-1.5 overflow-hidden rounded-full bg-ink-900">
            <div
              className={`h-full rounded-full transition-all duration-500 ${tone === "fast" ? "bg-aria-500" : "bg-ink-600"}`}
              style={{ width: `${Math.max((row.avg_daily_usage / peak) * 100, 3)}%` }}
            />
          </div>
        </Link>
      ))}
    </Card>
  );
}
