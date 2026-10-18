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

REVIEW_COMPONENTS = {
    "positive": [
        ("The room was spotless and comfortable.", "The staff were warm, attentive, and quick to help.",
         "The {feature} made the stay especially enjoyable."),
        ("We loved staying near the {area}.", "Check-in was smooth and the room was peaceful at night.",
         "It was an easy choice for a relaxing visit to {city}."),
        ("The service felt thoughtful from arrival to departure.", "Every shared area was clean and beautifully maintained.",
         "I would gladly return to this hotel."),
        ("Our bed was comfortable and the room felt fresh.", "A small request was handled immediately by the front desk.",
         "The team made us feel genuinely welcome."),
        ("Breakfast was fresh, well presented, and varied.", "The facilities were in excellent condition throughout our stay.",
         "This hotel exceeded our expectations."),
        ("The location made it simple to explore {city}.", "The staff offered helpful recommendations without being pushy.",
         "The whole stay felt polished and well organized."),
        ("We had a quiet room with plenty of natural light.", "Housekeeping kept everything tidy and replenished.",
         "It was exactly the comfortable base we needed."),
        ("The arrival experience was friendly and efficient.", "The room had thoughtful touches and a very comfortable bed.",
         "We left feeling rested and looked after."),
        ("The hotel combined a beautiful setting with dependable service.", "The breakfast team were cheerful each morning.",
         "It is an excellent option for both short and longer stays."),
        ("From the lobby to the room, everything felt inviting.", "Staff handled questions with patience and genuine care.",
         "We would recommend it to friends visiting {city}."),
    ],
    "mixed": [
        ("The location near the {area} was convenient.", "The room was clean, although hallway noise woke us once.",
         "It was a reasonable stay overall."),
        ("The {feature} was a real highlight.", "Some bathroom fixtures and furnishings need updating.",
         "The hotel worked well for a short visit, but it was not perfect."),
        ("The room was comfortable and the staff were polite.", "The restaurant was expensive and dinner service was slow.",
         "The experience was acceptable for the price."),
        ("We enjoyed the clean room and convenient surroundings.", "Wi-Fi was unreliable and check-in took longer than expected.",
         "A few practical details kept it from feeling seamless."),
        ("Several parts of the stay were genuinely pleasant.", "The facilities looked slightly dated in places.",
         "The value was fair, though expectations should stay realistic."),
        ("The bed was comfortable and the location saved us time.", "Breakfast options were limited during the quieter hours.",
         "It was a decent base for exploring {city}."),
        ("The staff answered our questions and the room was tidy.", "The walls were thin enough to hear neighboring guests.",
         "Light sleepers may want to request a quieter room."),
        ("The public areas were attractive and well located.", "Our room was smaller than expected for the price.",
         "It was fine for a couple of nights."),
        ("The check-in team were friendly and the lobby was welcoming.", "One elevator was out of service during our stay.",
         "The inconvenience was manageable but worth mentioning."),
        ("We liked the atmosphere and the helpful local recommendations.", "Some amenities were unavailable at the time of our visit.",
         "The hotel has promise, but consistency could improve."),
    ],
    "negative": [
        ("Our room was dirty on arrival.", "The air conditioning failed and the staff did not resolve it.",
         "This was a disappointing stay from the beginning."),
        ("Check-in was extremely slow and the room was not ready.", "The service team seemed uninterested when we asked for help.",
         "I would not recommend this hotel."),
        ("The room needed serious maintenance.", "The Wi-Fi was unusable and the price felt unreasonable.",
         "The experience was frustrating from start to finish."),
        ("Noise continued late into the night.", "Breakfast was cold and nobody responded properly to our complaints.",
         "I expected much better service."),
        ("The photographs gave a misleading impression.", "Our room was cramped, poorly cleaned, and missing basic comforts.",
         "The staff offered no useful solution."),
        ("The bathroom had not been cleaned properly.", "Several fixtures were broken and the front desk dismissed the issue.",
         "The stay was not worth what we paid."),
        ("Our arrival was chaotic and the promised room was unavailable.", "We waited too long for basic information and assistance.",
         "It was a stressful start to the trip."),
        ("The room was uncomfortable despite being advertised as upgraded.", "The mattress was worn and street noise made sleep difficult.",
         "I would choose another hotel in {city} next time."),
        ("The restaurant experience was disappointing.", "Food arrived cold, prices were high, and staff were difficult to reach.",
         "The hotel needs to improve its basic service standards."),
        ("The property looked neglected in several areas.", "Cleaning was inconsistent and our requests were repeatedly forgotten.",
         "The overall experience fell well below expectations."),
    ],
}

REVIEW_NOTES = {
    "positive": [
        "The atmosphere was calm and welcoming.",
        "The little details made a difference.",
        "Everything felt easy and well cared for.",
        "It was a memorable part of our trip.",
        "The experience felt worth the cost.",
        "We felt comfortable throughout the visit.",
        "The team consistently went the extra mile.",
        "It is easy to see why guests return.",
        "We would happily stay here again.",
        "The hotel delivered exactly what we hoped for.",
    ],
    "mixed": [
        "A little more attention to detail would help.",
        "The positives were balanced by these small frustrations.",
        "None of the issues ruined the entire visit.",
        "The experience depended on which room we received.",
        "It may suit travelers with modest expectations.",
        "We found the hotel adequate rather than special.",
        "The staff were trying, but the process felt uneven.",
        "A few improvements would make this a stronger choice.",
        "The stay was ordinary rather than memorable.",
        "We might return if the weaker areas are addressed.",
    ],
    "negative": [
        "The problems affected the whole visit.",
        "We left feeling that the hotel had let us down.",
        "The advertised standard was not reflected in reality.",
        "These issues should have been addressed before our arrival.",
        "The experience did not match the price.",
        "We regretted not choosing another property.",
        "There was too little attention to guest comfort.",
        "The management needs to take these complaints seriously.",
        "This was not the relaxing stay we had planned.",
        "I hope the hotel improves before our next visit.",
    ],
}

REVIEW_CONTEXTS = {
    "positive": [
        "We visited during a busy weekend.",
        "This was our first stay at the property.",
        "We were traveling as a couple.",
        "Our family appreciated the thoughtful service.",
        "We stayed for a work trip.",
        "The hotel was a convenient base for sightseeing.",
        "We spent three nights here.",
        "The team made a strong first impression.",
        "The property was even better than expected.",
        "We appreciated how smoothly everything ran.",
        "The staff remembered our preferences.",
        "The setting made the visit feel special.",
        "It was a particularly comfortable stay.",
    ],
    "mixed": [
        "We visited during a busy weekend.",
        "This was our first stay at the property.",
        "We were traveling as a couple.",
        "Our family noticed both strengths and weaknesses.",
        "We stayed for a work trip.",
        "The hotel was a convenient base for sightseeing.",
        "We spent three nights here.",
        "The experience varied from day to day.",
        "The property has a solid foundation.",
        "We tried to keep our expectations reasonable.",
        "Some details were better than others.",
        "The setting was stronger than the service.",
        "It was an acceptable stay overall.",
    ],
    "negative": [
        "We visited during a busy weekend.",
        "This was our first stay at the property.",
        "We were traveling as a couple.",
        "Our family found the problems difficult to overlook.",
        "We stayed for a work trip.",
        "The hotel was a poor base for sightseeing.",
        "We spent three nights here.",
        "The problems continued throughout the visit.",
        "The property needs substantial attention.",
        "We tried to give the hotel several chances.",
        "Basic guest expectations were not met.",
        "The setting could not make up for the service.",
        "It was an uncomfortable stay overall.",
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
        components = REVIEW_COMPONENTS[category]
        notes = REVIEW_NOTES[category]
        contexts = REVIEW_CONTEXTS[category]
        for offset in range(count):
            first, second, third = (
                components[(offset + hotel_index) % len(components)]
            )
            planned_reviews.append((
                f"{first} {second} {third} {notes[(offset * 3 + hotel_index) % len(notes)]} {contexts[(offset * 7 + hotel_index) % len(contexts)]}",
                5 if category == "positive" else 3 if category == "mixed" else 1,
            ))

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
