"use client";

import Link from "next/link";
import { usePathname, useRouter } from "next/navigation";
import { useCallback, useEffect, useState } from "react";

import { AriaMark } from "@/components/aria/AriaMark";
import { CommandBar } from "@/components/aria/CommandBar";
import { AuthScreen } from "@/components/auth/AuthScreen";
import { AuthModal } from "@/components/auth/AuthModal";
import { useBusiness } from "@/lib/BusinessContext";
import { ThemeSwitcher } from "@/lib/theme";

const NAV = [
  { href: "/", label: "Command", icon: HomeIcon },
  { href: "/inventory", label: "Stock", icon: BoxIcon },
  { href: "/memory", label: "Memory", icon: ClockIcon },
  { href: "/analytics", label: "Analytics", icon: ChartIcon },
  { href: "/customers", label: "People", icon: PeopleIcon },
];

export function AppShell({ children }: { children: React.ReactNode }) {
  const pathname = usePathname();
  const router = useRouter();
  const {
    user,
    businesses,
    business,
    summary,
    needsOnboarding,
    loading,
    switchBusiness,
    logout,
    showAuthModal,
    setShowAuthModal,
  } = useBusiness();

  const [commandOpen, setCommandOpen] = useState(false);
  const [switcherOpen, setSwitcherOpen] = useState(false);

  const onboarding = pathname.startsWith("/onboarding");

  // Cmd/Ctrl-K shortcut
  useEffect(() => {
    const onKey = (e: KeyboardEvent) => {
      if ((e.metaKey || e.ctrlKey) && e.key.toLowerCase() === "k") {
        e.preventDefault();
        setCommandOpen((v) => !v);
      }
    };
    window.addEventListener("keydown", onKey);
    return () => window.removeEventListener("keydown", onKey);
  }, []);

  useEffect(() => {
    if (!loading && user && needsOnboarding && !onboarding) router.replace("/onboarding");
  }, [loading, user, needsOnboarding, onboarding, router]);

  const openCommand = useCallback(() => setCommandOpen(true), []);

  if (loading) {
    return (
      <div className="flex min-h-dvh flex-col items-center justify-center gap-5 bg-ink-990">
        <span className="relative grid h-16 w-16 place-items-center">
          <span className="absolute inset-0 animate-breathe rounded-full bg-aria-500/15 blur-xl" />
          <AriaMark className="relative h-12 w-12" />
        </span>
        <p className="text-sm text-ink-500">Waking A.R.I.A.…</p>
      </div>
    );
  }

  if (!user) {
    return <AuthScreen />;
  }

  if (onboarding) {
    return <div className="min-h-dvh bg-ink-990 text-warm-50">{children}</div>;
  }

  return (
    <div className="min-h-dvh bg-ink-990 text-warm-50">
      {/* Desktop rail */}
      <aside className="fixed inset-y-0 left-0 z-40 hidden w-64 flex-col border-r border-ink-850 bg-ink-980 lg:flex">
        <div className="flex items-center gap-2.5 px-5 py-5">
          <AriaMark className="h-9 w-9" />
          <div className="min-w-0 flex-1">
            <p className="font-display text-[15px] font-bold leading-none tracking-tight text-warm-50">
              A.R.I.A.
            </p>
            <p className="mt-1 truncate text-[10.5px] leading-none text-ink-500">
              <span className="font-semibold text-aria-400">A</span>daptive{" "}
              <span className="font-semibold text-aria-400">R</span>etail{" "}
              <span className="font-semibold text-aria-400">I</span>ntelligence
            </p>
          </div>
        </div>

        <div className="mx-5 hairline" />

        <button
          onClick={openCommand}
          className="press group mx-3 mt-4 flex items-center gap-2.5 rounded-xl border border-ink-850 bg-ink-900 px-3 py-2.5 text-left text-sm text-ink-500 transition-all hover:border-aria-500/30 hover:bg-aria-500/[0.06] hover:text-warm-50"
        >
          <SearchIcon className="h-4 w-4 transition-colors group-hover:text-aria-500" />
          <span className="flex-1">Ask A.R.I.A.…</span>
          <kbd className="rounded-md border border-ink-850 bg-ink-950 px-1.5 py-0.5 font-sans text-[10px] text-ink-500">
            ⌘K
          </kbd>
        </button>

        <nav className="mt-5 flex-1 space-y-0.5 px-3">
          {NAV.map((item) => {
            const active = item.href === "/" ? pathname === "/" : pathname.startsWith(item.href);
            const Icon = item.icon;
            return (
              <Link
                key={item.href}
                href={item.href}
                aria-current={active ? "page" : undefined}
                className={`group relative flex items-center gap-3 rounded-xl px-3 py-2.5 text-sm transition-all duration-200 ${
                  active
                    ? "bg-aria-500/[0.09] font-semibold text-aria-400"
                    : "text-ink-400 hover:bg-ink-900 hover:text-warm-50"
                }`}
              >
                {/* A thin red marker rather than a slab of colour. */}
                <span
                  className={`absolute left-0 top-1/2 h-5 w-[3px] -translate-y-1/2 rounded-r-full bg-aria-500 transition-all duration-200 ${
                    active ? "opacity-100" : "opacity-0"
                  }`}
                />
                <Icon className="h-[18px] w-[18px]" />
                {item.label}
              </Link>
            );
          })}
        </nav>

        <div className="px-3 pb-2">
          <p className="mb-1.5 px-1 text-[10px] font-semibold uppercase tracking-[0.12em] text-ink-600">
            Appearance
          </p>
          <ThemeSwitcher />
        </div>

        {/* Business Switcher & Account Component */}
        <div className="relative m-3 mt-2">
          <button
            onClick={() => setSwitcherOpen((v) => !v)}
            className="press w-full rounded-xl border border-ink-850 bg-ink-900 p-3 text-left transition-colors hover:border-aria-500/25 focus:outline-none"
          >
            <div className="flex items-center justify-between">
              <div className="min-w-0 flex-1">
                <p className="flex items-center gap-2 text-sm font-semibold text-warm-50">
                  <span aria-hidden>{summary?.type_emoji ?? "🏬"}</span>
                  <span className="truncate">{business?.business_name ?? "My Business"}</span>
                </p>
                <p className="mt-0.5 truncate text-[11px] text-ink-500">
                  {summary?.type_label ?? business?.business_type} · Switch ▼
                </p>
              </div>
            </div>
          </button>

          {switcherOpen && (
            <div className="animate-scale-in absolute bottom-full left-0 z-50 mb-2 w-full origin-bottom rounded-2xl border border-ink-850 bg-ink-950 p-2 shadow-panel">
              <div className="mb-1 border-b border-ink-850 px-2 py-1.5 text-[10px] font-semibold uppercase tracking-[0.12em] text-ink-500">
                {user ? `Account: ${user.name}` : "Workspaces"}
              </div>

              <div className="max-h-48 space-y-1 overflow-y-auto">
                {businesses.map((b) => (
                  <button
                    key={b.id}
                    onClick={async () => {
                      setSwitcherOpen(false);
                      await switchBusiness(b.id);
                    }}
                    className={`flex w-full items-center justify-between rounded-lg px-2.5 py-2 text-left text-xs transition-colors ${
                      b.id === business?.id
                        ? "bg-aria-500/10 font-semibold text-aria-400"
                        : "text-ink-300 hover:bg-ink-900 hover:text-warm-50"
                    }`}
                  >
                    <span className="truncate">{b.business_name}</span>
                    <span className="text-[10px] capitalize text-ink-500">{b.business_type}</span>
                  </button>
                ))}
              </div>

              <div className="mt-2 space-y-1 border-t border-ink-850 pt-1">
                <button
                  onClick={() => {
                    setSwitcherOpen(false);
                    router.push("/onboarding");
                  }}
                  className="w-full rounded-lg px-2.5 py-2 text-left text-xs font-semibold text-aria-400 transition-colors hover:bg-aria-500/10"
                >
                  + Add Another Business
                </button>
                <Link
                  href="/settings"
                  onClick={() => setSwitcherOpen(false)}
                  className="block w-full rounded-lg px-2.5 py-2 text-left text-xs text-ink-400 transition-colors hover:bg-ink-900 hover:text-warm-50"
                >
                  ⚙ Settings
                </Link>
                {user ? (
                  <button
                    onClick={() => {
                      setSwitcherOpen(false);
                      logout();
                    }}
                    className="w-full rounded-lg px-2.5 py-2 text-left text-xs text-red-300 transition-colors hover:bg-red-950"
                  >
                    Sign Out ({user.phone})
                  </button>
                ) : (
                  <button
                    onClick={() => {
                      setSwitcherOpen(false);
                      setShowAuthModal(true);
                    }}
                    className="w-full rounded-lg px-2.5 py-2 text-left text-xs text-aria-400 transition-colors hover:bg-aria-500/10"
                  >
                    Sign In / Register
                  </button>
                )}
              </div>
            </div>
          )}
        </div>
      </aside>

      {/* Mobile header */}
      <header className="sticky top-0 z-30 flex items-center gap-2.5 border-b border-ink-850 bg-ink-990/85 px-4 py-3 backdrop-blur-xl lg:hidden">
        <AriaMark className="h-8 w-8" />
        <div className="min-w-0 flex-1">
          <p className="font-display text-sm font-bold leading-none tracking-tight text-warm-50">
            A.R.I.A.
          </p>
          {summary && (
            <p className="mt-1 truncate text-[11px] leading-none text-ink-500">
              {summary.type_emoji} {summary.business_name}
            </p>
          )}
        </div>
        <ThemeSwitcher compact />
        <button
          onClick={() => setShowAuthModal(true)}
          className="press rounded-lg border border-ink-850 bg-ink-900 px-2.5 py-1.5 text-xs font-medium text-ink-300"
        >
          {user ? user.name.split(" ")[0] : "Account"}
        </button>
        <button
          onClick={openCommand}
          aria-label="Ask A.R.I.A."
          className="press rounded-lg border border-ink-850 bg-ink-900 p-2 text-ink-400 transition-colors hover:border-aria-500/30 hover:text-aria-400"
        >
          <SearchIcon className="h-4 w-4" />
        </button>
      </header>

      <main className="mx-auto w-full max-w-5xl px-4 pb-28 pt-6 lg:pl-72 lg:pr-8 lg:pt-8">
        {children}
      </main>

      {/* Mobile bar */}
      <nav
        aria-label="Primary"
        className="fixed inset-x-0 bottom-0 z-40 border-t border-ink-850 bg-ink-990/90 backdrop-blur-xl lg:hidden"
        style={{ paddingBottom: "env(safe-area-inset-bottom, 0px)" }}
      >
        <div className="relative mx-auto flex max-w-2xl items-stretch">
          {NAV.slice(0, 2).map((item) => (
            <MobileTab key={item.href} item={item} pathname={pathname} className="pr-6" />
          ))}
          <div className="w-16" />
          {NAV.slice(2, 4).map((item) => (
            <MobileTab key={item.href} item={item} pathname={pathname} className="pl-6" />
          ))}

          {/* Talking to A.R.I.A. stays the primary action on mobile. */}
          <button
            onClick={openCommand}
            aria-label="Ask A.R.I.A."
            className="absolute -top-6 left-1/2 grid h-16 w-16 -translate-x-1/2 place-items-center rounded-full border border-aria-500/30 bg-ink-950 shadow-voice transition-transform duration-200 hover:scale-105 active:scale-100"
          >
            <span className="absolute inset-0 animate-breathe rounded-full bg-aria-500/20 blur-lg" />
            <AriaMark className="relative h-9 w-9" />
          </button>
        </div>
      </nav>

      <CommandBar open={commandOpen} onClose={() => setCommandOpen(false)} />
      <AuthModal isOpen={showAuthModal} onClose={() => setShowAuthModal(false)} />
    </div>
  );
}

function MobileTab({
  item,
  pathname,
  className = "",
}: {
  item: (typeof NAV)[number];
  pathname: string;
  className?: string;
}) {
  const active = item.href === "/" ? pathname === "/" : pathname.startsWith(item.href);
  const Icon = item.icon;
  return (
    <Link
      href={item.href}
      aria-current={active ? "page" : undefined}
      className={`relative flex flex-1 flex-col items-center gap-1 py-3 text-[10px] font-semibold transition-colors ${className} ${
        active ? "text-aria-400" : "text-ink-500 hover:text-ink-300"
      }`}
    >
      <span
        className={`absolute top-0 h-[2.5px] w-7 rounded-b-full bg-aria-500 transition-opacity duration-200 ${
          active ? "opacity-100" : "opacity-0"
        }`}
      />
      <Icon className="h-[18px] w-[18px]" />
      {item.label}
    </Link>
  );
}

type IconProps = { className?: string };
const base = (className?: string) => ({
  className,
  viewBox: "0 0 24 24",
  fill: "none",
  stroke: "currentColor",
  strokeWidth: 1.7,
  strokeLinecap: "round" as const,
  strokeLinejoin: "round" as const,
  "aria-hidden": true,
});

function HomeIcon({ className }: IconProps) {
  return (
    <svg {...base(className)}>
      <path d="M3 10.5 12 3l9 7.5" />
      <path d="M5 9.5V21h14V9.5" />
    </svg>
  );
}
function BoxIcon({ className }: IconProps) {
  return (
    <svg {...base(className)}>
      <path d="M3 7.5 12 3l9 4.5v9L12 21l-9-4.5z" />
      <path d="M3 7.5 12 12l9-4.5M12 12v9" />
    </svg>
  );
}
function ClockIcon({ className }: IconProps) {
  return (
    <svg {...base(className)}>
      <circle cx="12" cy="12" r="9" />
      <path d="M12 7v5l3.5 2" />
    </svg>
  );
}
function ChartIcon({ className }: IconProps) {
  return (
    <svg {...base(className)}>
      <path d="M4 20V10M10 20V4M16 20v-7M22 20H2" />
    </svg>
  );
}
function PeopleIcon({ className }: IconProps) {
  return (
    <svg {...base(className)}>
      <circle cx="9" cy="8" r="3.2" />
      <path d="M3 20c0-3.3 2.7-5.5 6-5.5s6 2.2 6 5.5" />
      <path d="M16 5.2a3.2 3.2 0 0 1 0 5.6M18 14.8c2 .7 3 2.5 3 5.2" />
    </svg>
  );
}
function SearchIcon({ className }: IconProps) {
  return (
    <svg {...base(className)}>
      <circle cx="11" cy="11" r="7" />
      <path d="m20 20-3.5-3.5" />
    </svg>
  );
}
