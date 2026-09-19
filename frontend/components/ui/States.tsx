"use client";

import type { ReactNode } from "react";
import { Button } from "./Primitives";

export function LoadingRows({ count = 4 }: { count?: number }) {
  return (
    <div className="space-y-3" aria-busy="true" aria-label="Loading">
      {Array.from({ length: count }).map((_, i) => (
        <div
          key={i}
          className="panel p-5"
          // Staggered so the page fills in rather than flashing as one block.
          style={{ animationDelay: `${i * 70}ms` }}
        >
          <div className="skeleton h-3 w-1/4" />
          <div className="skeleton mt-3.5 h-7 w-1/3" />
          <div className="skeleton mt-3 h-2.5 w-2/5" />
        </div>
      ))}
    </div>
  );
}

/**
 * Empty is not an error. These read as A.R.I.A. saying the shelf is simply
 * still quiet, and point at the one thing that would fill it.
 */
export function EmptyState({
  title,
  description,
  action,
}: {
  title: string;
  description: string;
  action?: ReactNode;
}) {
  return (
    <div className="panel px-6 py-16 text-center">
      <div className="relative mx-auto grid h-14 w-14 place-items-center">
        <span className="absolute inset-0 rounded-full bg-aria-500/10 blur-lg" />
        <span className="relative grid h-14 w-14 place-items-center rounded-2xl border border-aria-500/25 bg-aria-500/[0.06]">
          <svg
            viewBox="0 0 24 24"
            className="h-6 w-6 fill-none stroke-aria-500"
            strokeWidth={1.6}
            strokeLinecap="round"
            strokeLinejoin="round"
            aria-hidden
          >
            <path d="M12 14a3 3 0 0 0 3-3V5a3 3 0 0 0-6 0v6a3 3 0 0 0 3 3z" />
            <path d="M18.5 11a6.5 6.5 0 0 1-13 0M12 17.5V21" />
          </svg>
        </span>
      </div>
      <h3 className="mt-5 text-[19px] font-semibold tracking-tight text-warm-50">{title}</h3>
      <p className="mx-auto mt-2 max-w-sm text-sm leading-relaxed text-ink-400">{description}</p>
      {action && <div className="mt-7 flex justify-center">{action}</div>}
    </div>
  );
}

/**
 * Failures say plainly that nothing was saved.
 * Silence after a failed write is how a user ends up trusting a number that
 * was never recorded.
 */
export function ErrorState({
  message,
  onRetry,
  title = "Something went wrong",
}: {
  message: string;
  onRetry?: () => void;
  title?: string;
}) {
  return (
    <div className="rounded-2xl border border-red-500/25 bg-red-950 px-6 py-10 text-center">
      <div className="mx-auto grid h-12 w-12 place-items-center rounded-2xl border border-red-500/30 bg-red-500/10 text-lg font-bold text-red-300">
        !
      </div>
      <h3 className="mt-4 text-base font-semibold text-warm-50">{title}</h3>
      <p className="mx-auto mt-1.5 max-w-sm text-sm leading-relaxed text-ink-300">{message}</p>
      {onRetry && (
        <div className="mt-6 flex justify-center">
          <Button variant="secondary" onClick={onRetry}>
            Try again
          </Button>
        </div>
      )}
    </div>
  );
}

export function Toast({
  message,
  tone = "success",
}: {
  message: string;
  tone?: "success" | "error";
}) {
  return (
    <div
      role="status"
      className="pointer-events-none fixed inset-x-0 bottom-28 z-50 flex justify-center px-4 lg:bottom-8"
    >
      <div
        className={`animate-slide-up flex items-center gap-2.5 rounded-xl border px-5 py-3.5 text-sm font-medium shadow-panel ${
          tone === "success"
            ? "border-aria-500/25 bg-ink-950 text-warm-50"
            : "border-red-500/30 bg-red-950 text-red-300"
        }`}
      >
        <span
          className={`grid h-5 w-5 shrink-0 place-items-center rounded-full text-[11px] font-bold ${
            tone === "success" ? "bg-aria-500/15 text-aria-400" : "bg-red-500/15 text-red-300"
          }`}
        >
          {tone === "success" ? "✓" : "!"}
        </span>
        {message}
      </div>
    </div>
  );
}

/**
 * The confirmation A.R.I.A. shows after it has actually done something.
 *
 * Every value here is passed in from a real result — the component renders
 * what happened, it never invents or assumes an outcome.
 */
export function ActionCard({
  title,
  subject,
  change,
  note,
  tone = "success",
}: {
  title: string;
  subject?: string | null;
  change?: string | null;
  note?: string | null;
  tone?: "success" | "pending" | "error";
}) {
  const skin = {
    success: {
      frame: "border-aria-500/25 bg-aria-950",
      rail: "bg-aria-500",
      badge: "bg-aria-500/15 text-aria-400",
      glyph: "✓",
      label: "text-aria-400",
    },
    pending: {
      frame: "border-amber-500/25 bg-amber-950",
      rail: "bg-amber-500",
      badge: "bg-amber-500/15 text-amber-300",
      glyph: "?",
      label: "text-amber-300",
    },
    error: {
      frame: "border-red-500/25 bg-red-950",
      rail: "bg-red-500",
      badge: "bg-red-500/15 text-red-300",
      glyph: "!",
      label: "text-red-300",
    },
  }[tone];

  return (
    <div
      className={`animate-slide-up relative overflow-hidden rounded-2xl border px-5 py-4 shadow-soft ${skin.frame}`}
    >
      <span className={`absolute inset-y-0 left-0 w-[3px] ${skin.rail}`} />
      <div className="flex items-center gap-2.5">
        <span
          className={`grid h-5 w-5 shrink-0 place-items-center rounded-full text-[11px] font-bold ${skin.badge}`}
        >
          {skin.glyph}
        </span>
        <p
          className={`text-[11px] font-semibold uppercase tracking-[0.1em] ${skin.label}`}
        >
          {title}
        </p>
      </div>

      {(subject || change) && (
        <div className="mt-3 flex items-baseline justify-between gap-4">
          {subject && (
            <p className="min-w-0 truncate text-[17px] font-semibold tracking-tight text-warm-50">
              {subject}
            </p>
          )}
          {change && (
            <p className="shrink-0 font-display text-[17px] font-semibold tabular-nums text-warm-50">
              {change}
            </p>
          )}
        </div>
      )}

      {note && <p className="mt-2 text-[13px] leading-relaxed text-ink-400">{note}</p>}
    </div>
  );
}
