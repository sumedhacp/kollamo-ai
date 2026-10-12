import os
import re
from typing import List, Dict
import requests
from pathlib import Path
from dotenv import load_dotenv

# Automatically locate and load .env from project root or backend directory
env_path = Path(__file__).resolve().parents[2] / ".env"
if env_path.exists():
    load_dotenv(dotenv_path=env_path)
else:
    load_dotenv()

try:
    from google import genai
    from google.genai import types
except ImportError:
    genai = None


class ManglishTranslatorService:
    """
    100% Dynamic Translation Engine.
    - Zero hardcoded dictionaries, vocabulary lists, or regex templates.
    - Primary: AI Translation via Gemini (understands colloquial Manglish & Malayalam).
    - Secondary: Resilient neural Google GTX translation fallback.
    """

    _client = None

    @classmethod
    def _get_client(cls):
        if cls._client is None and genai is not None:
            api_key = os.getenv("GEMINI_API_KEY")
            if api_key:
                cls._client = genai.Client(api_key=api_key)
        return cls._client

    @classmethod
    def contains_malayalam_script(cls, text: str) -> bool:
        """Dynamically checks if string contains Malayalam Unicode codepoints."""
        return any("\u0D00" <= char <= "\u0D7F" for char in text)

    @classmethod
    def get_token_breakdown(cls, text: str) -> List[Dict[str, str]]:
        tokens = re.findall(r"[\w']+|[^\w\s]", text)
        result = []
        for token in tokens:
            if not token.isalnum():
                result.append({"token": token, "type": "PUNCTUATION"})
            elif any("\u0D00" <= c <= "\u0D7F" for c in token):
                result.append({"token": token, "type": "Malayalam Script"})
            elif token.isascii() and token.isalpha():
                result.append({"token": token, "type": "Manglish / English"})
            else:
                result.append({"token": token, "type": "Alphanumeric"})
        return result

    @classmethod
    def _translate_with_llm(cls, text: str) -> str:
        """Dynamic zero-shot translation of Manglish and Malayalam script into natural English."""
        client = cls._get_client()
        if not client:
            return ""

        prompt = (
            "You are a linguistic translation engine specialized in South Asian code-mixed text. "
            "Translate the given text into fluent, natural English. The input may be in native Malayalam script, "
            "colloquial Romanized Manglish, or mixed English. "
            "Output ONLY the plain English translation without quotes, brackets, preamble, or explanations.\n\n"
            f"Input text: {text}"
        )

        response = client.models.generate_content(
            model="gemini-3.8-flash",
            contents=prompt,
            config=types.GenerateContentConfig(
                temperature=0.2,
                max_output_tokens=1024,
            )
        )
        if response and response.text:
            return response.text.strip().strip('"').strip("'")
        return ""

    @classmethod
    def _translate_script_gtx(cls, text: str) -> str:
        """Dynamic neural fallback endpoint for native Malayalam script."""
        try:
            url = "https://translate.googleapis.com/translate_a/single"
            params = {
                "client": "gtx",
                "sl": "ml",
                "tl": "en",
                "dt": "t",
                "q": text
            }
            resp = requests.get(
                url,
                params=params,
                headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"},
                timeout=3.5
            )
            if resp.status_code == 200:
                data = resp.json()
                parts = [p[0] for p in data[0] if p and p[0]]
                return "".join(parts).strip()
        except Exception:
            pass
        return ""

    @classmethod
    def translate_manglish_to_english(cls, text: str) -> str:
        cleaned = text.strip()
        if not cleaned:
            return ""

        # Step 1: AI translation (handles both colloquial Manglish & Malayalam script dynamically)
        try:
            ai_result = cls._translate_with_llm(cleaned)
            if ai_result:
                return ai_result
        except Exception:
            pass

        # Step 2: Dynamic fallback for native Malayalam script via neural endpoint
        if cls.contains_malayalam_script(cleaned):
            script_result = cls._translate_script_gtx(cleaned)
            if script_result:
                return script_result

        # Step 3: Return original cleaned text if external engines are completely unreachable
        return cleaned

    def translate(self, text: str) -> str:
        """Instance alias to support services expecting translation_service.translate(text)."""
        return self.translate_manglish_to_english(text)


# Singleton instance expected by inference.py
translation_service = ManglishTranslatorService()
