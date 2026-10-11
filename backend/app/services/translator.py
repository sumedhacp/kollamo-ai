from __future__ import annotations

import functools
import html
import re
import unicodedata
from dataclasses import dataclass
from enum import Enum
from typing import List, Optional, Tuple
import requests


class LanguageKind(str, Enum):
    MALAYALAM = "malayalam"
    ENGLISH = "english"
    MANGLISH = "manglish"
    MIXED = "mixed"
    UNKNOWN = "unknown"


@dataclass(frozen=True)
class TranslationResult:
    text: str
    confidence: float
    source_language: str
    intermediate_malayalam: Optional[str]
    method: str


class UnifiedTranslationEngine:
    MALAYALAM_RE = re.compile(r"[\u0D00-\u0D7F]")
    LATIN_RE = re.compile(r"[A-Za-z]")
    LATIN_WORD_RE = re.compile(r"[a-zA-Z']+")
    HTML_RE = re.compile(r"<[^>]+>", re.IGNORECASE)
    EMOJI_RE = re.compile(
        r"[\U00010000-\U0010ffff\u2600-\u26ff\u2700-\u27bf\uFE00-\uFE0F\u200D]+",
        flags=re.UNICODE,
    )

    TRANSLIT_ENDPOINT = "https://inputtools.google.com/request"
    TRANSLATE_ENDPOINT = "https://translate.googleapis.com/translate_a/single"
    REQUEST_TIMEOUT = 5.0

    # Universal conversational Manglish phonetics & verbal contractions
    PHONETIC_NORMALIZATIONS = (
        # Convert colloquial dressing compound "ittu kandittundu" to literary participle "dharichu kandittundu"
        (r"\bittu\s+(\w+)?kandattind\b|\bittu\s+(\w+)?kanditund\b", r"dharichu kandittundu"),
        # Relative verbal past contractions: aara thanne -> aara thannathu (ആരാണ് തന്നത് - "who gave")
        (r"\baara\s+thanne\b|\baaranu\s+thanne\b", "aara thannathu"),
        # Ablative question markers: evidena / evidenna / evidunnu -> canonical "evide ninnaanu" ("from where")
        (r"\bevidena\b|\bevidenna\b|\bevidunna\b|\bevidunnu\b", "evide ninnaanu"),
        # Evaluative discourse interjection: map informal "kolam" / "kollam" directly to "കൊള്ളാം" (nice/good)
        (r"^kolam\b|\bkolam\b|^kollam\b|\bkollam\b", "കൊള്ളാം"),
        (r"\bayind\b|\baayind\b|\bayittind\b", "aayittundu"),
        (r"\bcheythind\b|\bcheyind\b", "cheythittundu"),
        (r"\bittind\b|\bitind\b", "ittittundu"),
        (r"\b(\w+)attind\b", r"\1ittundu"),
        (r"\b(\w+)atund\b", r"\1ittundu"),
        (r"\b(\w+)itund\b", r"\1ittundu"),
        (r"\b(\w+)indoo\b|\b(\w+)indo\b", r"\1undo"),
        (r"\bindoo\b|\bindo\b|\bindu\b", "undo"),
        (r"\bettirikunna\b|\bettirikkunna\b", "ittirikkunna"),
        (r"\bcheyithirunnekil\b|\bcheythirunnekil\b", "cheythirunnenkil"),
        (r"\bonnude\b|\bonnkoodi\b", "onnukoodi"),
        (r"\bpolichenne\b|\bpolichelle\b", "adipoli aayene"),
        (r"\bayappo\b|\bayapo\b", "aayappol"),
    )

    # Discourse marker regex: ensures interjections at the sentence opening have a strong clause separator
    DISCOURSE_MARKER_RE = re.compile(
        r"^(കൊള്ളാം|super|pwoli|adipoli|nice|kidilan|mass|wow)\s+([,\s]*)?(ith|itha|ithu|aara|aaranu|evide|evide\s+ninnaanu|engane|enth|entha|dress|look)\b",
        re.IGNORECASE,
    )

    COMMON_ENGLISH_WORDS = {
        "the", "be", "to", "of", "and", "a", "in", "that", "have", "i",
        "it", "for", "not", "on", "with", "he", "as", "you", "do", "at",
        "this", "but", "his", "by", "from", "they", "we", "say", "her", "she",
        "or", "an", "will", "my", "one", "all", "would", "there", "their",
        "what", "so", "up", "out", "if", "about", "who", "get", "which", "go",
        "me", "when", "make", "can", "like", "time", "no", "just", "him", "know",
        "take", "people", "into", "year", "your", "good", "some", "could", "them",
        "see", "other", "than", "then", "now", "look", "only", "come", "its", "over",
        "think", "also", "back", "after", "use", "two", "how", "our", "work", "first",
        "well", "way", "even", "new", "want", "because", "any", "these", "give", "day",
        "most", "us", "is", "are", "was", "were", "been", "has", "had", "did", "does",
        "styling", "point", "on", "superb", "loved", "dress", "watch", "link",
        "agree", "with", "dear", "forgot", "mine", "missing", "feel", "wear",
        "acting", "cinema", "movie", "song", "climax", "scene", "music", "bgm",
        "bro", "brother", "sister", "nice", "great", "best", "worst", "bad", "love"
    }

    def __init__(self, *, timeout: float = REQUEST_TIMEOUT):
        self.timeout = timeout
        self.session = requests.Session()
        self.session.headers.update({
            "User-Agent": (
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/124.0.0.0 Safari/537.36"
            ),
            "Accept-Language": "en-US,en;q=0.9,ml;q=0.8",
        })

    @staticmethod
    def normalize(text: str) -> str:
        if not text:
            return ""
        text = html.unescape(text)
        text = unicodedata.normalize("NFC", text)
        text = text.replace("\u200b", "").replace("\ufeff", "").replace("\u00a0", " ")
        return re.sub(r"\s+", " ", text).strip()

    @classmethod
    def extract_emojis(cls, text: str) -> Tuple[str, List[Tuple[int, str]]]:
        emojis = []
        for m in cls.EMOJI_RE.finditer(text):
            emojis.append((m.start(), m.group()))
        cleaned = cls.EMOJI_RE.sub(" ", text)
        cleaned = re.sub(r"\s+", " ", cleaned).strip()
        return cleaned, emojis

    @classmethod
    def normalize_manglish_phonetics(cls, text: str) -> str:
        result = text
        for pattern, replacement in cls.PHONETIC_NORMALIZATIONS:
            result = re.sub(pattern, replacement, result, flags=re.IGNORECASE)
        # Separate introductory interjections with an exclamation mark so MT never treats them as subject agents
        result = cls.DISCOURSE_MARKER_RE.sub(r"\1! \3", result)
        return result

    @classmethod
    def is_malayalam_script(cls, text: str) -> bool:
        return bool(text and cls.MALAYALAM_RE.search(text))

    @classmethod
    def is_latin_script(cls, text: str) -> bool:
        return bool(text and cls.LATIN_RE.search(text))

    @classmethod
    def latin_words(cls, text: str) -> List[str]:
        return [w.lower() for w in cls.LATIN_WORD_RE.findall(text)]

    @classmethod
    def classify(cls, text: str) -> LanguageKind:
        has_ml = cls.is_malayalam_script(text)
        words = cls.latin_words(text)
        has_latin = bool(words)

        if has_ml and has_latin:
            return LanguageKind.MIXED
        if has_ml:
            return LanguageKind.MALAYALAM
        if not has_latin:
            return LanguageKind.UNKNOWN

        total_words = len(words)
        eng_matches = sum(1 for w in words if w in cls.COMMON_ENGLISH_WORDS)

        if eng_matches == total_words:
            return LanguageKind.ENGLISH

        if total_words > 0 and (eng_matches / total_words) >= 0.65:
            return LanguageKind.ENGLISH

        return LanguageKind.MANGLISH

    def transliterate_full_sentence(self, text: str) -> str:
        canonical = self.normalize_manglish_phonetics(text)
        params = {
            "text": canonical,
            "itc": "ml-t-i0-und",
            "num": "1",
            "cp": "0",
            "cs": "1",
            "ie": "utf-8",
            "oe": "utf-8",
        }
        try:
            resp = self.session.get(self.TRANSLIT_ENDPOINT, params=params, timeout=self.timeout)
            if resp.status_code == 200:
                data = resp.json()
                if isinstance(data, list) and len(data) >= 2 and data[0] == "SUCCESS":
                    segments = data[1]
                    parts = []
                    for seg in segments:
                        if isinstance(seg, list) and len(seg) >= 2 and seg[1]:
                            parts.append(seg[1][0])
                    if parts:
                        return " ".join(parts).strip()
        except Exception:
            pass
        return canonical

    def _cloud_translate(self, text: str, source: str = "auto", target: str = "en") -> Optional[str]:
        if not text:
            return None

        # Strategy 1: Google dict-chrome-ex
        try:
            params = {
                "client": "dict-chrome-ex",
                "sl": source,
                "tl": target,
                "dt": "t",
                "q": text,
            }
            resp = self.session.get(self.TRANSLATE_ENDPOINT, params=params, timeout=self.timeout)
            if resp.status_code == 200:
                data = resp.json()
                if isinstance(data, list) and data and isinstance(data[0], list):
                    chunks = [p[0] for p in data[0] if isinstance(p, list) and p and isinstance(p[0], str)]
                    res = "".join(chunks).strip()
                    if res and not self.HTML_RE.search(res):
                        return res
        except Exception:
            pass

        # Strategy 2: Google gtx
        try:
            params = {
                "client": "gtx",
                "sl": source,
                "tl": target,
                "dt": "t",
                "q": text,
            }
            resp = self.session.get(self.TRANSLATE_ENDPOINT, params=params, timeout=self.timeout)
            if resp.status_code == 200:
                data = resp.json()
                if isinstance(data, list) and data and isinstance(data[0], list):
                    chunks = [p[0] for p in data[0] if isinstance(p, list) and p and isinstance(p[0], str)]
                    res = "".join(chunks).strip()
                    if res and not self.HTML_RE.search(res):
                        return res
        except Exception:
            pass

        # Strategy 3: Deep Translator fallback
        try:
            from deep_translator import MyMemoryTranslator
            src_lang = "malayalam" if source in {"ml", "malayalam"} else "auto"
            translated = MyMemoryTranslator(source=src_lang, target=target).translate(text)
            if translated and not self.HTML_RE.search(translated) and "MYMEMORY WARNING" not in translated.upper():
                return translated.strip()
        except Exception:
            pass

        return None

    @staticmethod
    def post_process_english_semantics(text: str) -> str:
        cleaned = text
        cleaned = re.sub(
            r"\bseen\s+(this|it)\s+by\s+([^,.]+)",
            r"seen \2 wearing \1",
            cleaned,
            flags=re.IGNORECASE,
        )
        cleaned = re.sub(
            r"\b([A-Z][a-zA-Z\s]+?)\s+has\s+seen\s+this\b",
            r"Seen \1 wearing this",
            cleaned,
            flags=re.IGNORECASE,
        )
        cleaned = re.sub(r"\s+", " ", cleaned or "").strip()
        return (cleaned[:1].upper() + cleaned[1:]) if cleaned else ""

    def translate_detailed(self, text: str, source: str = "auto", target: str = "en") -> TranslationResult:
        normalized_raw = self.normalize(text)
        if not normalized_raw:
            return TranslationResult("", 1.0, "unknown", None, "empty")

        core_text, emojis = self.extract_emojis(normalized_raw)
        emoji_suffix = " " + " ".join(e[1] for e in emojis) if emojis else ""

        if not core_text and emojis:
            return TranslationResult(normalized_raw, 1.0, "emoji", None, "emoji_pass")

        kind = self.classify(core_text)

        # 1. Pure English comments -> Unchanged
        if kind == LanguageKind.ENGLISH:
            return TranslationResult(normalized_raw, 0.99, "english", None, "english_invariant")

        # 2. Pure Malayalam Script
        if kind == LanguageKind.MALAYALAM or (self.is_malayalam_script(core_text) and not self.is_latin_script(core_text)):
            translated = self._cloud_translate(core_text, source="ml", target="en")
            if translated:
                final_text = (self.post_process_english_semantics(translated) + emoji_suffix).strip()
                return TranslationResult(final_text, 0.95, "malayalam", core_text, "ml->en")

        # 3. Manglish or Mixed Code
        transliterated_ml = self.transliterate_full_sentence(core_text)
        translated = self._cloud_translate(transliterated_ml, source="ml", target="en")
        if translated and translated.strip().lower() != core_text.strip().lower():
            final_text = (self.post_process_english_semantics(translated) + emoji_suffix).strip()
            return TranslationResult(
                final_text,
                0.90,
                "manglish" if kind == LanguageKind.MANGLISH else "mixed",
                transliterated_ml,
                "manglish->ml->en",
            )

        # 4. Direct Cloud Translation fallback
        direct = self._cloud_translate(core_text, source="auto", target="en")
        if direct and direct.strip().lower() != core_text.strip().lower():
            final_text = (self.post_process_english_semantics(direct) + emoji_suffix).strip()
            return TranslationResult(
                final_text,
                0.85,
                kind.value,
                transliterated_ml,
                "direct->en",
            )

        return TranslationResult(normalized_raw, 0.20, kind.value, transliterated_ml, "fallback")

    def translate(self, text: str, source: str = "auto", target: str = "en") -> str:
        return self.translate_detailed(text, source=source, target=target).text


translation_service = UnifiedTranslationEngine()
