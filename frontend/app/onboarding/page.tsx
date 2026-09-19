"use client";

import { useCallback, useEffect, useState } from "react";
import { useRouter } from "next/navigation";

import { AriaCore, type CoreState } from "@/components/aria/AriaCore";
import { AriaMark } from "@/components/aria/AriaMark";
import { Button, Field, inputClass } from "@/components/ui/Primitives";
import { ErrorState } from "@/components/ui/States";
import { api } from "@/lib/api";
import { useBusiness } from "@/lib/BusinessContext";
import { useSpeechCapture } from "@/lib/useSpeechCapture";
import type { BusinessType } from "@/lib/types";

/**
 * Onboarding is the first proof that A.R.I.A. adapts.
 *
 * The owner says what they do; the assistant configures the catalogue, the
 * units and the vocabulary for that trade. When it cannot tell what the trade
 * is, it asks rather than guessing — a wrong guess here would misconfigure
 * everything downstream.
 */
export default function OnboardingPage() {
  const router = useRouter();
  const { user, reload } = useBusiness();

  const [types, setTypes] = useState<BusinessType[]>([]);
  const [selected, setSelected] = useState<BusinessType | null>(null);
  const [name, setName] = useState("");
  const [location, setLocation] = useState("");
  const [language, setLanguage] = useState("en");
  const [withDemo, setWithDemo] = useState(true);

  const [spoken, setSpoken] = useState("");
  const [notRecognised, setNotRecognised] = useState(false);
  const [detecting, setDetecting] = useState(false);
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const capture = useSpeechCapture(language === "en" ? "en-IN" : `${language}-IN`);

  useEffect(() => {
    api.businessTypes().then(setTypes).catch((e: Error) => setError(e.message));
  }, []);

  const describeBusiness = useCallback(async (text: string) => {
    const trimmed = text.trim();
    if (!trimmed) return;
    setSpoken(trimmed);
    setDetecting(true);
    setNotRecognised(false);
    try {
      const detection = await api.detectBusinessType(trimmed);
      if (detection.matched && detection.key) {
        const match = await api
          .businessTypes()
          .then((all) => all.find((t) => t.key === detection.key) ?? null);
        setSelected(match);
      } else {
        // Honest failure: no silent fallback to a default trade.
        setNotRecognised(true);
      }
    } catch (e) {
      setError((e as Error).message);
    } finally {
      setDetecting(false);
    }
  }, []);

  const submit = useCallback(async () => {
    if (!selected || !name.trim()) return;
    setSubmitting(true);
    setError(null);
    try {
      if (user) {
        await api.createUserBusiness(user.id, {
          business_name: name.trim(),
          business_type: selected.key,
          location: location.trim(),
          seed_catalogue: true,
          seed_demo_history: withDemo,
        });
      } else {
        await api.onboard({
          business_name: name.trim(),
          business_type: selected.key,
          location: location.trim(),
          default_language: language,
          seed_catalogue: true,
          seed_demo_history: withDemo,
        });
      }
      reload();
      router.replace("/");
    } catch (e) {
      setError((e as Error).message);
      setSubmitting(false);
    }
  }, [selected, name, location, language, withDemo, user, reload, router]);

  const coreState: CoreState = capture.listening
    ? "listening"
    : detecting
      ? "understanding"
      : selected
        ? "success"
        : capture.state === "denied"
          ? "denied"
          : "idle";

  return (
    <div className="mx-auto min-h-dvh w-full max-w-2xl px-4 py-10">
      <div className="flex items-center gap-2.5">
        <AriaMark className="h-9 w-9" />
        <div>
          <p className="text-sm font-semibold tracking-tight text-warm-50">A.R.I.A.</p>
          <p className="text-[11px] text-ink-500">Adaptive Retail Intelligence Assistant</p>
        </div>
      </div>

      <div className="aria-aura -mx-4 mt-8 rounded-3xl px-4 py-10 text-center">
        <h1 className="text-[28px] font-semibold leading-tight tracking-tight text-warm-50">
          What kind of business do you run?
        </h1>
        <p className="mx-auto mt-2 max-w-md text-sm leading-relaxed text-ink-400">
          Tell me in your own words and I&apos;ll set up the right products, units and vocabulary.
        </p>

        <div className="mt-8 flex justify-center">
          <AriaCore
            state={coreState}
            levels={capture.listening ? capture.levels : undefined}
            size="md"
            labelOverride={
              selected
                ? { label: `Recognised ${selected.descriptor}`, hint: "Confirm the details below" }
                : coreState === "idle"
                  ? { label: "Tap and tell me", hint: "e.g. “I run a bakery”" }
                  : undefined
            }
            onActivate={
              capture.supported
                ? () =>
                    capture.listening
                      ? capture.stop()
                      : capture.start((t) => void describeBusiness(t))
                : undefined
            }
          />
        </div>

        {capture.listening && (capture.transcript || capture.interim) && (
          <p className="mt-4 text-[15px] text-warm-50">
            {capture.transcript}
            <span className="text-ink-500">{capture.interim}</span>
          </p>
        )}

        <div className="mx-auto mt-6 flex max-w-md gap-2">
          <input
            value={spoken}
            onChange={(e) => setSpoken(e.target.value)}
            onKeyDown={(e) => e.key === "Enter" && void describeBusiness(spoken)}
            placeholder="e.g. I run a bakery"
            aria-label="Describe your business"
            className={inputClass}
          />
          <Button onClick={() => void describeBusiness(spoken)} disabled={!spoken.trim() || detecting}>
            {detecting ? "…" : "Go"}
          </Button>
        </div>

        {notRecognised && (
          <p className="mx-auto mt-4 max-w-md rounded-xl border border-amber-500/30 bg-amber-950 px-4 py-3 text-sm text-amber-300">
            I don&apos;t know that trade yet, so I won&apos;t guess — picking wrong would set up the
            wrong catalogue. Choose the closest one below.
          </p>
        )}
      </div>

      {error && (
        <div className="mt-6">
          <ErrorState message={error} />
        </div>
      )}

      {/* Trade picker */}
      <section className="mt-8">
        <p className="text-[11px] font-semibold uppercase tracking-[0.1em] text-ink-500">
          {selected ? "Business type" : "Or pick one"}
        </p>
        <div className="mt-3 grid grid-cols-2 gap-2.5 sm:grid-cols-3">
          {types.map((t) => {
            const active = selected?.key === t.key;
            return (
              <button
                key={t.key}
                onClick={() => {
                  setSelected(t);
                  setNotRecognised(false);
                }}
                className={`rounded-xl border px-3 py-3 text-left transition-colors ${
                  active
                    ? "border-aria-500/40 bg-aria-500/10"
                    : "border-ink-850 bg-ink-950 hover:border-ink-850 hover:bg-ink-900"
                }`}
              >
                <span className="text-lg" aria-hidden>
                  {t.emoji}
                </span>
                <p
                  className={`mt-1 text-sm font-medium ${active ? "text-aria-400" : "text-warm-50"}`}
                >
                  {t.label}
                </p>
                <p className="mt-0.5 text-[11px] leading-relaxed text-ink-500">
                  {t.starter_product_count} products · {t.units.slice(0, 3).join(", ")}
                </p>
              </button>
            );
          })}
        </div>
      </section>

      {/* Confirm */}
      {selected && (
        <section className="animate-slide-up mt-8 space-y-4 rounded-2xl border border-ink-850 bg-ink-950 p-5">
          <div>
            <p className="text-sm font-medium text-warm-50">
              {selected.emoji} Setting up {selected.descriptor}
            </p>
            <p className="mt-1 text-xs leading-relaxed text-ink-400">
              I&apos;ll add {selected.starter_product_count} products your trade usually stocks —{" "}
              {selected.starter_product_names.slice(0, 4).join(", ")} and more — with{" "}
              {selected.units.slice(0, 4).join(", ")} as natural units. All at zero stock until you
              tell me otherwise.
            </p>
          </div>

          <Field label="Business name">
            <input
              value={name}
              onChange={(e) => setName(e.target.value)}
              placeholder={`e.g. ${selected.key === "bakery" ? "Sunrise Bakery" : "Ravi Stores"}`}
              className={inputClass}
              aria-label="Business name"
            />
          </Field>

          <div className="grid gap-4 sm:grid-cols-2">
            <Field label="Location" hint="Optional">
              <input
                value={location}
                onChange={(e) => setLocation(e.target.value)}
                placeholder="Hyderabad"
                className={inputClass}
                aria-label="Location"
              />
            </Field>
            <Field label="Reply language" hint="You can speak any of them">
              <select
                value={language}
                onChange={(e) => setLanguage(e.target.value)}
                className={inputClass}
                aria-label="Reply language"
              >
                <option value="en">English</option>
                <option value="te">Telugu</option>
                <option value="hi">Hindi</option>
              </select>
            </Field>
          </div>

          <label className="flex cursor-pointer items-start gap-3 rounded-xl border border-ink-850 bg-ink-900 p-3.5">
            <input
              type="checkbox"
              checked={withDemo}
              onChange={(e) => setWithDemo(e.target.checked)}
              className="mt-0.5 h-4 w-4 accent-aria-500"
            />
            <span>
              <span className="block text-sm font-medium text-warm-50">
                Add three weeks of example trading
              </span>
              <span className="mt-0.5 block text-xs leading-relaxed text-ink-400">
                So analytics and predictions have history to work from. Every row is labelled as
                demo data in your memory and is never presented as something you said.
              </span>
            </span>
          </label>

          <Button onClick={() => void submit()} disabled={!name.trim() || submitting} fullWidth>
            {submitting ? "Setting up…" : "Start using A.R.I.A."}
          </Button>
        </section>
      )}
    </div>
  );
}
