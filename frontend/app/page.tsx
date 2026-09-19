"use client";

import Link from "next/link";
import { useCallback, useEffect, useState } from "react";
import { useRouter } from "next/navigation";

import { AriaCore, type CoreState } from "@/components/aria/AriaCore";
import { UnderstandingChain, languageLabel } from "@/components/aria/UnderstandingChain";
import { Card, SectionLabel, Stat } from "@/components/ui/Primitives";
import { ActionCard, ErrorState, LoadingRows } from "@/components/ui/States";
import { api } from "@/lib/api";
import { useBusiness } from "@/lib/BusinessContext";
import { useSpeechCapture } from "@/lib/useSpeechCapture";
import {
  EVENT_META,
  TONE_TEXT_DARK,
  clockTime,
  formatQty,
  formatSigned,
  rupees,
} from "@/lib/format";
import type {
  Customer,
  InventoryEvent,
  ProductStatus,
  StockAlert,
  VoiceInterpretation,
} from "@/lib/types";

function greeting() {
  const hour = new Date().getHours();
  if (hour < 12) return "Good morning";
  if (hour < 17) return "Good afternoon";
  return "Good evening";
}

/** The owner's first name, from the authenticated profile. Never invented. */
function firstName(name?: string | null) {
  const first = name?.trim().split(/\s+/)[0];
  return first || null;
}

/**
 * The command centre.
 *
 * Not a dashboard with a microphone bolted on: the core is the primary
 * control, and the state of the business sits beneath it as context for the
 * next thing the owner will say. A.R.I.A. opens the conversation rather than
 * heading a page.
 */
export default function CommandCentre() {
  const router = useRouter();
  const { user, business, summary, loading: ctxLoading, error: ctxError, reload } = useBusiness();

  const [products, setProducts] = useState<ProductStatus[]>([]);
  const [events, setEvents] = useState<InventoryEvent[]>([]);
  const [alerts, setAlerts] = useState<StockAlert[]>([]);
  const [customers, setCustomers] = useState<Customer[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  // Voice
  const [lang, setLang] = useState("en-IN");
  const [result, setResult] = useState<VoiceInterpretation | null>(null);
  const [thinking, setThinking] = useState(false);
  const [voiceError, setVoiceError] = useState<string | null>(null);
  const capture = useSpeechCapture(lang);

  useEffect(() => {
    try {
      const saved = localStorage.getItem("aria.language");
      if (saved) setLang(saved);
    } catch {
      /* private mode */
    }
  }, []);

  const load = useCallback(() => {
    if (!business) return;
    setLoading(true);
    setError(null);
    Promise.all([
      api.inventory(business.id),
      api.events(business.id, 8),
      api.alerts(business.id),
      api.customers(business.id),
    ])
      .then(([inv, evts, alertRows, people]) => {
        setProducts(inv);
        setEvents(evts);
        setAlerts(alertRows);
        setCustomers(people);
      })
      .catch((e: Error) => setError(e.message))
      .finally(() => setLoading(false));
  }, [business]);

  useEffect(load, [load]);

  const handleTranscript = useCallback(
    async (text: string) => {
      if (!business || !text.trim()) return;
      setThinking(true);
      setVoiceError(null);
      setResult(null);
      try {
        const interpretation = await api.processVoice(business.id, text, lang, lang.split("-")[0]);
        setResult(interpretation);
        if (interpretation.status === "recorded" || interpretation.status === "amended") {
          load();
          router.refresh();
        }
      } catch (e) {
        setVoiceError((e as Error).message);
      } finally {
        setThinking(false);
      }
    },
    [business, lang, load, router]
  );

  if (ctxError) return <ErrorState message={ctxError} onRetry={reload} />;
  if (ctxLoading || (loading && !products.length && !error)) {
    return (
      <div className="space-y-8">
        <div className="space-y-3">
          <div className="skeleton h-3 w-32" />
          <div className="skeleton h-10 w-72" />
        </div>
        <div className="skeleton h-72 w-full rounded-3xl" />
        <LoadingRows count={2} />
      </div>
    );
  }
  if (error) return <ErrorState message={error} onRetry={load} />;

  const coreState: CoreState =
    capture.state === "denied"
      ? "denied"
      : capture.state === "unsupported"
        ? "unsupported"
        : capture.listening
          ? "listening"
          : thinking
            ? "understanding"
            : result?.status === "recorded" || result?.status === "amended"
              ? "success"
              : result?.status === "needs_confirmation"
                ? "confirming"
                : result?.status === "rejected" || voiceError
                  ? "error"
                  : "idle";

  const outstanding = customers.reduce((sum, c) => sum + c.outstanding_credit, 0);
  const owing = customers.filter((c) => c.outstanding_credit > 0).length;
  const healthy = products.filter((p) => p.status === "healthy").length;
  const todayCount = events.filter(
    (e) => new Date(`${e.occurred_at}Z`).toDateString() === new Date().toDateString()
  ).length;

  const name = firstName(user?.name);
  const recorded = result?.status === "recorded" || result?.status === "amended";

  return (
    <div className="space-y-10">
      {/* Hero — A.R.I.A. welcomes the owner and waits. */}
      <section className="aria-aura -mx-4 -mt-6 rounded-b-[28px] px-4 pb-8 pt-10 lg:-mx-8 lg:-mt-8 lg:px-8 lg:pt-14">
        <header className="text-center">
          <p className="eyebrow">
            {summary ? `${summary.type_emoji} ${summary.business_name}` : business?.business_name}
          </p>
          <h1 className="mt-3 text-[34px] font-semibold leading-[1.1] tracking-tight text-warm-50 sm:text-[40px]">
            {greeting()}
            {name ? `, ${name}` : ""}.
          </h1>
          <p className="mx-auto mt-2.5 max-w-md text-[16px] leading-relaxed text-ink-400">
            What would you like to take care of today?
          </p>
        </header>

        <div className="mt-9 flex justify-center">
          <AriaCore
            state={coreState}
            levels={capture.listening ? capture.levels : undefined}
            language={result?.detected_language ? languageLabel(result.detected_language) : null}
            confidence={result && !thinking ? result.confidence : null}
            size="lg"
            onActivate={
              capture.supported
                ? () => {
                    if (capture.listening) {
                      capture.stop();
                    } else {
                      setResult(null);
                      setVoiceError(null);
                      capture.start((t) => void handleTranscript(t));
                    }
                  }
                : undefined
            }
          />
        </div>

        {/* Live transcript while speaking. */}
        {capture.listening && (capture.transcript || capture.interim) && (
          <p className="mx-auto mt-7 max-w-xl text-center text-[17px] leading-relaxed text-warm-50">
            {capture.transcript}
            <span className="text-ink-500">{capture.interim}</span>
          </p>
        )}

        {(capture.error || voiceError) && (
          <p className="mx-auto mt-7 max-w-xl rounded-xl border border-red-500/25 bg-red-950 px-4 py-3 text-center text-sm text-red-300">
            {capture.error ?? voiceError}
          </p>
        )}

        {capture.state === "unsupported" && !capture.error && (
          <p className="mx-auto mt-7 max-w-xl text-center text-xs text-ink-500">
            This browser has no speech recognition. Press ⌘K to type to A.R.I.A. instead.
          </p>
        )}

        {/* The pipeline, made visible. */}
        {(thinking || result) && (
          <div className="mx-auto mt-9 max-w-xl space-y-3">
            <UnderstandingChain
              transcript={capture.transcript || result?.transcript}
              result={result}
              thinking={thinking}
            />
            {result && (
              <>
                <ActionCard
                  title={
                    recorded
                      ? result.event_type
                        ? `${EVENT_META[result.event_type].label} recorded`
                        : "Recorded"
                      : result.status === "needs_confirmation"
                        ? "Needs your confirmation"
                        : "Not recorded"
                  }
                  subject={result.product_name}
                  change={
                    result.resulting_quantity !== null
                      ? `${formatQty(result.resulting_quantity)} ${result.resulting_unit}`
                      : null
                  }
                  note={result.message}
                  tone={recorded ? "success" : result.status === "needs_confirmation" ? "pending" : "error"}
                />
                {result.candidates.length > 0 && result.status !== "recorded" && (
                  <div className="flex flex-wrap gap-1.5">
                    {result.candidates.slice(0, 6).map((c) => (
                      <span
                        key={c.product_id}
                        className="rounded-lg border border-ink-850 bg-ink-900 px-2.5 py-1 text-xs text-ink-300"
                      >
                        {c.name}
                      </span>
                    ))}
                  </div>
                )}
              </>
            )}
          </div>
        )}
      </section>

      {/* Business state */}
      <section className="space-y-3.5">
        <SectionLabel>Current state</SectionLabel>
        <div className="grid grid-cols-2 gap-3 lg:grid-cols-4">
          <Stat label="Products" value={products.length} hint={`${healthy} comfortably stocked`} />
          <Stat
            label="Need attention"
            value={alerts.length}
            tone={alerts.length ? "warn" : "good"}
            hint={alerts.length ? alerts[0].product_name : "Nothing urgent"}
          />
          <Stat
            label="Outstanding credit"
            value={rupees(outstanding)}
            tone={outstanding > 0 ? "warn" : "good"}
            hint={owing ? `${owing} customers` : "Credit book is clear"}
          />
          <Stat label="Recorded today" value={todayCount} hint="Business events" />
        </div>
      </section>

      {/* Attention */}
      {alerts.length > 0 && (
        <section className="space-y-3.5">
          <SectionLabel
            action={
              <Link
                href="/analytics"
                className="text-xs font-semibold text-aria-400 transition-colors hover:text-aria-400"
              >
                All insights →
              </Link>
            }
          >
            Needs attention
          </SectionLabel>
          <div className="space-y-2.5">
            {alerts.slice(0, 3).map((a) => (
              <Link
                key={a.product_id}
                href={`/inventory/${a.product_id}`}
                className={`focus-ring group relative block overflow-hidden rounded-2xl border p-4 pl-5 shadow-soft transition-all duration-200 hover:shadow-lift ${
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
                  <p className="shrink-0 font-display text-[17px] font-semibold tabular-nums text-warm-50">
                    {formatQty(a.current_quantity)}
                    <span className="ml-1 text-xs font-normal text-ink-500">{a.base_unit}</span>
                  </p>
                </div>
              </Link>
            ))}
          </div>
        </section>
      )}

      {/* Recent memory */}
      <section className="space-y-3.5">
        <SectionLabel
          action={
            <Link
              href="/memory"
              className="text-xs font-semibold text-aria-400 transition-colors hover:text-aria-400"
            >
              Full memory →
            </Link>
          }
        >
          Just happened
        </SectionLabel>
        {events.length === 0 ? (
          <Card className="px-6 py-10 text-center">
            <p className="text-[15px] font-medium text-warm-50">
              Your business memory is still quiet.
            </p>
            <p className="mx-auto mt-1.5 max-w-sm text-sm leading-relaxed text-ink-400">
              Press the core above and tell A.R.I.A. what happened — it will appear here.
            </p>
          </Card>
        ) : (
          <Card className="divide-y divide-ink-850">
            {events.map((e) => {
              const meta = EVENT_META[e.event_type];
              return (
                <div key={e.id} className="flex items-center justify-between gap-3 px-5 py-3.5">
                  <div className="flex min-w-0 items-center gap-3.5">
                    {/* Timeline marker — small, red, and the same on every row. */}
                    <span className="relative grid h-7 w-7 shrink-0 place-items-center rounded-full border border-aria-500/25">
                      <span className={`text-xs ${TONE_TEXT_DARK[meta.tone]}`}>{meta.icon}</span>
                    </span>
                    <div className="min-w-0">
                      <p className="truncate text-[14px] font-medium text-warm-50">
                        {meta.label} · {e.product_name}
                      </p>
                      <p className="mt-0.5 text-[11.5px] text-ink-500">
                        {clockTime(e.occurred_at)}
                        {e.customer_name ? ` · ${e.customer_name}` : ""}
                        {e.source === "demo" ? " · demo data" : ""}
                      </p>
                    </div>
                  </div>
                  <span
                    className={`shrink-0 text-[14px] font-semibold tabular-nums ${
                      e.delta > 0 ? "text-emerald-500" : "text-ink-300"
                    }`}
                  >
                    {formatSigned(e.delta)}
                  </span>
                </div>
              );
            })}
          </Card>
        )}
      </section>
    </div>
  );
}
