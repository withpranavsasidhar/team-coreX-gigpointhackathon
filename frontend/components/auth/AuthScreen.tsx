"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import { api } from "@/lib/api";
import { useBusiness } from "@/lib/BusinessContext";
import { Button, Card, inputClass } from "@/components/ui/Primitives";
import { ErrorState } from "@/components/ui/States";
import { AriaMark } from "@/components/aria/AriaMark";
import { ThemeSwitcher } from "@/lib/theme";

export function AuthScreen() {
  const router = useRouter();
  const { loginUser, businesses, switchBusiness } = useBusiness();
  const [mode, setMode] = useState<"signin" | "register" | "select_business">("signin");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // Form states
  const [name, setName] = useState("");
  const [phone, setPhone] = useState("");
  const [password, setPassword] = useState("");
  const [confirmPassword, setConfirmPassword] = useState("");

  const validatePhone = (p: string) => {
    const digits = p.replace(/\D/g, "");
    if (digits.length < 10) return "Please enter a valid 10-digit mobile number.";
    return null;
  };

  const handleLogin = async (e: React.FormEvent) => {
    e.preventDefault();
    const phoneErr = validatePhone(phone);
    if (phoneErr) {
      setError(phoneErr);
      return;
    }

    setLoading(true);
    setError(null);
    try {
      const res = await api.login({ phone, password });
      loginUser(res);
      if (res.businesses.length === 0) {
        router.push("/onboarding");
      } else if (res.businesses.length > 1) {
        setMode("select_business");
      }
    } catch (err) {
      setError((err as Error).message);
    } finally {
      setLoading(false);
    }
  };

  const handleRegister = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!name.trim()) {
      setError("Full Name is required.");
      return;
    }
    const phoneErr = validatePhone(phone);
    if (phoneErr) {
      setError(phoneErr);
      return;
    }
    if (password.length < 4) {
      setError("Password must be at least 4 characters.");
      return;
    }
    if (password !== confirmPassword) {
      setError("Passwords do not match.");
      return;
    }

    setLoading(true);
    setError(null);
    try {
      const res = await api.register({
        name,
        phone,
        password,
        confirm_password: confirmPassword,
      });
      loginUser(res);
      router.push("/onboarding");
    } catch (err) {
      setError((err as Error).message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="relative flex min-h-dvh flex-col items-center justify-center bg-ink-990 p-4 text-warm-50">
      {/* The warm red light A.R.I.A. lives in. */}
      <div className="aria-aura pointer-events-none absolute inset-x-0 top-0 h-[55vh]" />

      <div className="absolute right-4 top-4 z-10">
        <ThemeSwitcher compact />
      </div>

      <div className="relative w-full max-w-md space-y-7">
        {/* Header Branding */}
        <div className="space-y-4 text-center">
          <div className="relative mx-auto grid h-20 w-20 place-items-center">
            <span className="absolute inset-0 animate-breathe rounded-full bg-aria-500/15 blur-xl" />
            <AriaMark className="relative h-20 w-20 drop-shadow-sm" />
          </div>
          <div>
            <h1 className="font-display text-[32px] font-bold leading-none tracking-tight text-warm-50">
              A.R.I.A.
            </h1>
            <p className="mt-2.5 text-xs tracking-wide text-ink-400">
              <span className="font-bold text-aria-500">A</span>daptive{" "}
              <span className="font-bold text-aria-500">R</span>etail{" "}
              <span className="font-bold text-aria-500">I</span>ntelligence{" "}
              <span className="font-bold text-aria-500">A</span>ssistant
            </p>
          </div>
        </div>

        <Card className="p-6 shadow-panel">
          {/* Mode Switcher Tabs */}
          {mode !== "select_business" && (
            <div className="mb-6 grid grid-cols-2 gap-1 rounded-xl border border-ink-850 bg-ink-900 p-1">
              <button
                type="button"
                onClick={() => {
                  setMode("signin");
                  setError(null);
                }}
                className={`rounded-lg py-2.5 text-xs font-semibold transition-all duration-200 ${
                  mode === "signin"
                    ? "bg-ink-950 text-aria-400 shadow-soft"
                    : "text-ink-500 hover:text-warm-50"
                }`}
              >
                Sign In
              </button>
              <button
                type="button"
                onClick={() => {
                  setMode("register");
                  setError(null);
                }}
                className={`rounded-lg py-2.5 text-xs font-semibold transition-all duration-200 ${
                  mode === "register"
                    ? "bg-ink-950 text-aria-400 shadow-soft"
                    : "text-ink-500 hover:text-warm-50"
                }`}
              >
                Create Account
              </button>
            </div>
          )}

          {error && (
            <div className="mb-4">
              <ErrorState message={error} />
            </div>
          )}

          {mode === "signin" && (
            <form onSubmit={handleLogin} className="space-y-4">
              <div>
                <label className="mb-1.5 block text-[13px] font-semibold text-ink-300">
                  Mobile Number
                </label>
                <input
                  type="tel"
                  value={phone}
                  onChange={(e) => setPhone(e.target.value)}
                  placeholder="e.g. 9876543210"
                  required
                  className={inputClass}
                />
              </div>
              <div>
                <label className="mb-1.5 block text-[13px] font-semibold text-ink-300">
                  Password
                </label>
                <input
                  type="password"
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  placeholder="••••••••"
                  required
                  className={inputClass}
                />
              </div>
              <Button type="submit" disabled={loading} className="w-full">
                {loading ? "Signing in..." : "Sign In"}
              </Button>
            </form>
          )}

          {mode === "register" && (
            <form onSubmit={handleRegister} className="space-y-4">
              <div>
                <label className="mb-1.5 block text-[13px] font-semibold text-ink-300">
                  Full Name
                </label>
                <input
                  type="text"
                  value={name}
                  onChange={(e) => setName(e.target.value)}
                  placeholder="e.g. Pranav Sasidhar"
                  required
                  className={inputClass}
                />
              </div>
              <div>
                <label className="mb-1.5 block text-[13px] font-semibold text-ink-300">
                  Mobile Number
                </label>
                <input
                  type="tel"
                  value={phone}
                  onChange={(e) => setPhone(e.target.value)}
                  placeholder="e.g. 9876543210"
                  required
                  className={inputClass}
                />
              </div>
              <div>
                <label className="mb-1.5 block text-[13px] font-semibold text-ink-300">
                  Password
                </label>
                <input
                  type="password"
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  placeholder="••••••••"
                  required
                  className={inputClass}
                />
              </div>
              <div>
                <label className="mb-1.5 block text-[13px] font-semibold text-ink-300">
                  Confirm Password
                </label>
                <input
                  type="password"
                  value={confirmPassword}
                  onChange={(e) => setConfirmPassword(e.target.value)}
                  placeholder="••••••••"
                  required
                  className={inputClass}
                />
              </div>
              <Button type="submit" disabled={loading} className="w-full">
                {loading ? "Creating account..." : "Create Account & Setup Store"}
              </Button>
            </form>
          )}

          {mode === "select_business" && (
            <div className="space-y-3">
              <h2 className="text-base font-semibold tracking-tight text-warm-50">
                Choose your business
              </h2>
              <p className="mb-3 text-xs text-ink-400">Select a store playground to open:</p>
              {businesses.map((b) => (
                <button
                  key={b.id}
                  onClick={async () => {
                    await switchBusiness(b.id);
                  }}
                  className="press flex w-full items-center justify-between rounded-xl border border-ink-850 bg-ink-900 p-3.5 text-left transition-all hover:border-aria-500/35 hover:bg-aria-500/[0.05]"
                >
                  <div>
                    <p className="text-sm font-semibold text-warm-50">{b.business_name}</p>
                    <p className="text-xs capitalize text-ink-400">{b.business_type}</p>
                  </div>
                  <span className="text-xs font-semibold text-aria-400">Open →</span>
                </button>
              ))}
              <div className="pt-2">
                <Button
                  variant="secondary"
                  onClick={() => router.push("/onboarding")}
                  className="w-full"
                >
                  + Add Another Business
                </Button>
              </div>
            </div>
          )}
        </Card>

        <p className="text-center text-[11px] leading-relaxed text-ink-500">
          Speak. Stock. Smarter. — in English, తెలుగు or हिन्दी.
        </p>
      </div>
    </div>
  );
}
