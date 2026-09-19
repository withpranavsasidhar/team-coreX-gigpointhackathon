"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";

const TABS = [
  { href: "/", label: "Home", icon: "⌂" },
  { href: "/inventory", label: "Stock", icon: "▤" },
  { href: "/ask", label: "Ask", icon: "?" },
  { href: "/insights", label: "Insights", icon: "◫" },
];

export function BottomNav() {
  const pathname = usePathname();
  const speaking = pathname.startsWith("/speak");

  return (
    <nav
      aria-label="Primary"
      className="fixed inset-x-0 bottom-0 z-40 border-t border-ink-850 bg-ink-990/90 backdrop-blur-xl"
      style={{ paddingBottom: "env(safe-area-inset-bottom, 0px)" }}
    >
      <div className="relative mx-auto flex max-w-2xl items-stretch">
        {TABS.map((tab, index) => {
          const active = tab.href === "/" ? pathname === "/" : pathname.startsWith(tab.href);
          return (
            <Link
              key={tab.href}
              href={tab.href}
              aria-current={active ? "page" : undefined}
              className={`flex flex-1 flex-col items-center gap-1 py-3 text-[11px] font-medium transition-colors ${
                index === 1 ? "pr-7" : index === 2 ? "pl-7" : ""
              } ${active ? "text-aria-400" : "text-ink-500 hover:text-ink-300"}`}
            >
              <span className="text-lg leading-none">{tab.icon}</span>
              {tab.label}
            </Link>
          );
        })}

        {/* Voice stays reachable from every screen — the product's core action. */}
        <Link
          href="/speak"
          aria-label="Speak"
          aria-current={speaking ? "page" : undefined}
          className={`focus-ring absolute -top-5 left-1/2 flex h-14 w-14 -translate-x-1/2 items-center justify-center rounded-full text-white transition-all ${
            speaking ? "scale-105 bg-aria-700" : "bg-aria-600 shadow-voice hover:scale-105"
          }`}
        >
          <svg viewBox="0 0 24 24" className="h-6 w-6 fill-white" aria-hidden>
            <path d="M12 14a3 3 0 0 0 3-3V5a3 3 0 0 0-6 0v6a3 3 0 0 0 3 3z" />
            <path d="M17 11a5 5 0 0 1-10 0H5a7 7 0 0 0 6 6.92V21h2v-3.08A7 7 0 0 0 19 11h-2z" />
          </svg>
        </Link>
      </div>
    </nav>
  );
}
