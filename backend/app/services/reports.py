import os
import json
from datetime import datetime, timedelta, timezone, date
from sqlalchemy.orm import Session
from app.db.models import CheckIn
from google import genai
from google.genai import types
from dotenv import load_dotenv

load_dotenv()

# Configure Gemini
api_key = os.getenv("GEMINI_API_KEY")
client = genai.Client(api_key=api_key)

REPORT_PROMPT = """
You are 'Serene', a supportive AI bestie and wellness data scientist. 
I am going to give you a summary of a user's health and mood data from the past 7 days.
Your job is to:
1. Write a personalized, empathetic summary of how their week went (1-2 sentences).
2. Highlight a "Biggest Win" (e.g., "You stayed consistent with sleep!").
3. Suggest one "Focus Area" for next week.

Format your response as a JSON object with three keys: "summary", "win", and "focus".
"""

def generate_weekly_report(db: Session, user_id: int):
    """
    Aggregates last 7 days of data for a specific user and generates an AI wellness report.
    Groups multiple check-ins per day into averages.
    """
    one_week_ago = datetime.now(timezone.utc) - timedelta(days=7)
    
    # Get last 7 days of check-ins for this user
    checkins = (
        db.query(CheckIn)
        .filter(CheckIn.user_id == user_id, CheckIn.timestamp >= one_week_ago)
        .order_by(CheckIn.timestamp.asc())
        .all()
    )
    
    if not checkins:
        return {
            "summary": "I don't have enough data yet to write your weekly report, bestie! Keep checking in.",
            "win": "Starting your journey!",
            "focus": "Consistent check-ins."
        }
    
    # Group by date
    daily_data = {}
    for c in checkins:
        # Normalize timestamp to date
        day = c.timestamp.date() if hasattr(c.timestamp, 'date') else datetime.fromisoformat(str(c.timestamp)).date()
        if day not in daily_data:
            daily_data[day] = {"moods": [], "sleeps": []}
        daily_data[day]["moods"].append(c.mood)
        daily_data[day]["sleeps"].append(c.sleep_hours)
    
    # Calculate daily averages
    daily_averages = []
    for day, vals in daily_data.items():
        daily_averages.append({
            "day": day,
            "avg_mood": sum(vals["moods"]) / len(vals["moods"]),
            "avg_sleep": sum(vals["sleeps"]) / len(vals["sleeps"])
        })
    
    # Calculate weekly overall averages from daily averages
    avg_mood = sum(d["avg_mood"] for d in daily_averages) / len(daily_averages)
    avg_sleep = sum(d["avg_sleep"] for d in daily_averages) / len(daily_averages)
    
    data_summary = f"""
    Over the last 7 days (Aggregated by Day):
    - Average Mood: {avg_mood:.1f}/10
    - Average Sleep: {avg_sleep:.1f} hours
    - Total Data Points (Check-ins): {len(checkins)}
    - Active Days: {len(daily_averages)}
    """
    
    try:
        response = client.models.generate_content(
            model="gemini-2.0-flash-lite",
            contents=[types.Content(role="user", parts=[types.Part(text=data_summary)])],
            config=types.GenerateContentConfig(
                system_instruction=REPORT_PROMPT,
                temperature=0.7,
                response_mime_type="application/json"
            )
        )
        
        return json.loads(response.text)
    except Exception as e:
        print(f"ERROR_REPORT: Gemini error: {e}")
        if "429" in str(e):
            return {
                "summary": "I'm having a little trouble gathering your report right now because I've hit my daily data limit with Google! 📊☕",
                "win": "Showing up for yourself!",
                "focus": "Take a rest and check back later."
            }
        return {
            "summary": f"Your week had an average mood of {avg_mood:.1f}. You're doing your best!",
            "win": "You showed up for yourself.",
            "focus": "Keep tracking your stats!"
        }
