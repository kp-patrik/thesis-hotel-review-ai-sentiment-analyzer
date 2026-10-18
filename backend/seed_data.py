"""Replace the development dataset with curated hotels and meaningful reviews."""

from database import Hotel, Review, SessionLocal
from database_config import SAMPLE_HOTELS
from sentiment import sentiment_analyzer

REVIEWS_BY_HOTEL = {
    "Grand Plaza Hotel": [
        ("Alice Johnson", "The room was spotless, spacious, and quiet despite the central Manhattan location. The concierge arranged excellent theatre tickets and the staff were genuinely helpful.", 5),
        ("Bob Smith", "The location is ideal for exploring the city, but traffic noise was noticeable at night. The room was comfortable and the front desk responded quickly.", 3),
        ("Maria Garcia", "We loved the skyline view and the rooftop restaurant. Check-in was fast, housekeeping was attentive, and the bed was exceptionally comfortable.", 5),
        ("Daniel Brown", "The hotel looks luxurious, but our bathroom needed maintenance and the Wi-Fi dropped several times during a work call. The price felt high for that experience.", 2),
        ("Sophie Wilson", "A polished hotel with excellent service and an unbeatable location. I would happily stay here again when visiting New York.", 5),
    ],
    "Ocean Breeze Resort": [
        ("Carla Davis", "The beachfront location is beautiful, and the pool area was clean and relaxing. The spa treatment was excellent and the staff made our anniversary special.", 5),
        ("Michael Wilson", "The view from our balcony was wonderful, but the restaurant was overpriced and dinner service was slow. The room itself was clean and comfortable.", 3),
        ("Nina Taylor", "Perfect resort for a quiet beach holiday. The direct beach access, warm service, and peaceful rooms made this our favorite stay in Miami.", 5),
        ("James Anderson", "The beach was crowded and several facilities looked dated. We also waited nearly an hour for room service, which was disappointing for the price.", 2),
        ("Olivia Moore", "The resort has lovely gardens, a great pool, and friendly employees. Breakfast had plenty of fresh options and everything felt well maintained.", 4),
    ],
    "Mountain View Lodge": [
        ("Emma Taylor", "The fireplace, wooden rooms, and mountain views created a wonderfully cozy atmosphere. It was the perfect base for our ski trip.", 5),
        ("Lucas Martin", "The lodge is close to the slopes and the staff were welcoming. Our room was warm, although the mattress was firmer than expected.", 4),
        ("Grace Lee", "The hot chocolate by the fireplace was a lovely touch, and the trail recommendations were useful. We had a peaceful and memorable stay.", 5),
        ("Noah Harris", "The scenery is beautiful, but the room was smaller than advertised and the heating was unreliable on the coldest night.", 2),
        ("Mia Clark", "A charming lodge with helpful staff and excellent access to outdoor activities. I would recommend it to anyone visiting Aspen.", 5),
    ],
    "Downtown Business Hotel": [
        ("Frank Miller", "The conference rooms had reliable Wi-Fi, comfortable seating, and excellent presentation equipment. The location made meetings easy to reach.", 5),
        ("Rachel Lewis", "The room was clean and the desk was suitable for working, but noise from the hallway made it difficult to sleep before an early meeting.", 3),
        ("Henry Walker", "Fast check-in, professional staff, and an excellent breakfast service. This hotel made a busy business trip much easier.", 5),
        ("Eva Hall", "The air conditioning in our room was noisy and the restaurant closed earlier than expected. It was functional, but not especially comfortable.", 2),
        ("Thomas Young", "A practical and modern hotel with dependable internet and convenient transport links. Good value for short business stays.", 4),
    ],
    "Historic Boutique Inn": [
        ("Grace Lee", "The restored architecture and antique furniture give this inn real character. Our room was beautiful, and the breakfast felt homemade and fresh.", 5),
        ("Samuel King", "The garden was peaceful and the staff were kind. The historic staircase is charming, although guests with heavy luggage may find it difficult.", 4),
        ("Chloe Wright", "A romantic and memorable stay in a lovely historic building. The room was clean, quiet, and thoughtfully decorated.", 5),
        ("William Scott", "The property is attractive, but our room was smaller than expected and the bathroom fixtures need updating. Service was still friendly.", 3),
        ("Lily Green", "Wonderful southern hospitality, beautiful details, and a calm courtyard. The inn feels personal in a way large hotels do not.", 5),
    ],
}


def analyze_review(text: str) -> tuple[str, float]:
    result = sentiment_analyzer.analyze_sentiment(text)
    if "error" in result:
        raise RuntimeError(f"Could not analyze curated review: {result['error']}")
    return result["label"], result["score"]


def reset_curated_dataset() -> None:
    db = SessionLocal()
    try:
        db.query(Review).delete(synchronize_session=False)
        db.query(Hotel).delete(synchronize_session=False)

        for hotel_data in SAMPLE_HOTELS:
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

            reviews = REVIEWS_BY_HOTEL[hotel.name]
            scores = []
            for reviewer_name, review_text, rating in reviews:
                label, score = analyze_review(review_text)
                db.add(Review(
                    hotel_id=hotel.id,
                    reviewer_name=reviewer_name,
                    review_text=review_text,
                    sentiment_label=label,
                    sentiment_score=score,
                ))
                scores.append(score)

            hotel.total_reviews = len(scores)
            hotel.average_sentiment = sum(scores) / len(scores)
            hotel.rating = sum(rating for _, _, rating in reviews) / len(reviews)

        db.commit()
        print(f"Created {len(SAMPLE_HOTELS)} hotels and {sum(len(v) for v in REVIEWS_BY_HOTEL.values())} meaningful reviews.")
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()


if __name__ == "__main__":
    reset_curated_dataset()
