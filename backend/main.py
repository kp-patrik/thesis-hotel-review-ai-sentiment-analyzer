from fastapi import FastAPI, Depends, HTTPException, status, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import List, Optional
from database import get_db, Hotel, Review, User
import models
from sentiment import sentiment_analyzer
from summarization import review_summarizer

# Auth helpers
import os
from datetime import datetime, timedelta
import jwt
from passlib.context import CryptContext
from fastapi.security import OAuth2PasswordBearer
from dotenv import load_dotenv
from email_utils import send_verification_email, send_password_reset_email

# Load .env
load_dotenv()

SECRET_KEY = os.getenv("SECRET_KEY")
if not SECRET_KEY:
    raise RuntimeError("SECRET_KEY must be set in the environment")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24  # 24 hours

# Use PBKDF2 to avoid bcrypt wheel/platform issues (safe for dev)
pwd_context = CryptContext(schemes=["pbkdf2_sha256"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")


def get_password_hash(password: str) -> str:
    if not isinstance(password, str):
        raise HTTPException(status_code=400, detail="Invalid password type")
    if len(password) < 6:
        raise HTTPException(status_code=400, detail="Password too short (min 6 chars)")
    # bcrypt historically limits to 72 bytes; defensively truncate to 72 bytes (encoded)
    pw_bytes = password.encode("utf-8")
    if len(pw_bytes) > 72:
        pw_bytes = pw_bytes[:72]
        password_to_hash = pw_bytes.decode("utf-8", errors="ignore")
    else:
        password_to_hash = password
    return pwd_context.hash(password_to_hash)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    # apply same truncation rule before verify to be consistent
    pw_bytes = plain_password.encode("utf-8")
    if len(pw_bytes) > 72:
        pw_bytes = pw_bytes[:72]
        plain_password = pw_bytes.decode("utf-8", errors="ignore")
    return pwd_context.verify(plain_password, hashed_password)


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta if expires_delta else timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def decode_access_token(token: str):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token expired")
    except Exception:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")


# Initialize FastAPI app
app = FastAPI(title="Hotel Review Sentiment Analysis API", version="1.0.0")

# Configure CORS - simplified for development
configured_origins = os.getenv("CORS_ORIGINS", "http://localhost:5173").split(",")
app.add_middleware(
    CORSMiddleware,
    allow_origins=[origin.strip() for origin in configured_origins if origin.strip()],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Pydantic models for auth
class RegisterRequest(BaseModel):
    username: str
    password: str
    email: Optional[str] = None


class LoginRequest(BaseModel):
    username: str
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


class UserResponse(BaseModel):
    id: int
    username: str
    email: Optional[str] = None
    is_verified: Optional[bool] = False


# Other Pydantic models
class SentimentAnalysisRequest(BaseModel):
    text: str


class SentimentAnalysisResponse(BaseModel):
    text: str
    label: str
    score: float
    confidence: float


class ReviewCreateRequest(BaseModel):
    hotel_id: int
    reviewer_name: Optional[str] = None
    review_text: str


class ReviewResponse(BaseModel):
    id: int
    hotel_id: int
    reviewer_name: str
    review_text: str
    sentiment_label: str
    sentiment_score: float
    created_at: str


class HotelResponse(BaseModel):
    id: int
    name: str
    location: str
    description: str
    average_sentiment: float
    total_reviews: int


class HotelDetailResponse(BaseModel):
    id: int
    name: str
    location: str
    description: str
    average_sentiment: float
    total_reviews: int
    reviews: List[ReviewResponse]


class SummarizationRequest(BaseModel):
    hotel_id: Optional[int] = None
    hotel_name: Optional[str] = None
    max_length: Optional[int] = 100
    min_length: Optional[int] = 20


class SummarizationResponse(BaseModel):
    hotel_id: int
    hotel_name: str
    summary: str
    total_reviews: int
    processed_reviews: int
    model_used: Optional[str] = None
    error: Optional[str] = None


# --- AUTH ENDPOINTS (register/login/me) ---
@app.post("/register", response_model=UserResponse)
def register(request: RegisterRequest, background_tasks: BackgroundTasks, db: Session = Depends(get_db)):
    if not request.username or not request.password:
        raise HTTPException(status_code=400, detail="Username and password required")
    existing = db.query(User).filter(User.username == request.username).first()
    if existing:
        raise HTTPException(status_code=400, detail="Username already exists")
    hashed = get_password_hash(request.password)
    # Try to create User record; be tolerant if model constructor differs
    try:
        user = User(username=request.username, email=request.email, hashed_password=hashed, is_verified=False)
    except TypeError:
        user = User(username=request.username, email=request.email, hashed_password=hashed)
        if hasattr(user, "is_verified"):
            setattr(user, "is_verified", False)

    db.add(user)
    db.commit()
    db.refresh(user)

    # send verification email in background (if email provided)
    if getattr(user, "email", None):
        token = create_access_token({"sub": user.username, "type": "verify"}, expires_delta=timedelta(hours=24))
        background_tasks.add_task(send_verification_email, user.email, user.username, token)

    return UserResponse(id=user.id, username=user.username, email=user.email, is_verified=getattr(user, "is_verified", False))


@app.post("/login", response_model=TokenResponse)
def login(request: LoginRequest, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.username == request.username).first()
    if not user or not verify_password(request.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Invalid username or password")
    token_data = {"sub": user.username, "user_id": user.id}
    access_token = create_access_token(token_data)
    return TokenResponse(access_token=access_token)


@app.get("/me", response_model=UserResponse)
def me(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    payload = decode_access_token(token)
    username = payload.get("sub")
    if not username:
        raise HTTPException(status_code=401, detail="Invalid authentication")
    user = db.query(User).filter(User.username == username).first()
    if not user:
        raise HTTPException(status_code=401, detail="User not found")
    return UserResponse(id=user.id, username=user.username, email=user.email, is_verified=getattr(user, "is_verified", False))


def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)) -> User:
    payload = decode_access_token(token)
    username = payload.get("sub")
    if not username:
        raise HTTPException(status_code=401, detail="Invalid authentication")
    user = db.query(User).filter(User.username == username).first()
    if not user:
        raise HTTPException(status_code=401, detail="User not found")
    return user


# --- NEW: request password reset ---
class PasswordResetRequest(BaseModel):
    username_or_email: str


@app.post("/request-password-reset")
def request_password_reset(request: PasswordResetRequest, background_tasks: BackgroundTasks, db: Session = Depends(get_db)):
    uoe = request.username_or_email.strip()
    user = db.query(User).filter((User.username == uoe) | (User.email == uoe)).first()
    # Always return 200 to avoid user enumeration; if user exists, send email
    if user and getattr(user, "email", None):
        token = create_access_token({"sub": user.username, "type": "password_reset"}, expires_delta=timedelta(hours=1))
        background_tasks.add_task(send_password_reset_email, user.email, user.username, token)
    return {"detail": "If an account exists with that email/username, a password reset link has been sent."}


# --- NEW: reset password ---
class PasswordResetConfirm(BaseModel):
    token: str
    new_password: str


@app.post("/reset-password")
def reset_password(request: PasswordResetConfirm, db: Session = Depends(get_db)):
    payload = decode_access_token(request.token)
    if payload.get("type") != "password_reset":
        raise HTTPException(status_code=400, detail="Invalid token")
    username = payload.get("sub")
    user = db.query(User).filter(User.username == username).first()
    if not user:
        raise HTTPException(status_code=400, detail="User not found")
    if not request.new_password or len(request.new_password) < 6:
        raise HTTPException(status_code=400, detail="Password too short (min 6 chars)")
    user.hashed_password = get_password_hash(request.new_password)
    db.commit()
    return {"detail": "Password updated successfully"}


# --- NEW: verify email (GET) ---
@app.get("/verify-email")
def verify_email(token: str, db: Session = Depends(get_db)):
    payload = decode_access_token(token)
    if payload.get("type") != "verify":
        raise HTTPException(status_code=400, detail="Invalid token")
    username = payload.get("sub")
    user = db.query(User).filter(User.username == username).first()
    if not user:
        raise HTTPException(status_code=400, detail="User not found")
    if hasattr(user, "is_verified"):
        user.is_verified = True
        db.commit()
    return {"detail": "Email verified successfully"}


# --- Sentiment analysis endpoint ---
@app.post("/analyze", response_model=SentimentAnalysisResponse)
async def analyze_sentiment(request: SentimentAnalysisRequest):
    if not request.text.strip():
        raise HTTPException(status_code=400, detail="Text cannot be empty")

    result = sentiment_analyzer.analyze_sentiment(request.text)

    if "error" in result:
        raise HTTPException(status_code=500, detail=f"Sentiment analysis failed: {result['error']}")

    return SentimentAnalysisResponse(
        text=request.text,
        label=result["label"],
        score=result["score"],
        confidence=result["confidence"]
    )


# --- Reviews (protected) ---
@app.post("/reviews", response_model=ReviewResponse)
async def create_review(request: ReviewCreateRequest, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    hotel = models.get_hotel(db, hotel_id=request.hotel_id)
    if hotel is None:
        raise HTTPException(status_code=404, detail="Hotel not found")

    reviewer_name = request.reviewer_name or current_user.username

    sentiment_result = sentiment_analyzer.analyze_sentiment(request.review_text)
    if "error" in sentiment_result:
        raise HTTPException(status_code=500, detail=f"Sentiment analysis failed: {sentiment_result['error']}")

    review = models.create_review(
        db=db,
        hotel_id=request.hotel_id,
        reviewer_name=reviewer_name,
        review_text=request.review_text,
        sentiment_label=sentiment_result["label"],
        sentiment_score=sentiment_result["score"]
    )

    return ReviewResponse(
        id=review.id,
        hotel_id=review.hotel_id,
        reviewer_name=review.reviewer_name,
        review_text=review.review_text,
        sentiment_label=review.sentiment_label,
        sentiment_score=review.sentiment_score,
        created_at=review.created_at.isoformat() if review.created_at else ""
    )


# --- Summarization ---
@app.post("/summarize", response_model=SummarizationResponse)
async def summarize_reviews(request: SummarizationRequest, db: Session = Depends(get_db)):
    if not request.hotel_id and not request.hotel_name:
        raise HTTPException(status_code=400, detail="Either hotel_id or hotel_name must be provided")

    hotel = None
    if request.hotel_id:
        hotel = models.get_hotel(db, hotel_id=request.hotel_id)
    elif request.hotel_name:
        hotel = models.get_hotel_by_name(db, hotel_name=request.hotel_name)

    if hotel is None:
        raise HTTPException(status_code=404, detail="Hotel not found")

    reviews = models.get_hotel_reviews(db, hotel_id=hotel.id)
    if not reviews:
        return SummarizationResponse(
            hotel_id=hotel.id,
            hotel_name=hotel.name,
            summary="No reviews available for this hotel yet.",
            total_reviews=0,
            processed_reviews=0
        )

    review_texts = [review.review_text for review in reviews if review.review_text]

    summary_result = review_summarizer.summarize_reviews(
        review_texts,
        max_length=request.max_length,
        min_length=request.min_length
    )

    return SummarizationResponse(
        hotel_id=hotel.id,
        hotel_name=hotel.name,
        summary=summary_result.get("summary", ""),
        total_reviews=summary_result.get("total_reviews", len(review_texts)),
        processed_reviews=summary_result.get("processed_reviews", len(review_texts)),
        model_used=summary_result.get("model_used"),
        error=summary_result.get("error")
    )


# --- Startup & public endpoints (health/hotels) ---
@app.on_event("startup")
async def startup_event():
    # Seed sample hotels if needed (seed function should avoid duplicates)
    db = next(get_db())
    try:
        models.seed_sample_hotels(db)
    finally:
        db.close()


@app.get("/")
async def root():
    return {"message": "Hotel Review Sentiment Analysis API"}


@app.get("/hotels", response_model=List[HotelResponse])
async def list_hotels(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    hotels = models.get_hotels(db, skip=skip, limit=limit)
    return [
        HotelResponse(
            id=h.id,
            name=h.name,
            location=h.location,
            description=h.description,
            average_sentiment=h.average_sentiment,
            total_reviews=h.total_reviews
        )
        for h in hotels
    ]


@app.get("/hotels/{hotel_id}", response_model=HotelDetailResponse)
async def get_hotel_detail(hotel_id: int, db: Session = Depends(get_db)):
    hotel = models.get_hotel(db, hotel_id=hotel_id)
    if hotel is None:
        raise HTTPException(status_code=404, detail="Hotel not found")

    reviews = models.get_hotel_reviews(db, hotel_id=hotel.id)

    return HotelDetailResponse(
        id=hotel.id,
        name=hotel.name,
        location=hotel.location,
        description=hotel.description,
        average_sentiment=hotel.average_sentiment,
        total_reviews=hotel.total_reviews,
        reviews=[
            ReviewResponse(
                id=r.id,
                hotel_id=r.hotel_id,
                reviewer_name=r.reviewer_name,
                review_text=r.review_text,
                sentiment_label=r.sentiment_label,
                sentiment_score=r.sentiment_score,
                created_at=r.created_at.isoformat() if r.created_at else ""
            )
            for r in reviews
        ]
    )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)