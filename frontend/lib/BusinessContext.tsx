"use client";

import { createContext, useCallback, useContext, useEffect, useState, type ReactNode } from "react";
import { api } from "./api";
import type { Business, BusinessSummary, LoginResponse, User } from "./types";

interface BusinessState {
  user: User | null;
  businesses: Business[];
  business: Business | null;
  summary: BusinessSummary | null;
  loading: boolean;
  error: string | null;
  needsOnboarding: boolean;
  showAuthModal: boolean;
  setShowAuthModal: (show: boolean) => void;
  switchBusiness: (businessId: string) => Promise<void>;
  loginUser: (res: LoginResponse) => void;
  logout: () => void;
  reload: () => void;
}

const Ctx = createContext<BusinessState>({
  user: null,
  businesses: [],
  business: null,
  summary: null,
  loading: true,
  error: null,
  needsOnboarding: false,
  showAuthModal: false,
  setShowAuthModal: () => {},
  switchBusiness: async () => {},
  loginUser: () => {},
  logout: () => {},
  reload: () => {},
});

const ACTIVE_BIZ_KEY = "aria.active_business_id";
const USER_KEY = "aria.user_session";

export function BusinessProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<User | null>(null);
  const [businesses, setBusinesses] = useState<Business[]>([]);
  const [business, setBusiness] = useState<Business | null>(null);
  const [summary, setSummary] = useState<BusinessSummary | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [needsOnboarding, setNeedsOnboarding] = useState(false);
  const [showAuthModal, setShowAuthModal] = useState(false);

  // Restore saved session from localStorage on mount
  useEffect(() => {
    try {
      const savedUser = localStorage.getItem(USER_KEY);
      if (savedUser) {
        setUser(JSON.parse(savedUser));
      }
    } catch {
      /* private mode */
    }
  }, []);

  const loadSummaryForBusiness = useCallback(async (b: Business) => {
    setBusiness(b);
    setNeedsOnboarding(false);
    try {
      const s = await api.summary(b.id);
      setSummary(s);
    } catch {
      setSummary(null);
    }
  }, []);

  const switchBusiness = useCallback(
    async (businessId: string) => {
      setLoading(true);
      setError(null);
      try {
        const b = await api.getBusiness(businessId);
        localStorage.setItem(ACTIVE_BIZ_KEY, b.id);
        await loadSummaryForBusiness(b);
      } catch (e) {
        setError((e as Error).message);
      } finally {
        setLoading(false);
      }
    },
    [loadSummaryForBusiness]
  );

  const load = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      let activeUser = user;
      if (!activeUser) {
        try {
          const raw = localStorage.getItem(USER_KEY);
          if (raw) activeUser = JSON.parse(raw);
        } catch {
          /* ignore */
        }
      }

      if (activeUser) {
        setUser(activeUser);
        const userBizs = await api.userBusinesses(activeUser.id);
        setBusinesses(userBizs);

        if (userBizs.length > 0) {
          const savedBizId = localStorage.getItem(ACTIVE_BIZ_KEY);
          const found = userBizs.find((b) => b.id === savedBizId) || userBizs[0];
          await loadSummaryForBusiness(found);
          setLoading(false);
          return;
        } else {
          setNeedsOnboarding(true);
          setBusiness(null);
          setSummary(null);
          setLoading(false);
          return;
        }
      }

      // Unauthenticated state: clear business and context
      setUser(null);
      setBusinesses([]);
      setBusiness(null);
      setSummary(null);
      setNeedsOnboarding(false);

    } catch (e: unknown) {
      const err = e as Error & { code?: string };
      if (err.code === "BUSINESS_REQUIRED" || /no business/i.test(err.message)) {
        setNeedsOnboarding(true);
        setBusiness(null);
      } else {
        setError(err.message);
      }
    } finally {
      setLoading(false);
    }
  }, [user, loadSummaryForBusiness]);

  useEffect(() => {
    void load();
  }, [load]);

  const loginUser = useCallback(
    (res: LoginResponse) => {
      setUser(res.user);
      setBusinesses(res.businesses);
      try {
        localStorage.setItem(USER_KEY, JSON.stringify(res.user));
      } catch {
        /* ignore */
      }
      if (res.businesses.length > 0) {
        const first = res.businesses[0];
        localStorage.setItem(ACTIVE_BIZ_KEY, first.id);
        void loadSummaryForBusiness(first);
      } else {
        setNeedsOnboarding(true);
        setBusiness(null);
      }
      setShowAuthModal(false);
    },
    [loadSummaryForBusiness]
  );

  const logout = useCallback(() => {
    setUser(null);
    setBusinesses([]);
    setBusiness(null);
    setSummary(null);
    try {
      localStorage.removeItem(USER_KEY);
      localStorage.removeItem(ACTIVE_BIZ_KEY);
    } catch {
      /* ignore */
    }
    // No manual load() here: `load` still closes over the pre-logout `user`
    // until this component re-renders, so calling it now would immediately
    // re-authenticate the user it was just asked to sign out. The effect
    // below re-runs `load` on its own once `user` settles to null.
  }, []);

  return (
    <Ctx.Provider
      value={{
        user,
        businesses,
        business,
        summary,
        loading,
        error,
        needsOnboarding,
        showAuthModal,
        setShowAuthModal,
        switchBusiness,
        loginUser,
        logout,
        reload: load,
      }}
    >
      {children}
    </Ctx.Provider>
  );
}

export const useBusiness = () => useContext(Ctx);
