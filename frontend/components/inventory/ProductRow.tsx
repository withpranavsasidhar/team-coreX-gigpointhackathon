"use client";

import Link from "next/link";
import { formatQty, relativeTime, STATUS_META, stockoutPhrase } from "@/lib/format";
import type { ProductStatus } from "@/lib/types";

export function ProductRow({ product }: { product: ProductStatus }) {
  const meta = STATUS_META[product.status];
  const coverRatio =
    product.minimum_quantity > 0
      ? Math.min(product.current_quantity / (product.minimum_quantity * 3), 1)
      : 1;

  return (
    <Link
      href={`/inventory/${product.id}`}
      className="focus-ring group block rounded-2xl border border-ink-850 bg-ink-950 p-5 shadow-soft transition-all duration-200 hover:border-aria-500/30 hover:shadow-lift"
    >
      <div className="flex items-start justify-between gap-4">
        <div className="min-w-0">
          <h3 className="truncate text-[15px] font-semibold tracking-tight text-warm-50">
            {product.name}
          </h3>
          {/* The number is the point of the row, so it carries the weight. */}
          <p className="mt-1.5 font-display text-[30px] font-semibold leading-none tabular-nums text-warm-50">
            {formatQty(product.current_quantity)}
            <span className="ml-1.5 text-sm font-normal text-ink-500">{product.base_unit}</span>
          </p>
        </div>

        <div className="flex shrink-0 flex-col items-end gap-2">
          <span
            className={`inline-flex items-center gap-1.5 rounded-full border px-2.5 py-1 text-[10.5px] font-bold uppercase tracking-wide ${meta.chip}`}
          >
            <span className={`h-1.5 w-1.5 rounded-full ${meta.dot}`} />
            {meta.label}
          </span>
          <span className="text-ink-600 transition-transform duration-200 group-hover:translate-x-0.5 group-hover:text-aria-500">
            ›
          </span>
        </div>
      </div>

      <div className="mt-4 h-1 overflow-hidden rounded-full bg-ink-900">
        <div
          className={`h-full rounded-full transition-all duration-500 ${meta.dot}`}
          style={{ width: `${Math.max(coverRatio * 100, 4)}%` }}
        />
      </div>

      <div className="mt-3 flex items-center justify-between text-[11.5px] text-ink-500">
        <span>{stockoutPhrase(product.estimated_days_to_stockout)}</span>
        <span>{relativeTime(product.last_movement_at)}</span>
      </div>
    </Link>
  );
}
