"""Create a deterministic development dataset with meaningful hotel reviews."""

from database import Hotel, Review, SessionLocal
from sentiment import sentiment_analyzer

HOTELS_COUNT = 100
REVIEWS_PER_HOTEL = 50

CITY_PROFILES = [
    ("New York", "NY", "city-center", "skyline views"),
    ("Miami", "FL", "beachfront", "direct beach access"),
    ("Aspen", "CO", "mountain", "ski trails"),
    ("Chicago", "IL", "business district", "conference facilities"),
    ("Charleston", "SC", "historic district", "a peaceful courtyard"),
    ("San Francisco", "CA", "waterfront", "harbor views"),
    ("Seattle", "WA", "downtown", "a rooftop lounge"),
    ("Boston", "MA", "historic center", "walkable attractions"),
    ("Austin", "TX", "entertainment district", "live music nearby"),
    ("Portland", "OR", "garden quarter", "local restaurants"),
    ("Denver", "CO", "city center", "easy access to hiking"),
    ("Nashville", "TN", "music district", "evening entertainment"),
    ("Savannah", "GA", "old town", "shaded gardens"),
    ("San Diego", "CA", "coastal", "sunset walks"),
    ("New Orleans", "LA", "French Quarter", "historic architecture"),
    ("Washington", "DC", "museum quarter", "major landmarks"),
    ("Philadelphia", "PA", "old city", "excellent dining"),
    ("Orlando", "FL", "resort area", "family attractions"),
    ("Las Vegas", "NV", "central strip", "evening shows"),
    ("Honolulu", "HI", "island coast", "ocean views"),
]

HOTEL_STYLES = [
    ("Grand", "luxury", ["wifi", "spa", "gym", "restaurant", "concierge"]),
    ("Harbor", "resort", ["wifi", "pool", "spa", "restaurant", "parking"]),
    ("Pine", "lodge", ["wifi", "fireplace", "restaurant", "parking", "hiking"]),
    ("Civic", "business", ["wifi", "conference", "restaurant", "gym", "parking"]),
    ("Heritage", "boutique", ["wifi", "restaurant", "garden", "library", "courtyard"]),
]

REVIEWERS = [
    "Alex Morgan", "Jordan Taylor", "Casey Brooks", "Riley Parker", "Morgan Ellis",
    "Jamie Carter", "Taylor Reed", "Avery Cooper", "Cameron Hayes", "Drew Bennett",
]

REVIEW_TEMPLATES = {
    "positive": [
        ("The room was spotless and comfortable, and the staff were warm and attentive. "
         "The {feature} made the stay especially enjoyable.", 5),
        ("We loved the location near the {area}. Check-in was quick, breakfast was fresh, "
         "and the room was quiet at night.", 5),
        ("The service was excellent and the facilities were beautifully maintained. "
         "I would gladly return to {city}.", 5),
        ("Everything was clean, comfortable, and well organized. The staff solved a small "
         "request immediately and made us feel genuinely welcome.", 5),
        ("A wonderful stay with a comfortable bed, excellent breakfast, and friendly service. "
         "This hotel exceeded our expectations.", 5),
    ],
    "mixed": [
        ("The location near the {area} was convenient and the room was clean, but hallway "
         "noise woke us one night. Overall, it was a reasonable stay.", 3),
        ("The {feature} was beautiful, but the bathroom fixtures need updating. "
         "The hotel was suitable for a short visit, though not perfect.", 3),
        ("The room was comfortable and the staff were polite, but the restaurant was expensive "
         "and service was slower than expected.", 3),
        ("We enjoyed the location and the clean room. However, the Wi-Fi was unreliable and "
         "the check-in process took longer than expected.", 3),
        ("Some parts of the stay were excellent, while others felt average for the price. "
         "The staff were helpful but the facilities look slightly dated.", 3),
    ],
    "negative": [
        ("Our room was dirty on arrival, the air conditioning failed, and the staff did not "
         "resolve the problem. This was a disappointing stay.", 1),
        ("The check-in process was extremely slow, the room was not ready, and the service "
         "was unhelpful. I would not recommend this hotel.", 1),
        ("The room needed serious maintenance, the Wi-Fi was unusable, and the price was "
         "unreasonable. The experience was frustrating from start to finish.", 1),
        ("Noise continued late into the night, breakfast was cold, and no one responded to "
         "our complaints. I expected much better service.", 2),
        ("The photographs were misleading. Our room was cramped and poorly cleaned, and the "
         "staff offered no useful solution.", 1),
    ],
}

# Each profile produces a visibly different hotel average while keeping 50 reviews.
SENTIMENT_PROFILES = [
    ("positive", 35, "mixed", 10, "negative", 5),
    ("positive", 20, "mixed", 20, "negative", 10),
    ("positive", 8, "mixed", 12, "negative", 30),
    ("positive", 15, "mixed", 25, "negative", 10),
    ("positive", 25, "mixed", 10, "negative", 15),
]


def build_hotels() -> list[dict]:
    hotels = []
    for index in range(HOTELS_COUNT):
        city, state, area, feature = CITY_PROFILES[index % len(CITY_PROFILES)]
        style, category, amenities = HOTEL_STYLES[index % len(HOTEL_STYLES)]
        suffix = index // len(CITY_PROFILES) + 1
        name = f"{style} {city} {category.title()} {suffix}"
        hotels.append({
            "name": name,
            "location": f"{city}, {state}",
            "description": (
                f"A {category} hotel in the {area} of {city}, offering {feature} "
                "and comfortable accommodation for leisure and business travelers."
            ),
            "category": category,
            "amenities": amenities,
        })
    return hotels


def build_reviews(hotel: dict, hotel_index: int) -> list[tuple[str, str, int]]:
    city = hotel["location"].split(",")[0]
    area = CITY_PROFILES[hotel_index % len(CITY_PROFILES)][2]
    feature = CITY_PROFILES[hotel_index % len(CITY_PROFILES)][3]
    profile = SENTIMENT_PROFILES[hotel_index % len(SENTIMENT_PROFILES)]
    planned_reviews = []
    for category, count in zip(profile[::2], profile[1::2]):
        templates = REVIEW_TEMPLATES[category]
        for offset in range(count):
            planned_reviews.append(templates[offset % len(templates)])

    reviews = []
    for review_index, (template, rating) in enumerate(planned_reviews):
        reviewer = REVIEWERS[(hotel_index + review_index) % len(REVIEWERS)]
        text = template.format(city=city, area=area, feature=feature)
        reviews.append((reviewer, text, rating))
    return reviews


def reset_curated_dataset() -> None:
    hotels_data = build_hotels()
    all_review_texts = [
        text
        for hotel_index, hotel in enumerate(hotels_data)
        for _, text, _ in build_reviews(hotel, hotel_index)
    ]
    analyses = sentiment_analyzer.analyze_many(all_review_texts)
    if len(analyses) != len(all_review_texts):
        raise RuntimeError("Sentiment analysis returned an incomplete result batch")

    db = SessionLocal()
    try:
        db.query(Review).delete(synchronize_session=False)
        db.query(Hotel).delete(synchronize_session=False)
        analysis_index = 0

        for hotel_index, hotel_data in enumerate(hotels_data):
            hotel = Hotel(
                name=hotel_data["name"],
                location=hotel_data["location"],
                description=hotel_data["description"],
                category=hotel_data["category"],
                amenities=",".join(hotel_data["amenities"]),
                rating=0.0,
                average_sentiment=0.0,
                total_reviews=0,
            )
            db.add(hotel)
            db.flush()

            reviews = build_reviews(hotel_data, hotel_index)
            scores = []
            for reviewer_name, review_text, rating in reviews:
                analysis = analyses[analysis_index]
                analysis_index += 1
                if "error" in analysis:
                    raise RuntimeError(f"Could not analyze seeded review: {analysis['error']}")
                db.add(Review(
                    hotel_id=hotel.id,
                    reviewer_name=reviewer_name,
                    review_text=review_text,
                    sentiment_label=analysis["label"],
                    sentiment_score=analysis["score"],
                ))
                scores.append(analysis["score"])

            hotel.total_reviews = len(scores)
            hotel.average_sentiment = sum(scores) / len(scores)
            hotel.rating = sum(rating for _, _, rating in reviews) / len(reviews)

        db.commit()
        print(f"Created {HOTELS_COUNT} hotels and {len(all_review_texts)} meaningful reviews.")
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()


if __name__ == "__main__":
    reset_curated_dataset()
