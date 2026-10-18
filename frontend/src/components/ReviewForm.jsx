import React, { useState } from 'react';
import { useAuth } from '../auth/AuthProvider';
import { API_BASE_URL } from '../services/api';

const getApiBase = () => {
  return API_BASE_URL.replace(/\/$/, "");
};

async function postReviewPayload(payload) {
  const apiBase = getApiBase();
  const url = `${apiBase}/reviews`;
  const token = (typeof window !== "undefined") ? localStorage.getItem("token") : null;

  const headers = {
    "Content-Type": "application/json",
    "Accept": "application/json",
    ...(token ? { "Authorization": `Bearer ${token}` } : {}),
  };

  console.debug("[ReviewForm] POST", url, "headers:", { hasAuth: !!headers.Authorization }, "payload:", payload);

  const res = await fetch(url, {
    method: "POST",
    headers,
    body: JSON.stringify(payload),
    credentials: "omit",
  });

  const text = await res.text();
  let data;
  try { data = text ? JSON.parse(text) : null; } catch { data = text; }

  if (!res.ok) {
    const err = new Error(data?.detail || data?.error || res.statusText || "Request failed");
    err.status = res.status;
    err.body = data;
    throw err;
  }

  return data;
}

function pushRecentReviewForUser(userId, review) {
  try {
    const key = `recent_reviews_user_${userId ?? 'anon'}`;
    const raw = localStorage.getItem(key);
    const arr = raw ? JSON.parse(raw) : [];
    // Avoid duplicates by id
    if (!arr.find(r => r.id === review.id)) {
      arr.unshift(review);
      localStorage.setItem(key, JSON.stringify(arr.slice(0, 50))); // keep recent 50
    }
  } catch (e) {
    console.warn("pushRecentReviewForUser failed", e);
  }
}

const ReviewForm = ({ hotelId, onReviewAdded }) => {
  const { user } = useAuth();
  const userId = user?.id ?? null;

  const [formData, setFormData] = useState({
    reviewer_name: user?.username || user?.name || '',
    review_text: ''
  });
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');

  const handleChange = (e) => {
    setFormData({
      ...formData,
      [e.target.name]: e.target.value
    });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();

    setError('');
    setSuccess('');

    if (!formData.reviewer_name.trim() || !formData.review_text.trim()) {
      setError('Please fill in all fields');
      return;
    }

    setLoading(true);

    try {
      const reviewData = {
        hotel_id: hotelId,
        reviewer_name: formData.reviewer_name.trim(),
        review_text: formData.review_text.trim()
      };

      const newReview = await postReviewPayload(reviewData);

      setSuccess('Review submitted successfully!');
      setFormData({ reviewer_name: user?.username || user?.name || '', review_text: '' });

      if (onReviewAdded) onReviewAdded(newReview);

      // Dispatch event
      try {
        window.dispatchEvent(new CustomEvent('review:created', { detail: { review: newReview, userId } }));
        console.debug("[ReviewForm] dispatched review:created event", newReview);
      } catch (err) {
        console.warn("[ReviewForm] could not dispatch review:created event", err);
      }

      // Persist under per-user key
      if (userId != null) {
        pushRecentReviewForUser(userId, newReview);
      } else {
        // If no user id, keep the old behavior but under anon key
        pushRecentReviewForUser('anon', newReview);
      }

    } catch (err) {
      console.error("[ReviewForm] submit error:", err);
      if (err.status === 401) {
        setError('Not authenticated — please sign in and try again.');
      } else {
        const message = err?.body?.detail || err?.message || 'Failed to submit review';
        setError(message);
      }
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="card">
      <h3>Write a Review</h3>

      {error && <div className="error" style={{ background: "#fdecea", color: "#b71c1c", padding: 8, borderRadius: 6 }}>{error}</div>}
      {success && <div className="success" style={{ background: "#e6ffed", color: "#1a7f37", padding: 8, borderRadius: 6 }}>{success}</div>}

      <form onSubmit={handleSubmit}>
        <div className="form-group" style={{ marginBottom: 10 }}>
          <label htmlFor="reviewer_name">Your Name</label>
          <input
            type="text"
            id="reviewer_name"
            name="reviewer_name"
            value={formData.reviewer_name}
            onChange={handleChange}
            className="form-control"
            placeholder="Enter your name"
            disabled={loading}
          />
        </div>

        <div className="form-group" style={{ marginBottom: 10 }}>
          <label htmlFor="review_text">Your Review</label>
          <textarea
            id="review_text"
            name="review_text"
            value={formData.review_text}
            onChange={handleChange}
            className="form-control textarea"
            placeholder="Share your experience at this hotel..."
            rows="4"
            disabled={loading}
          />
        </div>

        <button
          type="submit"
          className="btn"
          disabled={loading}
        >
          {loading ? 'Analyzing & Submitting...' : 'Submit Review'}
        </button>
      </form>
    </div>
  );
};

export default ReviewForm;