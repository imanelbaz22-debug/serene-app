import os
from app.db.database import Base, engine, SQLALCHEMY_DATABASE_URL
from app.db.models import CheckIn, ChatMessage, JournalEntry

# Extract path from URL (e.g. sqlite:///./serene.db -> ./serene.db)
db_path = SQLALCHEMY_DATABASE_URL.replace("sqlite:///", "")

if os.path.exists(db_path):
    print(f"Removing existing database: {db_path}")
    os.remove(db_path)
else:
    print(f"Database {db_path} not found.")

print("Creating new database tables...")
Base.metadata.create_all(bind=engine)
print("Database reset successfully.")
