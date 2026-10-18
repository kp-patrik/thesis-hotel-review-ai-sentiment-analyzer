# Development Guide

This guide covers the current local workflow for the Hotel Review AI Sentiment Analyzer.

## Prerequisites

- Windows PowerShell, macOS, or Linux
- Python 3.12 or newer
- Node.js 18 or newer
- Git
- Enough disk space for the Hugging Face models

## Start the backend

From the repository root:

```powershell
cd backend
python -m venv venv
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt
Copy-Item .env.example .env
```

Set a unique `SECRET_KEY` in `backend/.env`, then initialize the schema:

```powershell
python migrations.py create
python seed_data.py
uvicorn main:app --reload --port 8000
```

The API is available at `http://localhost:8000` and Swagger UI at
`http://localhost:8000/docs`.

`seed_data.py` creates 100 hotels and 5,000 meaningful reviews while preserving
registered users. It intentionally replaces the hotel and review dataset, so
use it only for development data regeneration.

## Start the frontend

Open a second terminal:

```powershell
cd frontend
npm install
Copy-Item .env.example .env.local
npm run dev
```

Open the URL printed by Vite, normally `http://localhost:5173`.
The default API URL is `http://127.0.0.1:8000`.

## Main application areas

- **Hotels** — browse hotels by aggregate sentiment and review count.
- **Hotel details** — view category-based photos, open the photo carousel,
  inspect amenities and the embedded location map, and filter reviews by
  positive, neutral, or negative aggregate sentiment.
- **Sentiment Analyzer** — submit custom text to the DistilBERT model.
- **Review Summaries** — generate summaries that include representative
  feedback and factual sentiment proportions.
- **Profile** — view account information and the account creation date.
- **Edit profile** — update username, email, bio, photo, and password.
- **Theme toggle** — switch between persistent light and dark themes.

## API conventions

- `POST /reviews` requires a JWT and always uses the authenticated username as
  the reviewer name.
- `PUT /me` requires a JWT. Password changes require the current password.
- `GET /hotels/{hotel_id}` returns hotel details, amenities, and reviews.
- `POST /summarize` samples across the full review set to avoid summaries
  being biased toward reviews at the start of the database ordering.

## Email and local development

Without SMTP configuration, verification and password-reset emails are printed
to the backend terminal. This fallback is for development only.

## Validation

Run the smallest relevant checks after changes:

```powershell
# Backend syntax
cd backend
python -m py_compile main.py database.py migrations.py seed_data.py summarization.py

# Frontend lint and production build
cd ..\frontend
npm run lint
npm run build
```

## Environment and privacy

- Never commit `backend/.env`, `frontend/.env.local`, credentials, tokens, or
  private SMTP settings.
- Use `.env.example` files as templates.
- The local SQLite database and virtual environments are development-only.
- Hotel gallery images currently come from Unsplash URLs. Confirm licensing or
  replace them with approved assets before production distribution.
