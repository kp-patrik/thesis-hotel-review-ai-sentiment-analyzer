import random
from datetime import datetime
from faker import Faker
from database import SessionLocal, Hotel, Review

fake = Faker()
db = SessionLocal()

# Config
NUM_HOTELS = 200           # Total hotels to create
REVIEWS_PER_HOTEL = 50     # Reviews per hotel

# Hotel categories, price ranges, and amenities pool
categories = ["luxury", "resort", "boutique", "business", "lodge"]
price_ranges = ["$", "$$", "$$$", "$$$$"]
amenities_pool = [
    "wifi", "spa", "gym", "pool", "restaurant", "parking",
    "beach", "fireplace", "concierge", "conference", "water_sports",
    "hiking", "library", "courtyard"
]

# --- CREATE HOTELS ---
hotels = []
for _ in range(NUM_HOTELS):
    amenities_str = ",".join(random.sample(amenities_pool, k=random.randint(3, 6)))
    hotel = Hotel(
        name=fake.company() + " Hotel",
        location=fake.city() + ", " + fake.state_abbr(),
        description=fake.paragraph(nb_sentences=3),
        rating=0.0,               # Will be updated after reviews
        average_sentiment=0.0,
        total_reviews=0,
        category=random.choice(categories),
        price_range=random.choice(price_ranges),
        amenities=amenities_str
    )
    db.add(hotel)
    hotels.append(hotel)

db.commit()

# Load hotels with IDs
hotels = db.query(Hotel).all()
print(f"✅ Created {len(hotels)} hotels")

# --- CREATE REVIEWS ---
for hotel in hotels:
    total_score = 0.0
    total_rating = 0.0
    for _ in range(REVIEWS_PER_HOTEL):
        sentiment_score = random.uniform(0.0, 1.0)
        review_rating = round(random.uniform(1, 5), 1)  # 1 to 5 stars
        review = Review(
            hotel_id=hotel.id,
            reviewer_name=fake.name(),
            review_text=fake.paragraph(nb_sentences=3),
            sentiment_label=random.choice(["POSITIVE", "NEGATIVE", "NEUTRAL"]),
            sentiment_score=sentiment_score
        )
        db.add(review)
        total_score += sentiment_score
        total_rating += review_rating

    # Update hotel stats
    hotel.total_reviews = REVIEWS_PER_HOTEL
    hotel.average_sentiment = total_score / REVIEWS_PER_HOTEL
    hotel.rating = total_rating / REVIEWS_PER_HOTEL  # Average 1-5 stars

db.commit()
print(f"✅ Created {NUM_HOTELS * REVIEWS_PER_HOTEL} reviews and updated hotel stats including ratings")
