import sys
import os
from unittest.mock import MagicMock, patch

# Add the app directory to sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '.')))

from app.services.chat import chat_service
from app.db.database import SessionLocal
from app.db.models import User

def debug_quota():
    db = SessionLocal()
    # Ensure a test user exists
    user = db.query(User).filter(User.clerk_id == "user_2test_bestie_mock").first()
    if not user:
        user = User(clerk_id="user_2test_bestie_mock", username="MockBestie")
        db.add(user)
        db.commit()
        db.refresh(user)

    print("--- Testing Chat Fallback (Simulating 429) ---")
    # Patch the generate_content to simulate 429
    with patch('google.genai.models.Models.generate_content') as mock_gen:
        mock_gen.side_effect = Exception("429 Too Many Requests")
        
        # 1. Test Relationship keyword
        print("\nInput: 'I fought with my partner'")
        res = chat_service.get_response(db, user.id, "I fought with my partner")
        print(f"Response: {res}")
        
        # 2. Test Work keyword
        print("\nInput: 'Work is so busy'")
        res = chat_service.get_response(db, user.id, "Work is so busy")
        print(f"Response: {res}")
        
    db.close()

if __name__ == "__main__":
    debug_quota()
