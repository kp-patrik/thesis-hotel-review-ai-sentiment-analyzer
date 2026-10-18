from transformers import pipeline
from typing import Dict, Any, List
import logging
import os

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ReviewSummarizer:
    def __init__(self):
        """Initialize the text summarization pipeline"""
        self.summarizer = None
        self.model_name = None
        
        # Set cache directory to avoid permission issues
        os.environ['TRANSFORMERS_CACHE'] = '/tmp/transformers_cache'
        
        # Try to load the most efficient model for our use case
        try:
            logger.info("Loading t5-small model for summarization")
            self.summarizer = pipeline(
                "summarization",
                model="t5-small",
                device=-1,  # Force CPU usage for better compatibility
                max_length=150,
            )
            self.model_name = "t5-small"
            logger.info("Successfully loaded t5-small model")
        except Exception as e:
            logger.error(f"Failed to load model: {e}")
            logger.info("Using fallback extractive summarization")
    
    def _extractive_summary(self, reviews: List[str], max_sentences: int = 3) -> str:
        """Simple extractive summarization as fallback"""
        if not reviews:
            return "No reviews available to summarize."
        
        # Combine and filter reviews
        sentences = []
        for review in reviews:
            if review and len(review.strip()) > 20:
                # Simple sentence splitting
                review_sentences = review.replace('!', '.').replace('?', '.').split('.')
                sentences.extend([s.strip() for s in review_sentences if len(s.strip()) > 15])
        
        if not sentences:
            return "Unable to extract meaningful sentences from reviews."
        
        # Score sentences based on length and sentiment indicators
        positive_words = {'great', 'excellent', 'amazing', 'wonderful', 'fantastic', 'perfect', 'love', 'beautiful', 'clean', 'friendly'}
        negative_words = {'terrible', 'awful', 'bad', 'poor', 'disappointing', 'dirty', 'rude', 'worst', 'horrible', 'noisy'}
        
        scored_sentences = []
        for sentence in sentences:
            score = 0
            words = set(sentence.lower().split())
            
            # Score based on sentiment words
            score += len(words & positive_words) * 2
            score += len(words & negative_words) * 2
            
            # Prefer moderate length sentences
            if 30 <= len(sentence) <= 150:
                score += 1
            
            scored_sentences.append((score, sentence))
        
        # Sort by score and take top sentences
        scored_sentences.sort(key=lambda x: x[0], reverse=True)
        top_sentences = [sent for _, sent in scored_sentences[:max_sentences]]
        
        return " ".join(top_sentences) if top_sentences else "Unable to generate a meaningful summary."
    
    def _preprocess_reviews(self, reviews: List[str]) -> str:
        """Preprocess and concatenate reviews for summarization"""
        if not reviews:
            return ""
        
        # Filter and clean reviews
        processed_reviews = []
        for review in reviews:
            if review and len(review.strip()) > 10:
                clean_review = " ".join(review.strip().split())
                processed_reviews.append(clean_review)
        
        # Sample across the full list so ordering cannot hide later complaints.
        sample_size = min(len(processed_reviews), 12)
        if len(processed_reviews) > sample_size:
            indexes = [
                round(index * (len(processed_reviews) - 1) / (sample_size - 1))
                for index in range(sample_size)
            ]
            representative_reviews = [processed_reviews[index] for index in indexes]
        else:
            representative_reviews = processed_reviews

        combined_text = " ".join(representative_reviews)
        max_chars = 1800

        if len(combined_text) > max_chars:
            combined_text = combined_text[:max_chars].rsplit(" ", 1)[0] + "..."
        
        return combined_text
    
    def summarize_reviews(
        self,
        reviews: List[str],
        max_length: int = 100,
        min_length: int = 20,
        sentiment_counts: Dict[str, int] | None = None,
        sentiment_examples: Dict[str, str] | None = None,
    ) -> Dict[str, Any]:
        """Summarize a list of reviews"""
        if not reviews:
            return {
                "summary": "No reviews available to summarize.",
                "total_reviews": 0,
                "processed_reviews": 0
            }
        
        processed_count = len([r for r in reviews if r and len(r.strip()) > 10])
        
        if processed_count == 0:
            return {
                "summary": "No meaningful reviews available to summarize.",
                "total_reviews": len(reviews),
                "processed_reviews": 0
            }
        
        try:
            if self.summarizer:
                # Use AI model for summarization
                combined_text = self._preprocess_reviews(reviews)
                
                if len(combined_text.strip()) < 50:
                    return {
                        "summary": "Insufficient review content to generate a summary.",
                        "total_reviews": len(reviews),
                        "processed_reviews": 0
                    }
                
                summary_result = self.summarizer(
                    combined_text,
                    max_length=max_length,
                    min_length=min_length,
                    do_sample=False,
                    clean_up_tokenization_spaces=True
                )
                
                summary_text = summary_result[0]['summary_text'] if summary_result else "Unable to generate summary."
                if sentiment_counts:
                    total = sum(sentiment_counts.values())
                    positive = sentiment_counts.get("POSITIVE", 0)
                    negative = sentiment_counts.get("NEGATIVE", 0)
                    summary_text = (
                        f"{summary_text} Overall sentiment: {positive / total:.0%} positive "
                        f"and {negative / total:.0%} negative across the analyzed reviews."
                    )
                    if sentiment_examples:
                        if sentiment_examples.get("POSITIVE"):
                            summary_text += f" Positive feedback mentioned: {sentiment_examples['POSITIVE']}"
                        if sentiment_examples.get("NEGATIVE"):
                            summary_text += f" Main concern mentioned: {sentiment_examples['NEGATIVE']}"
                
                return {
                    "summary": summary_text,
                    "total_reviews": len(reviews),
                    "processed_reviews": processed_count,
                    "input_length": len(combined_text),
                    "model_used": self.model_name
                }
            else:
                # Use fallback extractive summarization
                summary_text = self._extractive_summary(reviews, max_sentences=3)
                if sentiment_counts:
                    total = sum(sentiment_counts.values())
                    summary_text = (
                        f"{summary_text} Overall sentiment: "
                        f"{sentiment_counts.get('POSITIVE', 0) / total:.0%} positive and "
                        f"{sentiment_counts.get('NEGATIVE', 0) / total:.0%} negative."
                    )
                    if sentiment_examples:
                        if sentiment_examples.get("POSITIVE"):
                            summary_text += f" Positive feedback mentioned: {sentiment_examples['POSITIVE']}"
                        if sentiment_examples.get("NEGATIVE"):
                            summary_text += f" Main concern mentioned: {sentiment_examples['NEGATIVE']}"
                
                return {
                    "summary": summary_text,
                    "total_reviews": len(reviews),
                    "processed_reviews": processed_count,
                    "model_used": "extractive_fallback"
                }
                
        except Exception as e:
            logger.error(f"Error generating summary: {e}")
            
            # Try fallback method
            try:
                summary_text = self._extractive_summary(reviews, max_sentences=2)
                return {
                    "summary": summary_text,
                    "total_reviews": len(reviews),
                    "processed_reviews": processed_count,
                    "error": f"AI summarization failed, used fallback: {str(e)}",
                    "model_used": "extractive_fallback"
                }
            except Exception as fallback_error:
                return {
                    "summary": "Error generating summary. Please try again later.",
                    "error": str(e),
                    "total_reviews": len(reviews),
                    "processed_reviews": 0
                }

# Global instance
review_summarizer = ReviewSummarizer()
