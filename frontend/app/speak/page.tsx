"use client";

import Link from "next/link";
import { useCallback, useEffect, useMemo, useState } from "react";

import { ConfidenceMeter, MicButton, Waveform } from "@/components/voice/VoiceVisuals";
import { Button, Card, Field, SectionLabel, inputClass } from "@/components/ui/Primitives";
import { Toast } from "@/components/ui/States";
import { api } from "@/lib/api";
import { useBusiness } from "@/lib/BusinessContext";
import { EVENT_META, formatQty } from "@/lib/format";
import { useSpeechCapture } from "@/lib/useSpeechCapture";
import type { EventType, ProductCandidate, VoiceCapabilities, VoiceInterpretation } from "@/lib/types";

const LANGUAGES = [
  { code: "en-IN", label: "English" },
  { code: "te-IN", label: "తెలుగు" },
  { code: "hi-IN", label: "हिन्दी" },
];

const EXAMPLES: Record<string, string[]> = {
  en: [
    "I received five cartons of biscuits",
    "Sold three boxes of Maggi",
    "Ramesh took two oil packets and will pay tomorrow",
  ],
  te: [
    "Rendu cartons Coke vachayi",
    "నాలుగు బస్తాలు బియ్యం వచ్చాయి",
    "మూడు లీటర్లు నూనె అమ్మాము",
  ],
  hi: [
    "do kilo chawal becha",
    "दो कार्टन Coke आ गया",
    "पांच लीटर दूध खराब",
  ],
};

const LANGUAGE_LABELS: Record<string, string> = {
  en: "English",
  te: "తెలుగు",
  hi: "हिन्दी",
  "te-en": "Telugu + English",
  "hi-en": "Hindi + English",
};

const ACTIONS: EventType[] = [
  "STOCK_IN", "PURCHASE", "SALE", "STOCK_OUT", "CREDIT_SALE", "DAMAGE", "RETURN", "LOSS",
];

const UNITS = ["pieces", "kg", "litres", "bags", "cartons", "boxes", "dozens", "quintals"];

export default function SpeakPage() {
  const { business } = useBusiness();
  const [lang, setLang] = useState("en-IN");
  const capture = useSpeechCapture(lang);
  const replyLang = lang.split("-")[0];

  useEffect(() => {
    try {
      const saved = localStorage.getItem("aria.language");
      if (saved) setLang(saved);
    } catch {
      /* private mode */
    }
  }, []);

  function chooseLanguage(next: string) {
    setLang(next);
    try {
      localStorage.setItem("aria.language", next);
    } catch {
      /* private mode */
    }
  }

  const [caps, setCaps] = useState<VoiceCapabilities | null>(null);
  const [processing, setProcessing] = useState(false);
  const [result, setResult] = useState<VoiceInterpretation | null>(null);
  const [typed, setTyped] = useState("");
  const [toast, setToast] = useState<{ message: string; tone: "success" | "error" } | null>(null);

  // Editable draft used by the confirm/clarify path.
  const [draftProductId, setDraftProductId] = useState<string | null>(null);
  const [draftAction, setDraftAction] = useState<EventType>("STOCK_IN");
  const [draftQty, setDraftQty] = useState("");
  const [draftUnit, setDraftUnit] = useState("pieces");
  const [draftCustomer, setDraftCustomer] = useState("");
  const [saving, setSaving] = useState(false);
  const [saveError, setSaveError] = useState<string | null>(null);

  useEffect(() => {
    api.voiceCapabilities().then(setCaps).catch(() => setCaps(null));
  }, []);

  useEffect(() => {
    if (!toast) return;
    const t = setTimeout(() => setToast(null), 2800);
    return () => clearTimeout(t);
  }, [toast]);

  const hydrateDraft = useCallback((r: VoiceInterpretation) => {
    setDraftProductId(r.product_id);
    setDraftAction((r.event_type ?? "STOCK_IN") as EventType);
    setDraftQty(r.quantity != null ? String(r.quantity) : "");
    setDraftUnit(r.unit ?? r.candidates[0]?.base_unit ?? "pieces");
    setDraftCustomer(r.customer_name ?? "");
    setSaveError(null);
  }, []);

  const send = useCallback(
    async (text: string) => {
      if (!business || !text.trim()) return;
      setProcessing(true);
      setResult(null);
      try {
        const r = await api.processVoice(business.id, text.trim(), replyLang, replyLang);
        setResult(r);
        hydrateDraft(r);
        if (r.status === "recorded") setToast({ message: "Recorded", tone: "success" });
      } catch (e) {
        setToast({ message: (e as Error).message, tone: "error" });
      } finally {
        setProcessing(false);
      }
    },
    [business, hydrateDraft, replyLang]
  );

  function onMicClick() {
    if (capture.listening) {
      capture.stop();
      return;
    }
    setResult(null);
    capture.start((finalText) => void send(finalText));
  }

  async function confirmDraft() {
    if (!business || !draftProductId || !result) return;
    const qty = Number(draftQty);
    if (!qty || qty <= 0) {
      setSaveError("Enter a quantity greater than zero.");
      return;
    }
    if (draftAction === "CREDIT_SALE" && !draftCustomer.trim()) {
      setSaveError("A credit sale needs a customer name.");
      return;
    }

    setSaving(true);
    setSaveError(null);
    try {
      await api.createEvent(business.id, {
        product_id: draftProductId,
        event_type: draftAction,
        quantity: qty,
        unit: draftUnit,
        customer_name: draftCustomer.trim() || undefined,
        source: "voice",
        original_text: result.transcript,
        normalized_text: result.normalized_text,
        detected_language: result.detected_language,
        confidence: result.confidence,
      });
      setToast({ message: "Recorded", tone: "success" });
      setResult(null);
      setTyped("");
      capture.reset();
    } catch (e) {
      setSaveError((e as Error).message);
    } finally {
      setSaving(false);
    }
  }

  const liveText = `${capture.transcript} ${capture.interim}`.trim();
  const candidates: ProductCandidate[] = result?.candidates ?? [];
  const chosenUnits = useMemo(() => {
    const base = candidates.find((c) => c.product_id === draftProductId)?.base_unit;
    return base ? [base, ...UNITS.filter((u) => u !== base)] : UNITS;
  }, [candidates, draftProductId]);

  const showEditor =
    result && (result.status === "needs_confirmation" || result.status === "needs_clarification");

  return (
    <div className="space-y-6">
      <header className="flex items-center justify-between">
        <h1 className="text-[28px] font-semibold leading-tight text-warm-50">Speak</h1>
        <select
          value={lang}
          onChange={(e) => chooseLanguage(e.target.value)}
          className="focus-ring rounded-full border border-ink-850 bg-ink-950 px-3 py-2 text-sm"
          aria-label="Your language"
        >
          {LANGUAGES.map((l) => (
            <option key={l.code} value={l.code}>
              {l.label}
            </option>
          ))}
        </select>
      </header>

      {/* Mic stage */}
      <Card tone="dark" className="relative overflow-hidden px-6 py-9 text-center">
        <div className="pointer-events-none absolute left-1/2 top-1/2 h-72 w-72 -translate-x-1/2 -translate-y-1/2 rounded-full bg-aria-600/10 blur-3xl" />
        <div className="relative space-y-5">
          <div className="flex justify-center">
            <MicButton
              listening={capture.listening}
              processing={processing}
              onClick={onMicClick}
              disabled={!capture.supported}
            />
          </div>

          {capture.listening && <Waveform levels={capture.levels} active />}

          <div className="min-h-[52px]">
            {processing ? (
              <p className="text-sm text-ink-400">Understanding…</p>
            ) : capture.listening ? (
              <>
                <p className="text-lg font-medium text-warm-50">
                  {liveText || "Listening…"}
                </p>
                <p className="mt-1 text-[10.5px] font-bold uppercase tracking-[0.12em] text-aria-500">Recording</p>
              </>
            ) : (
              <>
                <p className="text-lg font-medium text-warm-50">What happened?</p>
                <p className="mt-1 text-sm text-ink-400">
                  {capture.supported ? "Tap the mic and say it naturally" : "Type what happened below"}
                </p>
              </>
            )}
          </div>
        </div>
      </Card>

      {/* Degraded / permission notices */}
      {capture.error && (
        <p className="rounded-xl border border-amber-500/30 bg-amber-950 px-4 py-3 text-sm text-amber-300">
          {capture.error}
        </p>
      )}
      {!capture.supported && (
        <p className="rounded-xl border border-amber-500/30 bg-amber-950 px-4 py-3 text-sm text-amber-300">
          This browser can&apos;t listen. Typing works exactly the same way.
        </p>
      )}
      {caps?.degraded_reason && (
        <p className="rounded-xl border border-ink-850 bg-ink-900 px-4 py-3 text-sm text-ink-400">
          {caps.degraded_reason}
        </p>
      )}

      {/* Typed fallback — always available */}
      <div className="flex gap-2">
        <input
          value={typed}
          onChange={(e) => setTyped(e.target.value)}
          onKeyDown={(e) => e.key === "Enter" && void send(typed)}
          placeholder="Or type what happened…"
          className={inputClass}
          aria-label="Type what happened"
        />
        <Button onClick={() => void send(typed)} disabled={!typed.trim() || processing}>
          Send
        </Button>
      </div>

      {!result && !processing && (
        <div className="space-y-2">
          <SectionLabel>Try saying</SectionLabel>
          <div className="flex flex-wrap gap-2">
            {(EXAMPLES[replyLang] ?? EXAMPLES.en).map((ex) => (
              <button
                key={ex}
                onClick={() => void send(ex)}
                className="focus-ring rounded-full border border-ink-850 bg-ink-950 px-4 py-2 text-left text-sm text-ink-400 hover:bg-ink-900"
              >
                {ex}
              </button>
            ))}
          </div>
        </div>
      )}

      {/* Success */}
      {result?.status === "recorded" && result.created_event && (
        <Card className="animate-slide-up border-aria-500/25 bg-aria-500/10 p-6 text-center">
          <div className="mx-auto flex h-12 w-12 items-center justify-center rounded-full bg-aria-600 text-xl text-white">
            ✓
          </div>
          <p className="mt-4 text-lg font-semibold text-warm-50">{result.message}</p>
          <p className="mt-1 text-sm text-ink-400">
            {result.product_name} is now{" "}
            <strong className="text-warm-50">
              {formatQty(result.resulting_quantity ?? 0)} {result.resulting_unit}
            </strong>
          </p>
          <div className="mt-4 flex flex-wrap items-center justify-center gap-3">
            <ConfidenceMeter score={result.confidence} />
            <span className="rounded-full border border-ink-850 bg-ink-950 px-2.5 py-1 text-[11px] font-medium text-ink-400">
              Heard {LANGUAGE_LABELS[result.detected_language] ?? result.detected_language}
            </span>
          </div>
          <div className="mt-5 flex justify-center gap-3">
            <Button variant="secondary" onClick={() => setResult(null)}>
              Say something else
            </Button>
            <Link
              href={`/inventory/${result.product_id}`}
              className="focus-ring inline-flex min-h-[44px] items-center rounded-xl px-5 text-[15px] font-medium text-aria-400 hover:bg-aria-500/10"
            >
              View product
            </Link>
          </div>
        </Card>
      )}

      {/* Rejected */}
      {result?.status === "rejected" && (
        <Card className="border-amber-500/25 bg-amber-950 p-6 text-center">
          <p className="text-base font-medium text-warm-50">{result.message}</p>
          {result.transcript && (
            <p className="mt-2 text-sm italic text-ink-400">&ldquo;{result.transcript}&rdquo;</p>
          )}
          <div className="mt-5 flex justify-center gap-3">
            <Button variant="secondary" onClick={() => setResult(null)}>
              Try again
            </Button>
            <Link
              href="/products/new"
              className="focus-ring inline-flex min-h-[44px] items-center rounded-xl px-5 text-[15px] font-medium text-aria-400 hover:bg-aria-500/10"
            >
              Add product
            </Link>
          </div>
        </Card>
      )}

      {/* Confirm / clarify */}
      {showEditor && result && (
        <Card className="animate-slide-up space-y-5 p-5">
          <div>
            <p className="text-sm italic text-ink-400">&ldquo;{result.transcript}&rdquo;</p>
            <p className="mt-2 text-base font-medium text-warm-50">{result.message}</p>
            <div className="mt-3 flex flex-wrap items-center gap-3">
              <ConfidenceMeter score={result.confidence} />
              <span className="rounded-full border border-ink-850 bg-ink-950 px-2.5 py-1 text-[11px] font-medium text-ink-400">
                Heard {LANGUAGE_LABELS[result.detected_language] ?? result.detected_language}
              </span>
            </div>
          </div>

          {candidates.length > 1 && (
            <div className="space-y-2">
              <SectionLabel>Which product?</SectionLabel>
              {candidates.map((c) => (
                <button
                  key={c.product_id}
                  onClick={() => {
                    setDraftProductId(c.product_id);
                    setDraftUnit(c.base_unit);
                  }}
                  className={`focus-ring flex w-full items-center justify-between rounded-xl border px-4 py-3 text-left transition-colors ${
                    draftProductId === c.product_id
                      ? "border-aria-500/40 bg-aria-500/10"
                      : "border-ink-850 bg-ink-950 hover:bg-ink-900"
                  }`}
                >
                  <span className="flex items-center gap-2.5">
                    <span
                      className={`h-4 w-4 rounded-full border-2 ${
                        draftProductId === c.product_id
                          ? "border-aria-500/40 bg-aria-600"
                          : "border-ink-850"
                      }`}
                    />
                    <span className="text-sm font-medium text-warm-50">{c.name}</span>
                  </span>
                  <span className="text-xs text-ink-400">
                    {formatQty(c.current_quantity)} {c.base_unit}
                  </span>
                </button>
              ))}
            </div>
          )}

          <div className="grid grid-cols-2 gap-3">
            <Field label="Action">
              <select
                value={draftAction}
                onChange={(e) => setDraftAction(e.target.value as EventType)}
                className={inputClass}
              >
                {ACTIONS.map((a) => (
                  <option key={a} value={a}>
                    {EVENT_META[a].label}
                  </option>
                ))}
              </select>
            </Field>
            <Field label="Quantity">
              <input
                type="number"
                inputMode="decimal"
                min="0"
                step="0.1"
                value={draftQty}
                onChange={(e) => setDraftQty(e.target.value)}
                placeholder="0"
                className={inputClass}
                autoFocus={result.quantity == null}
              />
            </Field>
          </div>

          <div className={draftAction === "CREDIT_SALE" ? "grid grid-cols-2 gap-3" : ""}>
            <Field label="Unit">
              <select
                value={draftUnit}
                onChange={(e) => setDraftUnit(e.target.value)}
                className={inputClass}
              >
                {chosenUnits.map((u) => (
                  <option key={u} value={u}>
                    {u}
                  </option>
                ))}
              </select>
            </Field>
            {draftAction === "CREDIT_SALE" && (
              <Field label="Customer">
                <input
                  value={draftCustomer}
                  onChange={(e) => setDraftCustomer(e.target.value)}
                  placeholder="e.g. Ramesh"
                  className={inputClass}
                />
              </Field>
            )}
          </div>

          {result.notes.length > 0 && (
            <ul className="space-y-1 text-xs text-ink-400">
              {result.notes.map((n) => (
                <li key={n}>• {n}</li>
              ))}
            </ul>
          )}

          {saveError && (
            <p className="rounded-xl bg-red-950 px-4 py-3 text-sm text-red-300">{saveError}</p>
          )}

          <div className="flex gap-3">
            <Button onClick={confirmDraft} disabled={saving || !draftProductId} fullWidth>
              {saving ? "Recording…" : "Confirm"}
            </Button>
            <Button variant="secondary" onClick={() => setResult(null)}>
              Discard
            </Button>
          </div>
        </Card>
      )}

      {toast && <Toast message={toast.message} tone={toast.tone} />}
    </div>
  );
}
