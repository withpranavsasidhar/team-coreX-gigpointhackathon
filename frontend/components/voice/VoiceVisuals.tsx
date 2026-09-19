"use client";

export function MicButton({
  listening,
  processing,
  onClick,
  disabled,
}: {
  listening: boolean;
  processing: boolean;
  onClick: () => void;
  disabled?: boolean;
}) {
  return (
    <button
      onClick={onClick}
      disabled={disabled || processing}
      aria-label={listening ? "Stop recording" : "Start recording"}
      className={`focus-ring relative flex h-24 w-24 items-center justify-center rounded-full transition-all duration-200 disabled:opacity-60 ${
        listening
          ? "animate-voice-pulse bg-aria-600 shadow-voice-lg"
          : "bg-aria-600 shadow-voice hover:scale-105 active:scale-100"
      }`}
    >
      {processing ? (
        <span className="h-7 w-7 animate-spin rounded-full border-[3px] border-white/40 border-t-white" />
      ) : (
        <svg viewBox="0 0 24 24" className="h-9 w-9 fill-white" aria-hidden>
          <path d="M12 14a3 3 0 0 0 3-3V5a3 3 0 0 0-6 0v6a3 3 0 0 0 3 3z" />
          <path d="M17 11a5 5 0 0 1-10 0H5a7 7 0 0 0 6 6.92V21h2v-3.08A7 7 0 0 0 19 11h-2z" />
        </svg>
      )}
    </button>
  );
}

export function Waveform({ levels, active }: { levels: number[]; active: boolean }) {
  return (
    <div className="flex h-14 items-center justify-center gap-[3px]" aria-hidden>
      {levels.map((level, i) => (
        <span
          key={i}
          className={`w-[3px] rounded-full transition-all duration-75 ${
            active ? "bg-aria-500" : "bg-ink-850"
          }`}
          style={{ height: `${Math.max(level * 100, 8)}%` }}
        />
      ))}
    </div>
  );
}

export function ConfidenceMeter({ score }: { score: number }) {
  const pct = Math.round(score * 100);
  const filled = Math.max(1, Math.round(score * 5));
  const tone = score >= 0.75 ? "bg-aria-500" : score >= 0.5 ? "bg-amber-500" : "bg-red-500";
  const label = score >= 0.75 ? "High confidence" : score >= 0.5 ? "Needs a check" : "Unsure";

  return (
    <div className="flex items-center gap-2.5">
      <div className="flex gap-1" aria-hidden>
        {Array.from({ length: 5 }).map((_, i) => (
          <span key={i} className={`h-1.5 w-1.5 rounded-full ${i < filled ? tone : "bg-ink-850"}`} />
        ))}
      </div>
      <span className="text-xs text-ink-400">
        {label} · {pct}%
      </span>
    </div>
  );
}
