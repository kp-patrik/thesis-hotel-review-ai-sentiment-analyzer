import React, { useState, useEffect, useCallback } from 'react';
import { useParams, Link } from 'react-router-dom';
import { hotelService } from '../services/api';
import ReviewItem from '../components/ReviewItem';
import ReviewForm from '../components/ReviewForm';
import SentimentBadge from '../components/SentimentBadge';
import ReviewSummary from '../components/ReviewSummary';
import './HotelDetail.css';

const GALLERY_IMAGES = {
  luxury: [
    'https://images.unsplash.com/photo-1564501049412-61c2a3083791?auto=format&fit=crop&w=1200&q=85',
    'https://images.unsplash.com/photo-1582719478250-c89cae4dc85b?auto=format&fit=crop&w=900&q=85',
    'https://images.unsplash.com/photo-1590490360182-c33d57733427?auto=format&fit=crop&w=900&q=85',
  ],
  resort: [
    'https://images.unsplash.com/photo-1540541338287-41700207dee6?auto=format&fit=crop&w=1200&q=85',
    'https://images.unsplash.com/photo-1566073771259-6a8506099945?auto=format&fit=crop&w=900&q=85',
    'https://images.unsplash.com/photo-1549294413-26f195200c16?auto=format&fit=crop&w=900&q=85',
  ],
  lodge: [
    'https://images.unsplash.com/photo-1510798831971-661eb04b3739?auto=format&fit=crop&w=1200&q=85',
    'https://images.unsplash.com/photo-1542718610-a1d656d1884c?auto=format&fit=crop&w=900&q=85',
    'https://images.unsplash.com/photo-1449158743715-0a90ebb6d2d8?auto=format&fit=crop&w=900&q=85',
  ],
  business: [
    'https://images.unsplash.com/photo-1551882547-ff40c63fe5fa?auto=format&fit=crop&w=1200&q=85',
    'https://images.unsplash.com/photo-1497366754035-f200968a6e72?auto=format&fit=crop&w=900&q=85',
    'https://images.unsplash.com/photo-1566665797739-1674de7a421a?auto=format&fit=crop&w=900&q=85',
  ],
  boutique: [
    'https://images.unsplash.com/photo-1566665797739-1674de7a421a?auto=format&fit=crop&w=1200&q=85',
    'https://images.unsplash.com/photo-1618221195710-dd6b41faaea6?auto=format&fit=crop&w=900&q=85',
    'https://images.unsplash.com/photo-1595576508898-0ad5c879a061?auto=format&fit=crop&w=900&q=85',
  ],
};

const AMENITY_LABELS = {
  wifi: 'Free Wi-Fi',
  spa: 'Spa & wellness',
  gym: 'Fitness center',
  restaurant: 'Restaurant',
  concierge: 'Concierge',
  pool: 'Swimming pool',
  parking: 'Parking',
  fireplace: 'Fireplace lounge',
  hiking: 'Hiking access',
  conference: 'Conference rooms',
  garden: 'Garden',
  library: 'Library',
  courtyard: 'Courtyard',
};

const HotelDetail = () => {
  const { id } = useParams();
  const [hotel, setHotel] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [reviewFilter, setReviewFilter] = useState('all');

  const fetchHotelDetails = useCallback(async () => {
    try {
      const data = await hotelService.getHotelById(id);
      setHotel(data);
    } catch (err) {
      setError('Failed to load hotel details');
      console.error('Error fetching hotel details:', err);
    } finally {
      setLoading(false);
    }
  }, [id]);

  useEffect(() => {
    fetchHotelDetails();
  }, [fetchHotelDetails]);

  const handleReviewAdded = () => {
    // Refresh hotel details to get updated data
    fetchHotelDetails();
  };

  const getOverallSentiment = (score) => {
    if (score > 0.6) return 'POSITIVE';
    if (score < 0.4) return 'NEGATIVE';
    return 'NEUTRAL';
  };

  const getSentimentStats = (reviews) => {
    const stats = { positive: 0, negative: 0, neutral: 0 };
    
    reviews.forEach(review => {
      if (review.sentiment_score > 0.6) {
        stats.positive++;
      } else if (review.sentiment_score < 0.4) {
        stats.negative++;
      } else {
        stats.neutral++;
      }
    });
    
    return stats;
  };

  if (loading) {
    return (
      <div className="container">
        <div className="loading">Loading hotel details...</div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="container">
        <div className="error">{error}</div>
        <Link to="/" className="btn btn-secondary">Back to Hotels</Link>
      </div>
    );
  }

  if (!hotel) {
    return (
      <div className="container">
        <div className="error">Hotel not found</div>
        <Link to="/" className="btn btn-secondary">Back to Hotels</Link>
      </div>
    );
  }

  const sentimentStats = getSentimentStats(hotel.reviews);
  const gallery = GALLERY_IMAGES[hotel.category] || GALLERY_IMAGES.boutique;
  const amenities = hotel.amenities?.length
    ? hotel.amenities.map((amenity) => AMENITY_LABELS[amenity] || amenity)
    : ['Free Wi-Fi', '24-hour reception', 'Daily housekeeping'];
  const filteredReviews = hotel.reviews
    .filter((review) => reviewFilter === 'all' || review.sentiment_label.toLowerCase() === reviewFilter)
    .sort((a, b) => new Date(b.created_at) - new Date(a.created_at));
  const mapUrl = `https://www.google.com/maps?q=${encodeURIComponent(hotel.location)}&output=embed`;

  return (
    <div className="container">
      <Link to="/" className="btn btn-secondary" style={{ marginBottom: '1rem' }}>
        ← Back to Hotels
      </Link>

      <section className="hotel-hero card">
        <div className="hotel-hero__copy">
          <span className="hotel-kicker">{hotel.category || 'Hotel'} stay</span>
          <h1>{hotel.name}</h1>
          <p className="location hotel-location">📍 {hotel.location}</p>
          <p className="hotel-description">{hotel.description}</p>
          <div className="hotel-hero__score">
          <SentimentBadge 
            sentiment={getOverallSentiment(hotel.average_sentiment)} 
            score={hotel.average_sentiment}
          />
            <span>Based on {hotel.total_reviews} reviews</span>
          </div>
        </div>
        <div className="hotel-hero__gallery">
          <img src={gallery[0]} alt={`${hotel.name} exterior`} />
          <div>
            <img src={gallery[1]} alt={`${hotel.name} room`} />
            <img src={gallery[2]} alt={`${hotel.name} interior`} />
          </div>
        </div>
      </section>

      <section className="hotel-info-grid">
        <div className="card hotel-amenities">
          <div className="section-heading">
            <div>
              <span className="hotel-kicker">Everything you need</span>
              <h2>Amenities</h2>
            </div>
            <span className="amenity-count">{amenities.length}</span>
          </div>
          <div className="amenities-list">
            {amenities.map((amenity) => <span key={amenity}>✓ {amenity}</span>)}
          </div>
        </div>
        <div className="card hotel-map-card">
          <div className="section-heading">
            <div>
              <span className="hotel-kicker">Find your way</span>
              <h2>Location</h2>
            </div>
            <span className="map-pin">⌖</span>
          </div>
          <iframe title={`Map showing ${hotel.name}`} src={mapUrl} loading="lazy" />
        </div>
      </section>

      {/* Sentiment Statistics */}
      {hotel.total_reviews > 0 && (
        <div className="stats">
          <div className="stat-card">
            <div className="number" style={{ color: '#28a745' }}>
              {sentimentStats.positive}
            </div>
            <div className="label">Positive</div>
          </div>
          <div className="stat-card">
            <div className="number" style={{ color: '#6c757d' }}>
              {sentimentStats.neutral}
            </div>
            <div className="label">Neutral</div>
          </div>
          <div className="stat-card">
            <div className="number" style={{ color: '#dc3545' }}>
              {sentimentStats.negative}
            </div>
            <div className="label">Negative</div>
          </div>
          <div className="stat-card">
            <div className="number">
              {((hotel.average_sentiment) * 100).toFixed(0)}%
            </div>
            <div className="label">Overall Score</div>
          </div>
        </div>
      )}

      {/* Review Summary */}
      <ReviewSummary 
        hotelId={parseInt(id)} 
        totalReviews={hotel.total_reviews} 
      />

      {/* Review Form */}
      <ReviewForm hotelId={parseInt(id)} onReviewAdded={handleReviewAdded} />

      {/* Reviews List */}
      <div className="card">
        <div className="reviews-heading">
          <div>
            <span className="hotel-kicker">Guest experiences</span>
            <h3>Reviews ({filteredReviews.length})</h3>
          </div>
          <div className="review-filters" role="group" aria-label="Filter reviews">
            {['all', 'positive', 'neutral', 'negative'].map((filter) => (
              <button key={filter} type="button" className={reviewFilter === filter ? 'active' : ''} onClick={() => setReviewFilter(filter)}>
                {filter[0].toUpperCase() + filter.slice(1)}
              </button>
            ))}
          </div>
        </div>
        
        {filteredReviews.length === 0 ? (
          <p style={{ color: '#666', fontStyle: 'italic' }}>
            No {reviewFilter === 'all' ? '' : reviewFilter} reviews yet.
          </p>
        ) : (
          <div>
            {filteredReviews.map(review => (
                <ReviewItem key={review.id} review={review} />
              ))}
          </div>
        )}
      </div>
    </div>
  );
};

export default HotelDetail;
