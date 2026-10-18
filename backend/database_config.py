"""
Database configuration and data definitions
Centralized place for all database-related constants and sample data
"""

import os
from typing import List, Dict, Any

# Database Configuration
DATABASE_CONFIG = {
    "sqlite": {
        "url": "sqlite:///./hotel_reviews.db",
        "connect_args": {"check_same_thread": False}
    },
    "postgresql": {
        "url": "postgresql://user:password@localhost/hotel_reviews",
        "connect_args": {}
    },
    "mysql": {
        "url": "mysql://user:password@localhost/hotel_reviews", 
        "connect_args": {}
    }
}

# Current database type
DATABASE_TYPE = os.getenv("DATABASE_TYPE", "sqlite")

# Sample Data Definitions
SAMPLE_HOTELS: List[Dict[str, Any]] = [
    {
        "name": "Grand Plaza Hotel",
        "location": "New York, NY",
        "description": "Luxury hotel in the heart of Manhattan with stunning city views.",
        "category": "luxury",
        "amenities": ["wifi", "spa", "gym", "restaurant", "parking"]
    },
    {
        "name": "Ocean Breeze Resort", 
        "location": "Miami, FL",
        "description": "Beachfront resort with world-class amenities and spa services.",
        "category": "resort",
        "amenities": ["beach", "pool", "spa", "restaurant", "wifi"]
    },
    {
        "name": "Mountain View Lodge",
        "location": "Aspen, CO", 
        "description": "Cozy mountain lodge perfect for skiing and outdoor adventures.",
        "category": "lodge",
        "amenities": ["ski", "fireplace", "wifi", "restaurant", "parking"]
    },
    {
        "name": "Downtown Business Hotel",
        "location": "Chicago, IL",
        "description": "Modern business hotel with conference facilities and fine dining.",
        "category": "business", 
        "amenities": ["wifi", "conference", "restaurant", "gym", "parking"]
    },
    {
        "name": "Historic Boutique Inn",
        "location": "Charleston, SC",
        "description": "Charming historic inn with southern hospitality and antique furnishings.",
        "category": "boutique",
        "amenities": ["wifi", "restaurant", "historic", "garden"]
    }
]

SAMPLE_REVIEWS: List[Dict[str, Any]] = [
    {
        "hotel_id": 1,
        "reviewer_name": "Alice Johnson",
        "review_text": "Outstanding hotel! The staff was incredibly helpful and the room was spotless. Will definitely stay here again!",
        "rating": 5
    },
    {
        "hotel_id": 1,
        "reviewer_name": "Bob Smith",
        "review_text": "Good location in Manhattan, but the room was a bit noisy due to street traffic. Service was decent.",
        "rating": 3
    },
    {
        "hotel_id": 2, 
        "reviewer_name": "Carol Davis",
        "review_text": "Amazing beachfront views! The resort exceeded all expectations. Perfect for a romantic getaway.",
        "rating": 5
    },
    {
        "hotel_id": 2,
        "reviewer_name": "David Wilson", 
        "review_text": "Beautiful location but the food at the restaurant was overpriced and mediocre quality.",
        "rating": 3
    },
    {
        "hotel_id": 3,
        "reviewer_name": "Emma Taylor",
        "review_text": "Cozy lodge with stunning mountain views. Perfect for our ski trip! Highly recommended.",
        "rating": 4
    },
    {
        "hotel_id": 4,
        "reviewer_name": "Frank Miller",
        "review_text": "Excellent business hotel. Conference facilities were top-notch and the location is perfect for meetings.",
        "rating": 4
    },
    {
        "hotel_id": 5,
        "reviewer_name": "Grace Lee",
        "review_text": "Charming historic property with beautiful architecture. The antique furnishings really add character.",
        "rating": 4
    }
]

# Test data for development
TEST_SENTIMENT_EXAMPLES = [
    {"text": "This hotel is absolutely amazing!", "expected": "POSITIVE"},
    {"text": "Terrible service and dirty rooms.", "expected": "NEGATIVE"},
    {"text": "The hotel was okay, nothing special.", "expected": "NEUTRAL"},
    {"text": "Best vacation ever! Staff was wonderful!", "expected": "POSITIVE"},
    {"text": "Worst experience of my life. Avoid at all costs!", "expected": "NEGATIVE"}
]

def get_database_url() -> str:
    """Get database URL based on current configuration"""
    return DATABASE_CONFIG[DATABASE_TYPE]["url"]

def get_connect_args() -> Dict[str, Any]:
    """Get database connection arguments"""
    return DATABASE_CONFIG[DATABASE_TYPE]["connect_args"]
