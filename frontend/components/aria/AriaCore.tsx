"use client";

import { useEffect, useMemo, useState } from "react";

/**
 * The A.R.I.A. Voice Core — the product's visual identity.
 *
 * This is not a microphone button with decoration around it. The core is a
 * readout of the assistant's actual state: the ring reacts to real microphone
 * energy, the rings only ripple while audio is genuinely arriving, and each
 * phase of the pipeline has a distinct appearance so the owner can see where
 * their sentence has got to.
 *
 * Every state below corresponds to something the system is really doing. There
 * is no state that plays a pleasing animation while nothing happens.
 *
 * Visually: a clean central surface inside a soft rose aura. Red here always
 * means A.R.I.A. is engaged — amber means it needs the owner, and the danger
 * red of a failure is deeper and flatter, never glowing.
 */
export type CoreState =
  | "idle"
  | "listening"
  | "transcribing"
  | "understanding"
  | "confirming"
  | "acting"
  | "success"
  | "error"
  | "denied"
  | "unsupported";

const STATE_COPY: Record<CoreState, { label: string; hint: string }> = {
  idle: { label: "Talk to A.R.I.A.", hint: "Tell me what happened" },
  listening: { label: "I'm listening", hint: "Speak naturally — any language" },
  transcribing: { label: "Transcribing", hint: "Writing down what you said" },
  understanding: { label: "Understanding", hint: "Working out the business action" },
  confirming: { label: "Needs your confirmation", hint: "Check this before I record it" },
  acting: { label: "Taking care of it", hint: "Writing to your business memory" },
  success: { label: "Done.", hint: "Your business remembers this" },
  error: { label: "Something went wrong", hint: "Nothing was saved" },
  denied: { label: "Microphone blocked", hint: "Allow access, or type instead" },
  unsupported: { label: "Voice unavailable here", hint: "This browser has no speech recognition" },
};

// Rose red means the assistant is working. Amber means it needs the owner.
// Deep red means it failed and, critically, that nothing was written.
const STATE_AURA: Record<CoreState, string> = {
  idle: "bg-aria-500/15",
  listening: "bg-aria-500/30",
  transcribing: "bg-aria-500/26",
  understanding: "bg-aria-500/26",
  confirming: "bg-amber-500/25",
  acting: "bg-aria-500/32",
  success: "bg-aria-500/28",
  error: "bg-red-500/22",
  denied: "bg-red-500/18",
  unsupported: "bg-ink-500/15",
};

const ACTIVE: CoreState[] = ["listening", "transcribing", "understanding", "acting"];

interface AriaCoreProps {
  state: CoreState;
  /** Real microphone energy, 0..1 per band, straight from the AnalyserNode. */
  levels?: number[];
  language?: string | null;
  confidence?: number | null;
  size?: "sm" | "md" | "lg";
  onActivate?: () => void;
  disabled?: boolean;
  /** Off in compact surfaces where the surrounding UI already says the state. */
  showLabel?: boolean;
  /**
   * Overrides the default state copy. Needed where a state means something
   * different from recording — onboarding's "success" is a recognised trade,
   * not a saved business event, and must not claim otherwise.
   */
  labelOverride?: { label: string; hint: string };
}

const SIZES = {
  sm: { box: "h-24 w-24", inner: "h-16 w-16", icon: "h-6 w-6", bar: 2 },
  md: { box: "h-40 w-40", inner: "h-28 w-28", icon: "h-9 w-9", bar: 3 },
  lg: { box: "h-56 w-56", inner: "h-40 w-40", icon: "h-12 w-12", bar: 4 },
};

// Three specks, placed once. Deliberately few — ambience, not confetti.
const MOTES = [
  { top: "8%", left: "16%", delay: "0s" },
  { top: "72%", left: "8%", delay: "2.1s" },
  { top: "22%", left: "86%", delay: "4.2s" },
];

export function AriaCore({
  state,
  levels,
  language,
  confidence,
  size = "lg",
  onActivate,
  disabled = false,
  showLabel = true,
  labelOverride,
}: AriaCoreProps) {
  const dims = SIZES[size];
  const copy = labelOverride ?? STATE_COPY[state];
  const isActive = ACTIVE.includes(state);
  const hearing = state === "listening" && !!levels?.length;
  const failed = state === "error" || state === "denied";

  // Average energy drives the core's scale, so a loud voice visibly moves it.
  const energy = useMemo(() => {
    if (!levels?.length) return 0;
    return levels.reduce((sum, v) => sum + v, 0) / levels.length;
  }, [levels]);

  return (
    <div className="flex flex-col items-center gap-5">
      <button
        type="button"
        onClick={onActivate}
        disabled={disabled || !onActivate}
        aria-label={copy.label}
        aria-live="polite"
        className={`group relative grid ${dims.box} place-items-center rounded-full outline-none transition-transform duration-300 focus-visible:ring-2 focus-visible:ring-aria-500 focus-visible:ring-offset-4 focus-visible:ring-offset-ink-990 ${
          onActivate && !disabled ? "cursor-pointer hover:scale-[1.03]" : "cursor-default"
        }`}
        style={{ transform: hearing ? `scale(${1 + energy * 0.06})` : undefined }}
      >
        {/* Ambient motes — only while A.R.I.A. is actually engaged. */}
        {isActive &&
          size !== "sm" &&
          MOTES.map((m, i) => (
            <span
              key={i}
              className="pointer-events-none absolute h-1 w-1 animate-float-slow rounded-full bg-aria-500"
              style={{ top: m.top, left: m.left, animationDelay: m.delay }}
            />
          ))}

        {/* Radial rings — only while audio is genuinely arriving. */}
        {hearing && (
          <>
            <span className="pointer-events-none absolute inset-0 animate-ripple rounded-full border border-aria-500/35" />
            <span
              className="pointer-events-none absolute inset-0 animate-ripple rounded-full border border-aria-500/25"
              style={{ animationDelay: "0.9s" }}
            />
          </>
        )}

        {/* The rose aura: warm lighting behind the core, never a gradient slab. */}
        <span
          className={`pointer-events-none absolute -inset-2 rounded-full blur-2xl transition-colors duration-500 ${STATE_AURA[state]} ${
            state === "idle" ? "animate-breathe" : ""
          }`}
        />

        {/* A thin held ring, so the core has an edge even at rest. */}
        <span
          className={`pointer-events-none absolute inset-0 rounded-full border transition-colors duration-500 ${
            failed
              ? "border-red-500/30"
              : state === "confirming"
                ? "border-amber-500/30"
                : "border-aria-500/25"
          }`}
        />

        {/* The thinking sweep: consideration, not a loading spinner. */}
        {(state === "understanding" || state === "acting" || state === "transcribing") && (
          <span className="pointer-events-none absolute inset-1 animate-sweep rounded-full border-2 border-transparent border-t-aria-500 border-r-aria-500/25" />
        )}

        {/* Core body — a clean lit surface at the centre of the aura. */}
        <span
          className={`relative grid ${dims.inner} place-items-center rounded-full border shadow-lift transition-colors duration-500 ${
            failed
              ? "border-red-500/30 bg-red-950"
              : state === "confirming"
                ? "border-amber-500/30 bg-amber-950"
                : "border-ink-850 bg-gradient-to-b from-ink-900 to-ink-950"
          }`}
        >
          {hearing ? (
            <WaveForm levels={levels!} barWidth={dims.bar} />
          ) : state === "success" ? (
            <svg
              viewBox="0 0 24 24"
              className={`${dims.icon} animate-scale-in fill-none stroke-aria-500`}
              strokeWidth={2.5}
              aria-hidden
            >
              <path d="M4 12.5l5 5L20 6.5" strokeLinecap="round" strokeLinejoin="round" />
            </svg>
          ) : failed || state === "unsupported" ? (
            <svg
              viewBox="0 0 24 24"
              className={`${dims.icon} fill-none stroke-red-400`}
              strokeWidth={2.2}
              aria-hidden
            >
              <path d="M12 8v5M12 16.5v.5" strokeLinecap="round" />
              <circle cx="12" cy="12" r="9" />
            </svg>
          ) : (
            <MicGlyph
              className={`${dims.icon} transition-colors duration-300 ${
                isActive ? "fill-aria-500" : "fill-ink-400 group-hover:fill-aria-500"
              }`}
            />
          )}
        </span>
      </button>

      {showLabel && (
        <div className="min-h-[3.25rem] text-center">
          <p
            className={`font-display text-[15px] font-semibold tracking-tight ${
              failed
                ? "text-red-300"
                : state === "confirming"
                  ? "text-amber-300"
                  : isActive || state === "success"
                    ? "text-aria-400"
                    : "text-warm-50"
            }`}
          >
            {copy.label}
            {(state === "listening" || state === "understanding" || state === "acting") && (
              <AnimatedDots />
            )}
          </p>
          <p className="mt-1 text-[13px] text-ink-500">{copy.hint}</p>

          {(language || confidence !== null) && (
            <div className="mt-2.5 flex items-center justify-center gap-2 text-[11px]">
              {language && (
                <span className="rounded-full border border-aria-500/25 bg-aria-500/10 px-2.5 py-0.5 font-semibold text-aria-400">
                  {language}
                </span>
              )}
              {confidence !== null && confidence !== undefined && (
                <span className="rounded-full border border-ink-850 bg-ink-900 px-2.5 py-0.5 font-medium tabular-nums text-ink-400">
                  {Math.round(confidence * 100)}% confident
                </span>
              )}
            </div>
          )}
        </div>
      )}
    </div>
  );
}

/** Mirrored bars driven by real per-band microphone energy. */
function WaveForm({ levels, barWidth }: { levels: number[]; barWidth: number }) {
  return (
    <span className="flex h-full w-full items-center justify-center gap-[3px] px-4">
      {levels.map((level, i) => (
        <span
          key={i}
          className="rounded-full bg-aria-500 transition-[height] duration-75"
          style={{
            width: barWidth,
            height: `${Math.max(8, level * 100)}%`,
            opacity: 0.55 + level * 0.45,
          }}
        />
      ))}
    </span>
  );
}

function AnimatedDots() {
  const [n, setN] = useState(0);
  useEffect(() => {
    const id = setInterval(() => setN((v) => (v + 1) % 4), 400);
    return () => clearInterval(id);
  }, []);
  return <span className="inline-block w-5 text-left">{".".repeat(n)}</span>;
}

function MicGlyph({ className }: { className?: string }) {
  return (
    <svg viewBox="0 0 24 24" className={className} aria-hidden>
      <path d="M12 14a3 3 0 0 0 3-3V5a3 3 0 0 0-6 0v6a3 3 0 0 0 3 3z" />
      <path d="M17 11a5 5 0 0 1-10 0H5a7 7 0 0 0 6 6.92V21h2v-3.08A7 7 0 0 0 19 11h-2z" />
    </svg>
  );
}
