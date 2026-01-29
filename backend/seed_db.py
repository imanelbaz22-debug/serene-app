from datetime import datetime, timedelta, timezone
from app.db.database import SessionLocal
from app.db.models import CheckIn
import random

db = SessionLocal()

print("Seeding database...")

# Create 10 check-ins over the last 10 days
for i in range(10):
    day_offset = 10 - i
    ts = datetime.now(timezone.utc) - timedelta(days=day_offset)
    
    # Random mood between 1 and 10
    mood = random.randint(3, 9)
    energy = random.randint(1, 10)
    sleep = random.uniform(5.0, 9.0)
    
    checkin = CheckIn(
        mood=mood,
        text=f"Seeded entry {i+1}",
        energy=energy,
        sleep_hours=sleep,
        timestamp=ts
    )
    db.add(checkin)

db.commit()
print("Successfully added 10 check-ins.")
db.close()
