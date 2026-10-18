// src/services/authApi.js
// Robust auth adapter:
// - login(...) trimite JSON și salvează access_token în localStorage (fallback sigur).
// - me(token) folosește direct fetch și trimite Authorization: Bearer <token> (nu mai depindem de api.me).
// - Restul folosește fallback-uri către api.js dacă există.

import * as apiModule from "./api";
const api = apiModule.default || apiModule;

const getApiBase = () => {
  if (typeof apiModule.API_BASE_URL === "string") return apiModule.API_BASE_URL.replace(/\/$/, "");
  if (typeof api?.defaults?.baseURL === "string") return api.defaults.baseURL.replace(/\/$/, "");
  return "http://127.0.0.1:8000";
};

async function parseResponseBody(res) {
  const text = await res.text();
  try { return text ? JSON.parse(text) : null; } catch { return text; }
}

// LOGIN: normalize args, send JSON, persist token to localStorage if present in response
export async function login(arg1, arg2) {
  // if underlying api.login exists, use it but still persist token if returned
  if (typeof api.login === "function") {
    if (typeof arg1 === "string" && typeof arg2 !== "undefined") {
      const res = await api.login({ username: arg1, password: arg2 });
      const tok = res?.access_token || res?.token || res?.data?.access_token || null;
      if (tok) {
        try { localStorage.setItem("token", tok); } catch (error) { console.warn("Could not save auth token", error); }
      }
      return res;
    }
    const res = await api.login(arg1);
    const tok = res?.access_token || res?.token || res?.data?.access_token || null;
    if (tok) {
      try { localStorage.setItem("token", tok); } catch (error) { console.warn("Could not save auth token", error); }
    }
    return res;
  }

  // normalize payload
  let payload;
  if (typeof arg1 === "string" && typeof arg2 !== "undefined") {
    payload = { username: arg1, password: arg2 };
  } else {
    payload = arg1 || {};
  }

  const url = `${getApiBase()}/login`;
  const res = await fetch(url, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      "Accept": "application/json",
    },
    body: JSON.stringify(payload),
    credentials: "omit",
  });

  const data = await parseResponseBody(res);
  if (!res.ok) {
    const err = new Error(data?.detail || data?.error || res.statusText);
    err.status = res.status;
    err.body = data;
    throw err;
  }

  // Persist token so other parts can read it from localStorage instantly
  const tok = data?.access_token || data?.token || data?.data?.access_token || null;
  if (tok) {
    try {
      localStorage.setItem("token", tok);
      console.debug("authApi.login: token saved (partial):", tok.slice ? tok.slice(0,10) + "..." : typeof tok);
    } catch (e) {
      console.warn("authApi.login: could not save token to localStorage", e);
    }
  } else {
    console.warn("authApi.login: login response has no token", data);
  }

  return data;
}

// ME: ALWAYS use a fetch that sets Authorization header using the passed token OR localStorage token.
// This avoids delegating to api.me/api.get which in this repo didn't attach the header.
export async function me(token) {
  const effectiveToken = token || (typeof window !== "undefined" ? localStorage.getItem("token") : null);

  if (!effectiveToken) {
    const err = new Error("No token provided for /me");
    err.status = 401;
    throw err;
  }

  const url = `${getApiBase()}/me`;
  const res = await fetch(url, {
    method: "GET",
    headers: {
      "Accept": "application/json",
      "Authorization": `Bearer ${effectiveToken}`,
    },
    credentials: "omit",
  });

  const data = await parseResponseBody(res);
  if (!res.ok) {
    const err = new Error(data?.detail || data?.error || res.statusText);
    err.status = res.status;
    err.body = data;
    throw err;
  }
  return data;
}

// Generic fallback wrappers for other endpoints
const callOrFallback = async (fnName, payload, fallbackPath) => {
  if (typeof api[fnName] === "function") {
    return api[fnName](payload);
  }
  if (typeof api.request === "function") {
    return api.request(fallbackPath || `/${fnName}`, { method: "POST", body: payload });
  }
  if (typeof api.post === "function") {
    return api.post(fallbackPath || `/${fnName}`, payload);
  }

  const url = `${getApiBase()}${fallbackPath || `/${fnName}`}`;
  const res = await fetch(url, {
    method: "POST",
    headers: { "Content-Type": "application/json", "Accept": "application/json" },
    body: JSON.stringify(payload),
  });
  const data = await parseResponseBody(res);
  if (!res.ok) {
    const err = new Error(data?.detail || data?.error || res.statusText);
    err.status = res.status;
    err.body = data;
    throw err;
  }
  return data;
};

export const register = (payload) => callOrFallback("register", payload, "/register");
export const updateProfile = (payload) => {
  if (typeof apiModule.authService?.updateProfile === "function") {
    return apiModule.authService.updateProfile(payload);
  }
  return fetch(`${getApiBase()}/me`, {
    method: "PUT",
    headers: {
      "Content-Type": "application/json",
      "Accept": "application/json",
      "Authorization": `Bearer ${localStorage.getItem("token") || localStorage.getItem("access_token")}`,
    },
    body: JSON.stringify(payload),
  }).then(async (res) => {
    const data = await parseResponseBody(res);
    if (!res.ok) {
      const error = new Error(data?.detail || data?.error || res.statusText);
      error.status = res.status;
      error.body = data;
      throw error;
    }
    return data;
  });
};
export const requestPasswordReset = (payload) => callOrFallback("requestPasswordReset", payload, "/request-password-reset");
export const resetPassword = (payload) => callOrFallback("resetPassword", payload, "/reset-password");
export const verifyEmail = ({ token }) => {
  if (typeof api.verifyEmail === "function") return api.verifyEmail({ token });
  if (typeof api.request === "function") return api.request(`/verify-email?token=${encodeURIComponent(token)}`, { method: "GET" });
  return callOrFallback("verifyEmail", { token }, `/verify-email?token=${encodeURIComponent(token)}`);
};

export default {
  login,
  me,
  register,
  updateProfile,
  requestPasswordReset,
  resetPassword,
  verifyEmail,
};