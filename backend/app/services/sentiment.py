POSITIVE_KEYWORDS = ["happy", "excited", "good", "great", "awesome", "better", "proud", "love", "yay", "bestie"]
NEGATIVE_KEYWORDS = ["sad", "stressed", "anxious", "angry", "bad", "terrible", "worst", "unhappy", "depressed", "tired", "oouf", "uugh", "broken"]

def analyze_sentiment_lite(text: str) -> str:
    """
    Returns 'positive', 'negative', or 'neutral' based on simple keyword matching.
    """
    text = (text or "").lower()
    pos_count = sum(1 for word in POSITIVE_KEYWORDS if word in text)
    neg_count = sum(1 for word in NEGATIVE_KEYWORDS if word in text)
    
    if pos_count > neg_count:
        return "positive"
    elif neg_count > pos_count:
        return "negative"
    return "neutral"
