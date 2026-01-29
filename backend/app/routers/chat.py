from fastapi import APIRouter, Depends
from pydantic import BaseModel
from app.services.chat import respond_to_chat
from sqlalchemy.orm import Session
from app.db.database import SessionLocal

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

from app.services.clerk_auth import get_current_user
from app.db.models import User
from app.db.database import get_db

router = APIRouter(prefix="/chat", tags=["chat"])

class ChatMessage(BaseModel):
    message: str

@router.post("/message")
def chat_endpoint(
    payload: ChatMessage, 
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    print(f"DEBUG: Received message from {current_user.username}: {payload.message}")
    response = respond_to_chat(db, current_user.id, payload.message)
    print(f"DEBUG: Returning response: {response}")
    return {"response": response}
