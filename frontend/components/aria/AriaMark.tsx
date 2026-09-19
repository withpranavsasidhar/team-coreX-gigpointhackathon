"use client";

import { useEffect, useId, useState } from "react";

/**
 * The A.R.I.A. mark.
 *
 * A full-body companion on the brand's red disc: a rounded head with a
 * visor-band face (not bare dot-eyes), a blockier torso, one arm raised in
 * a wave, an antenna (it listens), and a soundwave badge on its chest (it
 * talks back). Drawn rather than illustrated so it stays legible at 20px in
 * the rail and at 96px on the sign-in screen.
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
  const body = `aria-body-${uid}`;
  const visor = `aria-visor-${uid}`;

  return (
    <svg viewBox="0 0 64 64" width="32" height="32" className={className} aria-hidden>
      <defs>
        <radialGradient id={disc} cx="50%" cy="42%" r="65%">
          <stop offset="0%" stopColor="#E43B4A" />
          <stop offset="60%" stopColor="#C92332" />
          <stop offset="100%" stopColor="#7F0F1C" />
        </radialGradient>
        <linearGradient id={body} x1="0.2" y1="0" x2="0.8" y2="1">
          <stop offset="0%" stopColor="#FFFFFF" />
          <stop offset="100%" stopColor="#F1E1E2" />
        </linearGradient>
        <linearGradient id={visor} x1="0" y1="0" x2="1" y2="0">
          <stop offset="0%" stopColor="#A9142A" />
          <stop offset="100%" stopColor="#E43B4A" />
        </linearGradient>
      </defs>

      {/* The brand disc. */}
      <circle cx="32" cy="32" r="30" fill={`url(#${disc})`} />

      {/* Feet, then the lowered arm, so the torso overlaps them cleanly. */}
      <ellipse cx="25.5" cy="54" rx="4.6" ry="2.6" fill={`url(#${body})`} />
      <ellipse cx="37.5" cy="54" rx="4.6" ry="2.6" fill={`url(#${body})`} />
      <path d="M42.5 35C47.5 36.5 49 41 47.5 45.5" fill="none" stroke={`url(#${body})`} strokeWidth="6" strokeLinecap="round" />
      <circle cx="46.6" cy="46.4" r="3.6" fill={`url(#${body})`} />

      {/* Torso. */}
      <rect x="18" y="28" width="28" height="24" rx="12" fill={`url(#${body})`} />

      {/* Raised, waving arm. */}
      <path d="M21 33C15 31.5 12 27 13 22" fill="none" stroke={`url(#${body})`} strokeWidth="6" strokeLinecap="round" />
      <circle cx="12.6" cy="20" r="4" fill={`url(#${body})`} />

      {/* Head. */}
      <circle cx="32" cy="18.5" r="11.6" fill={`url(#${body})`} />

      {/* A signal antenna — it's listening. */}
      <line x1="32" y1="7" x2="32" y2="3" stroke="#C92332" strokeWidth="1.6" strokeLinecap="round" />
      <circle cx="32" cy="2.8" r="1.8" fill="#E43B4A" />

      {/* A visor face band, not bare eyes on skin. */}
      <rect x="23" y="15.4" width="18" height="6.8" rx="3.4" fill={`url(#${visor})`} />
      <circle cx="27.8" cy="18.8" r="1.7" fill="#FFF3F4" />
      <circle cx="36.2" cy="18.8" r="1.7" fill="#FFF3F4" />

      {/* A soundwave badge — it talks back. */}
      <rect x="26.8" y="35" width="10.4" height="6.8" rx="3.4" fill={`url(#${visor})`} />
      <g stroke="#FFF3F4" strokeWidth="1.2" strokeLinecap="round">
        <line x1="29.8" y1="37" x2="29.8" y2="39.8" />
        <line x1="32" y1="35.9" x2="32" y2="40.9" />
        <line x1="34.2" y1="37" x2="34.2" y2="39.8" />
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
