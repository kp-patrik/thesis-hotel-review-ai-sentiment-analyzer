import React from "react";

export default function About() {
  return (
    <main style={{ maxWidth: 900, margin: "36px auto", padding: 20 }}>
      <h1>About this project</h1>

      <p style={{ color: "#6c757d" }}>
        This project was created as part of a bachelor's thesis. Built with care and a lot of late-night debugging, it shows how automated text analysis can turn thousands of reviews into clear, actionable insights.
      </p>

      <section style={{ marginTop: 18 }}>
        <h2>What this app does</h2>
        <ul style={{ listStyle: "none", paddingLeft: 0, color: "#495057" }}>
          <li style={{ marginBottom: 8 }}>Collects and displays user reviews for hotels.</li>
          <li style={{ marginBottom: 8 }}>Automatically summarizes opinions and computes sentiment scores.</li>
          <li style={{ marginBottom: 8 }}>Lets users manage their reviews and view personalized dashboards.</li>
        </ul>
      </section>

      <section style={{ marginTop: 18 }}>
        <h2>Tech & approach</h2>
        <p style={{ color: "#6c757d" }}>
          Backend: FastAPI / Python (or the chosen framework). Frontend: React + Vite. Authentication uses JWT. Text processing relies on standard NLP techniques to extract sentiment and key points.
        </p>
      </section>

      <section style={{ marginTop: 18 }}>
        <h2>Thanks</h2>
        <p style={{ color: "#6c757d" }}>
          Huge thanks to my thesis supervisor, teammates and everyone who tested the app. This was built with passion and lots of coffee — feedback and improvements are welcome.
        </p>
      </section>
    </main>
  );
}