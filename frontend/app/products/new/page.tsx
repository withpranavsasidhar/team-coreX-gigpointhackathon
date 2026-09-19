"use client";

import Link from "next/link";
import { useRouter } from "next/navigation";
import { useEffect, useState } from "react";

import { Button, Card, Field, SectionLabel, inputClass } from "@/components/ui/Primitives";
import { Toast } from "@/components/ui/States";
import { api } from "@/lib/api";
import { useBusiness } from "@/lib/BusinessContext";

const FALLBACK_UNITS = ["pieces", "kg", "litres", "bags", "cartons", "boxes", "dozens", "quintals"];

export default function NewProductPage() {
  const router = useRouter();
  const { business } = useBusiness();

  const [units, setUnits] = useState<string[]>(FALLBACK_UNITS);
  const [name, setName] = useState("");
  const [category, setCategory] = useState("general");
  const [baseUnit, setBaseUnit] = useState("pieces");
  const [openingStock, setOpeningStock] = useState("");
  const [minimumQuantity, setMinimumQuantity] = useState("");
  const [reorderQuantity, setReorderQuantity] = useState("");
  const [price, setPrice] = useState("");

  const [conversionUnit, setConversionUnit] = useState("");
  const [conversionFactor, setConversionFactor] = useState("");

  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [toast, setToast] = useState<string | null>(null);

  useEffect(() => {
    api
      .supportedUnits()
      .then((r) => setUnits(r.units))
      .catch(() => setUnits(FALLBACK_UNITS));
  }, []);

  async function submit() {
    if (!business) return;
    if (!name.trim()) {
      setError("Give the product a name.");
      return;
    }

    const conversions =
      conversionUnit && Number(conversionFactor) > 0
        ? [{ unit_name: conversionUnit, factor_to_base_unit: Number(conversionFactor) }]
        : [];

    setSubmitting(true);
    setError(null);
    try {
      const created = await api.createProduct(business.id, {
        name: name.trim(),
        category: category.trim() || "general",
        base_unit: baseUnit,
        opening_stock: Number(openingStock) || 0,
        minimum_quantity: Number(minimumQuantity) || 0,
        reorder_quantity: Number(reorderQuantity) || 0,
        price: Number(price) || 0,
        conversions,
      });
      setToast("Product added");
      router.push(`/inventory/${created.id}`);
    } catch (e) {
      setError((e as Error).message);
      setSubmitting(false);
    }
  }

  const alternateUnits = units.filter((u) => u !== baseUnit);

  return (
    <div className="space-y-6">
      <Link href="/inventory" className="inline-flex items-center gap-1.5 text-sm text-ink-400 hover:text-warm-50">
        ‹ Inventory
      </Link>

      <header>
        <h1 className="text-[28px] font-semibold leading-tight text-warm-50">Add a product</h1>
        <p className="mt-1 text-sm text-ink-400">
          ARIA starts remembering this product from the moment you add it.
        </p>
      </header>

      <Card className="space-y-5 p-5">
        <Field label="Product name">
          <input
            value={name}
            onChange={(e) => setName(e.target.value)}
            placeholder="e.g. Sunflower Oil 1L"
            className={inputClass}
            autoFocus
          />
        </Field>

        <div className="grid grid-cols-2 gap-3">
          <Field label="Category">
            <input
              value={category}
              onChange={(e) => setCategory(e.target.value)}
              placeholder="grains"
              className={inputClass}
            />
          </Field>
          <Field label="Unit you count in">
            <select value={baseUnit} onChange={(e) => setBaseUnit(e.target.value)} className={inputClass}>
              {units.map((u) => (
                <option key={u} value={u}>
                  {u}
                </option>
              ))}
            </select>
          </Field>
        </div>

        <Field label="Opening stock" hint="Recorded as the first event in this product's history.">
          <input
            type="number"
            inputMode="decimal"
            min="0"
            step="0.1"
            value={openingStock}
            onChange={(e) => setOpeningStock(e.target.value)}
            placeholder="0"
            className={inputClass}
          />
        </Field>
      </Card>

      <div className="space-y-3">
        <SectionLabel>Stock thresholds</SectionLabel>
        <Card className="space-y-5 p-5">
          <div className="grid grid-cols-2 gap-3">
            <Field label="Minimum stock" hint="Warn me below this.">
              <input
                type="number"
                inputMode="decimal"
                min="0"
                value={minimumQuantity}
                onChange={(e) => setMinimumQuantity(e.target.value)}
                placeholder="0"
                className={inputClass}
              />
            </Field>
            <Field label="Reorder quantity" hint="Usual order size.">
              <input
                type="number"
                inputMode="decimal"
                min="0"
                value={reorderQuantity}
                onChange={(e) => setReorderQuantity(e.target.value)}
                placeholder="0"
                className={inputClass}
              />
            </Field>
          </div>

          <Field label="Price per unit">
            <input
              type="number"
              inputMode="decimal"
              min="0"
              value={price}
              onChange={(e) => setPrice(e.target.value)}
              placeholder="0"
              className={inputClass}
            />
          </Field>
        </Card>
      </div>

      <div className="space-y-3">
        <SectionLabel>Trade unit (optional)</SectionLabel>
        <Card className="space-y-4 p-5">
          <p className="text-sm leading-relaxed text-ink-400">
            If you buy in a bigger unit than you count in, tell ARIA how they relate — so &ldquo;2 cartons&rdquo;
            becomes the right number of {baseUnit}.
          </p>
          <div className="grid grid-cols-2 gap-3">
            <Field label="Bigger unit">
              <select
                value={conversionUnit}
                onChange={(e) => setConversionUnit(e.target.value)}
                className={inputClass}
              >
                <option value="">None</option>
                {alternateUnits.map((u) => (
                  <option key={u} value={u}>
                    {u}
                  </option>
                ))}
              </select>
            </Field>
            <Field label={`${baseUnit} per unit`}>
              <input
                type="number"
                inputMode="decimal"
                min="0"
                value={conversionFactor}
                onChange={(e) => setConversionFactor(e.target.value)}
                placeholder="24"
                className={inputClass}
                disabled={!conversionUnit}
              />
            </Field>
          </div>
        </Card>
      </div>

      {error && <p className="rounded-xl bg-red-950 px-4 py-3 text-sm text-red-300">{error}</p>}

      <Button onClick={submit} disabled={submitting} fullWidth>
        {submitting ? "Adding…" : "Add product"}
      </Button>

      {toast && <Toast message={toast} />}
    </div>
  );
}
