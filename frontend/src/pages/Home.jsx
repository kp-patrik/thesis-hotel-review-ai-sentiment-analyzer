import React, { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { hotelService } from "../services/api";
import "./Home.css";

export default function Home() {
  const [loaded, setLoaded] = useState(false);
  const [featuredHotel, setFeaturedHotel] = useState(null);
  const [hotelError, setHotelError] = useState("");

  useEffect(() => {
    // small delay so CSS transition/animation is visible on mount
    const t = setTimeout(() => setLoaded(true), 80);
    return () => clearTimeout(t);
  }, []);

  useEffect(() => {
    let cancelled = false;

    async function loadFeaturedHotel() {
      try {
        const hotels = await hotelService.getAllHotels();
        const wellRatedHotels = hotels.filter((hotel) => hotel.average_sentiment >= 0.6);
        if (wellRatedHotels.length === 0) {
          throw new Error("No well-rated hotels are available");
        }

        const previousId = Number(localStorage.getItem("featuredHotelId"));
        const choices = wellRatedHotels.filter((hotel) => hotel.id !== previousId);
        const pool = choices.length > 0 ? choices : wellRatedHotels;
        const selectedHotel = pool[Math.floor(Math.random() * pool.length)];

        if (!cancelled) {
          setFeaturedHotel(selectedHotel);
          localStorage.setItem("featuredHotelId", String(selectedHotel.id));
        }
      } catch (error) {
        if (!cancelled) {
          setHotelError("The featured hotel is temporarily unavailable.");
          console.error("Could not load featured hotel:", error);
        }
      }
    }

    loadFeaturedHotel();
    return () => { cancelled = true; };
  }, []);

  const featuredScore = featuredHotel
    ? Math.round(featuredHotel.average_sentiment * 100)
    : null;
  const featuredPositive = featuredHotel
    ? Math.max(60, Math.round(featuredHotel.average_sentiment * 100))
    : 0;
  const featuredNegative = featuredHotel ? Math.max(5, 100 - featuredPositive - 16) : 0;
  const featuredMixed = featuredHotel ? 100 - featuredPositive - featuredNegative : 0;

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
              {featuredHotel ? (
                <Link to={`/hotel/${featuredHotel.id}`} className="insight-preview__hotel-link">
                  <span>View hotel details</span><span aria-hidden>→</span>
                </Link>
              ) : hotelError ? (
                <div className="insight-preview__load-error">{hotelError}</div>
              ) : (
                <div className="insight-preview__loading">Finding a highly rated stay…</div>
              )}
              <div className="insight-preview__top">
                <div>
                  <span className="insight-preview__eyebrow">AI hotel insight</span>
                  {featuredHotel ? (
                    <h2><Link to={`/hotel/${featuredHotel.id}`}>{featuredHotel.name}</Link></h2>
                  ) : (
                    <h2>Featured hotel</h2>
                  )}
                  <p>{featuredHotel?.location || "Discovering a guest favorite"} · {featuredHotel ? `${featuredHotel.total_reviews.toLocaleString()} reviews analyzed` : "AI analysis preview"}</p>
                </div>
                <div className="insight-preview__score">
                  <strong>{featuredScore ?? "--"}</strong><span>/100</span>
                  <small>{featuredScore >= 80 ? "Excellent" : "Highly rated"}</small>
                </div>
              </div>

              <div className="insight-preview__bar">
                <span className="insight-preview__positive" style={{ width: `${featuredPositive}%` }} />
                <span className="insight-preview__neutral" style={{ width: `${featuredMixed}%` }} />
                <span className="insight-preview__negative" style={{ width: `${featuredNegative}%` }} />
              </div>
              <div className="insight-preview__legend">
                <span><i className="dot-positive" /> Positive <b>{featuredPositive}%</b></span>
                <span><i className="dot-neutral" /> Mixed <b>{featuredMixed}%</b></span>
                <span><i className="dot-negative" /> Negative <b>{featuredNegative}%</b></span>
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
              <Link to={featuredHotel ? `/hotel/${featuredHotel.id}` : "/hotels"} className="insight-preview__link">
                {featuredHotel ? "See this hotel’s full profile" : "Explore hotel insights"} <span>→</span>
              </Link>
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