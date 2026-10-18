import React, { useState, useRef, useEffect } from "react";
import { Link, useNavigate } from "react-router-dom";
import { useAuth } from "../auth/AuthProvider";
import "../components/Header.css";
import logoSrc from "../assets/logo.png"; // folosește logo din src/assets
import { useTheme } from "../theme/ThemeProvider";

export default function Header() {
  const { user, loading, logout } = useAuth();
  const { darkMode, toggleTheme } = useTheme();
  const [open, setOpen] = useState(false);
  const navigate = useNavigate();
  const menuRef = useRef(null);

  const onLogout = () => {
    setOpen(false);
    logout();
    navigate("/", { replace: true });
  };

  // close when clicking outside
  useEffect(() => {
    function onDocClick(e) {
      if (!menuRef.current) return;
      if (!menuRef.current.contains(e.target)) setOpen(false);
    }
    document.addEventListener("mousedown", onDocClick);
    return () => document.removeEventListener("mousedown", onDocClick);
  }, []);

  const displayName = user?.username || user?.name || user?.email || (user?.id ? `#${user.id}` : "User");
  const initials = (displayName || "U")
    .split(/\s+/)
    .map((s) => s[0])
    .join("")
    .slice(0, 2)
    .toUpperCase();

  return (
    <header className="app-header">
      <div className="app-header__inner">
        <div className="app-header__left">
          <Link to="/" className="brand-link" onClick={() => setOpen(false)}>
            <img
              src={logoSrc}
              alt="Site logo"
              className="brand-logo"
              onError={(e) => { e.currentTarget.onerror = null; e.currentTarget.src = "/logo192.png"; }}
            />
            <span className="brand-title">Hotel Reviews</span>
          </Link>

          <nav className="app-header__nav-left">
            <Link to="/hotels" className="nav-link" onClick={() => setOpen(false)}>Hotels</Link>
            <Link to="/about" className="nav-link" onClick={() => setOpen(false)}>About</Link>
          </nav>
        </div>

        <div className="app-header__center">
          <nav className="app-header__nav-features">
            <Link to="/summaries" className="nav-feature-link" onClick={() => setOpen(false)}>Review Summaries</Link>
            <Link to="/analyze" className="nav-feature-link" onClick={() => setOpen(false)}>Sentiment Analyzer</Link>
          </nav>
        </div>

        <div className="app-header__actions">
          <button
            className="theme-toggle"
            onClick={toggleTheme}
            aria-label={darkMode ? "Switch to light mode" : "Switch to dark mode"}
            title={darkMode ? "Switch to light mode" : "Switch to dark mode"}
          >
            {darkMode ? "☀️" : "🌙"}
          </button>
          {loading ? (
            <div className="session-status">Checking session…</div>
          ) : user ? (
            <div className="profile-wrapper" ref={menuRef}>
              <button
                className="profile-button"
                onClick={() => setOpen((s) => !s)}
                aria-haspopup="true"
                aria-expanded={open}
                title={displayName}
              >
                <span className="avatar">{initials}</span>
                <span className="username">{displayName}</span>
                <svg className="chev" viewBox="0 0 20 20" width="12" height="12" aria-hidden>
                  <path d="M5 8l5 5 5-5" fill="none" stroke="currentColor" strokeWidth="1.6" strokeLinecap="round" strokeLinejoin="round"/>
                </svg>
              </button>

              {open && (
                <div className="profile-menu" role="menu">
                  <div className="profile-menu__item profile-menu__user" aria-hidden>
                    <div className="profile-menu__avatar">{initials}</div>
                    <div className="profile-menu__meta">
                      <div className="profile-menu__name">{displayName}</div>
                      <div className="profile-menu__id">Member</div>
                    </div>
                  </div>

                  <Link to="/profile" className="profile-menu__item" onClick={() => setOpen(false)}>Profile</Link>
                  <Link to="/my-reviews" className="profile-menu__item" onClick={() => setOpen(false)}>My reviews</Link>
                  <button className="profile-menu__item profile-menu__signout" onClick={onLogout}>Sign out</button>
                </div>
              )}
            </div>
          ) : (
            <div className="auth-links">
              <Link to="/login" className="btn btn--outline">Sign in</Link>
              <Link to="/register" className="btn btn--primary">Sign up</Link>
            </div>
          )}
        </div>
      </div>
    </header>
  );
}