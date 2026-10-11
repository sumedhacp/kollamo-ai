# backend/app/services/language_guard.py
import re
import unicodedata
from typing import Tuple

class LanguageGuardService:
    """
    Validates that incoming text belongs to Malayalam script, English, or Manglish.
    Rejects Hindi, Tamil, Telugu, Arabic, and other unsupported scripts/dialects.
    """

    # Pure Manglish Exclusive Tokens (Not overlapping standard English vocabulary)
    MANGLISH_EXCLUSIVE_LEXICON = {
        # Core Grammar & Pronouns
        "aanu", "aano", "aayirunnu", "alla", "allallo", "alle", "allaatha",
        "undu", "und", "undo", "illa", "ille", "illallo", "illaatha",
        "njan", "njanum", "njangal", "nammal", "nammude", "nee", "neeyum", "ningal",
        "avan", "avalu", "eval", "ivan", "avaru", "pulli", "pullikaran", "pullikari",
        "ithu", "ith", "athu", "ath", "entha", "enthoke", "engane", "enganeyundu",
        "evide", "evidunnu", "eppol", "ippol", "eppozha", "ippozha", "pinne", "athukondu",
        "pakshe", "ennalum", "ennittu", "athre", "ithre", "athra", "ithra", "valare",
        "adhikam", "kure", "korach", "kurachu", "ellam", "ellarum", "ottum", "theere",
        "kandu", "kando", "kaanuka", "kaanan", "kettilla", "ketto", "paranju", "parayan",
        "cheythu", "cheyyan", "vannu", "varan", "poyi", "pokan", "kazhinju", "theernnu",
        "nokk", "nokku", "nokkuka", "vechu", "thudangi", "thudanguka",

        # Regional Slang & Colloquialisms
        "ippo", "innale", "ippazhe", "enthoru", "choykkan", "choychu", "bhayankara",
        "kayinju", "bejar", "bhejar", "parakkuka", "koyppam", "koyppamilla", "koyappam",
        "sulaimani", "mwonu", "mwole", "machambi", "orappilla", "orappanu", "kalipp",
        "kalippan", "thallu", "machane", "macha", "aliyan", "aliya", "kidilolskidilam",
        "kalakki", "polappan", "thakarthu", "panikitti", "alamb", "paripadi", "sambhavam",
        "sadhanam", "gadi", "gadye", "enthootu", "ennatha", "ennathaanu", "pinnentha",

        # Sentiment Markers
        "pwoli", "poli", "polichu", "pwolichu", "adipoli", "kollam", "kollaam",
        "kidu", "kidilan", "theepori", "romancham", "thooki", "rakshayilla",
        "sambavam", "kalakkal", "chummaalla", "veruppeer", "verupichu", "durantham",
        "kopp", "myru", "shokam", "chali", "oombiya", "oombichu", "valarebore",
        "kolloola", "pattoola", "thripthikaramalla", "padukkam", "koora", "veruthe",
        "padam", "sthalangal", "deivame", "enthamme"
    }

    # English Lexicon
    ENGLISH_LEXICON = {
        "the", "be", "to", "of", "and", "a", "in", "that", "have", "i", "it",
        "for", "not", "on", "with", "he", "as", "you", "do", "at", "this", "but",
        "his", "by", "from", "they", "we", "say", "her", "she", "or", "an", "will",
        "my", "one", "all", "would", "there", "their", "what", "so", "up", "out",
        "if", "about", "who", "get", "which", "go", "me", "when", "make", "can",
        "like", "time", "no", "just", "him", "know", "take", "people", "into",
        "year", "your", "good", "some", "could", "them", "see", "other", "than",
        "then", "now", "look", "only", "come", "its", "over", "think", "also",
        "back", "after", "use", "two", "how", "our", "work", "first", "well",
        "way", "even", "new", "want", "because", "any", "these", "give", "day",
        "most", "us", "great", "bad", "worst", "super", "awesome", "terrible",
        "masterpiece", "disaster", "acting", "story", "direction", "screenplay",
        "camera", "battery", "display", "update", "game", "graphics", "soundtrack",
        "review", "honest", "trailer", "teaser", "video", "content", "channel",
        "loved", "movie", "scene", "scenes", "music", "song", "audio", "actor"
    }

    ROMANIZED_UNSUPPORTED_LEXICON = {
        "hai", "nahi", "nahin", "bohot", "bahut", "achha", "achhi", "kaise", "kaisa",
        "kya", "kyun", "mera", "meri", "hum", "yaar", "bhai", "dekh", "dekho",
        "karo", "kripya", "sahi", "galat", "pata", "chalo", "batao", "mujhe", "tujhe",
        "irukku", "semma", "romba", "illai", "theriyum", "varum", "solla", "nanba",
        "thala", "thalapathy", "paathu", "mudiyala", "enga", "epdi", "ennaikku"
    }

    UNSUPPORTED_ALERT = (
        "Unsupported Language: This comment is not in Malayalam, Manglish, or English. "
        "Unable to process."
    )

    @classmethod
    def analyze_script(cls, text: str) -> str:
        scripts = {
            "DEVANAGARI": 0, "TAMIL": 0, "TELUGU": 0, "KANNADA": 0,
            "ARABIC": 0, "BENGALI": 0, "MALAYALAM": 0, "LATIN": 0
        }

        for char in text:
            if char.isspace() or unicodedata.category(char).startswith("P"):
                continue
            name = unicodedata.name(char, "")
            for s in scripts:
                if s in name:
                    scripts[s] += 1
                    break

        total_foreign = (
            scripts["DEVANAGARI"] + scripts["TAMIL"] + scripts["TELUGU"] +
            scripts["KANNADA"] + scripts["ARABIC"] + scripts["BENGALI"]
        )

        if total_foreign > 1 and total_foreign >= scripts["MALAYALAM"]:
            return "UNSUPPORTED_SCRIPT"

        if scripts["MALAYALAM"] > 0:
            return "MALAYALAM_SCRIPT"

        return "LATIN_SCRIPT"

    @classmethod
    def validate_text(cls, text: str) -> Tuple[bool, str, str]:
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
            return False, "UNSUPPORTED", cls.UNSUPPORTED_ALERT

        # Intercept unsupported Romanized languages (Hinglish/Tanglish)
        unsupported_hits = sum(1 for w in words if w in cls.ROMANIZED_UNSUPPORTED_LEXICON)
        if unsupported_hits >= 2 or (unsupported_hits == 1 and len(words) <= 3):
            return False, "UNSUPPORTED", cls.UNSUPPORTED_ALERT

        manglish_hits = sum(1 for w in words if w in cls.MANGLISH_EXCLUSIVE_LEXICON)
        english_hits = sum(1 for w in words if w in cls.ENGLISH_LEXICON)

        # Phonetic patterns specific to Malayalam romanization
        phonetic_patterns = len(re.findall(
            r"(zh|kk|tt|pp|mm|nn|ll|rr|aay|aan|yill|oola|aano|aayir|adip|pwol)",
            cleaned.lower()
        ))

        # Priority 1: Clear English check
        if english_hits > 0 and manglish_hits == 0 and phonetic_patterns == 0:
            return True, "ENGLISH", ""

        # Priority 2: Clear Manglish check
        if manglish_hits > 0 or phonetic_patterns >= 1:
            return True, "MANGLISH", ""

        # Priority 3: Majority English check
        if english_hits >= len(words) // 2:
            return True, "ENGLISH", ""

        # Short tokens with phonetic markers
        if len(words) <= 3 and phonetic_patterns >= 1:
            return True, "MANGLISH", ""

        return False, "UNSUPPORTED", cls.UNSUPPORTED_ALERT