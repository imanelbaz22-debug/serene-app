from app.services.streaks import get_current_streak
from app.db.database import SessionLocal

def debug_streak():
    print(f"Connecting to database...")
    db = SessionLocal()
    try:
        user_id = 2  # Based on previous debug output
        streak = get_current_streak(db, user_id)
        print(f"Calculated Streak for User {user_id}: {streak}")
    finally:
        db.close()

if __name__ == "__main__":
    debug_streak()
