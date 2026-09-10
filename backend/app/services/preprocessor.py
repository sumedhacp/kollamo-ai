import re
import emoji

class ManglishPreprocessor:
    @staticmethod
    def clean_text(text: str) -> str:
        """
        Cleans raw social media text while preserving emotional context tokens.
        """
        if not text or not isinstance(text, str):
            return ""

        # 1. Convert emojis to descriptive English tokens (e.g., 🔥 -> :fire:)
        cleaned = emoji.demojize(text, delimiters=(" :", ": "))

        # 2. Strip user handles, hashtags symbols (keep text), links, and HTML
        cleaned = re.sub(r"@[\w_]+", "", cleaned)
        cleaned = re.sub(r"https?://\S+|www\.\S+", "", cleaned)
        cleaned = re.sub(r"<.*?>", "", cleaned)
        cleaned = cleaned.replace("#", " ")

        # 3. Collapse character repetitions beyond 2 (e.g., 'superrrrrr' -> 'superr')
        cleaned = re.sub(r"(.)\1{2,}", r"\1\1", cleaned)

        # 4. Normalize redundant whitespace
        cleaned = re.sub(r"\s+", " ", cleaned).strip()

        return cleaned