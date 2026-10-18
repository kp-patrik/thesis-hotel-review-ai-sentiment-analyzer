import React, { createContext, useContext, useEffect, useState } from "react";
import * as authApi from "../services/authApi";

const AuthContext = createContext();

export function AuthProvider({ children }) {
  const [token, setToken] = useState(() => {
    try { return localStorage.getItem("token") || null; } catch { return null; }
  });
  const [user, setUser] = useState(() => {
    try { return JSON.parse(localStorage.getItem("user") || "null"); } catch { return null; }
  });
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    let cancelled = false;

    async function loadUser() {
      setLoading(true);

      if (!token) {
        console.debug("AuthProvider: no token available on load");
        setUser(null);
        setLoading(false);
        return;
      }

      console.debug("AuthProvider: calling /me with token (first 10 chars):", token?.slice?.(0,10) + "...");

      try {
        const me = await authApi.me(token);
        if (!cancelled) {
          console.debug("AuthProvider: /me returned:", me);
          setUser(me);
          try { localStorage.setItem("user", JSON.stringify(me)); } catch (e) { console.warn("Could not persist user to localStorage", e); }
        }
      } catch (e) {
        console.warn("AuthProvider: /me failed", e);
        // do not immediately clear user here in debug mode — keep logs
        try { localStorage.removeItem("user"); } catch (storageError) { console.warn("Could not remove cached user", storageError); }
        if (!cancelled) {
          setUser(null);
          // optionally clear token if you prefer:
          // setToken(null); localStorage.removeItem("token");
        }
      } finally {
        if (!cancelled) setLoading(false);
      }
    }

    loadUser();
    return () => { cancelled = true; };
  }, [token]);

  async function login(...args) {
    const res = await authApi.login(...args);
    const tok = res?.access_token || res?.token || res?.data?.access_token || null;
    if (!tok) {
      console.error("AuthProvider: login returned no token", res);
      throw new Error("No token returned from login");
    }
    try { localStorage.setItem("token", tok); } catch (e) { console.warn("AuthProvider: could not persist token", e); }
    setToken(tok);
    // do not attempt to call /me here; effect will run and populate user
    return res;
  }

  function logout() {
    try {
      localStorage.removeItem("token");
      localStorage.removeItem("access_token");
      localStorage.removeItem("user");
    } catch (storageError) {
      console.warn("Could not clear auth state", storageError);
    }
    setToken(null);
    setUser(null);
  }

  // debug: expose small helper to force-refresh user
  async function refreshUser() {
    try {
      const t = localStorage.getItem("token");
      const me = await authApi.me(t);
      setUser(me);
      localStorage.setItem("user", JSON.stringify(me));
      return me;
    } catch (e) {
      console.warn("refreshUser failed", e);
      throw e;
    }
  }

  return (
    <AuthContext.Provider value={{ token, user, loading, login, logout, refreshUser }}>
      {children}
    </AuthContext.Provider>
  );
}

export const useAuth = () => useContext(AuthContext);