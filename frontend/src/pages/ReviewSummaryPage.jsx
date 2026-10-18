import React, { useState, useEffect } from 'react';
import { hotelService, summarizationService } from '../services/api';

const ReviewSummaryPage = () => {
  const [hotels, setHotels] = useState([]);
  const [summaries, setSummaries] = useState({});
  const [loading, setLoading] = useState(true);
  const [loadingSummary, setLoadingSummary] = useState({});

  useEffect(() => {
    fetchHotels();
  }, []);

  const fetchHotels = async () => {
    try {
      const data = await hotelService.getAllHotels();
      setHotels(data.filter(hotel => hotel.total_reviews > 0));
    } catch (err) {
      console.error('Error fetching hotels:', err);
    } finally {
      setLoading(false);
    }
  };

  const generateSummary = async (hotelId) => {
    setLoadingSummary(prev => ({ ...prev, [hotelId]: true }));
    
    try {
      const result = await summarizationService.summarizeReviews(hotelId);
      setSummaries(prev => ({ ...prev, [hotelId]: result }));
    } catch (err) {
      setSummaries(prev => ({ 
        ...prev, 
        [hotelId]: { 
          summary: 'Failed to generate summary. Please try again.',
          error: 'Generation failed'
        }
      }));
    } finally {
      setLoadingSummary(prev => ({ ...prev, [hotelId]: false }));
    }
  };

  const generateAllSummaries = async () => {
    for (const hotel of hotels) {
      if (!summaries[hotel.id] && !loadingSummary[hotel.id]) {
        await generateSummary(hotel.id);
        await new Promise(resolve => setTimeout(resolve, 1000)); // Rate limiting
      }
    }
  };

  if (loading) {
    return (
      <div className="container">
        <div className="loading">Loading hotels...</div>
      </div>
    );
  }

  return (
    <div className="container">
      <div style={{ marginBottom: '2rem' }}>
        <h2 style={{ marginBottom: '1rem' }}>Review Summaries</h2>
        <p style={{ color: '#666', marginBottom: '1.5rem' }}>
          AI-generated summaries of guest reviews for each hotel
        </p>
        
        {hotels.length > 0 && (
          <button 
            onClick={generateAllSummaries}
            className="btn btn-primary"
            style={{ marginBottom: '2rem' }}
          >
            Generate All Summaries
          </button>
        )}
      </div>

      {hotels.length === 0 ? (
        <div className="card">
          <p>No hotels with reviews available.</p>
        </div>
      ) : (
        <div style={{ display: 'flex', flexDirection: 'column', gap: '1.5rem' }}>
          {hotels.map(hotel => (
            <div key={hotel.id} className="card">
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: '1rem' }}>
                <div>
                  <h3 style={{ margin: '0 0 0.5rem 0' }}>{hotel.name}</h3>
                  <p style={{ margin: '0 0 0.5rem 0', color: '#666' }}>📍 {hotel.location}</p>
                  <p style={{ margin: 0, fontSize: '0.9rem', color: '#888' }}>
                    {hotel.total_reviews} reviews • {(hotel.average_sentiment * 100).toFixed(0)}% sentiment
                  </p>
                </div>
                {!summaries[hotel.id] && !loadingSummary[hotel.id] && (
                  <button 
                    onClick={() => generateSummary(hotel.id)}
                    className="btn btn-secondary"
                  >
                    Generate Summary
                  </button>
                )}
              </div>

              {loadingSummary[hotel.id] && (
                <div style={{ 
                  padding: '1.5rem', 
                  textAlign: 'center', 
                  color: '#6c757d',
                  backgroundColor: '#f8f9fa',
                  borderRadius: '0.375rem'
                }}>
                  🤖 Analyzing {hotel.total_reviews} reviews...
                </div>
              )}

              {summaries[hotel.id] && (
                <div style={{ 
                  padding: '1.5rem', 
                  backgroundColor: '#f8f9fa',
                  borderRadius: '0.375rem'
                }}>
                  <h4 style={{ margin: '0 0 1rem 0' }}>📝 Summary</h4>
                  <div style={{ 
                    fontSize: '1rem', 
                    lineHeight: '1.6',
                    marginBottom: '1rem'
                  }}>
                    {summaries[hotel.id].summary}
                  </div>
                  
                  <div style={{ 
                    fontSize: '0.85rem', 
                    color: '#6c757d',
                    paddingTop: '1rem',
                    borderTop: '1px solid #dee2e6'
                  }}>
                    📊 {summaries[hotel.id].processed_reviews} of {summaries[hotel.id].total_reviews} reviews analyzed
                    {summaries[hotel.id].model_used && ` • 🤖 ${summaries[hotel.id].model_used}`}
                  </div>
                </div>
              )}
            </div>
          ))}
        </div>
      )}
    </div>
  );
};

export default ReviewSummaryPage;
