from transformers import pipeline
from typing import Dict, Any
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class SentimentAnalyzer:
    def __init__(self):
        """Initialize the sentiment analysis pipeline"""
        try:
            # Use DistilBERT model fine-tuned for sentiment analysis.
            self.classifier = pipeline(
                "sentiment-analysis",
                model="distilbert-base-uncased-finetuned-sst-2-english",
                top_k=None,
            )
            logger.info("Sentiment analysis model loaded successfully")
        except Exception as e:
            logger.error(f"Error loading sentiment model: {e}")
            self.classifier = None
    
    def analyze_sentiment(self, text: str) -> Dict[str, Any]:
        """
        Analyze sentiment of given text
        
        Args:
            text (str): Text to analyze
            
        Returns:
            Dict containing sentiment label, score, and confidence
        """
        if not self.classifier:
            return {
                "label": "NEUTRAL",
                "score": 0.5,
                "confidence": 0.0,
                "error": "Model not loaded"
            }
        
        try:
            if not isinstance(text, str) or not text.strip():
                raise ValueError("Text cannot be empty")

            # The model supports 512 tokens; truncation prevents oversized reviews
            # from failing inference while retaining the beginning of the review.
            results = self.classifier(text.strip(), truncation=True, max_length=512)
            
            # Text classification returns one list of scores per input text.
            if results and len(results) > 0:
                if isinstance(results[0], list):
                    results = results[0]

                # Get the highest scoring sentiment
                best_result = max(results, key=lambda x: x['score'])
                
                # Map model labels to our labels
                label_mapping = {
                    "POSITIVE": "POSITIVE",
                    "NEGATIVE": "NEGATIVE"
                }
                
                sentiment_label = label_mapping.get(best_result['label'], "NEUTRAL")
                confidence = best_result['score']
                
                # Convert to our scoring system (0-1 scale where 0.5 is neutral)
                if sentiment_label == "POSITIVE":
                    score = 0.5 + (confidence * 0.5)  # 0.5 to 1.0
                elif sentiment_label == "NEGATIVE":
                    score = 0.5 - (confidence * 0.5)  # 0.0 to 0.5
                else:
                    score = 0.5  # Neutral
                
                return {
                    "label": sentiment_label,
                    "score": round(score, 3),
                    "confidence": round(confidence, 3)
                }
            
        except Exception as e:
            logger.error(f"Error analyzing sentiment: {e}")
            return {
                "label": "NEUTRAL",
                "score": 0.5,
                "confidence": 0.0,
                "error": str(e)
            }
        
        return {
            "label": "NEUTRAL",
            "score": 0.5,
            "confidence": 0.0
        }

# Global instance
sentiment_analyzer = SentimentAnalyzer()
