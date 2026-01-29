from sqlalchemy.orm import Session
from datetime import datetime, timedelta, timezone
from typing import List
import numpy as np
from sklearn.linear_model import LinearRegression

from app.db.models import CheckIn

def mood_forecast(db: Session, user_id: int, days: int = 30):
    """
    Predicts mood trends for a specific user.
    """
    cutoff = datetime.now(timezone.utc) - timedelta(days=days)

    rows = (
        db.query(CheckIn)
        .filter(CheckIn.user_id == user_id, CheckIn.timestamp >= cutoff)
        .order_by(CheckIn.timestamp.asc())
        .all()
    )

    if not rows:
        raise ValueError(f"No check-ins found in last {days} days.")

    # Group by date to average multiple entries per day
    daily_data = {}
    for r in rows:
        day = r.timestamp.date() if hasattr(r.timestamp, 'date') else datetime.fromisoformat(str(r.timestamp)).date()
        if day not in daily_data:
            daily_data[day] = []
        daily_data[day].append(r.mood)
    
    # Calculate daily averages
    # Sort dates chronologically
    sorted_days = sorted(daily_data.keys())
    daily_averages = [sum(daily_data[d]) / len(daily_data[d]) for d in sorted_days]

    if len(daily_averages) < 3: # Reduced requirement slightly if using daily averages
        raise ValueError(f"Not enough active days in last {days} days (need at least 3 distinct days with data).")

    # Prepare regression data
    # X is the day index, y is the average mood
    X = np.array(range(len(daily_averages))).reshape(-1, 1)
    y = np.array(daily_averages)

    model = LinearRegression()
    model.fit(X, y)

    slope = model.coef_[0]
    r2 = model.score(X, y)

    # Predict next day mood
    next_day_idx = np.array([[len(daily_averages)]])
    next_prediction = model.predict(next_day_idx)[0]

    return {
        "days_used": days,
        "num_points": len(rows),
        "num_active_days": len(daily_averages),
        "trend_slope": round(float(slope), 3),
        "r2_score": round(float(r2), 3),
        "next_day_prediction": round(float(next_prediction), 2),
    }
