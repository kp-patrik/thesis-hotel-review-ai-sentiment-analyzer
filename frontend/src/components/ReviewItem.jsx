import React from 'react';
import SentimentBadge from './SentimentBadge';

const ReviewItem = ({ review }) => {
  const formatDate = (dateString) => {
    return new Date(dateString).toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'long',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    });
  };

  return (
    <div className="review-item">
      <div className="reviewer">{review.reviewer_name}</div>
      <div className="text">{review.review_text}</div>
      <div className="meta">
        <span>{formatDate(review.created_at)}</span>
        <SentimentBadge 
          sentiment={review.sentiment_label} 
          score={review.sentiment_score}
        />
      </div>
    </div>
  );
};

export default ReviewItem;
