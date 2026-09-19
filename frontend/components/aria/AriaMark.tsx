"use client";

import { useEffect, useId, useState } from "react";

/**
 * The A.R.I.A. mark.
 *
 * A single warm companion silhouette — no separate head/torso, no ear
 * pieces — topped with a small signal antenna (it listens) and a soundwave
 * badge on its chest (it talks back). Drawn rather than illustrated so it
 * stays legible at 20px in the rail and at 96px on the sign-in screen.
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

  const glow = `aria-glow-${uid}`;
  const body = `aria-body-${uid}`;
  const badge = `aria-badge-${uid}`;

  return (
    <svg viewBox="0 0 32 32" width="32" height="32" className={className} aria-hidden>
      <defs>
        <radialGradient id={glow} cx="50%" cy="55%" r="55%">
          <stop offset="0%" stopColor="#C92332" stopOpacity="0.3" />
          <stop offset="100%" stopColor="#C92332" stopOpacity="0" />
        </radialGradient>
        <linearGradient id={body} x1="0.2" y1="0" x2="0.8" y2="1">
          <stop offset="0%" stopColor="#FFFFFF" />
          <stop offset="100%" stopColor="#F3E4E5" />
        </linearGradient>
        <linearGradient id={badge} x1="0.15" y1="0" x2="0.85" y2="1">
          <stop offset="0%" stopColor="#E43B4A" />
          <stop offset="100%" stopColor="#A9142A" />
        </linearGradient>
      </defs>

      {/* Warm light around the mark. */}
      <circle cx="16" cy="17" r="13.5" fill={`url(#${glow})`} />

      {/* One continuous companion silhouette — no separate head/torso. */}
      <path
        d="M16 2.6C22 2.6 25.6 7.8 26 13.2C26.4 19 24.2 24.6 19.6 28.2C17 30.2 15 30.2 12.4 28.2C7.8 24.6 5.6 19 6 13.2C6.4 7.8 10 2.6 16 2.6Z"
        fill={`url(#${body})`}
      />

      {/* A signal antenna — it's listening. */}
      <line x1="16" y1="2.8" x2="16" y2="0.2" stroke="#C92332" strokeWidth="1.1" strokeLinecap="round" />
      <circle cx="16" cy="0.2" r="1.1" fill="#E43B4A" />
      <circle cx="16" cy="0.2" r="1.95" fill="none" stroke="#E43B4A" strokeOpacity="0.4" strokeWidth="0.5" />

      {/* Calm eyes and a warm smile. */}
      <rect x="11.6" y="11.2" width="2.5" height="3.1" rx="1.25" fill="#200C10" />
      <rect x="17.9" y="11.2" width="2.5" height="3.1" rx="1.25" fill="#200C10" />
      <path d="M13.6 16.8Q16 18.5 18.4 16.8" stroke="#200C10" strokeWidth="1" strokeLinecap="round" fill="none" />

      {/* A soundwave badge — it talks back. */}
      <rect x="11.8" y="21.2" width="8.4" height="5.4" rx="2.7" fill={`url(#${badge})`} />
      <g stroke="#FFF3F4" strokeWidth="1.05" strokeLinecap="round">
        <line x1="14" y1="22.6" x2="14" y2="25.2" />
        <line x1="16" y1="21.9" x2="16" y2="25.9" />
        <line x1="18" y1="22.6" x2="18" y2="25.2" />
      </g>
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
