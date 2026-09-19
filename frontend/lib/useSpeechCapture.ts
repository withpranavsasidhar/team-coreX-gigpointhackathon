"use client";

import { useCallback, useEffect, useRef, useState } from "react";

export type CaptureState = "idle" | "listening" | "denied" | "unsupported";

/**
 * Client-side speech provider, kept behind a stable hook interface so the
 * capture engine can be replaced (native app bridge, server-side STT) without
 * the voice screen changing.
 *
 * Audio levels come from a real AnalyserNode rather than a decorative
 * animation, so the waveform reflects what the microphone actually hears.
 */
export function useSpeechCapture(lang: string) {
  const [state, setState] = useState<CaptureState>("idle");
  const [transcript, setTranscript] = useState("");
  const [interim, setInterim] = useState("");
  const [levels, setLevels] = useState<number[]>(() => new Array(13).fill(0.08));
  const [error, setError] = useState<string | null>(null);

  const recognitionRef = useRef<SpeechRecognitionLike | null>(null);
  const streamRef = useRef<MediaStream | null>(null);
  const audioCtxRef = useRef<AudioContext | null>(null);
  const rafRef = useRef<number | null>(null);
  const finalRef = useRef("");
  const onDoneRef = useRef<((text: string) => void) | null>(null);

  useEffect(() => {
    const supported =
      typeof window !== "undefined" && !!(window.SpeechRecognition || window.webkitSpeechRecognition);
    if (!supported) setState("unsupported");
  }, []);

  const teardownAudio = useCallback(() => {
    if (rafRef.current !== null) cancelAnimationFrame(rafRef.current);
    rafRef.current = null;
    streamRef.current?.getTracks().forEach((t) => t.stop());
    streamRef.current = null;
    audioCtxRef.current?.close().catch(() => {});
    audioCtxRef.current = null;
    setLevels(new Array(13).fill(0.08));
  }, []);

  const startMeter = useCallback(async () => {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      streamRef.current = stream;
      const ctx = new AudioContext();
      audioCtxRef.current = ctx;
      const analyser = ctx.createAnalyser();
      analyser.fftSize = 64;
      ctx.createMediaStreamSource(stream).connect(analyser);
      const bins = new Uint8Array(analyser.frequencyBinCount);

      const tick = () => {
        analyser.getByteFrequencyData(bins);
        const next: number[] = [];
        for (let i = 0; i < 13; i++) {
          const v = bins[i + 2] ?? 0;
          next.push(Math.max(0.08, Math.min(v / 180, 1)));
        }
        setLevels(next);
        rafRef.current = requestAnimationFrame(tick);
      };
      tick();
    } catch {
      // Metering is a nicety; recognition can still proceed without it.
    }
  }, []);

  const stop = useCallback(() => {
    recognitionRef.current?.stop();
    recognitionRef.current = null;
    teardownAudio();
    setState((s) => (s === "listening" ? "idle" : s));
  }, [teardownAudio]);

  const start = useCallback(
    (onDone?: (text: string) => void) => {
      const Ctor = window.SpeechRecognition || window.webkitSpeechRecognition;
      if (!Ctor) {
        setState("unsupported");
        return;
      }

      onDoneRef.current = onDone ?? null;
      finalRef.current = "";
      setTranscript("");
      setInterim("");
      setError(null);

      const recognition = new Ctor();
      recognition.lang = lang;
      recognition.continuous = false;
      recognition.interimResults = true;
      recognition.maxAlternatives = 1;

      recognition.onstart = () => setState("listening");

      recognition.onresult = (event) => {
        let finalText = finalRef.current;
        let interimText = "";
        for (let i = event.resultIndex; i < event.results.length; i++) {
          const result = event.results[i];
          if (result.isFinal) finalText += result[0].transcript;
          else interimText += result[0].transcript;
        }
        finalRef.current = finalText;
        setTranscript(finalText);
        setInterim(interimText);
      };

      recognition.onerror = (event) => {
        if (event.error === "not-allowed" || event.error === "service-not-allowed") {
          setState("denied");
          setError("Microphone access was blocked. You can type instead.");
        } else if (event.error !== "aborted" && event.error !== "no-speech") {
          setError("Speech recognition failed. You can type instead.");
        }
      };

      recognition.onend = () => {
        teardownAudio();
        setState((s) => (s === "listening" ? "idle" : s));
        const text = (finalRef.current || "").trim();
        if (text) onDoneRef.current?.(text);
      };

      recognitionRef.current = recognition;
      recognition.start();
      void startMeter();
    },
    [lang, startMeter, teardownAudio]
  );

  useEffect(() => () => {
    recognitionRef.current?.abort();
    teardownAudio();
  }, [teardownAudio]);

  return {
    state,
    supported: state !== "unsupported",
    listening: state === "listening",
    transcript,
    interim,
    levels,
    error,
    start,
    stop,
    reset: () => {
      finalRef.current = "";
      setTranscript("");
      setInterim("");
      setError(null);
    },
  };
}
