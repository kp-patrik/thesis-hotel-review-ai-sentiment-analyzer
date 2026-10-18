from sqlalchemy.orm import Session
from database import Hotel, Review
from typing import List, Optional

def get_hotels(db: Session, skip: int = 0, limit: int = 100) -> List[Hotel]:
    """Get all hotels with pagination"""
    return db.query(Hotel).offset(skip).limit(limit).all()

def get_hotel(db: Session, hotel_id: int) -> Optional[Hotel]:
    """Get a specific hotel by ID"""
    return db.query(Hotel).filter(Hotel.id == hotel_id).first()

def create_hotel(db: Session, name: str, location: str, description: str = "") -> Hotel:
    """Create a new hotel"""
    db_hotel = Hotel(
        name=name,
        location=location,
        description=description
    )
    db.add(db_hotel)
    db.commit()
    db.refresh(db_hotel)
    return db_hotel

def create_review(
    db: Session,
    hotel_id: int,
    reviewer_name: str,
    review_text: str,
    sentiment_label: str,
    sentiment_score: float
) -> Review:
    """Create a new review"""
    db_review = Review(
        hotel_id=hotel_id,
        reviewer_name=reviewer_name,
        review_text=review_text,
        sentiment_label=sentiment_label,
        sentiment_score=sentiment_score
    )
    db.add(db_review)
    
    # Update hotel's average sentiment and review count
    hotel = get_hotel(db, hotel_id)
    if hotel:
        # Calculate new average sentiment
        total_score = hotel.average_sentiment * hotel.total_reviews
        total_score += sentiment_score
        hotel.total_reviews += 1
        hotel.average_sentiment = total_score / hotel.total_reviews
        
        db.commit()
        db.refresh(db_review)
    
    return db_review

def get_hotel_reviews(db: Session, hotel_id: int) -> List[Review]:
    """Get all reviews for a specific hotel"""
    return db.query(Review).filter(Review.hotel_id == hotel_id).all()

def get_hotel_by_name(db: Session, hotel_name: str) -> Optional[Hotel]:
    """Get a hotel by name (case-insensitive)"""
    return db.query(Hotel).filter(Hotel.name.ilike(f"%{hotel_name}%")).first()

def seed_sample_hotels(db: Session):
    """Seed database with sample hotels if empty"""
    if db.query(Hotel).first():
        return  # Already seeded
    
    sample_hotels = [
        {
            "name": "Grand Plaza Hotel",
            "location": "New York, NY",
            "description": "Luxury hotel in the heart of Manhattan with stunning city views."
        },
        {
            "name": "Ocean Breeze Resort",
            "location": "Miami, FL", 
            "description": "Beachfront resort with world-class amenities and spa services."
        },
        {
            "name": "Mountain View Lodge",
            "location": "Aspen, CO",
            "description": "Cozy mountain lodge perfect for skiing and outdoor adventures."
        },
        {
            "name": "Downtown Business Hotel",
            "location": "Chicago, IL",
            "description": "Modern business hotel with conference facilities and fine dining."
        },
        {
            "name": "Historic Boutique Inn",
            "location": "Charleston, SC",
            "description": "Charming historic inn with southern hospitality and antique furnishings."
        }
    ]
    
    for hotel_data in sample_hotels:
        create_hotel(db, **hotel_data)
    
    # Add sample reviews for testing summarization
    sample_reviews = [
        # Grand Plaza Hotel (id: 1) reviews
        {
            "hotel_id": 1,
            "reviewer_name": "John Smith",
            "review_text": "Absolutely fantastic stay at the Grand Plaza! The rooms were spacious and clean, with incredible views of the city skyline. Staff was professional and accommodating throughout our visit.",
            "sentiment_label": "POSITIVE",
            "sentiment_score": 0.9
        },
        {
            "hotel_id": 1,
            "reviewer_name": "Emily Johnson",
            "review_text": "The location couldn't be better - right in the heart of Manhattan. However, the rooms were quite noisy due to street traffic, and the WiFi was unreliable during our stay.",
            "sentiment_label": "NEGATIVE",
            "sentiment_score": 0.3
        },
        {
            "hotel_id": 1,
            "reviewer_name": "Michael Brown",
            "review_text": "Excellent service and luxurious amenities. The concierge helped us get tickets to a Broadway show. The restaurant on the top floor has amazing food and views. Highly recommended!",
            "sentiment_label": "POSITIVE",
            "sentiment_score": 0.95
        },
        # Ocean Breeze Resort (id: 2) reviews
        {
            "hotel_id": 2,
            "reviewer_name": "Sarah Wilson",
            "review_text": "Perfect beachfront location with direct access to the beach. The spa services were relaxing and the pool area was beautiful. Great for a romantic getaway.",
            "sentiment_label": "POSITIVE",
            "sentiment_score": 0.85
        },
        {
            "hotel_id": 2,
            "reviewer_name": "David Lee",
            "review_text": "The resort is showing its age - needs renovation. Food quality was disappointing for the price point. Beach was crowded and the service was slow.",
            "sentiment_label": "NEGATIVE",
            "sentiment_score": 0.25
        },
        # Mountain View Lodge (id: 3) reviews
        {
            "hotel_id": 3,
            "reviewer_name": "Lisa Chen",
            "review_text": "Cozy mountain atmosphere with stunning views. Perfect for a skiing vacation. The fireplace in the lobby was a nice touch, and the hot chocolate was delicious.",
            "sentiment_label": "POSITIVE",
            "sentiment_score": 0.8
        }
    ]
    
    for review_data in sample_reviews:
        create_review(db, **review_data)
