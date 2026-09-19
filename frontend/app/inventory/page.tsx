"use client";

import { useCallback, useEffect, useMemo, useState } from "react";

import { ProductRow } from "@/components/inventory/ProductRow";
import { LinkButton, PageHeader, inputClass } from "@/components/ui/Primitives";
import { EmptyState, ErrorState, LoadingRows } from "@/components/ui/States";
import { api } from "@/lib/api";
import { useBusiness } from "@/lib/BusinessContext";
import type { ProductStatus, StockStatus } from "@/lib/types";

const FILTERS: { key: "all" | StockStatus; label: string }[] = [
  { key: "all", label: "All" },
  { key: "critical", label: "Critical" },
  { key: "low", label: "Low" },
  { key: "healthy", label: "Healthy" },
];

export default function InventoryPage() {
  const { business, loading: businessLoading, error: businessError, reload } = useBusiness();
  const [products, setProducts] = useState<ProductStatus[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [query, setQuery] = useState("");
  const [filter, setFilter] = useState<"all" | StockStatus>("all");

  const load = useCallback(() => {
    if (!business) return;
    setLoading(true);
    setError(null);
    api
      .inventory(business.id)
      .then(setProducts)
      .catch((e: Error) => setError(e.message))
      .finally(() => setLoading(false));
  }, [business]);

  useEffect(load, [load]);

  const visible = useMemo(() => {
    const q = query.trim().toLowerCase();
    return products.filter((p) => {
      const matchesQuery = !q || p.name.toLowerCase().includes(q) || p.category.toLowerCase().includes(q);
      const matchesFilter =
        filter === "all" ||
        p.status === filter ||
        (filter === "critical" && p.status === "out_of_stock");
      return matchesQuery && matchesFilter;
    });
  }, [products, query, filter]);

  const counts = useMemo(
    () => ({
      needsAttention: products.filter((p) => p.status !== "healthy").length,
      total: products.length,
    }),
    [products]
  );

  if (businessError) return <ErrorState message={businessError} onRetry={reload} />;

  return (
    <div className="space-y-6">
      <PageHeader
        title="Stock"
        subtitle={`${counts.total} products · ${counts.needsAttention} need attention`}
        action={<LinkButton href="/products/new">+ Add</LinkButton>}
      />

      <div className="space-y-3">
        <input
          type="search"
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          placeholder="Search products…"
          className={inputClass}
          aria-label="Search products"
        />

        <div className="flex gap-2 overflow-x-auto pb-1">
          {FILTERS.map((f) => (
            <button
              key={f.key}
              onClick={() => setFilter(f.key)}
              className={`focus-ring press shrink-0 rounded-full border px-4 py-2 text-[13px] font-semibold transition-all ${
                filter === f.key
                  ? "border-aria-500/40 bg-aria-500/10 text-aria-400"
                  : "border-ink-850 bg-ink-950 text-ink-400 hover:border-aria-500/25 hover:text-warm-50"
              }`}
            >
              {f.label}
            </button>
          ))}
        </div>
      </div>

      {businessLoading || (loading && !products.length) ? (
        <LoadingRows count={5} />
      ) : error ? (
        <ErrorState message={error} onRetry={load} />
      ) : products.length === 0 ? (
        <EmptyState
          title="No products yet"
          description="Tell A.R.I.A. what you stock, or add a product here, and we'll get started."
          action={<LinkButton href="/products/new">Add your first product</LinkButton>}
        />
      ) : visible.length === 0 ? (
        <EmptyState
          title="Nothing matches that"
          description="Try a different search term, or clear the filter to see everything on your shelves."
        />
      ) : (
        <div className="space-y-3">
          {visible.map((p) => (
            <ProductRow key={p.id} product={p} />
          ))}
        </div>
      )}
    </div>
  );
}
