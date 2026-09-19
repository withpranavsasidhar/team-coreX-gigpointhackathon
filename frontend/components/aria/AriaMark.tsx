"use client";

import { useEffect, useId, useState } from "react";

/**
 * The A.R.I.A. mark.
 *
 * A warm companion on a rose-red disc: a soft white form, two calm eyes, and
 * two red listening pills where ears would be — the product is a voice
 * assistant, so the mark listens. Drawn rather than illustrated so it stays
 * legible at 20px in the rail and at 96px on the sign-in screen.
 *
 * If a bitmap logo is dropped at `public/aria-logo.png`, every mark in the
 * app uses it instead. The probe runs once per page load and is shared by all
 * instances, so a missing file costs one 404 and never blocks a render.
 *
 * The gradient ids are per-instance. The shell renders this mark more than
 * once and all but one copy is `display:none` at any width — a shared id
 * resolves to whichever definition comes first in the document, and a
 * definition inside a hidden subtree paints as nothing, so the visible copy
 * would silently lose its colour. Scoping the ids keeps each self-contained.
 */

const LOGO_FILE = "/aria-logo.png";

let probe: Promise<boolean> | null = null;

function hasCustomLogo(): Promise<boolean> {
  if (typeof window === "undefined") return Promise.resolve(false);
  probe ??= new Promise<boolean>((resolve) => {
    const img = new window.Image();
    img.onload = () => resolve(img.naturalWidth > 0);
    img.onerror = () => resolve(false);
    img.src = LOGO_FILE;
  });
  return probe;
}

export function AriaMark({ className }: { className?: string }) {
  const uid = useId().replace(/:/g, "");
  const [custom, setCustom] = useState(false);

  useEffect(() => {
    let live = true;
    void hasCustomLogo().then((ok) => live && setCustom(ok));
    return () => {
      live = false;
    };
  }, []);

  if (custom) {
    // eslint-disable-next-line @next/next/no-img-element
    return <img src={LOGO_FILE} alt="" aria-hidden className={`${className} object-contain`} />;
  }

  const disc = `aria-disc-${uid}`;
  const shell = `aria-shell-${uid}`;
  const glow = `aria-glow-${uid}`;

  return (
    <svg viewBox="0 0 32 32" width="32" height="32" className={className} aria-hidden>
      <defs>
        <linearGradient id={disc} x1="0.15" y1="0" x2="0.85" y2="1">
          <stop offset="0%" stopColor="#E43B4A" />
          <stop offset="55%" stopColor="#C92332" />
          <stop offset="100%" stopColor="#8E1220" />
        </linearGradient>
        <linearGradient id={shell} x1="0.3" y1="0" x2="0.7" y2="1">
          <stop offset="0%" stopColor="#FFFFFF" />
          <stop offset="100%" stopColor="#F6E9EA" />
        </linearGradient>
        <radialGradient id={glow} cx="50%" cy="50%" r="50%">
          <stop offset="60%" stopColor="#C92332" stopOpacity="0.28" />
          <stop offset="100%" stopColor="#C92332" stopOpacity="0" />
        </radialGradient>
      </defs>

      {/* Warm light around the mark. */}
      <circle cx="16" cy="16" r="16" fill={`url(#${glow})`} />

      {/* The red disc — the brand's anchor. */}
      <circle cx="16" cy="16" r="14.2" fill={`url(#${disc})`} />

      {/* Listening pills, where ears would be. */}
      <rect x="3.4" y="12.6" width="3.2" height="6.8" rx="1.6" fill="#FFF3F4" opacity="0.92" />
      <rect x="25.4" y="12.6" width="3.2" height="6.8" rx="1.6" fill="#FFF3F4" opacity="0.92" />

      {/* The companion: a soft, rounded, friendly form. */}
      <rect x="6.6" y="8.2" width="18.8" height="16.4" rx="8.2" fill={`url(#${shell})`} />

      {/* Two calm eyes. */}
      <circle cx="12.2" cy="14.9" r="1.55" fill="#210C10" />
      <circle cx="19.8" cy="14.9" r="1.55" fill="#210C10" />

      {/* A small heart — warmth, and the reason the product exists. */}
      <path
        d="M16 20.9c-1.55-1-2.45-1.69-2.45-2.52a1.23 1.23 0 0 1 2.45-.37 1.23 1.23 0 0 1 2.45.37c0 .83-.9 1.52-2.45 2.52z"
        fill="#C92332"
      />
    </svg>
  );
}

/**
 * The full lockup: mark plus the A.R.I.A. wordmark with its red initials.
 * Used where the brand introduces itself — sign-in, onboarding, the rail.
 */
export function AriaLockup({
  className = "",
  size = "md",
  tagline = true,
}: {
  className?: string;
  size?: "sm" | "md" | "lg";
  tagline?: boolean;
}) {
  const mark = { sm: "h-7 w-7", md: "h-9 w-9", lg: "h-14 w-14" }[size];
  const word = { sm: "text-sm", md: "text-base", lg: "text-2xl" }[size];
  const tag = { sm: "text-[10px]", md: "text-[11px]", lg: "text-xs" }[size];

  return (
    <div className={`flex items-center gap-2.5 ${className}`}>
      <AriaMark className={mark} />
      <div className="min-w-0">
        <p className={`font-display font-bold leading-none tracking-tight text-warm-50 ${word}`}>
          A.R.I.A.
        </p>
        {tagline && (
          <p className={`mt-1 truncate leading-none text-ink-500 ${tag}`}>
            <span className="font-semibold text-aria-400">A</span>daptive{" "}
            <span className="font-semibold text-aria-400">R</span>etail{" "}
            <span className="font-semibold text-aria-400">I</span>ntelligence{" "}
            <span className="font-semibold text-aria-400">A</span>ssistant
          </p>
        )}
      </div>
    </div>
  );
}
