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
    <div className="card" style={{ marginBottom: '1.5rem', backgroundColor: 'var(--surface-muted)' }}>
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '1rem' }}>
        <h3 style={{ margin: 0, color: 'var(--text)' }}>📝 Review Summary</h3>
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
          backgroundColor: 'var(--error-bg, #f8d7da)',
          border: '1px solid var(--error-border, #f5c6cb)',
          borderRadius: '0.375rem',
          color: 'var(--error-text, #721c24)',
          marginBottom: '1rem'
        }}>
          {error}
        </div>
      )}

      {loading && (
        <div style={{ 
          padding: '1.5rem', 
          textAlign: 'center', 
          color: 'var(--text-muted)',
          backgroundColor: 'var(--surface)',
          borderRadius: '0.375rem',
          border: '1px solid var(--border)'
        }}>
          🤖 Analyzing {totalReviews} reviews...
        </div>
      )}

      {summary && expanded && (
        <div style={{ 
          padding: '1.5rem', 
          backgroundColor: 'var(--surface)',
          borderRadius: '0.375rem',
          border: '1px solid var(--border)'
        }}>
          <div style={{ 
            fontSize: '1rem', 
            lineHeight: '1.6',
            color: 'var(--text)',
            marginBottom: '1rem'
          }}>
            {summary.summary}
          </div>
          
          <div style={{ 
            display: 'flex', 
            gap: '1rem', 
            fontSize: '0.85rem', 
            color: 'var(--text-muted)',
            paddingTop: '1rem',
            borderTop: '1px solid var(--border)'
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
          color: 'var(--text-muted)'
        }}>
          Get an AI-generated summary of all {totalReviews} reviews
        </div>
      )}
    </div>
  );
};

export default ReviewSummary;
