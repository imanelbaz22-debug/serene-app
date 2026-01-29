from datetime import datetime, date, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import func
from app.db.models import CheckIn

def get_current_streak(db: Session, user_id: int) -> int:
    """
    Calculates the current consecutive check-in streak for a user.
    """
    # Get unique dates of check-ins for this user, ordered descending
    checkin_dates = (
        db.query(func.date(CheckIn.timestamp))
        .filter(CheckIn.user_id == user_id)
        .group_by(func.date(CheckIn.timestamp))
        .order_by(func.date(CheckIn.timestamp).desc())
        .all()
    )
    
    # Convert from Row objects to date objects
    dates = [d[0] for d in checkin_dates]
    if isinstance(dates[0], str):
        dates = [datetime.strptime(d, "%Y-%m-%d").date() for d in dates]

    if not dates:
        return 0

    today = date.today()
    yesterday = today - timedelta(days=1)
    
    # If the last check-in was more than 1 day ago, the streak is broken
    if dates[0] < yesterday:
        return 0
        
    streak = 0
    current_expected_date = dates[0]
    
    for d in dates:
        if d == current_expected_date:
            streak += 1
            current_expected_date -= timedelta(days=1)
        else:
            # Streak broken
            break
            
    return streak
