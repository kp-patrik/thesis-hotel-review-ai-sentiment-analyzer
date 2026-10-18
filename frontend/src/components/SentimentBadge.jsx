import React from 'react';

const SentimentBadge = ({ sentiment, score }) => {
  const getSentimentClass = (sentiment) => {
    switch (sentiment) {
      case 'POSITIVE':
        return 'sentiment-positive';
      case 'NEGATIVE':
        return 'sentiment-negative';
      default:
        return 'sentiment-neutral';
    }
  };

  const getSentimentLabel = (sentiment, score) => {
    if (sentiment === 'POSITIVE') {
      return `Positive (${(score * 100).toFixed(0)}%)`;
    } else if (sentiment === 'NEGATIVE') {
      return `Negative (${(score * 100).toFixed(0)}%)`;
    } else {
      return 'Neutral';
    }
  };

  return (
    <span className={`sentiment-badge ${getSentimentClass(sentiment)}`}>
      {getSentimentLabel(sentiment, score)}
    </span>
  );
};

export default SentimentBadge;
