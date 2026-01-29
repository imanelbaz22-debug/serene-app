from sqlalchemy import create_engine, text
from app.db.database import SQLALCHEMY_DATABASE_URL
import os

def reset_sequences():
    print(f"Connecting to database: {SQLALCHEMY_DATABASE_URL}")
    engine = create_engine(SQLALCHEMY_DATABASE_URL)
    
    with engine.connect() as conn:
        # Tables to fix
        tables = ['users', 'chat_messages', 'checkins', 'journal_entries']
        
        for table in tables:
            print(f"Resetting sequence for {table}...")
            try:
                # PostgreSQL specific command to reset sequence to max(id)
                sql = text(f"SELECT setval(pg_get_serial_sequence('{table}', 'id'), coalesce(max(id),0) + 1, false) FROM {table};")
                conn.execute(sql)
                print(f"✅ Reset {table} sequence success.")
            except Exception as e:
                print(f"❌ Failed to reset {table}: {e}")
        
    print("Done! Sequences synchronized.")

if __name__ == "__main__":
    reset_sequences()
