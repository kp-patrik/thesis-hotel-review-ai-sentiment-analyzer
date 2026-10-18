import React from 'react';
import { useNavigate } from 'react-router-dom';
import SentimentBadge from './SentimentBadge';

const HotelCard = ({ hotel }) => {
  const navigate = useNavigate();

  const handleClick = () => {
    navigate(`/hotel/${hotel.id}`);
  };

  const getOverallSentiment = (score) => {
    if (score > 0.6) return 'POSITIVE';
    if (score < 0.4) return 'NEGATIVE';
    return 'NEUTRAL';
  };

  return (
    <div className="card hotel-card" onClick={handleClick}>
      <h3>{hotel.name}</h3>
      <p className="location">{hotel.location}</p>
      <p className="description">{hotel.description}</p>
      
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginTop: '1rem' }}>
        <div>
          <SentimentBadge 
            sentiment={getOverallSentiment(hotel.average_sentiment)} 
            score={hotel.average_sentiment}
          />
        </div>
        <div style={{ fontSize: '0.9rem', color: '#666' }}>
          {hotel.total_reviews} reviews
        </div>
      </div>
    </div>
  );
};

export default HotelCard;
