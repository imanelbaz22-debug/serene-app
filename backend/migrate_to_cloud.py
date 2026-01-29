import os
import sys
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Add app to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '.')))

from app.db.database import Base, SQLALCHEMY_DATABASE_URL as CLOUD_URL
from app.db.models import User, CheckIn, ChatMessage, JournalEntry

# Hardcoded SQLite source
SQLITE_URL = "sqlite:///./serene.db"

def migrate():
    if "sqlite" in CLOUD_URL:
        print("❌ Error: DATABASE_URL is still set to SQLite. Please provide a Neon PostgreSQL URL in .env")
        return

    print(f"🚀 Starting Migration: SQLite -> {CLOUD_URL.split('@')[-1]}")

    # Engines
    src_engine = create_engine(SQLITE_URL)
    dst_engine = create_engine(CLOUD_URL)

    # Create tables in Cloud
    print("📡 Creating tables in Cloud...")
    Base.metadata.create_all(bind=dst_engine)

    # Sessions
    SrcSession = sessionmaker(bind=src_engine)
    DstSession = sessionmaker(bind=dst_engine)
    
    src_db = SrcSession()
    dst_db = DstSession()

    try:
        # 1. Users
        users = src_db.query(User).all()
        print(f"👤 Migrating {len(users)} users...")
        for u in users:
            new_u = User(id=u.id, clerk_id=u.clerk_id, username=u.username, email=u.email, created_at=u.created_at)
            dst_db.merge(new_u)
        dst_db.commit()

        # 2. CheckIns
        checkins = src_db.query(CheckIn).all()
        print(f"📊 Migrating {len(checkins)} check-ins...")
        for c in checkins:
            new_c = CheckIn(id=c.id, user_id=c.user_id, mood=c.mood, text=c.text, energy=c.energy, sleep_hours=c.sleep_hours, timestamp=c.timestamp)
            dst_db.merge(new_c)
        dst_db.commit()

        # 3. Chat
        chats = src_db.query(ChatMessage).all()
        print(f"💬 Migrating {len(chats)} chat messages...")
        for m in chats:
            new_m = ChatMessage(id=m.id, user_id=m.user_id, role=m.role, content=m.content, timestamp=m.timestamp)
            dst_db.merge(new_m)
        dst_db.commit()

        # 4. Journal
        journals = src_db.query(JournalEntry).all()
        print(f"📜 Migrating {len(journals)} journals...")
        for j in journals:
            new_j = JournalEntry(id=j.id, user_id=j.user_id, content=j.content, summary=j.summary, advice=j.advice, timestamp=j.timestamp)
            dst_db.merge(new_j)
        dst_db.commit()

        print("✅ Migration Complete! Serene is now Cloud-Powered. ☁️✨")

    except Exception as e:
        print(f"❌ Migration Failed: {e}")
        dst_db.rollback()
    finally:
        src_db.close()
        dst_db.close()

if __name__ == "__main__":
    migrate()
