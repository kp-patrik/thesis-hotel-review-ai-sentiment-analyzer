import React, { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import "./Home.css";

export default function Home() {
  const [loaded, setLoaded] = useState(false);

  useEffect(() => {
    // small delay so CSS transition/animation is visible on mount
    const t = setTimeout(() => setLoaded(true), 80);
    return () => clearTimeout(t);
  }, []);

  return (
    <main className={`home-page ${loaded ? "is-loaded" : ""}`}>
      <section className="hero">
        <div className="hero__inner">
          <div className="hero__copy">
            <div className="badge">✨ New</div>
            <h1 className="hero__title">
              Find the best stay — faster
            </h1>
            <p className="hero__subtitle">
              Stop endless scrolling. Discover concise, trustworthy insights from real guest reviews — auto-summaries and sentiment scores show what matters most.
            </p>

            <div className="hero__cta">
              <Link to="/hotels" className="btn btn--primary cta-primary">Explore hotels</Link>
              <Link to="/register" className="btn btn--outline cta-secondary">Create free account</Link>
            </div>

            <ul className="hero__bullets">
              <li><strong>Save time:</strong> short answers, not long scrolls.</li>
              <li><strong>See real signals:</strong> sentiment and summaries surface common themes.</li>
              <li><strong>Share your story:</strong> write reviews and help others decide.</li>
            </ul>
          </div>

          <div className="hero__visual">
            <svg className="blob blob--1" viewBox="0 0 600 600" xmlns="http://www.w3.org/2000/svg" role="img" aria-hidden>
              <defs>
                <linearGradient id="g1" x1="0" x2="1">
                  <stop offset="0" stopColor="#e8f0ff" />
                  <stop offset="1" stopColor="#f6f9ff" />
                </linearGradient>
              </defs>
              <path d="M120,-160C168,-118,186,-52,189,16C192,84,179,156,134,195C89,234,12,241,-43,216C-98,191,-132,134,-168,76C-204,18,-241,-40,-214,-90C-187,-140,-96,-182,-22,-177C52,-172,96,-202,120,-160Z" fill="url(#g1)"/>
            </svg>

            <div className="insight-preview">
              <div className="insight-preview__top">
                <div>
                  <span className="insight-preview__eyebrow">AI hotel insight</span>
                  <h2>Hotel Bella</h2>
                  <p>New York · 1,248 reviews analyzed</p>
                </div>
                <div className="insight-preview__score">
                  <strong>82</strong><span>/100</span>
                  <small>Excellent</small>
                </div>
              </div>

              <div className="insight-preview__bar">
                <span className="insight-preview__positive" />
                <span className="insight-preview__neutral" />
                <span className="insight-preview__negative" />
              </div>
              <div className="insight-preview__legend">
                <span><i className="dot-positive" /> Positive <b>74%</b></span>
                <span><i className="dot-neutral" /> Mixed <b>16%</b></span>
                <span><i className="dot-negative" /> Negative <b>10%</b></span>
              </div>

              <div className="insight-preview__themes">
                <div className="insight-preview__theme">
                  <span className="theme-icon theme-icon--good">↑</span>
                  <div><strong>Guests love</strong><p>Location · Clean rooms · Staff</p></div>
                </div>
                <div className="insight-preview__theme">
                  <span className="theme-icon theme-icon--watch">!</span>
                  <div><strong>Worth noting</strong><p>Small rooms · Busy breakfast</p></div>
                </div>
              </div>

              <blockquote className="insight-preview__quote">
                “The location was perfect and the staff made us feel at home.”
              </blockquote>
              <Link to="/hotels" className="insight-preview__link">Explore hotel insights <span>→</span></Link>
            </div>

            <svg className="blob blob--2" viewBox="0 0 600 600" xmlns="http://www.w3.org/2000/svg" role="img" aria-hidden>
              <defs>
                <linearGradient id="g2" x1="0" x2="1">
                  <stop offset="0" stopColor="#fff7e8" />
                  <stop offset="1" stopColor="#fefcf5" />
                </linearGradient>
              </defs>
              <path d="M120,-160C168,-118,186,-52,189,16C192,84,179,156,134,195C89,234,12,241,-43,216C-98,191,-132,134,-168,76C-204,18,-241,-40,-214,-90C-187,-140,-96,-182,-22,-177C52,-172,96,-202,120,-160Z" fill="url(#g2)"/>
            </svg>
          </div>
        </div>
      </section>

      <section className="features">
        <h2 className="section-title">Why people love it</h2>
        <div className="features-grid">
          <article className="feature">
            <div className="feature__icon">🔍</div>
            <div>
              <h3>Signal, not noise</h3>
              <p>Auto-summaries and sentiment highlight what matters in thousands of reviews.</p>
            </div>
          </article>

          <article className="feature">
            <div className="feature__icon">⚡</div>
            <div>
              <h3>Fast decisions</h3>
              <p>See strengths and issues at a glance — book faster and smarter.</p>
            </div>
          </article>

          <article className="feature">
            <div className="feature__icon">🧭</div>
            <div>
              <h3>Trusted by travelers</h3>
              <p>Real guest reviews — add yours and help others choose better stays.</p>
            </div>
          </article>
        </div>
      </section>

      <section className="cta-band">
        <div className="cta-inner">
          <div>
            <h3>Ready to stop guessing?</h3>
            <p>Try the hotel explorer and see a summary in seconds.</p>
          </div>
          <Link to="/hotels" className="btn btn--primary cta-primary">Browse hotels</Link>
        </div>
      </section>
    </main>
  );
}