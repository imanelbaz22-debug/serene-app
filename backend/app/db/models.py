from sqlalchemy import Column, Integer, Float, DateTime, String, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime, timezone
from app.db.database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    clerk_id = Column(String, unique=True, index=True, nullable=False)
    username = Column(String, unique=True, index=True, nullable=True) # Optional, can be synced from Clerk
    email = Column(String, unique=True, index=True, nullable=True) # Optional, can be synced from Clerk
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    checkins = relationship("CheckIn", back_populates="user")
    chat_messages = relationship("ChatMessage", back_populates="user")
    journal_entries = relationship("JournalEntry", back_populates="user")

class CheckIn(Base):
    __tablename__ = "checkins"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    mood = Column(Integer, nullable=False)
    text = Column(String, nullable=True)
    energy = Column(Integer, nullable=True)
    sleep_hours = Column(Float, nullable=True)
    timestamp = Column(DateTime, nullable=False, default=lambda: datetime.now(timezone.utc))

    user = relationship("User", back_populates="checkins")

class ChatMessage(Base):
    __tablename__ = "chat_messages"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    role = Column(String, nullable=False) # 'user' or 'model'
    content = Column(String, nullable=False)
    timestamp = Column(DateTime, nullable=False, default=lambda: datetime.now(timezone.utc))

    user = relationship("User", back_populates="chat_messages")

class JournalEntry(Base):
    __tablename__ = "journal_entries"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    content = Column(String, nullable=False) # The long-form text
    summary = Column(String, nullable=True) # AI-generated summary
    advice = Column(String, nullable=True) # AI-generated advice
    timestamp = Column(DateTime, nullable=False, default=lambda: datetime.now(timezone.utc))

    user = relationship("User", back_populates="journal_entries")
