"use client";

import Link from "next/link";
import type { ReactNode } from "react";

type ButtonVariant = "primary" | "secondary" | "ghost" | "danger";

// Rose red is the assistant's colour and is reserved for its actions. A screen
// with three red buttons on it has told the owner nothing about which matters.
const VARIANTS: Record<ButtonVariant, string> = {
  primary:
    "bg-aria-600 text-white shadow-soft hover:bg-aria-700 hover:shadow-lift active:bg-aria-700",
  secondary:
    "border border-ink-850 bg-ink-950 text-warm-50 hover:border-aria-500/30 hover:bg-aria-500/[0.05]",
  ghost: "text-aria-400 hover:bg-aria-500/10",
  danger: "border border-red-500/30 bg-red-950 text-red-300 hover:border-red-500/50",
};

const BASE =
  "focus-ring press inline-flex min-h-[44px] items-center justify-center gap-2 rounded-[10px] px-5 text-[15px] font-semibold tracking-[-0.01em] disabled:cursor-not-allowed disabled:opacity-50 disabled:hover:translate-y-0";

export function Button({
  children,
  variant = "primary",
  className = "",
  type = "button",
  disabled,
  onClick,
  fullWidth,
}: {
  children: ReactNode;
  variant?: ButtonVariant;
  className?: string;
  type?: "button" | "submit";
  disabled?: boolean;
  onClick?: () => void;
  fullWidth?: boolean;
}) {
  return (
    <button
      type={type}
      onClick={onClick}
      disabled={disabled}
      className={`${BASE} ${VARIANTS[variant]} ${fullWidth ? "w-full" : ""} ${className}`}
    >
      {children}
    </button>
  );
}

export function LinkButton({
  href,
  children,
  variant = "primary",
  fullWidth,
}: {
  href: string;
  children: ReactNode;
  variant?: ButtonVariant;
  fullWidth?: boolean;
}) {
  return (
    <Link
      href={href}
      className={`${BASE} ${VARIANTS[variant]} ${fullWidth ? "w-full" : ""}`}
    >
      {children}
    </Link>
  );
}

// Background lives on a `tone` prop rather than a base class, because a
// background passed through className cannot reliably override one baked in —
// Tailwind resolves conflicts by stylesheet order, not prop order.
const CARD_TONES = {
  dark: "border-ink-850 bg-ink-950 shadow-soft",
  raised: "border-ink-850 bg-ink-900",
  light: "border-ink-850 bg-ink-950 shadow-soft",
} as const;

export function Card({
  children,
  className = "",
  tone = "dark",
  as = "div",
}: {
  children: ReactNode;
  className?: string;
  tone?: keyof typeof CARD_TONES;
  as?: "div" | "section";
}) {
  const Tag = as;
  return <Tag className={`rounded-2xl border ${CARD_TONES[tone]} ${className}`}>{children}</Tag>;
}

export function SectionLabel({ children, action }: { children: ReactNode; action?: ReactNode }) {
  return (
    <div className="flex items-baseline justify-between gap-3">
      <p className="eyebrow">{children}</p>
      {action}
    </div>
  );
}

export function PageHeader({
  title,
  subtitle,
  action,
}: {
  title: string;
  subtitle?: string;
  action?: ReactNode;
}) {
  return (
    <header className="flex flex-wrap items-end justify-between gap-4">
      <div>
        <h1 className="text-[30px] font-semibold leading-[1.12] tracking-tight text-warm-50">
          {title}
        </h1>
        {subtitle && <p className="mt-1.5 text-[14px] text-ink-400">{subtitle}</p>}
      </div>
      {action}
    </header>
  );
}

export function Field({
  label,
  hint,
  children,
}: {
  label: string;
  hint?: string;
  children: ReactNode;
}) {
  return (
    <label className="block">
      <span className="mb-1.5 block text-[13px] font-semibold text-ink-300">{label}</span>
      {children}
      {hint && <span className="mt-1.5 block text-xs text-ink-500">{hint}</span>}
    </label>
  );
}

export const inputClass =
  "w-full rounded-[10px] border border-ink-850 bg-ink-950 px-4 py-3 text-[15px] text-warm-50 outline-none transition-all duration-150 placeholder:text-ink-500 focus:border-aria-500/40 focus:ring-4 focus:ring-aria-500/10";

export const selectClass = inputClass;

/**
 * A labelled statistic. Numbers carry the weight here — large, tabular, and
 * the first thing read — with the label small and quiet above them.
 */
export function Stat({
  label,
  value,
  unit,
  tone = "neutral",
  hint,
}: {
  label: string;
  value: string | number;
  unit?: string;
  tone?: "neutral" | "good" | "warn" | "bad";
  hint?: string;
}) {
  const color = {
    neutral: "text-warm-50",
    good: "text-warm-50",
    warn: "text-amber-300",
    bad: "text-red-300",
  }[tone];

  return (
    <div className="group relative overflow-hidden rounded-2xl border border-ink-850 bg-ink-950 px-4 py-4 shadow-soft transition-all duration-200 hover:border-aria-500/25">
      <p className="text-[10.5px] font-semibold uppercase tracking-[0.1em] text-ink-500">{label}</p>
      <p
        className={`mt-2 font-display text-[28px] font-semibold leading-none tracking-tight tabular-nums ${color}`}
      >
        {value}
        {unit && <span className="ml-1 text-sm font-normal text-ink-500">{unit}</span>}
      </p>
      {hint && <p className="mt-2 text-[11px] leading-relaxed text-ink-500">{hint}</p>}
    </div>
  );
}

/**
 * Marks content as estimated rather than recorded.
 * Predictions must never look like facts, so anything derived carries this.
 */
export function EstimateTag({ children = "Estimate" }: { children?: ReactNode }) {
  return (
    <span className="rounded-md border border-ink-850 bg-ink-900 px-1.5 py-0.5 text-[10px] font-semibold uppercase tracking-wide text-ink-500">
      {children}
    </span>
  );
}
