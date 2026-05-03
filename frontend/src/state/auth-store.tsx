import { useCallback, useEffect, useMemo, useState } from "react";
import { api } from "../lib/api";

const API_BASE = import.meta.env.VITE_API_BASE_URL ?? "http://localhost:8000";
const TOKEN_KEY = "skilllens_token";

interface AuthUser {
  username: string;
  email?: string;
  avatar?: string;
}

export function useAuth() {
  const [user, setUser] = useState<AuthUser | null>(null);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    const params = new URLSearchParams(window.location.search);
    const tokenFromUrl = params.get("token");
    if (tokenFromUrl) {
      localStorage.setItem(TOKEN_KEY, tokenFromUrl);
      params.delete("token");
      const query = params.toString();
      window.history.replaceState({}, "", `${window.location.pathname}${query ? `?${query}` : ""}${window.location.hash}`);
    }

    const token = tokenFromUrl ?? localStorage.getItem(TOKEN_KEY);
    if (!token) return;

    let cancelled = false;
    setLoading(true);
    api
      .getMe(token)
      .then((profile) => {
        if (!cancelled) setUser(profile);
      })
      .catch(() => {
        localStorage.removeItem(TOKEN_KEY);
        if (!cancelled) setUser(null);
      })
      .finally(() => {
        if (!cancelled) setLoading(false);
      });

    return () => {
      cancelled = true;
    };
  }, []);

  const loginWithProvider = useCallback((provider: "github" | "google") => {
    setLoading(true);
    window.location.href = `${API_BASE}/api/auth/${provider}/login`;
  }, []);

  const login = useCallback(() => loginWithProvider("github"), [loginWithProvider]);

  const logout = useCallback(() => {
    localStorage.removeItem(TOKEN_KEY);
    setUser(null);
  }, []);

  return useMemo(
    () => ({
      user,
      loading,
      isAuthenticated: Boolean(user),
      login,
      loginWithProvider,
      logout,
    }),
    [user, loading, login, loginWithProvider, logout],
  );
}
