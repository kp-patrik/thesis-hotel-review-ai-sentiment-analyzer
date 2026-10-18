import React, { useState } from 'react';
import { summarizationService } from '../services/api';

const ReviewSummary = ({ hotelId, totalReviews }) => {
  const [summary, setSummary] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [expanded, setExpanded] = useState(false);

  const handleSummarize = async () => {
    setLoading(true);
    setError('');
    
    try {
      const result = await summarizationService.summarizeReviews(hotelId);
      setSummary(result);
      setExpanded(true);
    } catch (err) {
      setError('Failed to generate summary. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  if (totalReviews === 0) return null;

  return (
    <div className="card" style={{ marginBottom: '1.5rem', backgroundColor: '#f8f9fa' }}>
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '1rem' }}>
        <h3 style={{ margin: 0, color: '#495057' }}>📝 Review Summary</h3>
        {!summary ? (
          <button 
            onClick={handleSummarize}
            disabled={loading}
            className="btn btn-primary"
          >
            {loading ? 'Generating...' : 'Generate Summary'}
          </button>
        ) : (
          <button 
            onClick={() => setExpanded(!expanded)}
            className="btn btn-secondary"
          >
            {expanded ? 'Hide' : 'Show'} Summary
          </button>
        )}
      </div>

      {error && (
        <div style={{ 
          padding: '0.75rem', 
          backgroundColor: '#f8d7da', 
          border: '1px solid #f5c6cb',
          borderRadius: '0.375rem',
          color: '#721c24',
          marginBottom: '1rem'
        }}>
          {error}
        </div>
      )}

      {loading && (
        <div style={{ 
          padding: '1.5rem', 
          textAlign: 'center', 
          color: '#6c757d',
          backgroundColor: '#fff',
          borderRadius: '0.375rem',
          border: '1px solid #dee2e6'
        }}>
          🤖 Analyzing {totalReviews} reviews...
        </div>
      )}

      {summary && expanded && (
        <div style={{ 
          padding: '1.5rem', 
          backgroundColor: '#fff',
          borderRadius: '0.375rem',
          border: '1px solid #dee2e6'
        }}>
          <div style={{ 
            fontSize: '1rem', 
            lineHeight: '1.6',
            color: '#495057',
            marginBottom: '1rem'
          }}>
            {summary.summary}
          </div>
          
          <div style={{ 
            display: 'flex', 
            gap: '1rem', 
            fontSize: '0.85rem', 
            color: '#6c757d',
            paddingTop: '1rem',
            borderTop: '1px solid #dee2e6'
          }}>
            <span>📊 {summary.processed_reviews} of {summary.total_reviews} reviews</span>
            {summary.model_used && <span>🤖 {summary.model_used}</span>}
          </div>
        </div>
      )}

      {!summary && !loading && !error && (
        <div style={{ 
          padding: '1rem', 
          textAlign: 'center', 
          color: '#6c757d'
        }}>
          Get an AI-generated summary of all {totalReviews} reviews
        </div>
      )}
    </div>
  );
};

export default ReviewSummary;
