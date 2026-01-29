from fastapi import APIRouter, Depends
from pydantic import BaseModel
from datetime import datetime, timezone
from typing import Optional

from sqlalchemy.orm import Session
from app.db.database import get_db
from app.db import models

from app.services.clerk_auth import get_current_user
from app.db.models import User

router = APIRouter()

class CheckInCreate(BaseModel):
    mood: int
    text: Optional[str] = None
    energy: Optional[int] = None
    sleep_hours: Optional[float] = None
    timestamp: Optional[datetime] = None

@router.post("/")
def create_checkin(
    payload: CheckInCreate, 
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    ts = payload.timestamp or datetime.now(timezone.utc)

    checkin = models.CheckIn(
        user_id=current_user.id,
        mood=payload.mood,
        text=payload.text,
        energy=payload.energy,
        sleep_hours=payload.sleep_hours,
        timestamp=ts,
    )
    db.add(checkin)
    db.commit()
    db.refresh(checkin)

    return {
        "message": "check-in saved",
        "id": checkin.id,
        "timestamp": checkin.timestamp.isoformat(),
    }
