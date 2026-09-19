"use client";

import Link from "next/link";
import { useCallback, useEffect, useState } from "react";

import { Card, PageHeader, SectionLabel, Stat, inputClass } from "@/components/ui/Primitives";
import { EmptyState, ErrorState, LoadingRows } from "@/components/ui/States";
import { api } from "@/lib/api";
import { useBusiness } from "@/lib/BusinessContext";
import { rupees } from "@/lib/format";
import type { Customer, Supplier } from "@/lib/types";

/** People: who buys on credit, and who supplies the shop. */
export default function PeoplePage() {
  const { business } = useBusiness();
  const [customers, setCustomers] = useState<Customer[]>([]);
  const [suppliers, setSuppliers] = useState<Supplier[]>([]);
  const [tab, setTab] = useState<"customers" | "suppliers">("customers");
  const [q, setQ] = useState("");
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const load = useCallback(() => {
    if (!business) return;
    setLoading(true);
    setError(null);
    Promise.all([api.customers(business.id), api.suppliers(business.id).catch(() => [])])
      .then(([people, vendors]) => {
        setCustomers(people);
        setSuppliers(vendors);
      })
      .catch((e: Error) => setError(e.message))
      .finally(() => setLoading(false));
  }, [business]);

  useEffect(load, [load]);

  if (error) return <ErrorState message={error} onRetry={load} />;
  if (loading && !customers.length) return <LoadingRows count={4} />;

  const term = q.trim().toLowerCase();
  const shownCustomers = customers.filter((c) => !term || c.name.toLowerCase().includes(term));
  const shownSuppliers = suppliers.filter((s) => !term || s.name.toLowerCase().includes(term));

  const outstanding = customers.reduce((s, c) => s + c.outstanding_credit, 0);
  const owing = customers.filter((c) => c.outstanding_credit > 0);

  return (
    <div className="space-y-6">
      <PageHeader title="People" subtitle="Customers, credit and suppliers." />

      <div className="grid grid-cols-2 gap-3 lg:grid-cols-3">
        <Stat label="Customers" value={customers.length} />
        <Stat
          label="Outstanding"
          value={rupees(outstanding)}
          tone={outstanding ? "warn" : "good"}
          hint={owing.length ? `${owing.length} owe you` : "Credit book clear"}
        />
        <Stat label="Suppliers" value={suppliers.length} />
      </div>

      <div className="flex gap-1.5">
        {(["customers", "suppliers"] as const).map((t) => (
          <button
            key={t}
            onClick={() => setTab(t)}
            className={`rounded-full border px-4 py-1.5 text-xs font-medium capitalize transition-colors ${
              tab === t
                ? "border-aria-500/40 bg-aria-500/10 text-aria-400"
                : "border-ink-850 bg-ink-950 text-ink-400 hover:text-warm-50"
            }`}
          >
            {t}
          </button>
        ))}
      </div>

      <input
        value={q}
        onChange={(e) => setQ(e.target.value)}
        placeholder={`Search ${tab}…`}
        aria-label={`Search ${tab}`}
        className={inputClass}
      />

      {tab === "customers" ? (
        shownCustomers.length === 0 ? (
          <EmptyState
            title="No customers yet"
            description="Customers are created automatically when you record a credit sale by name — say “Ramesh took two boxes of oil, he'll pay Friday”."
          />
        ) : (
          <section className="space-y-3">
            <SectionLabel>{shownCustomers.length} people</SectionLabel>
            <Card className="divide-y divide-ink-850">
              {shownCustomers
                .slice()
                .sort((a, b) => b.outstanding_credit - a.outstanding_credit)
                .map((c) => (
                  <Link
                    key={c.id}
                    href={`/customers/${c.id}`}
                    className="flex items-center justify-between gap-3 px-5 py-4 transition-colors hover:bg-ink-900"
                  >
                    <div className="flex min-w-0 items-center gap-3">
                      <span className="grid h-9 w-9 shrink-0 place-items-center rounded-full border border-ink-850 bg-ink-900 text-sm font-medium text-ink-300">
                        {c.name.slice(0, 1).toUpperCase()}
                      </span>
                      <div className="min-w-0">
                        <p className="truncate text-sm font-medium text-warm-50">{c.name}</p>
                        <p className="text-xs text-ink-500">
                          {c.outstanding_credit > 0 ? "Has outstanding credit" : "Settled up"}
                        </p>
                      </div>
                    </div>
                    <span
                      className={`shrink-0 text-sm font-semibold tabular-nums ${
                        c.outstanding_credit > 0 ? "text-amber-300" : "text-ink-500"
                      }`}
                    >
                      {c.outstanding_credit > 0 ? rupees(c.outstanding_credit) : "—"}
                    </span>
                  </Link>
                ))}
            </Card>
          </section>
        )
      ) : (
        <SupplierList
          suppliers={shownSuppliers}
          businessId={business?.id}
          onChanged={load}
        />
      )}
    </div>
  );
}

function SupplierList({
  suppliers,
  businessId,
  onChanged,
}: {
  suppliers: Supplier[];
  businessId?: string;
  onChanged: () => void;
}) {
  const [name, setName] = useState("");
  const [supplies, setSupplies] = useState("");
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const add = async () => {
    if (!businessId || !name.trim()) return;
    setSaving(true);
    setError(null);
    try {
      await api.createSupplier(businessId, { name: name.trim(), supplies: supplies.trim() });
      setName("");
      setSupplies("");
      onChanged();
    } catch (e) {
      setError((e as Error).message);
    } finally {
      setSaving(false);
    }
  };

  return (
    <div className="space-y-4">
      <Card className="space-y-3 p-4">
        <p className="text-sm font-medium text-warm-50">Add a supplier</p>
        <div className="grid gap-2.5 sm:grid-cols-2">
          <input
            value={name}
            onChange={(e) => setName(e.target.value)}
            placeholder="Supplier name"
            aria-label="Supplier name"
            className={inputClass}
          />
          <input
            value={supplies}
            onChange={(e) => setSupplies(e.target.value)}
            onKeyDown={(e) => e.key === "Enter" && void add()}
            placeholder="What they supply"
            aria-label="What they supply"
            className={inputClass}
          />
        </div>
        {error && <p className="text-xs text-red-300">{error}</p>}
        <button
          onClick={() => void add()}
          disabled={!name.trim() || saving}
          className="rounded-lg bg-aria-600 px-4 py-2 text-sm font-medium text-white transition-colors hover:bg-aria-700 disabled:bg-ink-900 disabled:text-ink-500"
        >
          {saving ? "Adding…" : "Add supplier"}
        </button>
      </Card>

      {suppliers.length === 0 ? (
        <EmptyState
          title="No suppliers yet"
          description="Add the people you buy stock from, so lead times can inform what A.R.I.A. suggests ordering."
        />
      ) : (
        <Card className="divide-y divide-ink-850">
          {suppliers.map((s) => (
            <div key={s.id} className="flex items-center justify-between gap-3 px-5 py-4">
              <div className="min-w-0">
                <p className="truncate text-sm font-medium text-warm-50">{s.name}</p>
                <p className="truncate text-xs text-ink-500">
                  {s.supplies || "General supplies"} · {s.lead_time_days}-day lead time
                </p>
              </div>
              {s.phone && <span className="shrink-0 text-xs text-ink-400">{s.phone}</span>}
            </div>
          ))}
        </Card>
      )}
    </div>
  );
}
