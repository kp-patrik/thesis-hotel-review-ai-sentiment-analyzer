import React, { useState, useEffect, useCallback } from 'react';
import { useParams, Link } from 'react-router-dom';
import { hotelService } from '../services/api';
import ReviewItem from '../components/ReviewItem';
import ReviewForm from '../components/ReviewForm';
import SentimentBadge from '../components/SentimentBadge';
import ReviewSummary from '../components/ReviewSummary';

const HotelDetail = () => {
  const { id } = useParams();
  const [hotel, setHotel] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

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

  return (
    <div className="container">
      <Link to="/" className="btn btn-secondary" style={{ marginBottom: '1rem' }}>
        ← Back to Hotels
      </Link>

      {/* Hotel Information */}
      <div className="card">
        <h1>{hotel.name}</h1>
        <p className="location" style={{ fontSize: '1.1rem', marginBottom: '1rem' }}>
          📍 {hotel.location}
        </p>
        <p style={{ marginBottom: '1.5rem', lineHeight: '1.6' }}>
          {hotel.description}
        </p>
        
        <div style={{ display: 'flex', alignItems: 'center', gap: '1rem' }}>
          <SentimentBadge 
            sentiment={getOverallSentiment(hotel.average_sentiment)} 
            score={hotel.average_sentiment}
          />
          <span style={{ color: '#666' }}>
            Based on {hotel.total_reviews} reviews
          </span>
        </div>
      </div>

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
        <h3>Reviews ({hotel.reviews.length})</h3>
        
        {hotel.reviews.length === 0 ? (
          <p style={{ color: '#666', fontStyle: 'italic' }}>
            No reviews yet. Be the first to write a review!
          </p>
        ) : (
          <div>
            {hotel.reviews
              .sort((a, b) => new Date(b.created_at) - new Date(a.created_at))
              .map(review => (
                <ReviewItem key={review.id} review={review} />
              ))}
          </div>
        )}
      </div>
    </div>
  );
};

export default HotelDetail;
