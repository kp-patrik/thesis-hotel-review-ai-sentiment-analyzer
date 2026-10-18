# Hotel Review Sentiment Analysis - Development Setup

This directory contains a complete hotel review sentiment analysis web application with both backend and frontend components.

## Quick Start

Run the setup script to install all dependencies:

```bash
./setup.sh
```

Then start both servers:

**Backend (Terminal 1):**
```bash
cd backend
source venv/bin/activate
uvicorn main:app --reload
```

**Frontend (Terminal 2):**
```bash
cd frontend
npm run dev
```

Visit `http://localhost:5173` to use the application.

## Project Structure

```
hotel-review-nlp/
├── backend/                 # FastAPI backend
│   ├── main.py             # Main FastAPI application
│   ├── database.py         # Database models and config
│   ├── models.py           # Business logic functions
│   ├── sentiment.py        # Sentiment analysis logic
│   └── requirements.txt    # Python dependencies
├── frontend/               # React frontend
│   ├── src/
│   │   ├── components/     # Reusable components
│   │   ├── pages/         # Page components
│   │   ├── services/      # API service layer
│   │   └── App.jsx        # Main app component
│   └── package.json       # Node.js dependencies
├── setup.sh               # Automated setup script
└── README.md             # This file
```

## Features

- **Hotel Listing**: Browse available hotels with sentiment scores
- **Hotel Details**: View individual hotel information and all reviews
- **Review Submission**: Add reviews with automatic sentiment analysis
- **Sentiment Analysis**: Real-time sentiment classification using DistilBERT
- **Sentiment Testing**: Standalone sentiment analyzer for testing

## Technology Stack

- **Backend**: FastAPI, SQLAlchemy, Hugging Face Transformers
- **Frontend**: React, Vite, React Router, Axios
- **Database**: SQLite
- **ML Model**: DistilBERT (fine-tuned for sentiment analysis)

## API Endpoints

- `GET /hotels` - List all hotels
- `GET /hotels/{id}` - Get hotel details with reviews
- `POST /reviews` - Submit a new review
- `POST /analyze` - Analyze text sentiment

## Development Notes

The application includes sample hotel data that's automatically seeded when the backend starts for the first time. The sentiment analysis uses a pre-trained DistilBERT model from Hugging Face for accurate results.
