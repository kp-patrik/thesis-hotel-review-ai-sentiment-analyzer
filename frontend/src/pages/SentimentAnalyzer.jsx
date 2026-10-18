import React, { useState } from 'react';
import { sentimentService } from '../services/api';
import SentimentBadge from '../components/SentimentBadge';

const SentimentAnalyzer = () => {
  const [text, setText] = useState('');
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const handleAnalyze = async (e) => {
    e.preventDefault();
    
    if (!text.trim()) {
      setError('Please enter some text to analyze');
      return;
    }

    setLoading(true);
    setError('');
    setResult(null);

    try {
      const data = await sentimentService.analyzeSentiment(text.trim());
      setResult(data);
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to analyze sentiment');
    } finally {
      setLoading(false);
    }
  };

  const handleClear = () => {
    setText('');
    setResult(null);
    setError('');
  };

  const sampleTexts = [
    "This hotel was absolutely amazing! The staff was friendly and the room was spotless.",
    "Terrible experience. The room was dirty and the service was awful.",
    "The hotel was okay. Nothing special but decent for the price.",
    "I had the most wonderful stay here. Everything exceeded my expectations!",
    "Poor location and overpriced. Would not recommend to anyone."
  ];

  return (
    <div className="container">
      <div className="card">
        <h2>Sentiment Analyzer</h2>
        <p style={{ color: '#666', marginBottom: '1.5rem' }}>
          Test the sentiment analysis model with your own text. Enter any hotel review or text 
          to see how it would be classified.
        </p>

        {error && <div className="error">{error}</div>}

        <form onSubmit={handleAnalyze}>
          <div className="form-group">
            <label htmlFor="text">Text to Analyze</label>
            <textarea
              id="text"
              value={text}
              onChange={(e) => setText(e.target.value)}
              className="form-control textarea"
              placeholder="Enter text here to analyze its sentiment..."
              rows="4"
              disabled={loading}
            />
          </div>

          <div style={{ display: 'flex', gap: '1rem', marginBottom: '1.5rem' }}>
            <button 
              type="submit" 
              className="btn"
              disabled={loading}
            >
              {loading ? 'Analyzing...' : 'Analyze Sentiment'}
            </button>
            <button 
              type="button" 
              className="btn btn-secondary"
              onClick={handleClear}
              disabled={loading}
            >
              Clear
            </button>
          </div>
        </form>

        {/* Sample texts */}
        <div style={{ marginBottom: '2rem' }}>
          <h4>Try these sample texts:</h4>
          <div style={{ display: 'flex', flexDirection: 'column', gap: '0.5rem' }}>
            {sampleTexts.map((sample, index) => (
              <button
                key={index}
                className="btn btn-secondary"
                style={{ 
                  textAlign: 'left', 
                  padding: '0.5rem',
                  fontSize: '0.9rem',
                  background: 'none',
                  color: '#667eea',
                  border: '1px solid #667eea'
                }}
                onClick={() => setText(sample)}
                disabled={loading}
              >
                "{sample}"
              </button>
            ))}
          </div>
        </div>

        {/* Results */}
        {result && (
          <div className="card" style={{ background: '#f8f9fa', border: '1px solid #e9ecef' }}>
            <h4>Analysis Result</h4>
            
            <div style={{ marginBottom: '1rem' }}>
              <strong>Text:</strong>
              <p style={{ 
                fontStyle: 'italic', 
                background: 'white', 
                padding: '1rem', 
                borderRadius: '5px',
                marginTop: '0.5rem'
              }}>
                "{result.text}"
              </p>
            </div>

            <div style={{ 
              display: 'grid', 
              gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', 
              gap: '1rem' 
            }}>
              <div>
                <strong>Sentiment:</strong>
                <div style={{ marginTop: '0.5rem' }}>
                  <SentimentBadge 
                    sentiment={result.label} 
                    score={result.score}
                  />
                </div>
              </div>
              
              <div>
                <strong>Confidence Score:</strong>
                <div style={{ marginTop: '0.5rem', fontSize: '1.1rem' }}>
                  {(result.confidence * 100).toFixed(1)}%
                </div>
              </div>
              
              <div>
                <strong>Sentiment Score:</strong>
                <div style={{ marginTop: '0.5rem', fontSize: '1.1rem' }}>
                  {(result.score * 100).toFixed(1)}%
                </div>
              </div>
            </div>

            <div style={{ marginTop: '1rem', fontSize: '0.9rem', color: '#666' }}>
              <p>
                <strong>How to read the scores:</strong><br/>
                • Sentiment Score: 0-50% = Negative, 50-60% = Neutral, 60-100% = Positive<br/>
                • Confidence Score: How certain the model is about its prediction
              </p>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default SentimentAnalyzer;
