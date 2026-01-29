import os
import time
from google import genai
from google.genai import types
from dotenv import load_dotenv

load_dotenv()

class GeminiWrapper:
    def __init__(self):
        self.api_key = os.getenv("GEMINI_API_KEY")
        if not self.api_key:
            print("WARNING: GEMINI_API_KEY not found in environment variables")
            self.client = None
        else:
            try:
                self.client = genai.Client(api_key=self.api_key)
            except Exception as e:
                print(f"ERROR: Failed to initialize Gemini client: {e}")
                self.client = None
        self.model_id = "gemini-2.0-flash-lite"

    def safe_generate(self, contents, system_instruction=None, temperature=0.7, response_mime_type=None):
        """
        Attempts to generate content from Gemini.
        Returns (text, is_quota_exceeded)
        """
        if not self.client:
            print("ERROR: Gemini client not initialized - triggering fallback")
            return None, True  # Trigger fallback to Mock Bestie
        
        try:
            config = {
                "temperature": temperature,
            }
            if system_instruction:
                config["system_instruction"] = system_instruction
            if response_mime_type:
                config["response_mime_type"] = response_mime_type

            response = self.client.models.generate_content(
                model=self.model_id,
                contents=contents,
                config=types.GenerateContentConfig(**config)
            )
            return response.text, False
        except Exception as e:
            error_str = str(e).lower()
            print(f"DEBUG_AI: Gemini error: {e}")
            if "429" in error_str or "quota" in error_str or "limit" in error_str:
                return None, True
            return None, False

# Global instance
gemini_wrapper = GeminiWrapper()
