"use client";

import { useCallback, useEffect, useRef, useState } from "react";

import { Button } from "@/components/ui/Primitives";

/**
 * Real device camera capture.
 *
 * Uses getUserMedia and draws the live frame to a canvas. There is no stock
 * photo and no placeholder path: if the camera cannot be opened, this says so
 * and offers upload instead.
 */

type Stage = "idle" | "starting" | "live" | "captured" | "denied" | "unsupported";

export function CameraCapture({
  onCapture,
  onCancel,
}: {
  onCapture: (dataUri: string) => void;
  onCancel: () => void;
}) {
  const videoRef = useRef<HTMLVideoElement>(null);
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const streamRef = useRef<MediaStream | null>(null);
  const [stage, setStage] = useState<Stage>("idle");
  const [error, setError] = useState<string | null>(null);
  const [preview, setPreview] = useState<string | null>(null);

  const stop = useCallback(() => {
    streamRef.current?.getTracks().forEach((t) => t.stop());
    streamRef.current = null;
  }, []);

  const start = useCallback(async () => {
    if (typeof navigator === "undefined" || !navigator.mediaDevices?.getUserMedia) {
      setStage("unsupported");
      setError("This browser cannot open a camera. You can upload a photo instead.");
      return;
    }

    setStage("starting");
    setError(null);
    try {
      const stream = await navigator.mediaDevices.getUserMedia({
        // Rear camera on a phone; falls back to whatever exists.
        video: { facingMode: { ideal: "environment" }, width: { ideal: 1920 } },
        audio: false,
      });
      streamRef.current = stream;
      if (videoRef.current) {
        videoRef.current.srcObject = stream;
        await videoRef.current.play().catch(() => {});
      }
      setStage("live");
    } catch (e) {
      const name = (e as Error).name;
      stop();
      if (name === "NotAllowedError" || name === "SecurityError") {
        setStage("denied");
        setError("Camera access is required to scan an image.");
      } else if (name === "NotFoundError" || name === "OverconstrainedError") {
        setStage("unsupported");
        setError("No camera was found on this device.");
      } else {
        setStage("unsupported");
        setError("The camera could not be opened.");
      }
    }
  }, [stop]);

  useEffect(() => {
    void start();
    return stop;
  }, [start, stop]);

  const capture = useCallback(() => {
    const video = videoRef.current;
    const canvas = canvasRef.current;
    if (!video || !canvas || !video.videoWidth) return;

    canvas.width = video.videoWidth;
    canvas.height = video.videoHeight;
    const context = canvas.getContext("2d");
    if (!context) return;
    context.drawImage(video, 0, 0, canvas.width, canvas.height);

    // JPEG at 0.88 keeps handwriting legible without an oversized payload.
    setPreview(canvas.toDataURL("image/jpeg", 0.88));
    setStage("captured");
    stop();
  }, [stop]);

  const retake = useCallback(() => {
    setPreview(null);
    void start();
  }, [start]);

  return (
    <div className="space-y-4">
      <div className="relative overflow-hidden rounded-2xl border border-ink-850 bg-ink-950">
        {stage === "captured" && preview ? (
          // eslint-disable-next-line @next/next/no-img-element
          <img src={preview} alt="Captured photo" className="w-full" />
        ) : (
          <video
            ref={videoRef}
            playsInline
            muted
            className={`w-full ${stage === "live" ? "" : "opacity-40"}`}
            style={{ aspectRatio: "4 / 3", objectFit: "cover" }}
          />
        )}

        {stage === "starting" && (
          <p className="absolute inset-0 grid place-items-center text-sm text-ink-400">
            Opening camera…
          </p>
        )}

        {(stage === "denied" || stage === "unsupported") && (
          <div className="absolute inset-0 grid place-items-center px-6 text-center">
            <div>
              <p className="text-sm text-red-300">{error}</p>
              <p className="mt-1 text-xs text-ink-500">
                You can upload a photo from your device instead.
              </p>
            </div>
          </div>
        )}
      </div>

      <canvas ref={canvasRef} className="hidden" />

      <div className="flex flex-wrap gap-2">
        {stage === "live" && <Button onClick={capture}>Capture</Button>}
        {stage === "captured" && (
          <>
            <Button onClick={() => preview && onCapture(preview)}>Use photo</Button>
            <Button variant="secondary" onClick={retake}>
              Retake
            </Button>
          </>
        )}
        {(stage === "denied" || stage === "unsupported") && (
          <Button variant="secondary" onClick={() => void start()}>
            Try camera again
          </Button>
        )}
        <Button variant="secondary" onClick={() => { stop(); onCancel(); }}>
          Cancel
        </Button>
      </div>
    </div>
  );
}
