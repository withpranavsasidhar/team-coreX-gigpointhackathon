"use client";

import { useEffect, useRef, useState, type ReactNode } from "react";

import { AriaMark } from "@/components/aria/AriaMark";
import { ThemeSwitcher } from "@/lib/theme";

/**
 * The introduction shown before anyone signs in.
 *
 * Purely presentational. It knows nothing about auth, businesses or
 * inventory — it renders, and hands off to the existing sign-in screen
 * through `onEnter`. Every colour is a theme token, so the page is as
 * considered in light mode as it is in dark.
 *
 * Motion is decorative only: each animation here is either a CSS animation
 * (neutralised by the global prefers-reduced-motion rule) or guarded by
 * `usePrefersReducedMotion`, so the page is fully readable without it.
 */

/* ── Content ───────────────────────────────────────────────────────── */

/** Real utterances the product ships with, from the backend's business types. */
const DEMO = [
  {
    say: "Rendu cartons Coke vachayi",
    tag: "Telugu + English",
    reads: [
      { k: "Understood", v: "Stock came in" },
      { k: "Item", v: "Coke" },
      { k: "Quantity", v: "2 cartons → 48 pieces" },
    ],
    reply: "Added 48 pieces of Coke. You now have 96.",
  },
  {
    say: "Ramesh took two boxes of oil, he'll pay Friday",
    tag: "English",
    reads: [
      { k: "Understood", v: "Sale on credit" },
      { k: "Customer", v: "Ramesh" },
      { k: "Settles", v: "Friday" },
    ],
    reply: "Recorded against Ramesh's account. Nothing else changed.",
  },
  {
    say: "Maida 10 kg vachindi",
    tag: "Telugu + English",
    reads: [
      { k: "Understood", v: "Stock came in" },
      { k: "Item", v: "Maida — matched from “flour”" },
      { k: "Quantity", v: "10 kg" },
    ],
    reply: "Added 10 kg of Maida. Stock is now 34 kg.",
  },
  {
    say: "Rice stock entha undi?",
    tag: "Telugu + English",
    reads: [
      { k: "Understood", v: "A question, not a change" },
      { k: "Item", v: "Rice" },
    ],
    reply: "18 bags — under your reorder point of 40.",
  },
];

const FEATURES = [
  {
    icon: MicIcon,
    title: "Talk, don't type",
    body:
      "Say it the way you'd say it to a person. “Ramesh took two oil packets, he'll pay Friday” becomes a structured ledger entry — costed, attributed, and yours.",
  },
  {
    icon: GlobeIcon,
    title: "Understands, not translates",
    body:
      "English, తెలుగు, हिन्दी and natural code-switching are read as meaning, not machine-translated. “5 kg maida vachindi” simply works.",
  },
  {
    icon: MemoryIcon,
    title: "A real business memory",
    body:
      "Every entry traces back to the exact sentence that created it, when it was said, and how certain A.R.I.A. was. Nothing is ever silently guessed.",
  },
  {
    icon: ScanIcon,
    title: "A.R.I.A. Vision",
    body:
      "Point a camera at a delivery note or a shelf. It reads the lines, shows you what it found, and waits for your word before touching stock.",
  },
  {
    icon: WalletIcon,
    title: "Credit book, built in",
    body:
      "Every “he'll pay later” is tracked against the right customer automatically. No second notebook, no end-of-month reconstruction.",
  },
  {
    icon: ChartIcon,
    title: "Honest intelligence",
    body:
      "Reorder points and stockout forecasts are labelled as estimates, because a prediction dressed up as a fact is just a lie with a number on it.",
  },
];

const STEPS = [
  {
    n: "01",
    title: "Speak",
    body: "Tap once and talk. Type instead if the shop is loud — the same understanding runs either way.",
  },
  {
    n: "02",
    title: "A.R.I.A. understands",
    body: "It matches your words against your products, your units and your customers — then shows you its reading before it acts.",
  },
  {
    n: "03",
    title: "Your business remembers",
    body: "Written to the ledger with its reasoning attached, and ready to answer “what changed today?” whenever you ask.",
  },
];

const STATS = [
  { value: 63, suffix: "M", label: "MSMEs in India", sub: "the people this is built for" },
  { value: 3, suffix: "", label: "Languages", sub: "spoken freely, even mixed" },
  { value: 9, suffix: "", label: "Shop types", sub: "pre-stocked from day one" },
  { value: 0, suffix: "", label: "Forms to fill", sub: "the conversation is the interface" },
];

/** The team. `handle` is the GitHub username — the card links to it. */
const TEAM = [
  { name: "Sudheer Simhadri", handle: "Sudheer3135" },
  { name: "Pranav Sasidhar", handle: "withpranavsasidhar" },
  { name: "N. GiriTharun", handle: "2300033198" },
];

const SECTIONS = [
  { href: "#features", label: "Features" },
  { href: "#how", label: "How it works" },
  { href: "#team", label: "Team" },
];

/* ── Motion helpers ────────────────────────────────────────────────── */

function usePrefersReducedMotion() {
  const [reduced, setReduced] = useState(false);
  useEffect(() => {
    const mq = window.matchMedia("(prefers-reduced-motion: reduce)");
    setReduced(mq.matches);
    const onChange = () => setReduced(mq.matches);
    mq.addEventListener("change", onChange);
    return () => mq.removeEventListener("change", onChange);
  }, []);
  return reduced;
}

/** Fades a block up the first time it enters the viewport, then stops watching. */
function Reveal({
  children,
  delay = 0,
  className = "",
}: {
  children: ReactNode;
  delay?: number;
  className?: string;
}) {
  const ref = useRef<HTMLDivElement>(null);
  const [shown, setShown] = useState(false);

  useEffect(() => {
    const el = ref.current;
    if (!el) return;
    if (typeof IntersectionObserver === "undefined") {
      setShown(true);
      return;
    }
    const io = new IntersectionObserver(
      (entries) => {
        if (entries.some((e) => e.isIntersecting)) {
          setShown(true);
          io.disconnect();
        }
      },
      { threshold: 0.1, rootMargin: "0px 0px -48px 0px" }
    );
    io.observe(el);
    return () => io.disconnect();
  }, []);

  return (
    <div
      ref={ref}
      style={{ transitionDelay: `${delay}ms` }}
      className={`transition-[opacity,transform] duration-700 ease-[cubic-bezier(0.22,1,0.36,1)] ${
        shown ? "translate-y-0 opacity-100" : "translate-y-5 opacity-0"
      } ${className}`}
    >
      {children}
    </div>
  );
}

/** Counts from zero to `to` once the number is on screen. */
function CountUp({ to, suffix = "" }: { to: number; suffix?: string }) {
  const ref = useRef<HTMLSpanElement>(null);
  const [value, setValue] = useState(0);
  const reduced = usePrefersReducedMotion();

  useEffect(() => {
    const el = ref.current;
    if (!el) return;
    if (reduced || to === 0 || typeof IntersectionObserver === "undefined") {
      setValue(to);
      return;
    }
    let raf = 0;
    const io = new IntersectionObserver(
      (entries) => {
        if (!entries.some((e) => e.isIntersecting)) return;
        io.disconnect();
        const start = performance.now();
        const tick = (now: number) => {
          const p = Math.min((now - start) / 1200, 1);
          // Ease-out cubic, so it decelerates into the final number.
          setValue(Math.round(to * (1 - Math.pow(1 - p, 3))));
          if (p < 1) raf = requestAnimationFrame(tick);
        };
        raf = requestAnimationFrame(tick);
      },
      { threshold: 0.4 }
    );
    io.observe(el);
    return () => {
      io.disconnect();
      cancelAnimationFrame(raf);
    };
  }, [to, reduced]);

  return (
    <span ref={ref} className="tabular-nums">
      {value}
      {suffix}
    </span>
  );
}

/* ── Page ──────────────────────────────────────────────────────────── */

export function LandingPage({
  onEnter,
  leaving = false,
}: {
  onEnter: () => void;
  leaving?: boolean;
}) {
  return (
    <div
      className={`min-h-dvh overflow-x-hidden bg-ink-990 text-warm-50 transition-all duration-500 ease-[cubic-bezier(0.4,0,0.2,1)] motion-safe:scroll-smooth ${
        leaving ? "scale-[0.97] opacity-0" : "scale-100 opacity-100"
      }`}
    >
      <TopBar onEnter={onEnter} />
      <Hero onEnter={onEnter} />
      <LiveDemo />
      <Features />
      <HowItWorks />
      <Stats />
      <Team />
      <FinalCta onEnter={onEnter} />
      <Footer />
    </div>
  );
}

/* ── Top bar ───────────────────────────────────────────────────────── */

function TopBar({ onEnter }: { onEnter: () => void }) {
  const [lifted, setLifted] = useState(false);

  useEffect(() => {
    const onScroll = () => setLifted(window.scrollY > 12);
    onScroll();
    window.addEventListener("scroll", onScroll, { passive: true });
    return () => window.removeEventListener("scroll", onScroll);
  }, []);

  return (
    <header
      className={`fixed inset-x-0 top-0 z-50 transition-all duration-300 ${
        lifted ? "border-b border-ink-850 bg-ink-990/80 backdrop-blur-xl" : "border-b border-transparent"
      }`}
    >
      <div className="mx-auto flex h-16 w-full max-w-6xl items-center gap-3 px-5 sm:px-8">
        <AriaMark className="h-8 w-8 shrink-0" />
        <p className="font-display text-[15px] font-bold tracking-tight text-warm-50">A.R.I.A.</p>

        <nav className="ml-6 hidden items-center gap-1 md:flex">
          {SECTIONS.map((s) => (
            <a
              key={s.href}
              href={s.href}
              className="rounded-lg px-3 py-2 text-[13px] font-medium text-ink-400 transition-colors hover:bg-ink-900 hover:text-warm-50"
            >
              {s.label}
            </a>
          ))}
        </nav>

        <div className="ml-auto flex items-center gap-2.5">
          <ThemeSwitcher compact />
          <button
            onClick={onEnter}
            className="press rounded-xl bg-aria-600 px-4 py-2 text-[13px] font-semibold text-white shadow-voice transition-colors hover:bg-aria-700"
          >
            Sign in
          </button>
        </div>
      </div>
    </header>
  );
}

/* ── Hero ──────────────────────────────────────────────────────────── */

function Hero({ onEnter }: { onEnter: () => void }) {
  const ref = useRef<HTMLElement>(null);

  // The spotlight follows the pointer by writing CSS variables, so moving the
  // mouse never re-renders the section.
  const onMove = (e: React.MouseEvent<HTMLElement>) => {
    const el = ref.current;
    if (!el) return;
    const r = el.getBoundingClientRect();
    el.style.setProperty("--mx", `${((e.clientX - r.left) / r.width) * 100}%`);
    el.style.setProperty("--my", `${((e.clientY - r.top) / r.height) * 100}%`);
  };

  return (
    <section
      ref={ref}
      onMouseMove={onMove}
      className="relative isolate overflow-hidden px-5 pb-20 pt-32 sm:px-8 sm:pb-28 sm:pt-40"
    >
      {/* Atmosphere: two slow rose-red lights and a pointer-tracked spotlight. */}
      <div
        aria-hidden
        className="animate-aurora pointer-events-none absolute -top-36 left-1/2 -z-10 h-[38rem] w-[38rem] -translate-x-1/2 rounded-full opacity-70 blur-3xl"
        style={{
          background:
            "radial-gradient(circle, rgb(var(--c-accent) / 0.28) 0%, rgb(var(--c-accent) / 0.08) 45%, transparent 70%)",
        }}
      />
      <div
        aria-hidden
        className="animate-aurora pointer-events-none absolute -right-24 top-40 -z-10 h-[24rem] w-[24rem] rounded-full opacity-60 blur-3xl"
        style={{
          animationDelay: "-7s",
          background:
            "radial-gradient(circle, rgb(var(--c-accent) / 0.2) 0%, transparent 68%)",
        }}
      />
      <div
        aria-hidden
        className="pointer-events-none absolute inset-0 -z-10 hidden lg:block"
        style={{
          background:
            "radial-gradient(520px circle at var(--mx, 50%) var(--my, 30%), rgb(var(--c-accent) / 0.1), transparent 70%)",
        }}
      />

      <div className="mx-auto max-w-4xl text-center">
        <Reveal>
          <div className="relative mx-auto mb-8 grid h-24 w-24 place-items-center">
            <span className="absolute inset-0 animate-breathe rounded-full bg-aria-500/20 blur-2xl" />
            <AriaMark className="relative h-24 w-24 drop-shadow-lg" />
          </div>
        </Reveal>

        <Reveal delay={80}>
          <p className="mx-auto mb-7 inline-flex items-center gap-2 rounded-full border border-aria-500/25 bg-aria-500/[0.07] px-3.5 py-1.5 text-[11.5px] font-semibold tracking-wide text-aria-400">
            <span className="relative flex h-1.5 w-1.5">
              <span className="absolute inline-flex h-full w-full animate-ripple rounded-full bg-aria-500" />
              <span className="relative inline-flex h-1.5 w-1.5 rounded-full bg-aria-500" />
            </span>
            Voice-first business memory
          </p>
        </Reveal>

        <Reveal delay={140}>
          <h1 className="font-display text-[40px] font-bold leading-[1.05] tracking-[-0.03em] text-warm-50 sm:text-[62px] lg:text-[76px]">
            Your business should
            <br />
            <span className="bg-gradient-to-br from-aria-500 via-aria-400 to-aria-700 bg-clip-text text-transparent">
              remember itself.
            </span>
          </h1>
        </Reveal>

        <Reveal delay={220}>
          <p className="mx-auto mt-7 max-w-2xl text-[16px] leading-relaxed text-ink-300 sm:text-[18px]">
            A.R.I.A. is an inventory assistant for India&apos;s small shops that you talk to
            instead of type into. Speak in English, తెలుగు, हिन्दी — or all three in one
            sentence — and your stock, credit book and history keep themselves.
          </p>
        </Reveal>

        <Reveal delay={300}>
          <div className="mt-10 flex flex-col items-center justify-center gap-3 sm:flex-row">
            <button
              onClick={onEnter}
              className="press group relative w-full overflow-hidden rounded-2xl bg-aria-600 px-7 py-3.5 text-[15px] font-semibold text-white shadow-voice-lg transition-colors hover:bg-aria-700 sm:w-auto"
            >
              {/* A highlight that sweeps across the button. */}
              <span
                aria-hidden
                className="animate-shine absolute inset-y-0 -left-full w-1/2 bg-gradient-to-r from-transparent via-white/25 to-transparent"
              />
              <span className="relative">Get started — it&apos;s free</span>
            </button>
            <a
              href="#demo"
              className="press w-full rounded-2xl border border-ink-850 bg-ink-950 px-7 py-3.5 text-center text-[15px] font-semibold text-ink-300 transition-all hover:border-aria-500/30 hover:text-warm-50 sm:w-auto"
            >
              See it understand
            </a>
          </div>
        </Reveal>

        <Reveal delay={380}>
          <div className="mt-8 flex flex-wrap items-center justify-center gap-x-5 gap-y-2 text-[12.5px] text-ink-500">
            <span>English</span>
            <Dot />
            <span>తెలుగు</span>
            <Dot />
            <span>हिन्दी</span>
            <Dot />
            <span>Mixed, mid-sentence</span>
          </div>
        </Reveal>
      </div>
    </section>
  );
}

function Dot() {
  return <span aria-hidden className="h-1 w-1 rounded-full bg-ink-700" />;
}

/* ── Live demo ─────────────────────────────────────────────────────── */

type Phase = "typing" | "thinking" | "answer";

function LiveDemo() {
  const [index, setIndex] = useState(0);
  const [chars, setChars] = useState(0);
  const [phase, setPhase] = useState<Phase>("typing");
  const reduced = usePrefersReducedMotion();
  const script = DEMO[index];

  useEffect(() => {
    const advance = () => {
      setIndex((v) => (v + 1) % DEMO.length);
      setChars(0);
      setPhase("typing");
    };

    // Without motion the line is simply shown complete, then rotated slowly.
    if (reduced) {
      if (chars !== script.say.length) {
        setChars(script.say.length);
        return;
      }
      if (phase !== "answer") {
        setPhase("answer");
        return;
      }
      const t = setTimeout(advance, 5000);
      return () => clearTimeout(t);
    }

    if (phase === "typing") {
      const t =
        chars < script.say.length
          ? setTimeout(() => setChars((c) => c + 1), 45)
          : setTimeout(() => setPhase("thinking"), 420);
      return () => clearTimeout(t);
    }

    if (phase === "thinking") {
      const t = setTimeout(() => setPhase("answer"), 900);
      return () => clearTimeout(t);
    }

    const t = setTimeout(advance, 3400);
    return () => clearTimeout(t);
  }, [phase, chars, index, reduced, script.say.length]);

  const typed = script.say.slice(0, chars);

  return (
    <section id="demo" className="scroll-mt-20 px-5 py-20 sm:px-8 sm:py-28">
      <div className="mx-auto max-w-3xl">
        <Reveal className="mb-10 text-center">
          <p className="eyebrow mb-3">Watch it work</p>
          <h2 className="font-display text-[28px] font-bold leading-tight tracking-tight text-warm-50 sm:text-[38px]">
            One sentence in. A real entry out.
          </h2>
        </Reveal>

        <Reveal delay={100}>
          <div className="relative overflow-hidden rounded-3xl border border-ink-850 bg-ink-950 shadow-panel">
            <div
              aria-hidden
              className="pointer-events-none absolute inset-x-0 top-0 h-px bg-gradient-to-r from-transparent via-aria-500/50 to-transparent"
            />

            {/* What the owner says */}
            <div className="flex items-start gap-4 border-b border-ink-850 p-5 sm:p-6">
              <span className="relative mt-0.5 grid h-11 w-11 shrink-0 place-items-center rounded-full border border-aria-500/30 bg-aria-500/[0.08]">
                {phase === "typing" && (
                  <span className="absolute inset-0 animate-ripple rounded-full border border-aria-500/40" />
                )}
                <MicIcon className="h-[18px] w-[18px] text-aria-500" />
              </span>
              <div className="min-w-0 flex-1 pt-1.5">
                {/* Two lines are reserved: the longest line wraps on a phone,
                    and the row must not grow as the text types itself in. */}
                <p className="min-h-[2.75rem] text-[16px] leading-snug text-warm-50 sm:min-h-0 sm:text-[18px]">
                  {typed}
                  {phase === "typing" && (
                    <span className="animate-caret ml-0.5 inline-block h-[1.05em] w-[2px] translate-y-[3px] bg-aria-500" />
                  )}
                </p>
                <p className="mt-2 text-[11px] font-semibold uppercase tracking-[0.1em] text-ink-500">
                  {script.tag}
                </p>
              </div>
            </div>

            {/* What A.R.I.A. read, and what it did. The floor is tall enough to
                hold the widest answer, so the card never jumps between lines —
                the chips stack on narrow screens and so need more of it. */}
            <div className="min-h-[22.5rem] p-5 sm:min-h-[13.5rem] sm:p-6">
              {phase === "thinking" && (
                <p className="flex items-center gap-2.5 text-sm text-ink-400">
                  <span className="h-3.5 w-3.5 animate-sweep rounded-full border-2 border-transparent border-t-aria-500" />
                  Checking your products…
                </p>
              )}

              {phase === "answer" && (
                <div className="animate-slide-up space-y-4">
                  <div className="grid gap-2 sm:grid-cols-3">
                    {script.reads.map((r, i) => (
                      <div
                        key={r.k}
                        className="animate-scale-in rounded-xl border border-ink-850 bg-ink-900 px-3.5 py-2.5"
                        style={{ animationDelay: `${i * 70}ms` }}
                      >
                        <p className="text-[10px] font-semibold uppercase tracking-[0.1em] text-ink-500">
                          {r.k}
                        </p>
                        <p className="mt-1 text-[13.5px] font-medium text-warm-50">{r.v}</p>
                      </div>
                    ))}
                  </div>

                  <div className="relative overflow-hidden rounded-2xl border border-ink-850 bg-ink-950 py-3.5 pl-5 pr-4">
                    <span className="absolute inset-y-0 left-0 w-[3px] bg-aria-500" />
                    <p className="flex items-center gap-1.5 text-[10px] font-semibold uppercase tracking-[0.12em] text-aria-400">
                      <span className="h-1.5 w-1.5 rounded-full bg-aria-500" />
                      A.R.I.A.
                    </p>
                    <p className="mt-2 text-[15px] leading-relaxed text-warm-50">{script.reply}</p>
                  </div>
                </div>
              )}
            </div>

            {/* Which line is playing */}
            <div className="flex items-center justify-center gap-1.5 border-t border-ink-850 py-3.5">
              {DEMO.map((d, i) => (
                <span
                  key={d.say}
                  aria-hidden
                  className={`h-1 rounded-full transition-all duration-500 ${
                    i === index ? "w-6 bg-aria-500" : "w-1.5 bg-ink-800"
                  }`}
                />
              ))}
            </div>
          </div>
        </Reveal>

        <Reveal delay={180}>
          <p className="mt-5 text-center text-[12.5px] leading-relaxed text-ink-500">
            Below its confidence threshold A.R.I.A. asks instead of acting — so it never
            quietly guesses at your stock.
          </p>
        </Reveal>
      </div>
    </section>
  );
}

/* ── Features ──────────────────────────────────────────────────────── */

function Features() {
  return (
    <section id="features" className="scroll-mt-20 px-5 py-20 sm:px-8 sm:py-28">
      <div className="mx-auto max-w-6xl">
        <Reveal className="mb-14 max-w-2xl">
          <p className="eyebrow mb-3">What makes it different</p>
          <h2 className="font-display text-[30px] font-bold leading-[1.1] tracking-tight text-warm-50 sm:text-[44px]">
            Not a dashboard with a microphone bolted on.
          </h2>
          <p className="mt-5 text-[16px] leading-relaxed text-ink-400">
            The voice core <em className="not-italic text-warm-50">is</em> the product. Everything
            else exists to give the owner context for the next thing they say to it.
          </p>
        </Reveal>

        <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
          {FEATURES.map((f, i) => {
            const Icon = f.icon;
            return (
              <Reveal key={f.title} delay={i * 70}>
                <article className="group relative h-full overflow-hidden rounded-2xl border border-ink-850 bg-ink-950 p-6 transition-all duration-300 hover:-translate-y-1 hover:border-aria-500/30 hover:shadow-lift">
                  {/* A light that warms the card on hover. */}
                  <span
                    aria-hidden
                    className="pointer-events-none absolute -right-16 -top-16 h-40 w-40 rounded-full opacity-0 blur-2xl transition-opacity duration-500 group-hover:opacity-100"
                    style={{
                      background:
                        "radial-gradient(circle, rgb(var(--c-accent) / 0.22) 0%, transparent 70%)",
                    }}
                  />
                  <span className="relative grid h-11 w-11 place-items-center rounded-xl border border-aria-500/25 bg-aria-500/[0.08] text-aria-500">
                    <Icon className="h-[19px] w-[19px]" />
                  </span>
                  <h3 className="relative mt-5 text-[17px] font-semibold tracking-tight text-warm-50">
                    {f.title}
                  </h3>
                  <p className="relative mt-2.5 text-[14px] leading-relaxed text-ink-400">
                    {f.body}
                  </p>
                </article>
              </Reveal>
            );
          })}
        </div>
      </div>
    </section>
  );
}

/* ── How it works ──────────────────────────────────────────────────── */

function HowItWorks() {
  return (
    <section id="how" className="scroll-mt-20 px-5 py-20 sm:px-8 sm:py-28">
      <div className="mx-auto max-w-5xl">
        <Reveal className="mb-14 text-center">
          <p className="eyebrow mb-3">How it works</p>
          <h2 className="font-display text-[30px] font-bold leading-tight tracking-tight text-warm-50 sm:text-[44px]">
            Three steps. No forms.
          </h2>
        </Reveal>

        <div className="relative grid gap-8 md:grid-cols-3 md:gap-6">
          {/* The thread that joins the steps on wide screens. */}
          <div
            aria-hidden
            className="absolute left-0 right-0 top-7 hidden h-px md:block"
            style={{
              background:
                "linear-gradient(90deg, transparent, rgb(var(--c-line)) 12%, rgb(var(--c-line)) 88%, transparent)",
            }}
          />
          {STEPS.map((s, i) => (
            <Reveal key={s.n} delay={i * 110} className="relative">
              <div className="relative grid h-14 w-14 place-items-center rounded-2xl border border-aria-500/25 bg-ink-990 font-display text-[15px] font-bold text-aria-400">
                <span
                  aria-hidden
                  className="absolute inset-0 rounded-2xl bg-aria-500/10 blur-md"
                />
                <span className="relative">{s.n}</span>
              </div>
              <h3 className="mt-5 text-[19px] font-semibold tracking-tight text-warm-50">
                {s.title}
              </h3>
              <p className="mt-2.5 text-[14px] leading-relaxed text-ink-400">{s.body}</p>
            </Reveal>
          ))}
        </div>
      </div>
    </section>
  );
}

/* ── Stats ─────────────────────────────────────────────────────────── */

function Stats() {
  return (
    <section className="px-5 py-14 sm:px-8">
      <div className="mx-auto max-w-6xl">
        <Reveal>
          <div className="grid gap-px overflow-hidden rounded-3xl border border-ink-850 bg-ink-850 sm:grid-cols-2 lg:grid-cols-4">
            {STATS.map((s) => (
              <div key={s.label} className="bg-ink-950 px-6 py-8 text-center">
                <p className="font-display text-[40px] font-bold leading-none tracking-tight text-warm-50">
                  <CountUp to={s.value} suffix={s.suffix} />
                </p>
                <p className="mt-3 text-[13.5px] font-semibold text-warm-50">{s.label}</p>
                <p className="mt-1 text-[12px] leading-relaxed text-ink-500">{s.sub}</p>
              </div>
            ))}
          </div>
        </Reveal>
      </div>
    </section>
  );
}

/* ── Team ──────────────────────────────────────────────────────────── */

/** Two letters from a name, ignoring punctuation: "N. GiriTharun" → "NG". */
function initials(name: string) {
  return name
    .split(/\s+/)
    .map((word) => word.replace(/[^A-Za-z]/g, "")[0])
    .filter(Boolean)
    .slice(0, 2)
    .join("")
    .toUpperCase();
}

function Team() {
  return (
    <section id="team" className="scroll-mt-20 px-5 py-20 sm:px-8 sm:py-28">
      <div className="mx-auto max-w-4xl text-center">
        <Reveal>
          <p className="eyebrow mb-3">The team</p>
          <h2 className="font-display text-[30px] font-bold leading-tight tracking-tight text-warm-50 sm:text-[44px]">
            Built by{" "}
            <span className="bg-gradient-to-br from-aria-500 to-aria-700 bg-clip-text text-transparent">
              Team coreX
            </span>
          </h2>
          <p className="mx-auto mt-5 max-w-xl text-[15px] leading-relaxed text-ink-400">
            Made for the GigPoint Hackathon — for the shopkeeper who has been holding an
            entire inventory in their head, and deserves better than a spreadsheet.
          </p>
        </Reveal>

        <div className="mt-12 flex flex-wrap items-stretch justify-center gap-4">
          {TEAM.map((m, i) => (
            <Reveal key={m.handle} delay={i * 100}>
              <a
                href={`https://github.com/${m.handle}`}
                target="_blank"
                rel="noreferrer noopener"
                className="group block w-60 rounded-2xl border border-ink-850 bg-ink-950 p-6 transition-all duration-300 hover:-translate-y-1 hover:border-aria-500/30 hover:shadow-lift"
              >
                <span className="relative mx-auto grid h-16 w-16 place-items-center rounded-full bg-gradient-to-br from-aria-500 to-aria-800 font-display text-[20px] font-bold text-white shadow-voice">
                  {initials(m.name)}
                </span>
                <h3 className="mt-4 text-[15.5px] font-semibold tracking-tight text-warm-50">
                  {m.name}
                </h3>
                <p className="mt-1 flex items-center justify-center gap-1.5 text-[12.5px] text-ink-500 transition-colors group-hover:text-aria-400">
                  <GitHubIcon className="h-3.5 w-3.5" />
                  {m.handle}
                </p>
              </a>
            </Reveal>
          ))}
        </div>
      </div>
    </section>
  );
}

/* ── Closing call to action ────────────────────────────────────────── */

function FinalCta({ onEnter }: { onEnter: () => void }) {
  return (
    <section className="px-5 pb-20 pt-10 sm:px-8 sm:pb-28">
      <div className="mx-auto max-w-5xl">
        <Reveal>
          <div className="relative isolate overflow-hidden rounded-[28px] border border-ink-850 bg-ink-950 px-6 py-16 text-center shadow-panel sm:px-14 sm:py-20">
            <div
              aria-hidden
              className="animate-aurora pointer-events-none absolute -top-40 left-1/2 -z-10 h-[30rem] w-[30rem] -translate-x-1/2 rounded-full blur-3xl"
              style={{
                background:
                  "radial-gradient(circle, rgb(var(--c-accent) / 0.25) 0%, transparent 68%)",
              }}
            />
            <AriaMark className="mx-auto h-14 w-14" />
            <h2 className="mt-7 font-display text-[30px] font-bold leading-[1.1] tracking-tight text-warm-50 sm:text-[46px]">
              Stop maintaining your inventory.
            </h2>
            <p className="mx-auto mt-4 max-w-xl text-[16px] leading-relaxed text-ink-300">
              Set your shop up in under a minute — then just tell A.R.I.A. what happened.
            </p>
            <button
              onClick={onEnter}
              className="press group relative mt-9 inline-flex overflow-hidden rounded-2xl bg-aria-600 px-8 py-4 text-[15px] font-semibold text-white shadow-voice-lg transition-colors hover:bg-aria-700"
            >
              <span
                aria-hidden
                className="animate-shine absolute inset-y-0 -left-full w-1/2 bg-gradient-to-r from-transparent via-white/25 to-transparent"
              />
              <span className="relative">Create your shop</span>
            </button>
            <p className="mt-5 text-[12.5px] text-ink-500">
              No card, no setup call. Works with the phone already on your counter.
            </p>
          </div>
        </Reveal>
      </div>
    </section>
  );
}

/* ── Footer ────────────────────────────────────────────────────────── */

function Footer() {
  return (
    <footer className="border-t border-ink-850 px-5 py-10 sm:px-8">
      <div className="mx-auto flex max-w-6xl flex-col items-center gap-4 text-center sm:flex-row sm:justify-between sm:text-left">
        <div className="flex items-center gap-2.5">
          <AriaMark className="h-7 w-7" />
          <div>
            <p className="font-display text-[13.5px] font-bold tracking-tight text-warm-50">
              A.R.I.A.
            </p>
            <p className="text-[11px] text-ink-500">Adaptive Retail Intelligence Assistant</p>
          </div>
        </div>
        <p className="text-[12px] leading-relaxed text-ink-500">
          A shopkeeper shouldn&apos;t have to maintain their inventory.
          <br className="hidden sm:block" /> Their business should remember itself.
        </p>
      </div>
    </footer>
  );
}

/* ── Icons ─────────────────────────────────────────────────────────── */

type IconProps = { className?: string };

function base(className?: string) {
  return {
    viewBox: "0 0 24 24",
    fill: "none",
    stroke: "currentColor",
    strokeWidth: 1.7,
    strokeLinecap: "round" as const,
    strokeLinejoin: "round" as const,
    className,
    "aria-hidden": true,
  };
}

function MicIcon({ className }: IconProps) {
  return (
    <svg {...base(className)}>
      <rect x="9" y="2.5" width="6" height="11" rx="3" />
      <path d="M5 11a7 7 0 0 0 14 0M12 18v3.5" />
    </svg>
  );
}

function GlobeIcon({ className }: IconProps) {
  return (
    <svg {...base(className)}>
      <circle cx="12" cy="12" r="9" />
      <path d="M3.5 9h17M3.5 15h17M12 3a15 15 0 0 1 0 18a15 15 0 0 1 0-18z" />
    </svg>
  );
}

function MemoryIcon({ className }: IconProps) {
  return (
    <svg {...base(className)}>
      <circle cx="12" cy="12" r="9" />
      <path d="M12 7v5l3.2 2" />
    </svg>
  );
}

function ScanIcon({ className }: IconProps) {
  return (
    <svg {...base(className)}>
      <path d="M3 9V6a1 1 0 0 1 1-1h3M21 9V6a1 1 0 0 0-1-1h-3M3 15v3a1 1 0 0 0 1 1h3M21 15v3a1 1 0 0 1-1 1h-3" />
      <circle cx="12" cy="12" r="3.2" />
    </svg>
  );
}

function WalletIcon({ className }: IconProps) {
  return (
    <svg {...base(className)}>
      <rect x="3" y="6" width="18" height="13" rx="2.5" />
      <path d="M3 10h18M16.5 14.5h.01" />
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

/** Solid mark, so it reads at 14px where a stroked one would not. */
function GitHubIcon({ className }: IconProps) {
  return (
    <svg viewBox="0 0 16 16" fill="currentColor" className={className} aria-hidden>
      <path d="M8 0C3.58 0 0 3.58 0 8c0 3.54 2.29 6.53 5.47 7.59.4.07.55-.17.55-.38 0-.19-.01-.82-.01-1.49-2.01.37-2.53-.49-2.69-.94-.09-.23-.48-.94-.82-1.13-.28-.15-.68-.52-.01-.53.63-.01 1.08.58 1.23.82.72 1.21 1.87.87 2.33.66.07-.52.28-.87.51-1.07-1.78-.2-3.64-.89-3.64-3.95 0-.87.31-1.59.82-2.15-.08-.2-.36-1.02.08-2.12 0 0 .67-.21 2.2.82a7.4 7.4 0 0 1 2-.27c.68 0 1.36.09 2 .27 1.53-1.04 2.2-.82 2.2-.82.44 1.1.16 1.92.08 2.12.51.56.82 1.27.82 2.15 0 3.07-1.87 3.75-3.65 3.95.29.25.54.73.54 1.48 0 1.07-.01 1.93-.01 2.2 0 .21.15.46.55.38A8.01 8.01 0 0 0 16 8c0-4.42-3.58-8-8-8z" />
    </svg>
  );
}
