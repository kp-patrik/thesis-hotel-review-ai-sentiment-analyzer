# 🎓 Thesis Project: Hotel Review AI Sentiment Analyzer

<p align="center">
  <strong>An AI-powered full-stack platform for analyzing sentiment in hotel reviews.</strong>
</p>

<p align="center">
  <a href="https://github.com/kp-patrik/thesis-hotel-review-ai-sentiment-analyzer">
    <img src="https://img.shields.io/badge/Project-Thesis%20Repository-6f42c1?style=for-the-badge" alt="Thesis project">
  </a>
  <img src="https://img.shields.io/badge/Python-3.12%2B-3776AB?style=for-the-badge&logo=python&logoColor=white" alt="Python 3.12 or newer">
  <img src="https://img.shields.io/badge/FastAPI-005571?style=for-the-badge&logo=fastapi" alt="FastAPI">
  <img src="https://img.shields.io/badge/React-20232A?style=for-the-badge&logo=react&logoColor=61DAFB" alt="React">
  <img src="https://img.shields.io/badge/AI-DistilBERT-FF6F00?style=for-the-badge" alt="DistilBERT">
</p>

## 📌 Project Overview

This repository contains my thesis project: a hotel-review management platform with an integrated artificial-intelligence sentiment analyzer.

The application accepts natural-language hotel reviews, processes them with a transformer-based NLP model, and returns a sentiment label, confidence value, and normalized score. The results are stored and presented through hotel-level dashboards, review history, and summary views.

The project demonstrates how an AI model can be integrated into a practical web application rather than used as an isolated experiment.

### Academic project caption

> **Hotel Review AI Sentiment Analyzer** is a full-stack thesis project that designs and implements an AI-assisted tool for classifying and analyzing sentiment in hotel reviews. The system combines a React user interface, a FastAPI REST API, a SQLAlchemy persistence layer, and the Hugging Face `distilbert-base-uncased-finetuned-sst-2-english` transformer model to provide automated sentiment scoring, review analytics, and hotel-level insight.

## 🖼️ Application Preview

Screenshots are stored in [`docs/screenshots/`](./docs/screenshots/). Add the images listed below using the exact filenames, then they will appear automatically in this section.

| Screen | Screenshot |
|---|---|
| Hotel listing and sentiment overview | ![Hotel listing](./docs/screenshots/01-hotel-list.png) |
| Hotel details and review history | ![Hotel details](./docs/screenshots/02-hotel-details.png) |
| AI sentiment analyzer | ![AI sentiment analyzer](./docs/screenshots/03-sentiment-analyzer.png) |
| Review submission and result | ![Review submission](./docs/screenshots/04-review-submission.png) |
| Review summary and analytics | ![Review summary](./docs/screenshots/05-review-summary.png) |
| Login and registration flow | ![Authentication](./docs/screenshots/06-authentication.png) |

### Recommended screenshot checklist

Capture the following at `1366 × 768` or wider, with browser developer tools closed:

1. **`01-hotel-list.png`** — homepage or hotel list showing several hotel cards and sentiment indicators.
2. **`02-hotel-details.png`** — a hotel page showing its average sentiment, review count, and review history.
3. **`03-sentiment-analyzer.png`** — the analyzer page with a sample review, predicted label, confidence, and score.
4. **`04-review-submission.png`** — a completed review form and the resulting sentiment feedback.
5. **`05-review-summary.png`** — the review-summary page showing the generated summary and analytics.
6. **`06-authentication.png`** — login or registration page, using demo data only.

Do not include passwords, email addresses, API keys, tokens, local file paths, or personal information in screenshots.

## ✨ Main Features

- **AI sentiment analysis** using a Hugging Face DistilBERT transformer model.
- **Interactive sentiment analyzer** for testing custom review text.
- **Hotel catalog** with descriptions, locations, review counts, and aggregate sentiment.
- **Curated development data** with 100 hotels and 50 realistic, hotel-specific reviews per hotel instead of placeholder text.
- **Review submission** with automatic sentiment classification and score calculation.
- **Review summaries** generated from the reviews associated with a hotel.
- **User authentication** with password hashing, JWT access tokens, email verification, and password-reset flows.
- **Persistent storage** using SQLite and SQLAlchemy.
- **REST API documentation** generated automatically by FastAPI and available through Swagger UI.
- **Responsive React interface** with protected pages, loading states, error handling, and reusable components.

## 🧠 AI Sentiment Analysis

The backend uses:

```text
Model:      distilbert-base-uncased-finetuned-sst-2-english
Provider:   Hugging Face Transformers
Task:       Natural-language sentiment classification
Output:     POSITIVE or NEGATIVE label, confidence, and normalized 0–1 score
```

Example API request:

```bash
curl -X POST "http://localhost:8000/analyze" \
  -H "Content-Type: application/json" \
  -d "{\"text\":\"The room was clean and the staff were wonderful.\"}"
```

Example response:

```json
{
  "text": "The room was clean and the staff were wonderful.",
  "label": "POSITIVE",
  "score": 0.99,
  "confidence": 0.98
}
```

The model is downloaded and cached by Transformers on its first use. The first backend startup may therefore take longer than subsequent starts.

## 🛠️ Technology Stack

| Layer | Technologies |
|---|---|
| Frontend | React 18, Vite, React Router, Axios, Recharts |
| Backend | Python, FastAPI, Uvicorn, Pydantic |
| AI/NLP | Hugging Face Transformers, DistilBERT, PyTorch |
| Data layer | SQLAlchemy ORM, SQLite |
| Authentication | JWT, PBKDF2 password hashing |
| Quality checks | ESLint, Python compilation, production build checks |

## 🗂️ Project Structure

```text
.
├── backend/
│   ├── main.py                 # FastAPI routes and authentication
│   ├── database.py             # SQLAlchemy engine and database models
│   ├── models.py               # Database operations and review statistics
│   ├── sentiment.py            # Transformer sentiment analyzer
│   ├── summarization.py        # Review summarization
│   ├── migrations.py           # Schema creation and upgrades
│   ├── requirements.txt        # Python dependencies
│   └── data/                   # Seed data
├── frontend/
│   ├── src/
│   │   ├── components/         # Reusable UI components
│   │   ├── pages/              # Application pages
│   │   ├── services/           # API clients
│   │   └── auth/               # Authentication state
│   ├── package.json
│   └── vite.config.js
├── docs/
│   └── screenshots/            # GitHub README screenshots
├── DEVELOPMENT.md
└── README.md
```

## 🚀 Getting Started

### Prerequisites

- Python 3.12 or newer
- Node.js 18 or newer
- Git
- Enough disk space for the downloaded transformer models

### 1. Clone the repository

```bash
git clone https://github.com/kp-patrik/thesis-hotel-review-ai-sentiment-analyzer.git
cd thesis-hotel-review-ai-sentiment-analyzer
```

### 2. Configure and start the backend

Windows PowerShell:

```powershell
cd backend
python -m venv venv
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt
Copy-Item .env.example .env
```

Edit `backend/.env` and replace `SECRET_KEY` with a unique value. Then initialize and start the API:

```powershell
python migrations.py create
python migrations.py seed
uvicorn main:app --reload --port 8000
```

To rebuild the local development database with the curated 100-hotel dataset and 5,000 meaningful reviews while preserving registered users:

```powershell
python seed_data.py
```

Backend URLs:

- API: <http://localhost:8000>
- Swagger documentation: <http://localhost:8000/docs>

### 3. Configure and start the frontend

In a second terminal:

```powershell
cd frontend
npm install
Copy-Item .env.example .env.local
npm run dev
```

Open <http://localhost:5173>.

The default frontend configuration expects the backend at `http://127.0.0.1:8000`. Change `VITE_API_BASE_URL` in `frontend/.env.local` if the API runs elsewhere.

## 🔌 API Overview

| Method | Endpoint | Purpose | Authentication |
|---|---|---|---|
| `GET` | `/` | API health message | Public |
| `GET` | `/hotels` | List hotels and aggregate sentiment | Public |
| `GET` | `/hotels/{hotel_id}` | Get hotel details and reviews | Public |
| `POST` | `/analyze` | Analyze custom text | Public |
| `POST` | `/register` | Create a user account | Public |
| `POST` | `/login` | Obtain a JWT access token | Public |
| `GET` | `/me` | Get the authenticated user | JWT |
| `POST` | `/reviews` | Submit and analyze a review | JWT |
| `POST` | `/summarize` | Summarize hotel reviews | Public |

## ✅ Verification

The project has been checked with:

```bash
# Python syntax
python -m compileall -q backend build_diploma_document.py

# Dependency audit
python backend/check_dependencies.py

# Frontend lint and production build
cd frontend
npm run lint
npm run build
```

## 🔐 Configuration and Privacy

- Never commit `backend/.env`, `frontend/.env.local`, credentials, tokens, or private email settings.
- Use `backend/.env.example` and `frontend/.env.example` as configuration templates.
- The local SQLite database and virtual environments are intentionally ignored by Git.
- Use a strong, unique `SECRET_KEY` outside development.

## 🎓 Thesis Context

This implementation can be discussed in a thesis through the following areas:

1. Natural-language processing and transformer-based classification.
2. Converting model confidence into application-level sentiment scores.
3. Integrating AI inference into a REST API.
4. Persisting and aggregating user-generated review data.
5. Designing a usable interface for interpreting model results.
6. Evaluating limitations, including language coverage, domain shift, and model bias.

## 🔭 Future Improvements

- Add a labeled hotel-review evaluation dataset and project-specific metrics.
- Support multilingual sentiment analysis.
- Add automated tests for API routes, authentication, and model output handling.
- Add time-series sentiment charts and exportable thesis evaluation reports.
- Add CI checks for linting, builds, and backend tests.

## 👤 Author

**Patrik**

- GitHub: [@kp-patrik](https://github.com/kp-patrik)
- Repository: [thesis-hotel-review-ai-sentiment-analyzer](https://github.com/kp-patrik/thesis-hotel-review-ai-sentiment-analyzer)

## 📄 License

Add the license required by your university or project supervisor before distributing the project publicly.
