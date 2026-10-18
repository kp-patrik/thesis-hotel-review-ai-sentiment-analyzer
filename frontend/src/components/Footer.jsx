import React from "react";
import { Link } from "react-router-dom";
import "./Footer.css";

export default function Footer() {
  return (
    <footer className="site-footer" role="contentinfo">
      <div className="site-footer__inner">
        <div className="site-footer__brand">
          <div className="site-footer__logo">KP</div>
          <div>
            <div className="site-footer__title">Hotel Reviews</div>
            <div className="site-footer__tag">Trusted guest reviews & summaries</div>
          </div>
        </div>

        <nav className="site-footer__links" aria-label="Footer">
          <div>
            <Link to="/about" className="site-footer__link">About</Link>
            <Link to="/hotels" className="site-footer__link">Hotels</Link>
            <Link to="/summaries" className="site-footer__link">Review Summaries</Link>
            <Link to="/analyze" className="site-footer__link">Sentiment Analyzer</Link>
          </div>
          <div>
            <Link to="/privacy" className="site-footer__link">Privacy</Link>
            <Link to="/terms" className="site-footer__link">Terms</Link>
            <a href="mailto:patrik.kiraly17@gmail.com" className="site-footer__link">Contact</a>
          </div>
        </nav>

        <div className="site-footer__meta">
          <p>
            © {new Date().getFullYear()} Patrik Kiraly. All rights reserved.
          </p>

          <p className="site-footer__notice">
            This project is the author's work (bachelor's thesis) and may not be copied or redistributed without permission.
          </p>

          <p className="site-footer__contact">
            For collaboration: <a href="mailto:patrik.kiraly17@gmail.com">patrik.kiraly17@gmail.com</a>
          </p>
        </div>
      </div>
    </footer>
  );
}