import json
from app.services.ai_service import gemini_wrapper
from google.genai import types

SUMMARIZE_PROMPT = """
You are 'Serene', a supportive AI bestie. I am going to give you a long journal entry/vent from my user.
Your job is to:
1. Summarize the main points into a concise 1-2 sentence "Takeaway".
2. Provide 2-3 actionable, empathetic "Bestie Advice" bullet points.

Format your response as a JSON object with two keys: "summary" and "advice" (as a string with bullet points).
"""

def summarize_journal(content: str):
    """
    Uses Gemini to summarize a long-form journal entry with fallback logic.
    """
    # 1. Attempt Gemini Call
    bot_text, quota_hit = gemini_wrapper.safe_generate(
        contents=[types.Content(role="user", parts=[types.Part(text=content)])],
        system_instruction=SUMMARIZE_PROMPT,
        response_mime_type="application/json"
    )

    if quota_hit:
        return {
            "summary": "I'm having a hard time summarizing this right now because I've hit my daily chat limit with Google! ☕",
            "advice": "• Take a deep breath.\n• Come back in a little while and I'll have more advice for you.\n• Keep writing if it feels good!"
        }
    
    if not bot_text:
        return {
            "summary": "I heard you, bestie. Even if my brain hit a glitch, I'm here for you.",
            "advice": "• Take a deep breath.\n• Remember that your feelings are valid.\n• Try writing more if it helps!"
        }

    try:
        return json.loads(bot_text)
    except Exception:
        return {
            "summary": "I'm listening, bestie. I couldn't quite summarize that, but I've got your back.",
            "advice": "• Let's keep talking.\n• Take one small step for yourself today."
        }
