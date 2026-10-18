import React, { useState, useEffect } from 'react';
import HotelCard from '../components/HotelCard';
import { hotelService } from '../services/api';

const HotelList = () => {
  const [hotels, setHotels] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    fetchHotels();
  }, []);

  const fetchHotels = async () => {
    try {
      const data = await hotelService.getAllHotels();
      setHotels(data);
    } catch (err) {
      setError('Failed to load hotels');
      console.error('Error fetching hotels:', err);
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="container">
        <div className="loading">Loading hotels...</div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="container">
        <div className="error">{error}</div>
      </div>
    );
  }

  return (
    <div className="container">
      <h2 style={{ marginBottom: '2rem', color: '#333' }}>Available Hotels</h2>
      
      {hotels.length === 0 ? (
        <div className="card">
          <p>No hotels available at the moment.</p>
        </div>
      ) : (
        <div className="hotel-grid">
          {hotels.map(hotel => (
            <HotelCard key={hotel.id} hotel={hotel} />
          ))}
        </div>
      )}
    </div>
  );
};

export default HotelList;
