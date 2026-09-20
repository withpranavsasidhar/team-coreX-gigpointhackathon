import type { Config } from "tailwindcss";

/**
 * A.R.I.A. — WHITE + ROSE RED + BLACK / DARK RED.
 *
 * Every colour below resolves to a CSS custom property declared in
 * app/globals.css, so the same class name renders correctly in both themes and
 * a theme switch is a single attribute flip on <html> rather than a second set
 * of classes on every element.
 *
 * The scales keep their historical names (`ink`, `warm`, `aria`) so no markup
 * had to be rewritten to gain a light mode — only their meaning is now
 * semantic rather than literal:
 *
 *   ink-990 → page          ink-850/800/700 → hairline → strong border
 *   ink-980 → sunk (rail)   ink-600 → faintest text
 *   ink-950 → card          ink-500/400/300/200 → muted → strong body text
 *   ink-900 → raised        warm-50 → primary text (near-black / near-white)
 *
 * `aria` is the brand red. It reads as "the assistant is doing something":
 * voice, confidence, focus, confirmation. Steps 200–400 are accent *text* and
 * therefore darken in light mode and lighten in dark mode; 500–900 are fills
 * and stay recognisably rose-red in both.
 */
const t = (name: string) => `rgb(var(--${name}) / <alpha-value>)`;

const config: Config = {
  // lib/ must be scanned too: the status and event colour maps live in
  // lib/format.ts, and Tailwind only emits classes it sees as literal strings.
  content: ["./app/**/*.{ts,tsx}", "./components/**/*.{ts,tsx}", "./lib/**/*.{ts,tsx}"],
  darkMode: ["class"],
  theme: {
    extend: {
      colors: {
        ink: {
          990: t("c-bg"),
          980: t("c-sunk"),
          950: t("c-surface"),
          900: t("c-raised"),
          850: t("c-line"),
          800: t("c-line-2"),
          700: t("c-line-3"),
          600: t("c-text-faint"),
          500: t("c-text-muted"),
          400: t("c-text-soft"),
          300: t("c-text-body"),
          200: t("c-text-strong"),
          100: t("c-line"),
          50: t("c-raised"),
        },
        warm: {
          50: t("c-text"),
          100: t("c-raised"),
          200: t("c-line-2"),
          300: t("c-text-muted"),
          400: t("c-text-soft"),
        },
        // The assistant's own colour — rose red.
        aria: {
          50: t("c-accent-wash"),
          100: t("c-accent-tint"),
          200: t("c-accent-text-deep"),
          300: t("c-accent-text-strong"),
          400: t("c-accent-text"),
          500: t("c-accent"),
          600: t("c-accent-solid"),
          700: t("c-accent-solid-hover"),
          800: t("c-accent-deep"),
          900: t("c-accent-deepest"),
          950: t("c-accent-surface"),
        },
        // Semantic danger. Deeper and cooler than the brand rose so a failure
        // never reads as ordinary A.R.I.A. activity.
        red: {
          50: t("c-danger-surface"),
          100: t("c-danger-text-deep"),
          200: t("c-danger-text-strong"),
          300: t("c-danger-text"),
          400: t("c-danger-bright"),
          500: t("c-danger"),
          600: t("c-danger-solid"),
          700: t("c-danger-deep"),
          800: t("c-danger-deep"),
          900: t("c-danger-deepest"),
          950: t("c-danger-surface"),
        },
        amber: {
          50: t("c-warn-surface"),
          100: t("c-warn-text-deep"),
          200: t("c-warn-text-strong"),
          300: t("c-warn-text"),
          400: t("c-warn-bright"),
          500: t("c-warn"),
          600: t("c-warn-solid"),
          700: t("c-warn-deep"),
          800: t("c-warn-deep"),
          900: t("c-warn-deepest"),
          950: t("c-warn-surface"),
        },
        // Reserved strictly for semantic success (resolved, healthy, paid).
        // The brand stays red.
        emerald: {
          200: t("c-ok-text-strong"),
          300: t("c-ok-text"),
          400: t("c-ok-bright"),
          500: t("c-ok"),
          600: t("c-ok-solid"),
          700: t("c-ok-deep"),
          950: t("c-ok-surface"),
        },
      },
      fontFamily: {
        sans: ["var(--font-sans)", "ui-sans-serif", "system-ui", "sans-serif"],
        display: ["var(--font-display)", "var(--font-sans)", "ui-sans-serif", "sans-serif"],
      },
      boxShadow: {
        // Light mode keeps shadows whisper-thin; dark mode replaces them with
        // a lit edge, because a drop shadow on near-black is invisible.
        soft: "var(--shadow-soft)",
        lift: "var(--shadow-lift)",
        panel: "var(--shadow-panel)",
        float: "var(--shadow-float)",
        // The only glow in the system, and it means A.R.I.A. is engaged.
        voice: "0 0 40px -6px rgb(var(--c-accent) / 0.35)",
        "voice-lg": "0 0 80px -8px rgb(var(--c-accent) / 0.45)",
      },
      keyframes: {
        "fade-in": { from: { opacity: "0" }, to: { opacity: "1" } },
        "slide-up": {
          from: { opacity: "0", transform: "translateY(10px)" },
          to: { opacity: "1", transform: "translateY(0)" },
        },
        "scale-in": {
          from: { opacity: "0", transform: "scale(0.96)" },
          to: { opacity: "1", transform: "scale(1)" },
        },
        shimmer: {
          "0%": { backgroundPosition: "-200% 0" },
          "100%": { backgroundPosition: "200% 0" },
        },
        "voice-pulse": {
          "0%, 100%": { transform: "scale(1)", boxShadow: "0 0 0 0 rgb(var(--c-accent) / 0.55)" },
          "50%": { transform: "scale(1.04)", boxShadow: "0 0 0 18px rgb(var(--c-accent) / 0)" },
        },
        // The core's resting state: alive, but not demanding attention.
        breathe: {
          "0%, 100%": { transform: "scale(1)", opacity: "0.8" },
          "50%": { transform: "scale(1.035)", opacity: "1" },
        },
        // Radial rings that leave the core while it is hearing something.
        ripple: {
          "0%": { transform: "scale(0.85)", opacity: "0.5" },
          "100%": { transform: "scale(2.05)", opacity: "0" },
        },
        // Thinking: a ring that sweeps rather than spins, so it reads as
        // consideration instead of a loading spinner.
        sweep: {
          from: { transform: "rotate(0deg)" },
          to: { transform: "rotate(360deg)" },
        },
        "count-up": {
          from: { opacity: "0", transform: "translateY(6px)" },
          to: { opacity: "1", transform: "translateY(0)" },
        },
        drift: {
          "0%": { transform: "translateY(0) scale(1)", opacity: "0" },
          "20%": { opacity: "0.6" },
          "100%": { transform: "translateY(-34px) scale(0.4)", opacity: "0" },
        },
        // Three ambient specks around the voice core. Deliberately few.
        "float-slow": {
          "0%, 100%": { transform: "translate3d(0,0,0)", opacity: "0.25" },
          "50%": { transform: "translate3d(0,-10px,0)", opacity: "0.6" },
        },
        // Introduction page: atmospheric light that drifts slowly enough to
        // read as lighting rather than as motion.
        aurora: {
          "0%, 100%": { transform: "translate3d(0,0,0) scale(1)" },
          "33%": { transform: "translate3d(3%,-4%,0) scale(1.08)" },
          "66%": { transform: "translate3d(-3%,3%,0) scale(0.95)" },
        },
        // A highlight that travels across a surface once per cycle.
        shine: {
          "0%": { transform: "translateX(-130%) skewX(-12deg)" },
          "55%, 100%": { transform: "translateX(240%) skewX(-12deg)" },
        },
        // The typewriter caret in the live demo.
        caret: {
          "0%, 45%": { opacity: "1" },
          "50%, 95%": { opacity: "0" },
          "100%": { opacity: "1" },
        },
      },
      animation: {
        "fade-in": "fade-in 0.22s ease-out",
        "slide-up": "slide-up 0.28s cubic-bezier(0.22, 1, 0.36, 1)",
        "scale-in": "scale-in 0.2s cubic-bezier(0.22, 1, 0.36, 1)",
        shimmer: "shimmer 1.6s ease-in-out infinite",
        "voice-pulse": "voice-pulse 1.6s ease-out infinite",
        breathe: "breathe 4.5s ease-in-out infinite",
        ripple: "ripple 2.6s ease-out infinite",
        sweep: "sweep 1.5s linear infinite",
        "count-up": "count-up 0.4s ease-out",
        "float-slow": "float-slow 6s ease-in-out infinite",
        aurora: "aurora 20s ease-in-out infinite",
        shine: "shine 3.6s ease-in-out infinite",
        caret: "caret 1.1s steps(1) infinite",
      },
    },
  },
  plugins: [],
};

export default config;
