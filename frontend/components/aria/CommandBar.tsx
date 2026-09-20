"use client";

import { useCallback, useEffect, useRef, useState } from "react";
import { useRouter } from "next/navigation";

import { AriaCore, type CoreState } from "./AriaCore";
import { UnderstandingChain } from "./UnderstandingChain";
import { AnswerVisual } from "@/components/intelligence/AnswerVisual";
import { api } from "@/lib/api";
import { useBusiness } from "@/lib/BusinessContext";
import { useSpeechCapture } from "@/lib/useSpeechCapture";
import type { AgentStatus, AriaChatResponse } from "@/lib/types";

/**
 * A.R.I.A. from anywhere.
 *
 * One surface, one endpoint. The backend decides whether the real agent or the
 * deterministic engine answers, and says which in `engine` — the client never
 * guesses, and never implies an AI answered when one did not.
 */

interface Turn {
  id: number;
  text: string;
  result?: AriaChatResponse;
  error?: string;
  /** Set once a proposed action has been approved or cancelled. */
  resolution?: { text: string; ok: boolean };
}

export function CommandBar({
  open,
  onClose,
  seedText = "",
}: {
  open: boolean;
  onClose: () => void;
  seedText?: string;
}) {
  const router = useRouter();
  const { business } = useBusiness();
  const [input, setInput] = useState(seedText);
  const [turns, setTurns] = useState<Turn[]>([]);
  const [busy, setBusy] = useState(false);
  const [lang, setLang] = useState("en-IN");
  const [conversationId, setConversationId] = useState<string | null>(null);
  const [agent, setAgent] = useState<AgentStatus | null>(null);
  const inputRef = useRef<HTMLInputElement>(null);
  const endRef = useRef<HTMLDivElement>(null);
  const capture = useSpeechCapture(lang);

  useEffect(() => {
    try {
      const saved = localStorage.getItem("aria.language");
      if (saved) setLang(saved);
    } catch {
      /* private mode */
    }
    api.ariaStatus().then(setAgent).catch(() => setAgent(null));
  }, []);

  useEffect(() => {
    if (open) {
      setInput(seedText);
      const id = setTimeout(() => inputRef.current?.focus(), 60);
      return () => clearTimeout(id);
    }
    capture.stop();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [open, seedText]);

  useEffect(() => {
    endRef.current?.scrollIntoView({ behavior: "smooth", block: "end" });
  }, [turns, busy]);

  const send = useCallback(
    async (raw: string, source: "text" | "voice" = "text") => {
      const text = raw.trim();
      if (!business || !text || busy) return;

      const id = Date.now();
      setInput("");
      setBusy(true);
      setTurns((t) => [...t, { id, text }]);

      try {
        const result = await api.ariaChat(business.id, text, {
          conversationId,
          language: lang.split("-")[0],
          source,
        });
        if (result.conversation_id) setConversationId(result.conversation_id);
        setTurns((t) => t.map((x) => (x.id === id ? { ...x, result } : x)));

        // A completed write means other screens are stale.
        const wrote =
          result.status === "completed" &&
          (result.tool_calls.some((c) => c.result && !c.result.error) ||
            result.interpretation?.status === "recorded" ||
            result.interpretation?.status === "amended");
        if (wrote) router.refresh();
      } catch (e) {
        setTurns((t) => t.map((x) => (x.id === id ? { ...x, error: (e as Error).message } : x)));
      } finally {
        setBusy(false);
      }
    },
    [business, busy, conversationId, lang, router]
  );

  const resolve = useCallback(
    async (turnId: number, actionId: string, approved: boolean) => {
      if (!business) return;
      setBusy(true);
      try {
        const result = await api.ariaConfirm(business.id, actionId, approved);
        setTurns((t) =>
          t.map((x) =>
            x.id === turnId
              ? { ...x, resolution: { text: result.response, ok: result.status === "completed" } }
              : x
          )
        );
        if (approved && result.status === "completed") router.refresh();
      } catch (e) {
        setTurns((t) =>
          t.map((x) =>
            x.id === turnId ? { ...x, resolution: { text: (e as Error).message, ok: false } } : x
          )
        );
      } finally {
        setBusy(false);
      }
    },
    [business, router]
  );

  useEffect(() => {
    if (!open) return;
    const onKey = (e: KeyboardEvent) => {
      if (e.key === "Escape") onClose();
    };
    window.addEventListener("keydown", onKey);
    return () => window.removeEventListener("keydown", onKey);
  }, [open, onClose]);

  if (!open) return null;

  const coreState: CoreState = capture.state === "denied"
    ? "denied"
    : capture.listening
      ? "listening"
      : busy
        ? "understanding"
        : "idle";

  return (
    <div className="fixed inset-0 z-[60] flex items-start justify-center overflow-y-auto bg-ink-990/70 p-4 pt-[8vh] backdrop-blur-md">
      <button
        type="button"
        aria-label="Close"
        className="absolute inset-0 cursor-default"
        onClick={onClose}
      />

      <div className="animate-slide-up relative w-full max-w-2xl overflow-hidden rounded-[20px] border border-ink-850 bg-ink-950 shadow-float">
        {/* Composer */}
        <div className="flex items-center gap-3 border-b border-ink-850 px-4 py-3">
          <AriaCore
            state={coreState}
            levels={capture.listening ? capture.levels : undefined}
            size="sm"
            showLabel={false}
            onActivate={
              capture.supported
                ? () =>
                    capture.listening
                      ? capture.stop()
                      : capture.start((t) => void send(t, "voice"))
                : undefined
            }
          />
          <div className="min-w-0 flex-1">
            <input
              ref={inputRef}
              value={capture.listening ? `${capture.transcript} ${capture.interim}`.trim() : input}
              onChange={(e) => setInput(e.target.value)}
              onKeyDown={(e) => e.key === "Enter" && void send(input)}
              readOnly={capture.listening}
              placeholder={
                capture.listening ? "Listening…" : "Ask A.R.I.A. anything, or tell it what happened…"
              }
              aria-label="Ask A.R.I.A."
              className="w-full bg-transparent text-[16px] tracking-[-0.01em] text-warm-50 outline-none placeholder:text-ink-500"
            />
            <p className="mt-1 text-[11px] text-ink-600">
              {capture.error ?? "Press Enter to send · Esc to close"}
            </p>
          </div>
          {/* A.R.I.A. Vision entry point. Labelled, not just an icon — a bare
              viewfinder glyph told no one it opens photo-based stocktaking. */}
          <button
            onClick={() => {
              onClose();
              router.push("/vision");
            }}
            aria-label="Scan a bill or shelf with A.R.I.A. Vision"
            title="Scan a bill or shelf with A.R.I.A. Vision"
            className="press flex shrink-0 items-center gap-1.5 rounded-lg border border-aria-500/25 bg-aria-500/[0.06] px-2.5 py-2 text-xs font-semibold text-aria-400 transition-colors hover:border-aria-500/45 hover:bg-aria-500/[0.12]"
          >
            <svg
              viewBox="0 0 24 24"
              className="h-4 w-4"
              fill="none"
              stroke="currentColor"
              strokeWidth={1.7}
              strokeLinecap="round"
              strokeLinejoin="round"
              aria-hidden
            >
              <path d="M3 9V6a1 1 0 0 1 1-1h3M21 9V6a1 1 0 0 0-1-1h-3M3 15v3a1 1 0 0 0 1 1h3M21 15v3a1 1 0 0 1-1 1h-3" />
              <circle cx="12" cy="12" r="3.2" />
            </svg>
            <span className="hidden sm:inline">Scan</span>
          </button>
          <button
            onClick={() => void send(input)}
            disabled={!input.trim() || busy}
            className="press shrink-0 rounded-lg bg-aria-600 px-4 py-2 text-sm font-semibold text-white shadow-soft transition-colors hover:bg-aria-700 disabled:cursor-not-allowed disabled:bg-ink-900 disabled:text-ink-500 disabled:shadow-none"
          >
            Send
          </button>
        </div>

        {/* Conversation */}
        <div className="max-h-[52vh] space-y-5 overflow-y-auto px-4 py-4">
          {turns.length === 0 && !busy && (
            <Suggestions agent={agent} onPick={(s) => void send(s)} />
          )}

          {turns.map((turn) => (
            <div key={turn.id} className="space-y-3">
              <div className="flex justify-end">
                <p className="max-w-[85%] rounded-2xl rounded-br-md border border-ink-850 bg-ink-900 px-4 py-2.5 text-[14.5px] leading-relaxed text-warm-50">
                  {turn.text}
                </p>
              </div>

              {turn.error && (
                <p className="rounded-xl border border-red-500/25 bg-red-950 px-4 py-3 text-sm text-red-300">
                  {turn.error}
                </p>
              )}

              {turn.result && (
                <div className="animate-slide-up space-y-3">
                  {/* The rule engine's command path still shows the full chain. */}
                  {turn.result.interpretation && (
                    <UnderstandingChain
                      transcript={turn.text}
                      result={turn.result.interpretation}
                    />
                  )}

                  <div
                    className={`relative overflow-hidden rounded-2xl border py-3.5 pl-5 pr-4 shadow-soft ${
                      turn.result.status === "error" || turn.result.status === "unavailable"
                        ? "border-red-500/25 bg-red-950"
                        : turn.result.requires_confirmation
                          ? "border-amber-500/25 bg-amber-950"
                          : "border-ink-850 bg-ink-950"
                    }`}
                  >
                    <span
                      className={`absolute inset-y-0 left-0 w-[3px] ${
                        turn.result.status === "error" || turn.result.status === "unavailable"
                          ? "bg-red-500"
                          : turn.result.requires_confirmation
                            ? "bg-amber-500"
                            : "bg-aria-500"
                      }`}
                    />
                    <p className="flex items-center gap-1.5 text-[10px] font-semibold uppercase tracking-[0.12em] text-aria-400">
                      <span className="h-1.5 w-1.5 rounded-full bg-aria-500" />
                      A.R.I.A.
                    </p>
                    <p className="mt-2 text-[15px] leading-relaxed text-warm-50">
                      {turn.result.response}
                    </p>
                    {turn.result.error && turn.result.status !== "completed" && (
                      <p className="mt-1.5 text-xs text-red-300">{turn.result.error}</p>
                    )}
                    <EngineBadge result={turn.result} />
                  </div>

                  {/* What the assistant actually did, from real tool results. */}
                  {turn.result.tool_calls.length > 0 && (
                    <ToolTrace calls={turn.result.tool_calls} />
                  )}

                  {/* Rule-engine question answers keep their visual. */}
                  {turn.result.answer_payload && (
                    <AnswerVisual result={turn.result.answer_payload} tone="dark" />
                  )}

                  {/* The confirmation gate. */}
                  {turn.result.pending_action && !turn.resolution && (
                    <div className="rounded-2xl border border-amber-500/25 bg-amber-950 px-4 py-3.5 shadow-soft">
                      <p className="text-sm leading-relaxed text-amber-300">{turn.result.pending_action.summary}</p>
                      <div className="mt-3 flex gap-2">
                        <button
                          onClick={() =>
                            void resolve(turn.id, turn.result!.pending_action!.id, true)
                          }
                          disabled={busy}
                          className="press rounded-lg bg-aria-600 px-4 py-2 text-sm font-semibold text-white shadow-soft transition-colors hover:bg-aria-700 disabled:opacity-50"
                        >
                          Confirm
                        </button>
                        <button
                          onClick={() =>
                            void resolve(turn.id, turn.result!.pending_action!.id, false)
                          }
                          disabled={busy}
                          className="press rounded-lg border border-ink-850 bg-ink-900 px-4 py-2 text-sm font-medium text-ink-400 transition-colors hover:text-warm-50 disabled:opacity-50"
                        >
                          Cancel
                        </button>
                      </div>
                    </div>
                  )}

                  {turn.resolution && (
                    <p
                      className={`rounded-xl border px-4 py-3 text-sm leading-relaxed ${
                        turn.resolution.ok
                          ? "border-aria-500/25 bg-aria-950 text-aria-400"
                          : "border-red-500/25 bg-red-950 text-red-300"
                      }`}
                    >
                      {turn.resolution.text}
                    </p>
                  )}
                </div>
              )}
            </div>
          ))}

          {busy && (
            <p className="flex items-center gap-2.5 text-sm text-ink-400">
              <span className="h-3.5 w-3.5 animate-sweep rounded-full border-2 border-transparent border-t-aria-500" />
              Checking your business…
            </p>
          )}
          <div ref={endRef} />
        </div>
      </div>
    </div>
  );
}

/** Says plainly which engine answered. Never implies AI when there was none. */
function EngineBadge({ result }: { result: AriaChatResponse }) {
  if (result.engine === "agent") {
    return (
      <p className="mt-2.5 text-[11px] text-ink-600">
        A.R.I.A. agent{result.model ? ` · ${result.model}` : ""}
      </p>
    );
  }
  return (
    <p className="mt-2.5 text-[11px] text-ink-600">
      Built-in engine · {result.notice ?? "AI is not configured."}
    </p>
  );
}

/** The real tool results behind an answer, so the work is inspectable. */
function ToolTrace({ calls }: { calls: AriaChatResponse["tool_calls"] }) {
  return (
    <div className="space-y-1.5">
      {calls.map((call, i) => {
        const failed = !!call.result?.error;
        return (
          <div
            key={i}
            className={`flex items-start gap-2.5 rounded-lg border px-3 py-2 text-xs ${
              failed
                ? "border-red-500/25 bg-red-950 text-red-300"
                : "border-ink-850 bg-ink-900 text-ink-400"
            }`}
          >
            <span className={failed ? "text-red-400" : "text-emerald-500"}>{failed ? "✕" : "✓"}</span>
            <div className="min-w-0">
              <span className="font-semibold capitalize text-warm-50">{call.tool.replace(/_/g, " ")}</span>
              {failed ? (
                <span className="ml-1.5">{call.result.error}</span>
              ) : (
                call.result?.resulting_quantity !== undefined && (
                  <span className="ml-1.5 tabular-nums">
                    {call.result.product} → {call.result.resulting_quantity}{" "}
                    {call.result.resulting_unit}
                  </span>
                )
              )}
            </div>
          </div>
        );
      })}
    </div>
  );
}

function Suggestions({
  agent,
  onPick,
}: {
  agent: AgentStatus | null;
  onPick: (s: string) => void;
}) {
  const { summary } = useBusiness();
  const spoken = summary?.sample_utterances ?? [];

  return (
    <div className="space-y-4">
      {agent && !agent.agent_available && (
        <p className="rounded-lg border border-ink-850 bg-ink-900 px-3.5 py-2.5 text-[11px] leading-relaxed text-ink-400">
          {agent.reason} Until then I answer with the built-in engine, which handles the phrasing
          it was built for.
        </p>
      )}

      {spoken.length > 0 && (
        <div>
          <p className="eyebrow mb-2.5">
            Tell me what happened
          </p>
          <div className="flex flex-wrap gap-2">
            {spoken.map((s) => (
              <Chip key={s} onClick={() => onPick(s)}>
                {s}
              </Chip>
            ))}
          </div>
        </div>
      )}
      <div>
        <p className="eyebrow mb-2.5">
          Or ask me
        </p>
        <div className="flex flex-wrap gap-2">
          {[
            "What's running low?",
            "What should I order?",
            "Who owes me money?",
            "What changed today?",
          ].map((s) => (
            <Chip key={s} onClick={() => onPick(s)}>
              {s}
            </Chip>
          ))}
        </div>
      </div>
    </div>
  );
}

function Chip({ children, onClick }: { children: React.ReactNode; onClick: () => void }) {
  return (
    <button
      onClick={onClick}
      className="press rounded-full border border-ink-850 bg-ink-900 px-3.5 py-1.5 text-xs font-medium text-ink-300 transition-all hover:border-aria-500/40 hover:bg-aria-500/[0.06] hover:text-aria-400"
    >
      {children}
    </button>
  );
}
