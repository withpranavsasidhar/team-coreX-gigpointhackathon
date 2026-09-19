"use client";

import { useCallback, useEffect, useRef, useState } from "react";

import { AnswerVisual } from "@/components/intelligence/AnswerVisual";
import { Button, Card, SectionLabel, inputClass } from "@/components/ui/Primitives";
import { ErrorState } from "@/components/ui/States";
import { api } from "@/lib/api";
import { useBusiness } from "@/lib/BusinessContext";
import { useSpeechCapture } from "@/lib/useSpeechCapture";
import type { QueryAnswer } from "@/lib/types";

const SUGGESTIONS = [
  "What's running low?",
  "What should I order?",
  "Why is rice stock low?",
  "Where did my biscuits go?",
  "What did I sell today?",
  "What did Ramesh take?",
];

interface Turn {
  question: string;
  result: QueryAnswer | null;
  error?: string;
}

export default function AskPage() {
  const { business } = useBusiness();
  const [turns, setTurns] = useState<Turn[]>([]);
  const [question, setQuestion] = useState("");
  const [thinking, setThinking] = useState(false);
  const endRef = useRef<HTMLDivElement>(null);

  const [lang, setLang] = useState("en-IN");
  const capture = useSpeechCapture(lang);

  useEffect(() => {
    try {
      const saved = localStorage.getItem("aria.language");
      if (saved) setLang(saved);
    } catch {
      /* private mode */
    }
  }, []);

  useEffect(() => {
    endRef.current?.scrollIntoView({ behavior: "smooth", block: "end" });
  }, [turns, thinking]);

  const send = useCallback(
    async (text: string) => {
      const asked = text.trim();
      if (!business || !asked) return;
      setQuestion("");
      setThinking(true);
      try {
        const result = await api.ask(business.id, asked, lang.split("-")[0]);
        setTurns((t) => [...t, { question: asked, result }]);
      } catch (e) {
        setTurns((t) => [...t, { question: asked, result: null, error: (e as Error).message }]);
      } finally {
        setThinking(false);
      }
    },
    [business, lang]
  );

  return (
    <div className="space-y-6">
      <header>
        <h1 className="text-[28px] font-semibold leading-tight text-warm-50">Ask A.R.I.A.</h1>
        <p className="mt-1 text-sm text-ink-400">
          Anything about your stock — answered from what actually happened.
        </p>
      </header>

      {turns.length === 0 && !thinking && (
        <div className="space-y-3">
          <SectionLabel>Try asking</SectionLabel>
          <div className="flex flex-wrap gap-2">
            {SUGGESTIONS.map((s) => (
              <button
                key={s}
                onClick={() => void send(s)}
                className="focus-ring rounded-full border border-ink-850 bg-ink-950 px-4 py-2 text-sm text-ink-400 transition-colors hover:bg-ink-900"
              >
                {s}
              </button>
            ))}
          </div>
        </div>
      )}

      <div className="space-y-6">
        {turns.map((turn, i) => (
          <div key={i} className="space-y-3">
            <div className="flex justify-end">
              <p className="max-w-[85%] rounded-2xl rounded-br-sm bg-ink-900 px-4 py-2.5 text-sm text-warm-50">
                {turn.question}
              </p>
            </div>

            {turn.error ? (
              <ErrorState message={turn.error} />
            ) : (
              turn.result && (
                <div className="animate-slide-up space-y-3">
                  <Card className="px-5 py-4">
                    <p className="text-[15px] leading-relaxed text-warm-50">{turn.result.answer}</p>
                  </Card>
                  <AnswerVisual result={turn.result} />
                </div>
              )
            )}
          </div>
        ))}

        {thinking && (
          <Card className="flex items-center gap-3 px-5 py-4">
            <span className="h-4 w-4 animate-spin rounded-full border-2 border-aria-500/30 border-t-aria-500" />
            <span className="text-sm text-ink-400">Checking your records…</span>
          </Card>
        )}
        <div ref={endRef} />
      </div>

      <div className="sticky bottom-24 flex gap-2 bg-ink-990/80 py-2 backdrop-blur">
        <input
          value={capture.listening ? `${capture.transcript} ${capture.interim}`.trim() : question}
          onChange={(e) => setQuestion(e.target.value)}
          onKeyDown={(e) => e.key === "Enter" && void send(question)}
          placeholder={capture.listening ? "Listening…" : "Ask about your stock…"}
          className={inputClass}
          aria-label="Ask a question"
          readOnly={capture.listening}
        />
        {capture.supported && (
          <Button
            variant="secondary"
            onClick={() => (capture.listening ? capture.stop() : capture.start((t) => void send(t)))}
          >
            {capture.listening ? "Stop" : "🎙"}
          </Button>
        )}
        <Button onClick={() => void send(question)} disabled={!question.trim() || thinking}>
          Ask
        </Button>
      </div>
    </div>
  );
}
