import re
import unicodedata
from typing import Tuple

class LanguageGuardService:
    """
    Validates that incoming text belongs to Malayalam script, English, or Manglish.
    Rejects Hindi, Tamil, Telugu, Arabic, and other unsupported scripts.
    """

    MANGLISH_LEXICON = {
        "aanu", "aayirunnu", "alla", "padam", "kollam", "pwoli", "adipoli",
        "polichu", "pwolichu", "kidu", "kidilan", "mass", "theepori", "chali",
        "bore", "kopp", "durantham", "veruppeer", "pakshe", "entha", "engane",
        "evide", "eppol", "ippol", "njan", "njangal", "nee", "ningal", "avaru",
        "ivan", "eval", "oru", "ethra", "und", "illa", "undo", "ille", "valare",
        "nalla", "kandu", "kanan", "kelkkan", "parayan", "acting", "scene", "theatre"
    }

    ENGLISH_LEXICON = {
        "the", "be", "to", "of", "and", "a", "in", "that", "have", "i", "it",
        "for", "not", "on", "with", "he", "as", "you", "do", "at", "this", "but",
        "his", "by", "from", "they", "we", "say", "her", "she", "or", "an", "will",
        "my", "one", "all", "would", "there", "their", "what", "so", "up", "out",
        "if", "about", "who", "get", "which", "go", "me", "movie", "good", "bad",
        "super", "great", "nice", "love", "worst", "trailer", "teaser", "song"
    }

    UNSUPPORTED_ALERT = "Unsupported Language: This comment is not in Malayalam, Manglish, or English. Unable to process."

    @classmethod
    def analyze_script(cls, text: str) -> str:
        scripts = {
            "DEVANAGARI": 0,
            "TAMIL": 0,
            "TELUGU": 0,
            "KANNADA": 0,
            "ARABIC": 0,
            "BENGALI": 0,
            "MALAYALAM": 0,
            "LATIN": 0
        }

        for char in text:
            if char.isspace() or unicodedata.category(char).startswith("P"):
                continue
            name = unicodedata.name(char, "")
            if "MALAYALAM" in name:
                scripts["MALAYALAM"] += 1
            elif "DEVANAGARI" in name:
                scripts["DEVANAGARI"] += 1
            elif "TAMIL" in name:
                scripts["TAMIL"] += 1
            elif "TELUGU" in name:
                scripts["TELUGU"] += 1
            elif "KANNADA" in name:
                scripts["KANNADA"] += 1
            elif "ARABIC" in name:
                scripts["ARABIC"] += 1
            elif "BENGALI" in name:
                scripts["BENGALI"] += 1
            elif "LATIN" in name:
                scripts["LATIN"] += 1

        total_foreign = (
            scripts["DEVANAGARI"] + scripts["TAMIL"] + scripts["TELUGU"] +
            scripts["KANNADA"] + scripts["ARABIC"] + scripts["BENGALI"]
        )

        if total_foreign > 2 and total_foreign > scripts["MALAYALAM"]:
            return "UNSUPPORTED_SCRIPT"

        if scripts["MALAYALAM"] > 0:
            return "MALAYALAM_SCRIPT"

        return "LATIN_SCRIPT"

    @classmethod
    def validate_text(cls, text: str) -> Tuple[bool, str, str]:
        """
        Returns: (is_supported: bool, detected_class: str, alert_message: str)
        Detected classes: 'MALAYALAM', 'MANGLISH', 'ENGLISH', or 'UNSUPPORTED'
        """
        cleaned = text.strip()
        if not cleaned:
            return False, "UNSUPPORTED", "Comment payload is empty."

        script_type = cls.analyze_script(cleaned)
        if script_type == "UNSUPPORTED_SCRIPT":
            return False, "UNSUPPORTED", cls.UNSUPPORTED_ALERT

        if script_type == "MALAYALAM_SCRIPT":
            return True, "MALAYALAM", ""

        words = re.findall(r"[a-zA-Z]+", cleaned.lower())
        if not words:
            return True, "ENGLISH", ""

        manglish_hits = sum(1 for w in words if w in cls.MANGLISH_LEXICON)
        english_hits = sum(1 for w in words if w in cls.ENGLISH_LEXICON)
        phonetic_patterns = len(re.findall(r"(aa|ee|oo|zh|th|ch|kk|tt|pp|mm|nn|ll|rr)", cleaned.lower()))

        if manglish_hits > 0 or phonetic_patterns >= 2:
            return True, "MANGLISH", ""

        if english_hits > 0:
            return True, "ENGLISH", ""

        return True, "MANGLISH", ""