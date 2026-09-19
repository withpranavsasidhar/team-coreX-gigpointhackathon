"use client";

import type { VoiceInterpretation } from "@/lib/types";
import { EVENT_META } from "@/lib/format";

/**
 * The pipeline, made visible.
 *
 * Each row appears only once that stage has actually produced something, so
 * the chain is a record of real work rather than a scripted animation. A stage
 * the system genuinely skipped never appears.
 */

const LANGUAGE_NAMES: Record<string, string> = {
  en: "English",
  te: "Telugu",
  hi: "Hindi",
  "te-en": "Telugu + English",
  "hi-en": "Hindi + English",
  "te-hi": "Telugu + Hindi",
  mixed: "Mixed",
};

export function languageLabel(code?: string | null): string {
  if (!code) return "";
  const key = code.toLowerCase();
  if (LANGUAGE_NAMES[key]) return LANGUAGE_NAMES[key];
  // Composite codes the detector emits for code-switched speech.
  const parts = key.split(/[-+]/).filter(Boolean);
  if (parts.length > 1) {
    return parts.map((p) => LANGUAGE_NAMES[p] ?? p.toUpperCase()).join(" + ");
  }
  return key.toUpperCase();
}

interface ChainProps {
  transcript?: string | null;
  result?: VoiceInterpretation | null;
  /** True while the request is still in flight. */
  thinking?: boolean;
}

export function UnderstandingChain({ transcript, result, thinking }: ChainProps) {
  if (!transcript && !result) return null;

  const heard = transcript || result?.transcript || "";
  const language = result?.detected_language;
  const eventMeta = result?.event_type ? EVENT_META[result.event_type] : null;

  return (
    <div className="space-y-2.5">
      {heard && (
        <ChainRow index={1} label="Heard">
          <p className="text-[15px] leading-relaxed text-warm-50">&ldquo;{heard}&rdquo;</p>
        </ChainRow>
      )}

      {language && (
        <ChainRow index={2} label="Language">
          <span className="inline-flex items-center gap-2">
            <span className="rounded-full border border-aria-500/25 bg-aria-500/10 px-2.5 py-1 text-xs font-semibold text-aria-400">
              {languageLabel(language)}
            </span>
            {result?.normalized_text && result.normalized_text !== heard && (
              <span className="text-xs text-ink-400">understood as meaning, not translated</span>
            )}
          </span>
        </ChainRow>
      )}

      {thinking && !result && (
        <ChainRow index={3} label="Understanding">
          <span className="flex items-center gap-2 text-sm text-ink-400">
            <span className="h-3.5 w-3.5 animate-sweep rounded-full border-2 border-transparent border-t-aria-500" />
            Working out the business action…
          </span>
        </ChainRow>
      )}

      {result?.event_type && (
        <ChainRow index={3} label="Business action">
          <div className="flex flex-wrap items-center gap-2">
            <span className="rounded-lg border border-aria-500/25 bg-aria-500/10 px-2.5 py-1 text-[10.5px] font-bold uppercase tracking-wide text-aria-400">
              {eventMeta?.label ?? result.event_type}
            </span>
            {result.product_name && (
              <span className="rounded-lg border border-ink-850 bg-ink-900 px-2.5 py-1 text-xs font-semibold text-warm-50">
                {result.product_name}
              </span>
            )}
            {result.quantity != null && (
              <span className="rounded-lg border border-ink-850 bg-ink-900 px-2.5 py-1 text-xs font-semibold tabular-nums text-warm-50">
                {result.quantity}
                {result.unit ? ` ${result.unit}` : ""}
              </span>
            )}
            {result.customer_name && (
              <span className="rounded-lg border border-ink-850 bg-ink-900 px-2.5 py-1 text-xs text-ink-300">
                for {result.customer_name}
              </span>
            )}
          </div>
        </ChainRow>
      )}

      {result?.confidence != null && (
        <ChainRow index={4} label="Confidence">
          <ConfidenceMeter value={result.confidence} status={result.status} />
        </ChainRow>
      )}
    </div>
  );
}

function ChainRow({
  index,
  label,
  children,
}: {
  index: number;
  label: string;
  children: React.ReactNode;
}) {
  return (
    <div className="animate-slide-up rounded-xl border border-ink-850 bg-ink-950 px-4 py-3 shadow-soft">
      <div className="flex items-start gap-3">
        <span className="mt-0.5 grid h-5 w-5 shrink-0 place-items-center rounded-full border border-aria-500/25 text-[10px] font-bold tabular-nums text-aria-400">
          {index}
        </span>
        <div className="min-w-0 flex-1">
          <p className="eyebrow">{label}</p>
          <div className="mt-1.5">{children}</div>
        </div>
      </div>
    </div>
  );
}

/**
 * Confidence is shown against the thresholds that actually govern execution,
 * so the number the owner sees is the number the system acted on.
 */
function ConfidenceMeter({ value, status }: { value: number; status?: string }) {
  const pct = Math.round(value * 100);
  const tone =
    status === "recorded" || status === "amended"
      ? { bar: "bg-aria-500", text: "text-aria-400", note: "High enough to record straight away" }
      : status === "needs_confirmation"
        ? { bar: "bg-amber-500", text: "text-amber-300", note: "Enough to propose, not to record" }
        : { bar: "bg-red-500", text: "text-red-300", note: "Too low to act on — I need to ask" };

  return (
    <div>
      <div className="flex items-baseline justify-between">
        <span className={`text-sm font-semibold tabular-nums ${tone.text}`}>{pct}%</span>
        <span className="text-[11px] text-ink-500">{tone.note}</span>
      </div>
      <div className="mt-1.5 h-1.5 overflow-hidden rounded-full bg-ink-900">
        <div className={`h-full rounded-full ${tone.bar} transition-all duration-500`} style={{ width: `${pct}%` }} />
      </div>
    </div>
  );
}
