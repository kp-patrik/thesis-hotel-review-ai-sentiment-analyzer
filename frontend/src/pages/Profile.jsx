import React from "react";
import { useAuth } from "../auth/AuthProvider";
import { Link } from "react-router-dom";

export default function Profile() {
  const { user, loading, refreshUser } = useAuth();

  if (loading) {
    return <div style={{ padding: 24 }}>Loading profile…</div>;
  }

  if (!user) {
    return (
      <div style={{ padding: 24 }}>
        <h2>You're not signed in</h2>
        <p><Link to="/login">Sign in</Link> to view your profile.</p>
      </div>
    );
  }

  const displayName = user?.username || user?.name || user?.email || `#${user.id}`;
  const initials = (displayName || "U").split(/\s+/).map(s => s[0]).join("").slice(0,2).toUpperCase();

  return (
    <main style={{ maxWidth: 980, margin: "24px auto", padding: "16px" }}>
      <div style={{
        display: "flex",
        gap: 24,
        alignItems: "flex-start",
      }}>
        <div style={{
          minWidth: 160,
          padding: 16,
          borderRadius: 12,
          background: "#fff",
          boxShadow: "0 8px 24px rgba(33,37,41,0.06)"
        }}>
          <div style={{
            width: 96,
            height: 96,
            borderRadius: 999,
            background: "linear-gradient(135deg, #0d6efd, #6ba6ff)",
            color: "white",
            display: "flex",
            alignItems: "center",
            justifyContent: "center",
            fontSize: 28,
            fontWeight: 700,
            marginBottom: 12
          }}>{initials}</div>

          <div style={{ fontWeight: 700, fontSize: 18 }}>{displayName}</div>
          {user?.email && <div style={{ color: "#6c757d", marginTop: 6 }}>{user.email}</div>}
          <div style={{ marginTop: 12 }}>
            <Link to="/profile/edit" className="btn btn--outline" style={{ padding: "8px 10px" }}>Edit profile</Link>
          </div>
        </div>

        <div style={{
          flex: 1,
          padding: 18,
          borderRadius: 12,
          background: "#fff",
          boxShadow: "0 8px 24px rgba(33,37,41,0.04)"
        }}>
          <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: 12 }}>
            <h2 style={{ margin: 0 }}>Account</h2>
            <div>
              <button className="btn btn--outline" onClick={() => refreshUser?.()}>Refresh</button>
            </div>
          </div>

          <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 12 }}>
            <div>
              <div style={{ color: "#6c757d", fontSize: 13 }}>Username</div>
              <div style={{ fontWeight: 700 }}>{user.username || "-"}</div>
            </div>
            <div>
              <div style={{ color: "#6c757d", fontSize: 13 }}>User ID</div>
              <div style={{ fontWeight: 700 }}>{user.id ?? "-"}</div>
            </div>
            <div>
              <div style={{ color: "#6c757d", fontSize: 13 }}>Email</div>
              <div style={{ fontWeight: 700 }}>{user.email || "-"}</div>
            </div>
            <div>
              <div style={{ color: "#6c757d", fontSize: 13 }}>Member since</div>
              <div style={{ fontWeight: 700 }}>{user.created_at ? new Date(user.created_at).toLocaleDateString() : "-"}</div>
            </div>
          </div>

          <hr style={{ margin: "18px 0", border: "none", borderTop: "1px solid #eef2f6" }} />

          <div>
            <h3 style={{ marginTop: 0 }}>Preferences</h3>
            <p style={{ color: "#6c757d" }}>Manage your preferences here. (This is a demo UI — wire to the real settings API as needed.)</p>
          </div>
        </div>
      </div>
    </main>
  );
}