"use client";

import Link from "next/link";
import { useCallback, useEffect, useState } from "react";

import { Button, Card, Field, PageHeader, SectionLabel, inputClass } from "@/components/ui/Primitives";
import { ErrorState, LoadingRows, Toast } from "@/components/ui/States";
import { api } from "@/lib/api";
import { ThemeSwitcher, useTheme } from "@/lib/theme";
import { useBusiness } from "@/lib/BusinessContext";
import type { VoiceCapabilities } from "@/lib/types";

const LANGUAGES = [
  { code: "en-IN", label: "English", short: "en" },
  { code: "te-IN", label: "తెలుగు · Telugu", short: "te" },
  { code: "hi-IN", label: "हिन्दी · Hindi", short: "hi" },
];

/** Settings: what A.R.I.A. can actually do here, stated plainly. */
export default function SettingsPage() {
  const { business, summary, reload } = useBusiness();
  const { theme, resolved } = useTheme();
  const [caps, setCaps] = useState<VoiceCapabilities | null>(null);
  const [lang, setLang] = useState("en-IN");
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [toast, setToast] = useState<string | null>(null);
  const [working, setWorking] = useState(false);

  useEffect(() => {
    try {
      const saved = localStorage.getItem("aria.language");
      if (saved) setLang(saved);
    } catch {
      /* private mode */
    }
    api
      .voiceCapabilities()
      .then(setCaps)
      .catch((e: Error) => setError(e.message))
      .finally(() => setLoading(false));
  }, []);

  useEffect(() => {
    if (!toast) return;
    const id = setTimeout(() => setToast(null), 3000);
    return () => clearTimeout(id);
  }, [toast]);

  const chooseLanguage = useCallback((code: string) => {
    setLang(code);
    try {
      localStorage.setItem("aria.language", code);
    } catch {
      /* private mode */
    }
    setToast("Language preference saved");
  }, []);

  const runAction = useCallback(
    async (fn: () => Promise<unknown>, message: string) => {
      setWorking(true);
      setError(null);
      try {
        await fn();
        reload();
        setToast(message);
      } catch (e) {
        setError((e as Error).message);
      } finally {
        setWorking(false);
      }
    },
    [reload]
  );

  if (loading) return <LoadingRows count={3} />;

  return (
    <div className="space-y-7">
      <PageHeader title="Settings" subtitle="Your business, your language, and what A.R.I.A. can do." />

      {error && <ErrorState message={error} />}

      {summary && (
        <section className="space-y-3">
          <SectionLabel>Business</SectionLabel>
          <Card className="space-y-3 p-5">
            <div className="flex items-center gap-3">
              <span className="text-2xl" aria-hidden>
                {summary.type_emoji}
              </span>
              <div>
                <p className="text-[17px] font-semibold tracking-tight text-warm-50">{summary.business_name}</p>
                <p className="text-xs text-ink-400">
                  {summary.type_label}
                  {summary.location ? ` · ${summary.location}` : ""}
                </p>
              </div>
            </div>
            <div className="grid grid-cols-2 gap-3 border-t border-ink-850 pt-3 text-xs text-ink-400">
              <span>
                <span className="font-semibold tabular-nums text-warm-50">
                  {summary.product_count}
                </span>{" "}
                products
              </span>
              <span className="text-right">
                <span className="font-semibold tabular-nums text-warm-50">
                  {summary.event_count}
                </span>{" "}
                recorded events
              </span>
            </div>
            <div>
              <p className="eyebrow">
                Units for this trade
              </p>
              <div className="mt-1.5 flex flex-wrap gap-1.5">
                {summary.units.slice(0, 8).map((u) => (
                  <span
                    key={u}
                    className="rounded-md border border-ink-850 bg-ink-900 px-2 py-0.5 text-[11px] font-medium text-ink-400"
                  >
                    {u}
                  </span>
                ))}
              </div>
            </div>
          </Card>
        </section>
      )}

      {/* Appearance. Purely visual — it touches no other stored preference. */}
      <section className="space-y-3">
        <SectionLabel>Appearance</SectionLabel>
        <Card className="p-5">
          <p className="text-xs leading-relaxed text-ink-400">
            Choose how A.R.I.A. looks. &ldquo;System&rdquo; follows your device, so the interface
            dims when your machine does. Your choice is remembered on this device.
          </p>
          <div className="mt-3.5 max-w-sm">
            <ThemeSwitcher />
          </div>
          <p className="mt-2.5 text-[11px] text-ink-500">
            Currently showing the {resolved} theme
            {theme === "system" ? ", following your system setting" : ""}.
          </p>
        </Card>
      </section>

      <section className="space-y-3">
        <SectionLabel>Reply language</SectionLabel>
        <Card className="p-5">
          <p className="text-xs leading-relaxed text-ink-400">
            A.R.I.A. understands English, Telugu, Hindi and mixed speech whatever you pick. This
            only sets which language it replies in, and which one speech recognition listens for
            first.
          </p>
          <div className="mt-3 flex flex-wrap gap-2">
            {LANGUAGES.map((l) => (
              <button
                key={l.code}
                onClick={() => chooseLanguage(l.code)}
                className={`press rounded-[10px] border px-4 py-2.5 text-sm font-medium transition-all ${
                  lang === l.code
                    ? "border-aria-500/40 bg-aria-500/10 font-semibold text-aria-400"
                    : "border-ink-850 bg-ink-900 text-ink-400 hover:border-aria-500/25 hover:text-warm-50"
                }`}
              >
                {l.label}
              </button>
            ))}
          </div>
        </Card>
      </section>

      {/* Honest capability reporting: what works here, and what does not. */}
      {caps && (
        <section className="space-y-3">
          <SectionLabel>What A.R.I.A. can do here</SectionLabel>
          <Card className="divide-y divide-ink-850">
            <CapabilityRow
              label="Conversational agent"
              value={caps.agent_available ? `Live · ${caps.agent_model}` : "Not configured"}
              ok={caps.agent_available}
              note={
                caps.agent_available
                  ? "A.R.I.A. can hold a conversation and act through approved tools."
                  : "Set AI_API_KEY and AI_MODEL in the backend .env to enable it. Until then the built-in engine answers — a real engine, not a simulation of AI."
              }
            />
            <CapabilityRow
              label="Understanding"
              value={caps.llm_enabled ? `Language model (${caps.ai_provider})` : "Rule-based engine"}
              ok
              note={
                caps.llm_enabled
                  ? "Full language-model understanding is active."
                  : "Extraction uses the deterministic rule engine. It handles the trained vocabulary but not free-form phrasing."
              }
            />
            <CapabilityRow
              label="Translation"
              value={caps.translation_available ? caps.translation_provider : "Not needed"}
              ok
              note={
                caps.translation_available
                  ? "Available for display translation. Understanding still reads meaning directly."
                  : "Telugu, Hindi and mixed speech are understood as meaning rather than translated, so no translation service is required."
              }
            />
            <CapabilityRow
              label="Speech to text"
              value={caps.stt_is_client_side ? "Your browser" : caps.stt_provider}
              ok
              note={
                caps.stt_is_client_side
                  ? "Audio never leaves your device — only the transcribed text is sent."
                  : undefined
              }
            />
            <CapabilityRow
              label="Acts automatically above"
              value={`${Math.round(caps.confidence_threshold * 100)}% confidence`}
              ok
              note={`Below ${Math.round(caps.clarification_threshold * 100)}% A.R.I.A. asks instead of guessing.`}
            />
            <CapabilityRow
              label="Languages"
              value={caps.supported_languages.join(", ").toUpperCase()}
              ok
            />
            {caps.degraded_reason && (
              <CapabilityRow label="Note" value="Running degraded" ok={false} note={caps.degraded_reason} />
            )}
          </Card>
        </section>
      )}

      {business && (
        <section className="space-y-3">
          <SectionLabel>Data</SectionLabel>
          <Card className="space-y-3 p-5">
            <div className="flex flex-wrap gap-2">
              <Button
                variant="secondary"
                onClick={() =>
                  void runAction(() => api.adoptCatalogue(business.id), "Starter catalogue added")
                }
                disabled={working}
              >
                Add my trade&apos;s starter products
              </Button>
              <Button
                variant="secondary"
                onClick={() =>
                  void runAction(() => api.seedDemo(business.id), "Demo trading history added")
                }
                disabled={working}
              >
                Add demo trading history
              </Button>
            </div>
            <p className="text-xs leading-relaxed text-ink-500">
              Demo history writes real ledger events through the same engine as live trading, each
              stamped as demo data in your memory. It is never presented as something you said, and
              it will not run twice on a business that already has events.
            </p>
            <Link
              href="/onboarding"
              className="inline-block text-xs font-semibold text-aria-400 transition-colors hover:text-aria-400"
            >
              + Add Another Business →
            </Link>
          </Card>
        </section>
      )}

      {toast && <Toast message={toast} />}
    </div>
  );
}

function CapabilityRow({
  label,
  value,
  ok,
  note,
}: {
  label: string;
  value: string;
  ok: boolean;
  note?: string;
}) {
  return (
    <div className="px-5 py-3.5">
      <div className="flex items-baseline justify-between gap-3">
        <span className="eyebrow">{label}</span>
        <span className={`text-sm font-medium ${ok ? "text-warm-50" : "text-amber-300"}`}>
          {value}
        </span>
      </div>
      {note && <p className="mt-1 text-xs leading-relaxed text-ink-500">{note}</p>}
    </div>
  );
}
