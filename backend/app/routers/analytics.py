from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db.database import SessionLocal
from app.services.regression import mood_forecast
from app.services.streaks import get_current_streak

from app.services.clerk_auth import get_current_user
from app.db.models import User, CheckIn
from app.db.database import get_db

router = APIRouter(prefix="/analytics", tags=["analytics"])

@router.get("/mood-forecast")
def get_mood_forecast(
    days: int = 30, 
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    try:
        return mood_forecast(db, current_user.id, days)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

from app.services.insights import analyze_checkin

@router.get("/insights/latest")
def get_latest_insights(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    # Get the most recent check-in for THIS user
    latest_checkin = (
        db.query(CheckIn)
        .filter(CheckIn.user_id == current_user.id)
        .order_by(CheckIn.timestamp.desc())
        .first()
    )
    
    if not latest_checkin:
        raise HTTPException(status_code=404, detail="No check-ins found to analyze")
        
    return analyze_checkin(latest_checkin)

@router.get("/streak")
def get_streak(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return {"streak": get_current_streak(db, current_user.id)}
