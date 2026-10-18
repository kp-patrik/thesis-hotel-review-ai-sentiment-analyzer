// frontend/src/services/reviewsApi.js
// Robust fallback for listing/creating/updating/deleting reviews.
// Ensures GET is used for list endpoints and logs attempts so you can debug 405 errors.
import { API_BASE_URL } from './api';

const getApiBase = () => {
  return API_BASE_URL.replace(/\/$/, "");
};

function authHeaders() {
  const token = (typeof window !== "undefined") ? localStorage.getItem("token") : null;
  return {
    "Accept": "application/json",
    // do not include Content-Type for GET requests
    ...(token ? { "Authorization": `Bearer ${token}` } : {}),
  };
}

function jsonHeaders() {
  const token = (typeof window !== "undefined") ? localStorage.getItem("token") : null;
  return {
    "Accept": "application/json",
    "Content-Type": "application/json",
    ...(token ? { "Authorization": `Bearer ${token}` } : {}),
  };
}

async function parseJson(res) {
  const text = await res.text();
  try { return text ? JSON.parse(text) : null; } catch { return text; }
}

export async function getMyReviews(userId) {
  const base = getApiBase();
  // try list endpoints in order — use GET explicitly
  const candidates = [
    { url: `${base}/users/${encodeURIComponent(userId)}/reviews`, method: "GET" },
    { url: `${base}/my-reviews`, method: "GET" },
    { url: `${base}/reviews?user_id=${encodeURIComponent(userId)}`, method: "GET" },
    { url: `${base}/reviews`, method: "GET" }, // last resort: GET /reviews (may return all)
  ];

  for (const c of candidates) {
    try {
      console.debug("reviewsApi.getMyReviews -> trying", c.method, c.url);
      const res = await fetch(c.url, { method: c.method, headers: authHeaders() });
      console.debug("reviewsApi.getMyReviews -> response", res.status, res.statusText, c.url);
      if (res.status === 405) {
        // server explicitly disallows this method for this URL — try next candidate
        console.warn("reviewsApi.getMyReviews -> 405 Method Not Allowed for", c.url);
        continue;
      }
      if (!res.ok) {
        // non-405 errors: log and try next candidate
        console.warn("reviewsApi.getMyReviews -> non-ok status", res.status, "for", c.url);
        continue;
      }
      const data = await parseJson(res);
      return Array.isArray(data) ? data : (data?.reviews || []);
    } catch (e) {
      console.debug("reviewsApi.getMyReviews: candidate failed", c.url, e);
    }
  }

  // nothing worked
  return [];
}

export async function createReview(payload) {
  const url = `${getApiBase()}/reviews`;
  const res = await fetch(url, {
    method: "POST",
    headers: jsonHeaders(),
    body: JSON.stringify(payload),
  });
  const data = await parseJson(res);
  if (!res.ok) {
    const err = new Error(data?.detail || data?.error || res.statusText);
    err.status = res.status;
    err.body = data;
    throw err;
  }
  return data;
}

export async function updateReview(id, payload) {
  const url = `${getApiBase()}/reviews/${encodeURIComponent(id)}`;
  // Try PATCH then PUT
  let res = await fetch(url, {
    method: "PATCH",
    headers: jsonHeaders(),
    body: JSON.stringify(payload),
  });
  if (!res.ok) {
    res = await fetch(url, {
      method: "PUT",
      headers: jsonHeaders(),
      body: JSON.stringify(payload),
    });
  }
  const data = await parseJson(res);
  if (!res.ok) {
    const err = new Error(data?.detail || data?.error || res.statusText);
    err.status = res.status;
    err.body = data;
    throw err;
  }
  return data;
}

export async function deleteReview(id) {
  const url = `${getApiBase()}/reviews/${encodeURIComponent(id)}`;
  const res = await fetch(url, {
    method: "DELETE",
    headers: authHeaders(),
  });
  if (res.status === 204 || res.status === 200) return true;
  const data = await parseJson(res);
  const err = new Error(data?.detail || data?.error || res.statusText);
  err.status = res.status;
  err.body = data;
  throw err;
}

export default {
  getMyReviews,
  createReview,
  updateReview,
  deleteReview,
};