"use client";

import {
  createContext,
  useCallback,
  useContext,
  useEffect,
  useMemo,
  useState,
  type ReactNode,
} from "react";

/**
 * Theme: light, dark, or follow the machine.
 *
 * Purely presentational — it touches nothing but a class on <html> and one
 * localStorage key of its own, so authentication, the active business and
 * every other stored preference are untouched by a theme change.
 *
 * The preference is written by the same key the blocking script in
 * app/layout.tsx reads, so a reload paints the chosen theme on the first
 * frame instead of flashing the other one.
 */

export type Theme = "light" | "dark" | "system";
export type ResolvedTheme = "light" | "dark";

export const THEME_KEY = "aria.theme";

/**
 * Runs before React hydrates, inline in <head>. Kept in one string so the
 * script and the provider can never disagree about the storage key.
 */
export const THEME_SCRIPT = `(function(){try{var t=localStorage.getItem("${THEME_KEY}");if(t!=="light"&&t!=="dark"&&t!=="system")t="system";var d=t==="dark"||(t==="system"&&window.matchMedia("(prefers-color-scheme: dark)").matches);var r=document.documentElement;r.classList.toggle("dark",d);r.dataset.theme=d?"dark":"light";r.style.colorScheme=d?"dark":"light";}catch(e){}})();`;

interface ThemeState {
  /** What the owner chose, including "system". */
  theme: Theme;
  /** What is actually on screen right now. */
  resolved: ResolvedTheme;
  setTheme: (next: Theme) => void;
}

const Ctx = createContext<ThemeState>({
  theme: "system",
  resolved: "dark",
  setTheme: () => {},
});

function systemPrefersDark(): boolean {
  if (typeof window === "undefined") return false;
  return window.matchMedia("(prefers-color-scheme: dark)").matches;
}

function apply(resolved: ResolvedTheme) {
  const root = document.documentElement;
  root.classList.toggle("dark", resolved === "dark");
  root.dataset.theme = resolved;
  root.style.colorScheme = resolved;
  // Keep the mobile browser chrome in step with the surface behind it.
  const meta = document.querySelector('meta[name="theme-color"]');
  if (meta) meta.setAttribute("content", resolved === "dark" ? "#0D0D0F" : "#FCFCFA");
}

export function ThemeProvider({ children }: { children: ReactNode }) {
  // Server and first client render must agree, so start from the default and
  // adopt the stored preference in an effect.
  const [theme, setThemeState] = useState<Theme>("system");
  const [resolved, setResolved] = useState<ResolvedTheme>("light");

  useEffect(() => {
    let stored: Theme = "system";
    try {
      const raw = localStorage.getItem(THEME_KEY);
      if (raw === "light" || raw === "dark" || raw === "system") stored = raw;
    } catch {
      /* private mode */
    }
    setThemeState(stored);
    const next: ResolvedTheme =
      stored === "system" ? (systemPrefersDark() ? "dark" : "light") : stored;
    setResolved(next);
    apply(next);
  }, []);

  // Only while following the system does an OS change move the interface.
  useEffect(() => {
    if (theme !== "system" || typeof window === "undefined") return;
    const mq = window.matchMedia("(prefers-color-scheme: dark)");
    const onChange = () => {
      const next: ResolvedTheme = mq.matches ? "dark" : "light";
      setResolved(next);
      apply(next);
    };
    mq.addEventListener("change", onChange);
    return () => mq.removeEventListener("change", onChange);
  }, [theme]);

  const setTheme = useCallback((next: Theme) => {
    setThemeState(next);
    try {
      localStorage.setItem(THEME_KEY, next);
    } catch {
      /* private mode — the theme still applies for this session */
    }
    const applied: ResolvedTheme = next === "system" ? (systemPrefersDark() ? "dark" : "light") : next;
    setResolved(applied);
    apply(applied);
  }, []);

  const value = useMemo(() => ({ theme, resolved, setTheme }), [theme, resolved, setTheme]);

  return <Ctx.Provider value={value}>{children}</Ctx.Provider>;
}

export const useTheme = () => useContext(Ctx);

const OPTIONS: { value: Theme; label: string; icon: ReactNode }[] = [
  { value: "light", label: "Light", icon: <SunIcon /> },
  { value: "system", label: "System", icon: <SystemIcon /> },
  { value: "dark", label: "Dark", icon: <MoonIcon /> },
];

/**
 * The switcher. `compact` is the icon-only form for the header and rail;
 * the full form, with labels, is used in Settings.
 */
export function ThemeSwitcher({ compact = false }: { compact?: boolean }) {
  const { theme, setTheme } = useTheme();

  return (
    <div
      role="radiogroup"
      aria-label="Colour theme"
      className={`inline-flex items-center gap-0.5 rounded-xl border border-ink-850 bg-ink-900 p-1 ${
        compact ? "" : "w-full"
      }`}
    >
      {OPTIONS.map((opt) => {
        const active = theme === opt.value;
        return (
          <button
            key={opt.value}
            role="radio"
            aria-checked={active}
            aria-label={opt.label}
            title={`${opt.label} theme`}
            onClick={() => setTheme(opt.value)}
            className={`press focus-ring flex items-center justify-center gap-1.5 rounded-lg text-xs font-medium transition-colors ${
              compact ? "h-7 w-7" : "h-9 flex-1"
            } ${
              active
                ? "bg-ink-950 text-aria-400 shadow-soft"
                : "text-ink-500 hover:text-warm-50"
            }`}
          >
            {opt.icon}
            {!compact && <span>{opt.label}</span>}
          </button>
        );
      })}
    </div>
  );
}

const glyph = {
  viewBox: "0 0 24 24",
  fill: "none",
  stroke: "currentColor",
  strokeWidth: 1.8,
  strokeLinecap: "round" as const,
  strokeLinejoin: "round" as const,
  className: "h-3.5 w-3.5",
  "aria-hidden": true,
};

function SunIcon() {
  return (
    <svg {...glyph}>
      <circle cx="12" cy="12" r="4" />
      <path d="M12 2v2M12 20v2M4.9 4.9l1.4 1.4M17.7 17.7l1.4 1.4M2 12h2M20 12h2M4.9 19.1l1.4-1.4M17.7 6.3l1.4-1.4" />
    </svg>
  );
}

function SystemIcon() {
  return (
    <svg {...glyph}>
      <rect x="2.5" y="4" width="19" height="13" rx="2" />
      <path d="M8 20.5h8" />
    </svg>
  );
}

function MoonIcon() {
  return (
    <svg {...glyph}>
      <path d="M20 14.2A8.2 8.2 0 0 1 9.8 4a8.2 8.2 0 1 0 10.2 10.2z" />
    </svg>
  );
}
