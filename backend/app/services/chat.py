import os
from typing import List, Dict
from sqlalchemy.orm import Session
from app.db.models import ChatMessage, JournalEntry
from app.services.ai_service import gemini_wrapper
from app.services.sentiment import analyze_sentiment_lite
from google.genai import types

SYSTEM_PROMPT = """
You are 'Serene', a highly empathetic, fun, and supportive 'AI Bestie'. 
Your goal is to listen to the user's problems (stress, relationships, health, work, sleep) and provide helpful, detailed, and personalized advice.

Guidelines:
1. Tone: Warm, light, and friendly. Use 'bestie' occasionally but don't overdo it. 
2. Empathy: Always validate the user's feelings first.
3. Detailed Tips: When giving advice, be specific and science-backed.
4. Interactive: Ask follow-up questions to understand the situation better.
5. Identity: You are Serene, the user's AI bestie.
6. Context: You have access to the user's recent journal entries. Use them to provide relevant context, but only if the user brings it up or it's directly relevant.
"""

class ChatService:
    def __init__(self):
        self.system_prompt = SYSTEM_PROMPT

    def mock_bestie_reply(self, message: str) -> str:
        """
        Provides a keyword-based fallback when Gemini hits a quota limit.
        """
        text = message.lower()
        sentiment = analyze_sentiment_lite(text)
        
        # 1. Topic Detection (Reuse logic from insights)
        reply = "I'm so sorry, bestie! My AI brain is taking a quick 60-second beauty nap (I've hit my free-tier limit). "
        
        advice = ""
        if any(word in text for word in ["fight", "partner", "breakup", "relationship"]):
            advice = "I hear you on that relationship stress. 💖 Try taking a 20-minute breather before talking again—it really helps the heart reset!"
        elif any(word in text for word in ["work", "job", "boss", "deadline"]):
            advice = "Ugh, work pressure is the worst! 💼 Try the Pomodoro technique for just 25 mins to get one small win."
        elif any(word in text for word in ["sleep", "tired", "awake"]):
            advice = "Sending you sleepy vibes! 🌙 Try the 4-7-8 breathing technique: inhale for 4, hold for 7, exhale for 8."
        elif sentiment == "negative":
            advice = "I can feel you're having a rough time. 💖 Even if my brain is on a break, I'm here. Drink a glass of water and take one deep breath for me?"
        else:
            advice = "I'm still here for you! I might be in 'Lite Mode' ✨ right now, but tell me more—I'm listening."

        return reply + "\n\n" + advice

    def local_greeting(self, message: str) -> str:
        msg = message.lower().strip().strip('!?. ')
        greetings = {
            "hi": "Hey bestie! My name is Serene and I'll be your bestie for today, tell me how are you feeling or what's on your mind? I gotchu! ✨",
            "hello": "Hi there, bestie! So glad to see you. How's your day going? I'm here to listen! 💖",
            "hey": "Hey hey! What's up? I'm all ears! ✨",
            "thanks": "Anytime, bestie! That's what I'm here for. You're doing great! ✨",
            "thank you": "You are so welcome! I've always got your back. 💖",
        }
        return greetings.get(msg)

    def get_response(self, db: Session, user_id: int, message: str) -> str:
        # 1. Try local greeting
        local_reply = self.local_greeting(message)
        if local_reply:
            self._save_chat(db, user_id, message, local_reply)
            return local_reply

        # 2. Get Chat History
        db_history = (
            db.query(ChatMessage)
            .filter(ChatMessage.user_id == user_id)
            .order_by(ChatMessage.timestamp.desc())
            .limit(10)
            .all()
        )
        db_history.reverse()
        
        # 3. Get Recent Journal Entries (Context Injection)
        recent_journals = (
            db.query(JournalEntry)
            .filter(JournalEntry.user_id == user_id)
            .order_by(JournalEntry.timestamp.desc())
            .limit(3)
            .all()
        )
        # Reverse to chronological order
        recent_journals.reverse()
        
        contents = []
        
        # Inject Journal Context as "System" or "User Context" messages
        if recent_journals:
            context_str = "Recent Journal Entries:\n"
            for journal in recent_journals:
                context_str += f"- [{journal.timestamp.strftime('%Y-%m-%d %H:%M')}] {journal.content}\n"
            
            # We add this as a 'user' message with a specific instruction or as part of the first message
            # But simpler here to just append it as a "context" message from the user
            # Or better, prepend to history as a system/model turn? 
            # Gemini supports 'user' and 'model'. We can prepend a 'user' message with this context.
            contents.append(types.Content(role="user", parts=[types.Part(text=f"Here is my recent journal context for reference (do not reply to this specific message, just use it for context):\n{context_str}")]))
            contents.append(types.Content(role="model", parts=[types.Part(text="Got it! I have your recent journal context in mind. What's on your mind now?")]))

        for msg in db_history:
            contents.append(types.Content(role=msg.role, parts=[types.Part(text=msg.content)]))
        
        # 4. Call Gemini Wrapper
        bot_text, quota_hit = gemini_wrapper.safe_generate(
            contents=contents + [types.Content(role="user", parts=[types.Part(text=message)])],
            system_instruction=self.system_prompt
        )

        if quota_hit:
            bot_text = self.mock_bestie_reply(message)
        elif not bot_text:
            bot_text = "Oouf, I hit a little snag! Can you say that again, bestie? ✨"

        # 5. Save everything
        self._save_chat(db, user_id, message, bot_text)
        return bot_text

    def _save_chat(self, db: Session, user_id: int, user_content: str, bot_content: str):
        user_msg = ChatMessage(user_id=user_id, role="user", content=user_content)
        bot_msg = ChatMessage(user_id=user_id, role="model", content=bot_content)
        db.add(user_msg)
        db.add(bot_msg)
        db.commit()

# Global instance
chat_service = ChatService()

def respond_to_chat(db: Session, user_id: int, message: str) -> str:
    return chat_service.get_response(db, user_id, message)
