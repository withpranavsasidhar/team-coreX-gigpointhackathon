"use client";

import { useCallback, useEffect, useRef, useState } from "react";
import { useRouter } from "next/navigation";

import { CameraCapture } from "@/components/vision/CameraCapture";
import { VisionReview, toReviewLines, type ReviewLine } from "@/components/vision/VisionReview";
import { Button, Card, PageHeader, inputClass } from "@/components/ui/Primitives";
import { ErrorState, Toast } from "@/components/ui/States";
import { api } from "@/lib/api";
import { useBusiness } from "@/lib/BusinessContext";
import type { VisionAnalysis, VisionApplyResult, VisionStatus } from "@/lib/types";

type Stage = "choose" | "camera" | "analyzing" | "review" | "done";

/**
 * A.R.I.A. Vision.
 *
 * Show it a stock list, a bill or a shelf. It reads, matches against the real
 * catalogue, and proposes — then waits. Inventory only moves after the owner
 * has reviewed the lines and pressed the button.
 */
export default function VisionPage() {
  const router = useRouter();
  const { business, summary } = useBusiness();

  const [status, setStatus] = useState<VisionStatus | null>(null);
  const [stage, setStage] = useState<Stage>("choose");
  const [hint, setHint] = useState("");
  const [analysis, setAnalysis] = useState<VisionAnalysis | null>(null);
  const [lines, setLines] = useState<ReviewLine[]>([]);
  const [applying, setApplying] = useState(false);
  const [result, setResult] = useState<VisionApplyResult | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [toast, setToast] = useState<string | null>(null);
  const fileRef = useRef<HTMLInputElement>(null);

  useEffect(() => {
    api.visionStatus().then(setStatus).catch(() => setStatus(null));
  }, []);

  useEffect(() => {
    if (!toast) return;
    const id = setTimeout(() => setToast(null), 3500);
    return () => clearTimeout(id);
  }, [toast]);

  const analyze = useCallback(
    async (dataUri: string) => {
      if (!business) return;
      setStage("analyzing");
      setError(null);
      setResult(null);
      try {
        const found = await api.visionAnalyze(business.id, dataUri, hint);
        if (found.error) {
          setError(found.error);
          setStage("choose");
          return;
        }
        setAnalysis(found);
        setLines(toReviewLines(found));
        setStage("review");
      } catch (e) {
        setError((e as Error).message);
        setStage("choose");
      }
    },
    [business, hint]
  );

  const onFile = useCallback(
    (file: File | undefined) => {
      if (!file) return;
      const maxMb = status?.max_image_mb ?? 8;
      if (file.size > maxMb * 1024 * 1024) {
        setError(`That image is ${(file.size / 1024 / 1024).toFixed(1)} MB. Please use one under ${maxMb} MB.`);
        return;
      }
      if (!/^image\/(jpeg|jpg|png|webp)$/i.test(file.type)) {
        setError("Use a JPG, PNG or WEBP photo.");
        return;
      }
      const reader = new FileReader();
      reader.onload = () => void analyze(String(reader.result));
      reader.onerror = () => setError("That file could not be read.");
      reader.readAsDataURL(file);
    },
    [analyze, status]
  );

  const apply = useCallback(async () => {
    if (!business || !analysis?.analysis_id) return;
    setApplying(true);
    setError(null);
    try {
      const payload = lines
        .filter((l) => l.include && l.chosenProductName && Number(l.editedQuantity) > 0)
        .map((l) => ({
          product_name: l.chosenProductName,
          quantity: Number(l.editedQuantity),
          unit: l.editedUnit || undefined,
          price: l.price ?? undefined,
        }));

      const applied = await api.visionApply(business.id, analysis.analysis_id, payload);
      setResult(applied);
      setStage("done");
      if (applied.counts.applied > 0) {
        setToast(applied.summary);
        router.refresh();
      }
    } catch (e) {
      setError((e as Error).message);
    } finally {
      setApplying(false);
    }
  }, [business, analysis, lines, router]);

  const reset = () => {
    setStage("choose");
    setAnalysis(null);
    setLines([]);
    setResult(null);
    setError(null);
  };

  return (
    <div className="space-y-6">
      <PageHeader
        title="A.R.I.A. Vision"
        subtitle="Show me your stock list, a bill, or a shelf."
      />

      {status && !status.available && (
        <Card tone="raised" className="p-4">
          <p className="text-sm text-amber-300">
            A.R.I.A. Vision requires a vision-capable AI model.
          </p>
          <p className="mt-1 text-xs leading-relaxed text-ink-400">
            {status.reason} Everything else in A.R.I.A. keeps working as it does now.
          </p>
        </Card>
      )}

      {error && <ErrorState message={error} title="I couldn't read that" />}

      {stage === "choose" && (
        <div className="space-y-4">
          <Card className="p-5">
            <label className="block">
              <span className="mb-1.5 block text-sm font-medium text-ink-300">
                What am I looking at? <span className="text-ink-500">(optional)</span>
              </span>
              <input
                value={hint}
                onChange={(e) => setHint(e.target.value)}
                placeholder="e.g. today's delivery note"
                aria-label="Image hint"
                className={inputClass}
              />
            </label>
          </Card>

          <div className="grid gap-3 sm:grid-cols-2">
            <button
              onClick={() => setStage("camera")}
              disabled={!status?.available}
              className="focus-ring rounded-2xl border border-ink-850 bg-ink-950 p-6 text-left transition-colors hover:border-aria-500/30 hover:bg-ink-900 disabled:cursor-not-allowed disabled:opacity-50"
            >
              <span className="text-2xl" aria-hidden>
                📷
              </span>
              <p className="mt-2 text-sm font-medium text-warm-50">Scan with camera</p>
              <p className="mt-0.5 text-xs text-ink-500">
                Point at a list, a bill, or your shelves
              </p>
            </button>

            <button
              onClick={() => fileRef.current?.click()}
              disabled={!status?.available}
              className="focus-ring rounded-2xl border border-ink-850 bg-ink-950 p-6 text-left transition-colors hover:border-aria-500/30 hover:bg-ink-900 disabled:cursor-not-allowed disabled:opacity-50"
            >
              <span className="text-2xl" aria-hidden>
                🖼
              </span>
              <p className="mt-2 text-sm font-medium text-warm-50">Upload an image</p>
              <p className="mt-0.5 text-xs text-ink-500">JPG, PNG or WEBP</p>
            </button>
          </div>

          <input
            ref={fileRef}
            type="file"
            accept="image/jpeg,image/png,image/webp"
            className="hidden"
            aria-label="Upload an image"
            onChange={(e) => {
              onFile(e.target.files?.[0]);
              e.target.value = "";
            }}
          />

          <p className="text-xs leading-relaxed text-ink-500">
            Your photo is read and then discarded — only the business lines it contains are
            kept, so nothing is added to your inventory until you confirm it.
          </p>
        </div>
      )}

      {stage === "camera" && (
        <CameraCapture onCapture={(uri) => void analyze(uri)} onCancel={reset} />
      )}

      {stage === "analyzing" && (
        <Card className="flex items-center gap-3 px-5 py-8">
          <span className="h-4 w-4 animate-sweep rounded-full border-2 border-transparent border-t-aria-500" />
          <span className="text-sm text-ink-300">Reading your image…</span>
        </Card>
      )}

      {stage === "review" && analysis && (
        <>
          {analysis.items.length === 0 ? (
            <Card className="px-5 py-8 text-center">
              <p className="text-sm text-warm-50">{analysis.summary}</p>
              {analysis.quality_advice && analysis.quality_advice.length > 0 && (
                <ul className="mt-2 space-y-0.5 text-xs text-ink-400">
                  {analysis.quality_advice.map((a) => (
                    <li key={a}>· {a}</li>
                  ))}
                </ul>
              )}
              <div className="mt-5 flex justify-center">
                <Button variant="secondary" onClick={reset}>
                  Try another image
                </Button>
              </div>
            </Card>
          ) : (
            <VisionReview
              analysis={analysis}
              lines={lines}
              onChange={setLines}
              onApply={() => void apply()}
              onCancel={reset}
              applying={applying}
              units={summary?.units ?? []}
            />
          )}
        </>
      )}

      {stage === "done" && result && (
        <div className="space-y-4">
          <Card
            className={`p-5 ${
              result.counts.applied > 0 ? "border-aria-500/30" : "border-red-500/30"
            }`}
          >
            <p className="text-[15px] text-warm-50">{result.summary}</p>
            {result.applied.length > 0 && (
              <ul className="mt-3 space-y-1.5">
                {result.applied.map((a, i) => (
                  <li key={i} className="flex items-center justify-between text-sm">
                    <span className="text-ink-300">{a.product}</span>
                    <span className="tabular-nums text-aria-400">
                      {a.applied_change > 0 ? "+" : ""}
                      {a.applied_change} → {a.resulting_quantity} {a.resulting_unit}
                    </span>
                  </li>
                ))}
              </ul>
            )}
            {result.failed.length > 0 && (
              <ul className="mt-3 space-y-1 border-t border-ink-850 pt-3">
                {result.failed.map((f, i) => (
                  <li key={i} className="text-xs text-red-300">
                    · {f.error}
                  </li>
                ))}
              </ul>
            )}
          </Card>
          <div className="flex gap-2">
            <Button onClick={reset}>Scan another</Button>
            <Button variant="secondary" onClick={() => router.push("/inventory")}>
              View stock
            </Button>
          </div>
        </div>
      )}

      {toast && <Toast message={toast} />}
    </div>
  );
}
