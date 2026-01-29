from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.db.database import SessionLocal
from app.services.reports import generate_weekly_report

from app.services.clerk_auth import get_current_user
from app.db.models import User
from app.db.database import get_db

router = APIRouter(prefix="/analytics/reports", tags=["reports"])

@router.get("/weekly")
def get_weekly_report(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Returns the latest AI-generated weekly report for the current user.
    """
    return generate_weekly_report(db, current_user.id)
