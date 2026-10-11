# backend/app/services/normalizer.py
import re
import html
import unicodedata
from typing import List, Dict, Tuple, Optional, Any
from pydantic import BaseModel

class TokenTag(BaseModel):
    token: str
    normalized: str
    tag: str
    type: str


class ManglishPhoneticNormalizer:
    """
    Sub-tokenization, phonetic normalization, and syllable collapsing engine for Manglish.
    Normalizes spelling variations (e.g., pwoli -> poli, pwoollliiii -> poli, adipoli -> poli).
    """

    REPEATED_CHARS = re.compile(r"(.)\1{1,}")

    # Canonical root dictionary for sentiment and discourse tokens
    CANONICAL_ROOT_MAP = {
        # Positivity & Hype clusters
        "poli": "poli", "pwoli": "poli", "polichu": "polichu", "pwolichu": "polichu",
        "adipoli": "adipoli", "adupichu": "adipoli", "kidu": "kidu", "kidilan": "kidilan",
        "kidilolskidilam": "kidilan", "kollam": "kollam", "kollaam": "kollam", "kollaamm": "kollam",
        "theepori": "theepori", "romancham": "romancham", "thooki": "thooki",

        # Negativity & Critique clusters
        "bore": "bore", "boring": "bore", "booor": "bore",
        "lag": "lag", "laaag": "lag", "chali": "chali", "chaali": "chali",
        "durantham": "durantham", "veruppeer": "veruppeer", "verupichu": "veruppeer",
        "shokam": "shokam", "shookam": "shokam", "kopp": "kopp",

        # Common auxiliaries & pronouns
        "aanu": "aanu", "aannu": "aanu", "aano": "aanu", "aayirunnu": "aayirunnu",
        "illa": "illa", "illaa": "illa", "ille": "illa", "undo": "undu", "und": "undu",
        "njan": "njan", "njanum": "njan", "padam": "padam", "paadam": "padam"
    }

    # Syllable and digraph replacement patterns
    SYLLABLE_REPLACEMENTS = [
        (r"p+w+o+", "po"),            # pwo / pwoo -> po
        (r"p+o+l+i+", "poli"),         # polii / pooli -> poli
        (r"k+o+l+[a|l]+m+", "kollam"),   # kollaam / koolam -> kollam
        (r"a+d+i+p+o+l+i+", "adipoli"), # adipoliii -> adipoli
        (r"k+i+d+u+", "kidu"),         # kiduuu -> kidu
        (r"b+o+r+e*", "bore"),         # boooore -> bore
        (r"l+a+a+g+", "lag"),          # laaag -> lag
        (r"c+h+a+l+i+", "chali"),      # chaaalii -> chali
    ]

    @classmethod
    def collapse_elongations(cls, token: str) -> str:
        """
        Collapses repeated characters down to a single instance (e.g., pwoollliiii -> pwoli).
        """
        if re.search(r"[\u0D00-\u0D7F]", token):
            return token
        return cls.REPEATED_CHARS.sub(r"\1", token.lower())

    @classmethod
    def canonicalize_token(cls, word: str) -> str:
        """
        Converts phonetic spelling variants into standardized root forms.
        """
        lowered = word.lower().strip()
        if not lowered or re.search(r"[\u0D00-\u0D7F]", lowered):
            return word

        # 1. Collapse elongated characters
        simplified = cls.collapse_elongations(lowered)

        # 2. Check regex syllable patterns
        for pattern, root in cls.SYLLABLE_REPLACEMENTS:
            if re.fullmatch(pattern, lowered) or re.fullmatch(pattern, simplified):
                return root

        # 3. Direct lookup in canonical map
        if lowered in cls.CANONICAL_ROOT_MAP:
            return cls.CANONICAL_ROOT_MAP[lowered]
        if simplified in cls.CANONICAL_ROOT_MAP:
            return cls.CANONICAL_ROOT_MAP[simplified]

        # 4. Standardize common suffixes
        if simplified.endswith("chuu") or simplified.endswith("chu"):
            stem = simplified[:-3] if simplified.endswith("chu") else simplified[:-4]
            if stem in ["pol", "pwol"]:
                return "polichu"

        return simplified

    @classmethod
    def normalize_sentence(cls, text: str) -> Tuple[str, Dict[str, str]]:
        if not text:
            return "", {}
        cleaned = html.unescape(text)
        pattern = r"[\u0D00-\u0D7F]+|[a-zA-Z0-9']+|[^\s\w\u0D00-\u0D7F]"
        tokens = re.findall(pattern, cleaned)
        norm_map = {}
        normalized = []

        for t in tokens:
            if re.match(r"^[a-zA-Z]+$", t):
                canon = cls.canonicalize_token(t)
                norm_map[t.lower()] = canon
                normalized.append(canon)
            else:
                norm_map[t.lower()] = t
                normalized.append(t)

        norm_text = " ".join(normalized)
        norm_text = re.sub(r"\s+([.,!?;:])", r"\1", norm_text)
        return norm_text.strip(), norm_map

    @classmethod
    def normalize(cls, text: str) -> str:
        res, _ = cls.normalize_sentence(text)
        return res

    @classmethod
    def check_language_support(cls, text: str):
        from app.services.language_guard import LanguageGuardService
        return LanguageGuardService.validate_text(text)


class TokenLanguageTagger:
    COMMON_ENGLISH = {
        "i", "wanna", "watch", "again", "movie", "film", "acting", "story", "direction",
        "scene", "songs", "bgm", "music", "super", "good", "bad", "waste", "time", "nice"
    }

    @classmethod
    def tag_word(cls, word: str) -> str:
        clean = word.strip()
        if not clean or re.match(r"^[^\w\s\u0D00-\u0D7F]+$", clean):
            return "[SYMBOL]"
        if re.search(r"[\u0D00-\u0D7F]", clean):
            return "[MALAYALAM_SCRIPT]"
        if clean.lower() in cls.COMMON_ENGLISH or clean.lower() in ["the", "a", "an", "is", "was", "it"]:
            return "[ENGLISH]"
        return "[MANGLISH]"

    @classmethod
    def tag_tokens(cls, raw_text: str, norm_map: Optional[Dict[str, str]] = None) -> List[TokenTag]:
        pattern = r"[\u0D00-\u0D7F]+|[a-zA-Z0-9']+|[^\s\w\u0D00-\u0D7F]"
        words = re.findall(pattern, raw_text)
        mapping = norm_map or {}
        results = []
        for w in words:
            tag = cls.tag_word(w)
            norm_w = mapping.get(w.lower(), w)
            results.append(TokenTag(token=w, normalized=norm_w, tag=tag, type=tag))
        return results

    @classmethod
    def tag_sentence(cls, text: str) -> List[TokenTag]:
        return cls.tag_tokens(text)


class GoogleTranslationService:
    """
    Translates colloquial Manglish and native Malayalam to English.
    """

    LEXICON_MAP = {
        "ennik": "I", "enikku": "I", "enikk": "I", "njan": "I", "njangal": "we",
        "nee": "you", "ningal": "you", "avan": "he", "aval": "she", "avaru": "they",
        "ith": "this", "ath": "that", "ee": "this", "aa": "that", "aanu": "is",
        "aayirunnu": "was", "alla": "not", "illa": "no", "aayi": "became",
        "nalonam": "very much", "nallonam": "very much", "valare": "very",
        "kooduthal": "more", "othiri": "a lot", "theere": "at all", "chumma": "simply",
        "pinne": "then", "vere": "other", "nthaalla": "what else",
        "ishatayi": "liked it", "ishtamayi": "liked it", "ishtapettu": "loved it",
        "ishtam": "like", "pwoli": "awesome", "poli": "awesome", "polichu": "awesome",
        "adipoli": "fantastic", "kidu": "superb", "kidilan": "terrific",
        "romancham": "goosebumps", "thooki": "rocked", "theepori": "fiery",
        "thakarthu": "killed it", "nalla": "good", "super": "super", "kollam": "good",
        "bore": "boring", "lag": "slow", "chali": "lame", "durantham": "disaster",
        "waste": "waste", "churandiyath": "plagiarized", "mosham": "bad",
        "kollilla": "not good", "ishtaayilla": "did not like", "ayila": "not",
        "padam": "movie", "cinema": "movie", "kandu": "watched", "kanan": "to watch",
        "nokki": "watched", "kelkkan": "to listen", "paattu": "song", "acting": "acting",
        "story": "story", "direction": "direction", "climax": "climax",
        "wanna": "want to", "gonna": "going to", "gotta": "got to",
        "again": "again", "watch": "watch", "see": "see"
    }

    PHONETIC_CONVERSIONS = [
        (r"\bennik\b|\benikku\b", "എനിക്ക്"),
        (r"\bnalonam\b|\bnallonam\b", "നന്നായി"),
        (r"\bishatayi\b|\bishtamayi\b|\bishtapettu\b", "ഇഷ്ടമായി"),
        (r"\bishtaayilla\b|\bishtam\s+ayila\b", "ഇഷ്ടമായില്ല"),
        (r"\bvere\b", "വേറെ"),
        (r"\bnthaalla\b|\benthaalla\b", "എന്താ അല്ലാ"),
        (r"\bpadam\b|\bcinema\b", "പടം"),
        (r"\bpwoli\b|\bpoli\b|\badipoli\b", "പൊളി"),
        (r"\bbore\b", "ബോർ"),
        (r"\blag\b", "ലാഗ്"),
        (r"\bvalare\b", "വളരെ"),
        (r"\bkollam\b", "കൊള്ളാം"),
        (r"\bkollilla\b", "കൊള്ളില്ല"),
        (r"\baayirunnu\b", "ആയിരുന്നു"),
        (r"\baanual\b|\baanu\b", "ആണ്")
    ]

    @classmethod
    def has_malayalam_script(cls, text: str) -> bool:
        return bool(re.search(r"[\u0D00-\u0D7F]", text))

    @classmethod
    def transliterate(cls, text: str) -> str:
        if cls.has_malayalam_script(text):
            return text
        res = text.lower()
        for pattern, replacement in cls.PHONETIC_CONVERSIONS:
            res = re.sub(pattern, replacement, res, flags=re.IGNORECASE)
        return res

    @classmethod
    def translate(cls, text: str) -> str:
        clean = text.strip()
        if not clean:
            return ""

        try:
            from deep_translator import GoogleTranslator

            is_mal = cls.has_malayalam_script(clean)
            query = clean if is_mal else cls.transliterate(clean)
            src = "ml" if (is_mal or cls.has_malayalam_script(query)) else "auto"

            res = GoogleTranslator(source=src, target="en").translate(query)
            if res and res.strip().lower() != clean.lower() and not cls.has_malayalam_script(res):
                out = res.strip()
                return out[:1].upper() + out[1:]
        except Exception:
            pass

        tokens = re.findall(r"[\w']+|[^\s\w]", clean)
        translated_tokens = []
        for t in tokens:
            lower = t.lower()
            canon = ManglishPhoneticNormalizer.canonicalize_token(lower)
            if canon in cls.LEXICON_MAP:
                translated_tokens.append(cls.LEXICON_MAP[canon])
            elif lower in cls.LEXICON_MAP:
                translated_tokens.append(cls.LEXICON_MAP[lower])
            else:
                translated_tokens.append(t)

        reconstructed = " ".join(translated_tokens)
        reconstructed = re.sub(r"\s+([.,!?;:])", r"\1", reconstructed)
        reconstructed = re.sub(r"\bI\s+(very much|a lot)\s+(liked it)\b", r"I \2 \1", reconstructed, flags=re.IGNORECASE)

        if reconstructed.strip().lower() == clean.lower():
            return f"Paraphrase: {clean}"

        return reconstructed[:1].upper() + reconstructed[1:]


PhoneticNormalizerService = ManglishPhoneticNormalizer
normalize_text = ManglishPhoneticNormalizer.normalize
normalize_sentence = ManglishPhoneticNormalizer.normalize_sentence
check_language_support = ManglishPhoneticNormalizer.check_language_support