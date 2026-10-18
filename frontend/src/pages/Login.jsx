import React, { useState } from "react";
import { Link } from "react-router-dom";
import * as authApi from "../services/authApi";

export default function Login() {
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [err, setErr] = useState(null);
  const [loading, setLoading] = useState(false);

  async function onSubmit(e) {
    e.preventDefault();
    setErr(null);
    setLoading(true);
    try {
      // call authApi.login directly to get raw response and persist token immediately
      const res = await authApi.login(username, password);
      console.debug("Login response:", res);

      const tok = res?.access_token || res?.token || res?.data?.access_token;
      if (!tok) {
        throw new Error("No token returned from login");
      }

      try {
        localStorage.setItem("token", tok);
        console.debug("Token saved to localStorage (partial):", tok.slice(0, 10) + "...");
      } catch (e) {
        console.warn("Could not save token to localStorage", e);
      }

      // reload so AuthProvider reads token from localStorage before calling /me
      window.location.href = "/";
    } catch (error) {
      console.error("Login failed", error);
      const message = error?.body?.detail || error?.message || JSON.stringify(error);
      setErr(typeof message === "string" ? message : JSON.stringify(message));
      setLoading(false);
    }
  }

  function fillDemoCreds() {
    setUsername("demo");
    setPassword("password");
  }

  return (
    <div style={{ maxWidth: 600, margin: "2rem auto" }}>
      <div className="card">
        <div className="card-body">
          <h2>Login</h2>
          <p>Sign in to access additional features. (You can also register a new account)</p>

          <form onSubmit={onSubmit}>
            <div className="form-group" style={{ marginBottom: 12 }}>
              <label>Username</label>
              <input
                className="form-control"
                placeholder="Enter username"
                value={username}
                onChange={(e) => setUsername(e.target.value)}
                autoFocus
              />
            </div>

            <div className="form-group" style={{ marginBottom: 12 }}>
              <label>Password</label>
              <input
                className="form-control"
                type="password"
                placeholder="Enter password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
              />
            </div>

            {err && <div style={{ color: "red", marginBottom: 12 }}>{err}</div>}

            <div style={{ display: "flex", gap: 8, alignItems: "center" }}>
              <button className="btn btn-primary" type="submit" disabled={loading}>
                {loading ? "Signing in..." : "Sign in"}
              </button>

              <button
                type="button"
                className="btn btn-secondary"
                onClick={fillDemoCreds}
              >
                Fill demo creds
              </button>

              <div style={{ marginLeft: "auto" }}>
                <Link to="/request-password-reset">Forgot password?</Link>
                {" · "}
                <Link to="/register">Sign up</Link>
              </div>
            </div>
          </form>
        </div>
      </div>
    </div>
  );
}