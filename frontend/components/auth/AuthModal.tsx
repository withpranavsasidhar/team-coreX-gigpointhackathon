"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import { api } from "@/lib/api";
import { useBusiness } from "@/lib/BusinessContext";
import { Button, Card, inputClass } from "@/components/ui/Primitives";
import { ErrorState } from "@/components/ui/States";

interface AuthModalProps {
  isOpen: boolean;
  onClose: () => void;
}

export function AuthModal({ isOpen, onClose }: AuthModalProps) {
  const router = useRouter();
  const { loginUser, user, businesses, switchBusiness } = useBusiness();
  const [mode, setMode] = useState<"signin" | "register" | "select_business">("signin");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // Form states
  const [name, setName] = useState("");
  const [phone, setPhone] = useState("");
  const [password, setPassword] = useState("");
  const [confirmPassword, setConfirmPassword] = useState("");

  if (!isOpen) return null;

  const handleLogin = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError(null);
    try {
      const res = await api.login({ phone, password });
      loginUser(res);
      if (res.businesses.length === 0) {
        router.push("/onboarding");
      } else if (res.businesses.length > 1) {
        setMode("select_business");
      } else {
        onClose();
      }
    } catch (err) {
      setError((err as Error).message);
    } finally {
      setLoading(false);
    }
  };

  const handleRegister = async (e: React.FormEvent) => {
    e.preventDefault();
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
      onClose();
    } catch (err) {
      setError((err as Error).message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-ink-990/80 p-4 backdrop-blur-sm">
      <Card className="w-full max-w-md p-6">
        <div className="flex items-center justify-between border-b border-ink-850 pb-4">
          <h2 className="text-lg font-semibold text-warm-50">
            {mode === "signin"
              ? "Sign In to A.R.I.A."
              : mode === "register"
              ? "Create Account"
              : "Choose Your Business"}
          </h2>
          <button
            onClick={onClose}
            className="text-ink-500 hover:text-warm-50 text-sm font-medium"
          >
            ✕
          </button>
        </div>

        {error && <div className="mt-4"><ErrorState message={error} /></div>}

        {mode === "signin" && (
          <form onSubmit={handleLogin} className="mt-4 space-y-4">
            <div>
              <label className="block text-xs font-medium text-ink-300 mb-1">Mobile Number</label>
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
              <label className="block text-xs font-medium text-ink-300 mb-1">Password</label>
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
            <div className="text-center pt-2">
              <button
                type="button"
                onClick={() => { setMode("register"); setError(null); }}
                className="text-xs text-aria-400 hover:underline"
              >
                Don&apos;t have an account? Register here
              </button>
            </div>
          </form>
        )}

        {mode === "register" && (
          <form onSubmit={handleRegister} className="mt-4 space-y-4">
            <div>
              <label className="block text-xs font-medium text-ink-300 mb-1">Full Name</label>
              <input
                type="text"
                value={name}
                onChange={(e) => setName(e.target.value)}
                placeholder="e.g. Ravi Kumar"
                required
                className={inputClass}
              />
            </div>
            <div>
              <label className="block text-xs font-medium text-ink-300 mb-1">Mobile Number</label>
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
              <label className="block text-xs font-medium text-ink-300 mb-1">Password</label>
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
              <label className="block text-xs font-medium text-ink-300 mb-1">Confirm Password</label>
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
              {loading ? "Creating account..." : "Register & Setup Business"}
            </Button>
            <div className="text-center pt-2">
              <button
                type="button"
                onClick={() => { setMode("signin"); setError(null); }}
                className="text-xs text-aria-400 hover:underline"
              >
                Already have an account? Sign in
              </button>
            </div>
          </form>
        )}

        {mode === "select_business" && (
          <div className="mt-4 space-y-3">
            <p className="text-xs text-ink-400 mb-2">Select a business playground to enter:</p>
            {businesses.map((b) => (
              <button
                key={b.id}
                onClick={async () => {
                  await switchBusiness(b.id);
                  onClose();
                }}
                className="w-full text-left p-3 rounded-xl border border-ink-850 bg-ink-900 hover:border-aria-500/40 hover:bg-ink-900 transition-colors flex items-center justify-between"
              >
                <div>
                  <p className="text-sm font-semibold text-warm-50">{b.business_name}</p>
                  <p className="text-xs text-ink-400 capitalize">{b.business_type}</p>
                </div>
                <span className="text-xs text-aria-400">Open Playground →</span>
              </button>
            ))}
            <div className="pt-2">
              <Button
                variant="secondary"
                onClick={() => {
                  router.push("/onboarding");
                  onClose();
                }}
                className="w-full"
              >
                + Add Another Business
              </Button>
            </div>
          </div>
        )}
      </Card>
    </div>
  );
}
