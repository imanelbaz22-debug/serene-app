from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import List
from app.db.database import SessionLocal
from app.db.models import JournalEntry
from app.services.journal import summarize_journal

from app.services.clerk_auth import get_current_user
from app.db.models import User, JournalEntry
from app.db.database import get_db

from datetime import datetime, timezone
from app.db.models import User, JournalEntry, ChatMessage

router = APIRouter(prefix="/journal", tags=["journal"])

class JournalCreate(BaseModel):
    content: str

@router.post("/")
def create_journal_entry(
    payload: JournalCreate, 
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if not payload.content:
        raise HTTPException(status_code=400, detail="Journal content cannot be empty")
    
    # AI Summarization
    analysis = summarize_journal(payload.content)
    
    entry = JournalEntry(
        user_id=current_user.id,
        content=payload.content,
        summary=analysis.get("summary"),
        advice=analysis.get("advice")
    )
    
    db.add(entry)
    db.commit()
    db.refresh(entry)
    
    return entry

@router.get("/")
def get_journal_entries(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    # 1. Get Journal Entries
    journal_entries = (
        db.query(JournalEntry)
        .filter(JournalEntry.user_id == current_user.id)
        .all()
    )
    
    # 2. Get Chat Messages
    chat_messages = (
        db.query(ChatMessage)
        .filter(ChatMessage.user_id == current_user.id)
        .all()
    )
    
    # 3. Transform and Merge
    unified_history = []
    
    for entry in journal_entries:
        unified_history.append({
            "id": f"journal_{entry.id}",
            "db_id": entry.id,
            "type": "journal",
            "content": entry.content,
            "summary": entry.summary,
            "advice": entry.advice,
            "timestamp": entry.timestamp,
            "role": "user" # Implicitly user
        })
        
    for msg in chat_messages:
        unified_history.append({
            "id": f"chat_{msg.id}",
            "db_id": msg.id,
            "type": "chat",
            "content": msg.content,
            "role": msg.role,
            "timestamp": msg.timestamp,
            # Chat messages don't have separate summary/advice fields usually, 
            # but if it's a model response, the content IS the advice.
            "summary": None, 
            "advice": None
        })
        
    # 4. Sort by Timestamp Descending
    unified_history.sort(key=lambda x: x["timestamp"], reverse=True)
    
    return unified_history

@router.delete("/{entry_id}")
def delete_journal_entry(
    entry_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    entry = (
        db.query(JournalEntry)
        .filter(JournalEntry.id == entry_id, JournalEntry.user_id == current_user.id)
        .first()
    )
    
    if not entry:
        raise HTTPException(status_code=404, detail="Journal entry not found")
        
    db.delete(entry)
    db.commit()
    
    return {"message": "Journal entry deleted"}
