"use client";

import { useEffect, useState } from "react";

import { Button, Card, SectionLabel, inputClass } from "@/components/ui/Primitives";
import { formatQty } from "@/lib/format";
import type { VisionAnalysis, VisionItem } from "@/lib/types";

/**
 * The review step.
 *
 * Nothing on this screen has touched inventory. Every line is editable, every
 * line can be dropped, and a line the reading was unsure of starts excluded
 * rather than quietly included.
 */

export interface ReviewLine extends VisionItem {
  key: string;
  include: boolean;
  editedQuantity: string;
  editedUnit: string;
  chosenProductId: string | null;
  chosenProductName: string | null;
}

export function toReviewLines(analysis: VisionAnalysis): ReviewLine[] {
  return analysis.items.map((item, index) => ({
    ...item,
    key: `${index}-${item.raw_name}`,
    // Only lines the system is genuinely confident in are pre-selected.
    include: item.ready,
    editedQuantity: item.quantity !== null ? String(item.quantity) : "",
    editedUnit: item.unit ?? item.base_unit ?? "",
    chosenProductId: item.product_id,
    chosenProductName: item.product_name,
  }));
}

const BAND_CHIP: Record<string, string> = {
  high: "border-aria-500/30 bg-aria-500/10 text-aria-400",
  medium: "border-amber-500/30 bg-amber-500/10 text-amber-300",
  low: "border-red-500/30 bg-red-500/10 text-red-300",
};

const BAND_LABEL: Record<string, string> = {
  high: "High confidence",
  medium: "Medium confidence",
  low: "Low confidence",
};

export function VisionReview({
  analysis,
  lines,
  onChange,
  onApply,
  onCancel,
  applying,
  units,
}: {
  analysis: VisionAnalysis;
  lines: ReviewLine[];
  onChange: (lines: ReviewLine[]) => void;
  onApply: () => void;
  onCancel: () => void;
  applying: boolean;
  units: string[];
}) {
  const update = (key: string, patch: Partial<ReviewLine>) =>
    onChange(lines.map((l) => (l.key === key ? { ...l, ...patch } : l)));

  const selected = lines.filter((l) => l.include);
  const applicable = selected.filter(
    (l) => l.chosenProductName && Number(l.editedQuantity) > 0
  );

  return (
    <div className="space-y-5">
      <div>
        <h2 className="text-lg font-semibold text-warm-50">{analysis.summary}</h2>
        {analysis.notes && <p className="mt-1 text-sm text-ink-400">{analysis.notes}</p>}
        {analysis.document_type && analysis.document_type !== "unknown" && (
          <p className="mt-2 flex flex-wrap gap-2 text-[11px]">
            <span className="rounded-full border border-ink-850 bg-ink-900 px-2 py-0.5 text-ink-300">
              {analysis.document_type.replace(/_/g, " ")}
            </span>
            {analysis.language && (
              <span className="rounded-full border border-aria-500/25 bg-aria-500/10 px-2 py-0.5 text-aria-400">
                {analysis.language}
              </span>
            )}
            {analysis.model && (
              <span className="rounded-full border border-ink-850 bg-ink-900 px-2 py-0.5 text-ink-500">
                read by {analysis.model}
              </span>
            )}
          </p>
        )}
      </div>

      {/* Image quality guidance, only when the reading actually flagged it. */}
      {analysis.quality_advice && analysis.quality_advice.length > 0 && (
        <Card tone="raised" className="p-4">
          <p className="text-sm text-amber-300">This photo was hard to read.</p>
          <ul className="mt-1.5 space-y-0.5 text-xs text-ink-300">
            {analysis.quality_advice.map((a) => (
              <li key={a}>· {a}</li>
            ))}
          </ul>
        </Card>
      )}

      {/* Invoice header, when a bill was read. */}
      {analysis.invoice && Object.values(analysis.invoice).some(Boolean) && (
        <Card className="p-4">
          <SectionLabel>Invoice details</SectionLabel>
          <div className="mt-2 grid grid-cols-2 gap-3 text-sm sm:grid-cols-4">
            {Object.entries(analysis.invoice)
              .filter(([, v]) => v)
              .map(([k, v]) => (
                <div key={k}>
                  <p className="text-[11px] uppercase tracking-wider text-ink-600">
                    {k.replace(/_/g, " ")}
                  </p>
                  <p className="mt-0.5 text-warm-50">{String(v)}</p>
                </div>
              ))}
          </div>
        </Card>
      )}

      <div className="space-y-2.5">
        {lines.map((line) => (
          <Card
            key={line.key}
            className={`p-4 transition-opacity ${line.include ? "" : "opacity-55"}`}
          >
            <div className="flex items-start gap-3">
              <input
                type="checkbox"
                checked={line.include}
                onChange={(e) => update(line.key, { include: e.target.checked })}
                aria-label={`Include ${line.raw_name}`}
                className="mt-1 h-4 w-4 shrink-0 accent-aria-500"
              />

              <div className="min-w-0 flex-1 space-y-3">
                <div className="flex flex-wrap items-baseline justify-between gap-2">
                  <div className="min-w-0">
                    <p className="text-sm font-medium text-warm-50">
                      {line.chosenProductName ?? (line.normalized_name || line.raw_name)}
                    </p>
                    <p className="mt-0.5 text-xs text-ink-500">
                      Read as &ldquo;{line.raw_name}&rdquo;
                      {line.current_quantity !== null && line.chosenProductName
                        ? ` · currently ${formatQty(line.current_quantity)} ${line.base_unit}`
                        : ""}
                    </p>
                  </div>
                  <span
                    className={`shrink-0 rounded-full border px-2 py-0.5 text-[10px] font-medium ${
                      BAND_CHIP[line.confidence_band]
                    }`}
                  >
                    {BAND_LABEL[line.confidence_band]} · {Math.round(line.confidence * 100)}%
                  </span>
                </div>

                {/* Anything the reading could not settle, said plainly. */}
                {line.issues.length > 0 && (
                  <ul className="space-y-0.5 text-xs text-amber-300">
                    {line.issues.map((issue) => (
                      <li key={issue}>· {issue}</li>
                    ))}
                  </ul>
                )}
                {line.item_note && (
                  <p className="text-xs text-ink-400">{line.item_note}</p>
                )}

                {/* Every field editable before anything is applied. */}
                <div className="grid gap-2 sm:grid-cols-3">
                  <label className="block">
                    <span className="mb-1 block text-[11px] uppercase tracking-wider text-ink-600">
                      Quantity
                    </span>
                    <input
                      type="number"
                      inputMode="decimal"
                      value={line.editedQuantity}
                      onChange={(e) => update(line.key, { editedQuantity: e.target.value })}
                      placeholder="Enter"
                      aria-label={`Quantity for ${line.raw_name}`}
                      className={`${inputClass} py-2 text-sm`}
                    />
                  </label>

                  <label className="block">
                    <span className="mb-1 block text-[11px] uppercase tracking-wider text-ink-600">
                      Unit
                    </span>
                    <select
                      value={line.editedUnit}
                      onChange={(e) => update(line.key, { editedUnit: e.target.value })}
                      aria-label={`Unit for ${line.raw_name}`}
                      className={`${inputClass} py-2 text-sm`}
                    >
                      <option value="">Product default</option>
                      {units.map((u) => (
                        <option key={u} value={u}>
                          {u}
                        </option>
                      ))}
                    </select>
                  </label>

                  <label className="block">
                    <span className="mb-1 block text-[11px] uppercase tracking-wider text-ink-600">
                      Product
                    </span>
                    <select
                      value={line.chosenProductId ?? ""}
                      onChange={(e) => {
                        const match = line.candidates.find(
                          (c) => c.product_id === e.target.value
                        );
                        update(line.key, {
                          chosenProductId: match?.product_id ?? null,
                          chosenProductName: match?.product_name ?? null,
                        });
                      }}
                      aria-label={`Product for ${line.raw_name}`}
                      className={`${inputClass} py-2 text-sm`}
                    >
                      <option value="">
                        {line.candidates.length ? "Choose a product" : "Not in catalogue"}
                      </option>
                      {line.candidates.map((c) => (
                        <option key={c.product_id} value={c.product_id}>
                          {c.product_name} ({Math.round(c.score * 100)}%)
                        </option>
                      ))}
                    </select>
                  </label>
                </div>

                {/* Unknown products are never created silently. */}
                {line.suggest_create && (
                  <p className="rounded-lg border border-ink-850 bg-ink-900 px-3 py-2 text-xs text-ink-300">
                    {line.candidates.length > 0 ? (
                      <>
                        None of these is a close match for &ldquo;
                        {line.normalized_name || line.raw_name}&rdquo;. Pick the right one above,
                        or{" "}
                      </>
                    ) : (
                      <>
                        &ldquo;{line.normalized_name || line.raw_name}&rdquo; isn&apos;t in your
                        catalogue.{" "}
                      </>
                    )}
                    <a href="/products/new" className="text-aria-400 hover:underline">
                      add it as a new product
                    </a>
                    . I won&apos;t create it on my own.
                  </p>
                )}
              </div>
            </div>
          </Card>
        ))}
      </div>

      <div className="sticky bottom-4 flex flex-wrap items-center gap-2 rounded-2xl border border-ink-850 bg-ink-950/95 p-3 backdrop-blur">
        <Button onClick={onApply} disabled={applicable.length === 0 || applying}>
          {applying
            ? "Adding…"
            : `Add ${applicable.length} item${applicable.length === 1 ? "" : "s"} to inventory`}
        </Button>
        <Button variant="secondary" onClick={onCancel} disabled={applying}>
          Cancel
        </Button>
        {selected.length > applicable.length && (
          <p className="text-xs text-amber-300">
            {selected.length - applicable.length} selected line
            {selected.length - applicable.length === 1 ? "" : "s"} still need a product and
            quantity.
          </p>
        )}
      </div>
    </div>
  );
}
