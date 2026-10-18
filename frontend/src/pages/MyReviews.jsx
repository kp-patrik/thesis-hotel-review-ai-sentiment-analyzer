import React, { useEffect, useState, useCallback } from "react";
import { useAuth } from "../auth/AuthProvider";
import { API_BASE_URL } from "../services/api";

const API_BASE = API_BASE_URL.replace(/\/$/, "");

function authHeaders(includeJson = false) {
  const token = (typeof window !== "undefined") ? localStorage.getItem("token") : null;
  const base = {
    Accept: "application/json",
    ...(token ? { Authorization: `Bearer ${token}` } : {}),
  };
  if (includeJson) base["Content-Type"] = "application/json";
  return base;
}

function getRecentReviewsForUser(userId) {
  try {
    const key = `recent_reviews_user_${userId ?? 'anon'}`;
    const raw = localStorage.getItem(key);
    if (!raw) return [];
    const arr = JSON.parse(raw);
    return Array.isArray(arr) ? arr : [];
  } catch (e) {
    console.warn("getRecentReviewsForUser failed", e);
    return [];
  }
}

async function tryGet(url) {
  try {
    console.debug("MyReviews: GET", url);
    const res = await fetch(url, { method: "GET", headers: authHeaders(false) });
    const text = await res.text();
    let data;
    try { data = text ? JSON.parse(text) : null; } catch { data = text; }
    return { ok: res.ok, status: res.status, data };
  } catch (e) {
    console.warn("MyReviews: request failed", url, e);
    return { ok: false, status: 0, data: null };
  }
}

export default function MyReviews() {
  const { user, loading } = useAuth();
  const [reviews, setReviews] = useState(null);
  const [loadingReviews, setLoadingReviews] = useState(false);
  const [error, setError] = useState(null);

  const displayNamesToMatch = (user) => {
    if (!user) return [];
    const names = [];
    if (user.username) names.push(user.username);
    if (user.name) names.push(user.name);
    if (user.email) names.push(user.email);
    if (user.username) names.push(user.username.toLowerCase());
    return names;
  };

  const loadReviews = useCallback(async () => {
    if (!user) return;
    setLoadingReviews(true);
    setError(null);

    try {
      const userId = user.id;
      const candidates = [
        `${API_BASE}/users/${encodeURIComponent(userId)}/reviews`,
        `${API_BASE}/reviews?user_id=${encodeURIComponent(userId)}`,
        `${API_BASE}/my-reviews`,
        `${API_BASE}/reviews`,
      ];

      let list = [];
      for (const url of candidates) {
        const { ok, status, data } = await tryGet(url);
        console.debug("MyReviews: tried", url, "status", status);
        if (!ok) continue;

        if (Array.isArray(data)) {
          list = data;
          break;
        }

        if (data && Array.isArray(data.reviews)) {
          list = data.reviews;
          break;
        }

        if (data && Array.isArray(data.items)) {
          list = data.items;
          break;
        }

        if (data && typeof data === "object") {
          const candidateArray = Object.values(data).find(v => Array.isArray(v));
          if (candidateArray) {
            list = candidateArray;
            break;
          }
        }
      }

      if (list.length > 0) {
        const names = displayNamesToMatch(user);
        if (names.length && !list.some(r => r.user_id || r.author_id || r.user)) {
          const filtered = list.filter(r => {
            const rn = (r.reviewer_name || r.reviewer || r.author || "").toString();
            const rnLower = rn.toLowerCase();
            return names.some(n => rnLower.includes(n.toString().toLowerCase()));
          });
          if (filtered.length) list = filtered;
        }
      }

      // Merge per-user persisted recent reviews only
      const recent = getRecentReviewsForUser(userId);
      if (recent.length > 0) {
        const existingIds = new Set(list.map(r => r.id));
        const toAdd = recent.filter(r => !existingIds.has(r.id));
        if (toAdd.length) list = [...toAdd, ...list];
      }

      setReviews(list);
    } catch (e) {
      console.error("MyReviews: load failed", e);
      setError("Failed to load your reviews.");
      setReviews([]);
    } finally {
      setLoadingReviews(false);
    }
  }, [user]);

  useEffect(() => {
    loadReviews();
  }, [loadReviews]);

  useEffect(() => {
    function onCreated(ev) {
      // ensure event belongs to this user before reloading
      try {
        const evUser = ev?.detail?.userId ?? null;
        if (evUser != null && user?.id != null && String(evUser) !== String(user.id)) {
          console.debug("MyReviews: ignoring review:created for other user", evUser);
          return;
        }
      } catch (e) {
        // fallback: continue
      }
      console.debug("MyReviews: received review:created event", ev.detail);
      loadReviews();
    }
    window.addEventListener("review:created", onCreated);
    return () => window.removeEventListener("review:created", onCreated);
  }, [loadReviews, user]);

  if (loading) return <div style={{ padding: 24 }}>Checking session…</div>;
  if (!user) return (
    <div style={{ padding: 24 }}>
      <h2>You are not signed in</h2>
      <p>Please sign in to manage your reviews.</p>
    </div>
  );

  return (
    <main style={{ maxWidth: 980, margin: "24px auto", padding: "16px" }}>
      <div style={{
        padding: 18,
        borderRadius: 12,
        background: "var(--surface)",
        boxShadow: "0 8px 24px var(--shadow)"
      }}>
        <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
          <h2 style={{ margin: 0 }}>My reviews</h2>
          <div>
            <button className="btn btn--outline" onClick={loadReviews} disabled={loadingReviews}>Refresh</button>
          </div>
        </div>

        <div style={{ marginTop: 16 }}>
          {loadingReviews && <div>Loading your reviews…</div>}
          {!loadingReviews && error && <div style={{ color: "red" }}>{error}</div>}
          {!loadingReviews && reviews && reviews.length === 0 && (
            <div>No reviews yet. Visit a hotel page to write your first review.</div>
          )}

          {!loadingReviews && reviews && reviews.length > 0 && (
            <div style={{ display: "grid", gap: 12, marginTop: 12 }}>
              {reviews.map((r) => (
                <article key={r.id || JSON.stringify(r)} style={{
                  padding: 12,
                  borderRadius: 8,
                  border: "1px solid var(--border)",
                  background: "var(--surface-muted)",
                  display: "flex",
                  gap: 12,
                  alignItems: "flex-start",
                  justifyContent: "space-between"
                }}>
                  <div style={{ flex: 1 }}>
                    <div style={{ display: "flex", alignItems: "center", gap: 12 }}>
                      <div style={{ fontWeight: 700 }}>{r.title || r.hotel_name || `Review #${r.id || "?"}`}</div>
                      <div style={{ color: "var(--text-muted)", fontSize: 13 }}>{r.created_at ? new Date(r.created_at).toLocaleString() : ""}</div>
                      <div style={{ marginLeft: "auto", color: "#5360d6", fontWeight: 700 }}>{r.rating ? `${r.rating}★` : ""}</div>
                    </div>
                    <div style={{ marginTop: 8, color: "var(--text)" }}>{r.review_text || r.text || r.body || r.comment || ""}</div>
                  </div>

                  <div style={{ display: "flex", flexDirection: "column", gap: 8 }}>
                  </div>
                </article>
              ))}
            </div>
          )}
        </div>
      </div>
    </main>
  );
}