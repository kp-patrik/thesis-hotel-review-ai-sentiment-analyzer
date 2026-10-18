"""
Database migrations for Hotel Review App
Handles database schema creation and seeding
"""

from sqlalchemy import create_engine, text, inspect
from database import Base, engine, SessionLocal
import models

def create_tables():
    """Create all database tables"""
    print("Creating database tables...")
    Base.metadata.create_all(bind=engine)
    if "is_verified" not in {column["name"] for column in inspect(engine).get_columns("users")}:
        with engine.begin() as connection:
            connection.execute(text("ALTER TABLE users ADD COLUMN is_verified BOOLEAN NOT NULL DEFAULT 0"))
        print("Added users.is_verified column")
    print("Tables created successfully")

def seed_sample_data():
    """Seed database with sample hotels and reviews"""
    db = SessionLocal()
    try:
        # Check if hotels already exist
        existing_hotels = models.get_hotels(db, limit=1)
        if existing_hotels:
            print("⚠️  Sample data already exists, skipping seed")
            return

        print("Seeding sample hotels...")
        
        # Sample hotels data
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
        
        # Create hotels
        for hotel_data in sample_hotels:
            models.create_hotel(db, **hotel_data)
        
        print("✅ Sample hotels seeded successfully")
        
        # Add some sample reviews for demonstration
        sample_reviews = [
            {
                "hotel_id": 1,
                "reviewer_name": "Alice Johnson",
                "review_text": "Outstanding hotel! The staff was incredibly helpful and the room was spotless.",
                "sentiment_label": "POSITIVE",
                "sentiment_score": 0.95
            },
            {
                "hotel_id": 1,
                "reviewer_name": "Bob Smith", 
                "review_text": "Good location but the room was a bit noisy.",
                "sentiment_label": "NEUTRAL",
                "sentiment_score": 0.6
            },
            {
                "hotel_id": 2,
                "reviewer_name": "Carol Davis",
                "review_text": "Amazing beachfront views! Perfect vacation spot.",
                "sentiment_label": "POSITIVE", 
                "sentiment_score": 0.92
            }
        ]
        
        for review_data in sample_reviews:
            models.create_review(db, **review_data)
            
        print("✅ Sample reviews seeded successfully")
        
    except Exception as e:
        print(f"❌ Error seeding data: {e}")
        db.rollback()
    finally:
        db.close()

def reset_database():
    """Drop and recreate all tables (WARNING: Deletes all data)"""
    print("⚠️  Resetting database - THIS WILL DELETE ALL DATA!")
    Base.metadata.drop_all(bind=engine)
    create_tables()
    seed_sample_data()
    print("✅ Database reset complete")

def backup_data():
    """Export current data to SQL file"""
    import os
    backup_file = "database_backup.sql"
    
    # Use sqlite3 command to create backup
    db_path = "hotel_reviews.db" 
    os.system(f"sqlite3 {db_path} .dump > {backup_file}")
    print(f"✅ Database backed up to {backup_file}")

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1:
        command = sys.argv[1]
        
        if command == "create":
            create_tables()
        elif command == "seed":
            seed_sample_data()
        elif command == "reset":
            reset_database()
        elif command == "backup":
            backup_data()
        else:
            print("Usage: python migrations.py [create|seed|reset|backup]")
    else:
        print("Available commands:")
        print("  python migrations.py create  - Create database tables")
        print("  python migrations.py seed    - Seed sample data") 
        print("  python migrations.py reset   - Reset database (DELETES ALL DATA)")
        print("  python migrations.py backup  - Backup database to SQL file")
