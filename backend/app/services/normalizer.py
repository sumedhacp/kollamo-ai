# backend/app/services/normalizer.py
import os
import re
import unicodedata
from typing import List, Dict, Tuple, Optional
from pydantic import BaseModel

class TokenTag(BaseModel):
    token: str
    normalized: str
    tag: str  # [ENGLISH], [MANGLISH], [MALAYALAM_SCRIPT], [PUNCTUATION]

class ManglishPhoneticNormalizer:
    """
    Syllable-aware phonetic normalizer for Romanized Malayalam.
    Collapses elongations, handles digraph variance (pw/th/zh), preserves Unicode
    grapheme clusters, and maps spelling variants to canonical root lemmas.
    """

    CANONICAL_LEMMA_MAP: Dict[str, str] = {
        "poli": "pwoli", "pwoli": "pwoli", "polichu": "pwolichu", "pwolichu": "pwolichu",
        "adipoli": "adipoli", "adipwoli": "adipoli", "athipoli": "adipoli", "athipwoli": "adipoli",
        "athipoly": "adipoli", "adipoly": "adipoli", "adhipoli": "adipoli",
        "kollam": "kollam", "kolam": "kollam", "kollaam": "kollam", "kollamm": "kollam",
        "kollilla": "kollilla", "kolloola": "kollilla",
        "kidu": "kidu", "kidilam": "kidilam", "kidhilan": "kidilam", "kidilan": "kidilam",
        "theepori": "theepori", "theepwori": "theepori", "thakarthu": "thakarthu",
        "nannayi": "nannayi", "nannaayi": "nannayi", "nannaytund": "nannayittund",
        "nalla": "nalla", "nala": "nalla", "valare": "valare",
        "ishtam": "ishtam", "ishtapettu": "ishtapettu", "ishtaayi": "ishtapettu",
        "bore": "bore", "bor": "bore", "boar": "bore",
        "lag": "lag", "laag": "lag", "lagg": "lag",
        "chali": "chali", "chaly": "chali", "durantham": "durantham", "durantam": "durantham",
        "veruppeer": "veruppeer", "veruppir": "veruppeer", "oombu": "oombu", "oombi": "oombu",
        "kopp": "kopp", "kop": "kopp", "shokam": "shokam", "sokam": "shokam",
        "nashtam": "nashtam", "nastam": "nashtam", "mosham": "mosham", "mosam": "mosham",
        "ennik": "enikku", "enikk": "enikku", "enikku": "enikku", "eniku": "enikku",
        "njan": "njan", "njaan": "njan", "pakshe": "pakshe", "pakse": "pakshe",
        "aanu": "aanu", "aan": "aanu", "anu": "aanu",
        "aayirunnu": "aayirunnu", "aarnnu": "aayirunnu", "aayirnu": "aayirunnu",
        "aayi": "aayi", "ayi": "aayi", "aayittund": "aayittund", "ayittund": "aayittund",
        "padam": "padam", "paadam": "padam", "cinema": "cinema", "sinima": "cinema",
        "theere": "theere", "thala": "thala", "vedana": "vedana", "eduthu": "eduthu"
    }

    @classmethod
    def collapse_elongations(cls, text: str) -> str:
        text = re.sub(r"([b-df-hj-np-tv-zB-DF-HJ-NP-TV-Z])\1{2,}", r"\1", text)
        text = re.sub(r"([aeiouAEIOU])\1{2,}", r"\1\1", text)
        return text

    @classmethod
    def phonetic_sound_cluster(cls, word: str) -> str:
        w = word.lower()
        if w in cls.CANONICAL_LEMMA_MAP:
            return cls.CANONICAL_LEMMA_MAP[w]

        w_norm = re.sub(r"\bpw", "p", w)
        w_norm = re.sub(r"\bbw", "b", w_norm)
        w_norm = re.sub(r"th", "t", w_norm)
        w_norm = re.sub(r"dh", "d", w_norm)
        w_norm = re.sub(r"zh", "l", w_norm)
        w_norm = re.sub(r"aa", "a", w_norm)
        w_norm = re.sub(r"ee", "i", w_norm)
        w_norm = re.sub(r"oo", "u", w_norm)
        w_norm = re.sub(r"(.)\1+", r"\1", w_norm)

        for raw_variant, canonical in cls.CANONICAL_LEMMA_MAP.items():
            candidate = re.sub(r"(.)\1+", r"\1", (
                raw_variant.replace("aa", "a")
                           .replace("ee", "i")
                           .replace("th", "t")
                           .replace("dh", "d")
                           .replace("zh", "l")
                           .replace("pw", "p")
            ))
            if w_norm == candidate:
                return canonical

        return w

    @classmethod
    def normalize_sentence(cls, sentence: str) -> Tuple[str, Dict[str, str]]:
        collapsed = cls.collapse_elongations(sentence)
        tokens = re.findall(r"[\u0D00-\u0D7F]+|[a-zA-Z0-9']+|[^\w\s]", collapsed)
        normalized_tokens = []
        transformations = {}

        for token in tokens:
            if token.isascii() and token.isalnum():
                lemma = cls.phonetic_sound_cluster(token)
                normalized_tokens.append(lemma)
                if token.lower() != lemma:
                    transformations[token] = lemma
            else:
                normalized_tokens.append(token)

        reconstructed = " ".join(normalized_tokens)
        reconstructed = re.sub(r"\s+([.,!?;:])", r"\1", reconstructed)
        return reconstructed, transformations

class TokenLanguageTagger:
    """
    Tags each token as [ENGLISH], [MANGLISH], [MALAYALAM_SCRIPT], or [PUNCTUATION].
    """

    ENGLISH_LEXICON = {
        "the", "be", "to", "of", "and", "a", "in", "that", "have", "i", "it",
        "for", "not", "on", "with", "he", "as", "you", "do", "at", "this", "but",
        "his", "by", "from", "they", "we", "say", "her", "she", "or", "an", "will",
        "my", "one", "all", "would", "there", "their", "what", "so", "up", "out",
        "if", "about", "who", "get", "which", "go", "me", "movie", "film", "acting",
        "direction", "music", "bgm", "actor", "actress", "visuals", "story", "good",
        "bad", "worst", "best", "super", "superb", "great", "nice", "love", "loved",
        "waste", "time", "money", "climax", "interval", "first", "second", "half",
        "disaster", "scene", "songs", "screenplay", "performance", "theater", "ott",
        "review", "flop", "hit", "blockbuster", "family", "audience", "watch", "must",
        "full", "total"
    }

    MANGLISH_AFFIXES = (
        "aayi", "ayi", "aayirunnu", "aanu", "anu", "undu", "illa", "alla",
        "il", "um", "inte", "kku", "ode", "e", "o", "ath", "ith", "aane", "ik", "kk"
    )

    @classmethod
    def is_malayalam_script(cls, word: str) -> bool:
        return any("MALAYALAM" in unicodedata.name(c, "") for c in word if not c.isspace())

    @classmethod
    def tag_tokens(cls, text: str, normalizer_map: Optional[Dict[str, str]] = None) -> List[TokenTag]:
        if normalizer_map is None:
            normalizer_map = {}

        raw_tokens = re.findall(r"[\u0D00-\u0D7F]+|[a-zA-Z0-9']+|[.,!?;:]", text)
        tagged_results: List[TokenTag] = []

        for t in raw_tokens:
            if not t.isalnum() and not cls.is_malayalam_script(t):
                tagged_results.append(TokenTag(token=t, normalized=t, tag="[PUNCTUATION]"))
                continue

            if cls.is_malayalam_script(t):
                tagged_results.append(TokenTag(token=t, normalized=t, tag="[MALAYALAM_SCRIPT]"))
                continue

            lower = t.lower()
            normalized_lemma = normalizer_map.get(t, lower)

            if lower in cls.ENGLISH_LEXICON:
                tagged_results.append(TokenTag(token=t, normalized=normalized_lemma, tag="[ENGLISH]"))
                continue

            if lower.endswith(cls.MANGLISH_AFFIXES) or lower in ManglishPhoneticNormalizer.CANONICAL_LEMMA_MAP:
                tagged_results.append(TokenTag(token=t, normalized=normalized_lemma, tag="[MANGLISH]"))
                continue

            if re.search(r"(aa|ee|oo|zh|th|ch|kk|tt|pp|mm|nn|ll|rr|yi)", lower):
                tagged_results.append(TokenTag(token=t, normalized=normalized_lemma, tag="[MANGLISH]"))
            else:
                tagged_results.append(TokenTag(token=t, normalized=normalized_lemma, tag="[ENGLISH]"))

        return tagged_results

class GoogleTranslationService:
    """
    Translates arbitrary code-mixed Manglish/Malayalam into fluent English.
    Uses Google Cloud Translation if configured, with a comprehensive semantic dictionary
    fallback that produces actual English instead of echoing Malayalam script.
    """

    ENGLISH_SEMANTIC_LEXICON = {
        # Core Nouns / Entities
        "padam": "movie", "cinema": "movie", "film": "film", "acting": "acting",
        "visuals": "visuals", "bgm": "background score", "music": "music",
        "story": "story", "climax": "climax", "direction": "direction",
        "interval": "interval", "scene": "scene", "thala": "head",
        "vedana": "pain", "paisa": "money", "theatre": "theatre",

        # Pronouns
        "ithu": "this", "ath": "that", "athu": "that", "njan": "I",
        "enikku": "to me", "ennik": "to me", "nee": "you", "ningal": "you",

        # Verbs / Aspectual Auxiliaries
        "kandu": "watched", "kanan": "to watch", "eduthu": "got", "poyi": "wasted",
        "aanu": "is", "aayirunnu": "was", "aayi": "became", "aayittund": "turned out",
        "und": "has", "undu": "has", "illa": "no", "alla": "not",

        # Positives & Slang
        "pwoli": "awesome", "polichu": "were awesome", "pwolichu": "were awesome",
        "adipoli": "fantastic", "adipwoli": "fantastic", "kidu": "superb",
        "kidilan": "terrific", "kidilam": "terrific", "kollam": "good",
        "nalla": "good", "theepori": "firebrand", "super": "super",
        "nannayi": "well done", "ishtapettu": "liked",

        # Negatives
        "theere": "not at all", "kollilla": "good", "bore": "boring",
        "lag": "laggy", "chali": "cringe", "durantham": "a disaster",
        "waste": "waste", "mosham": "bad", "shokam": "pathetic",
        "kopp": "nonsense", "oombu": "terrible", "bad": "bad",

        # Conjunctions / Adverbs
        "pakshe": "but", "valare": "very", "full": "totally", "total": "total",
        "must": "must", "watch": "watch", "ennu": "that", "vicharichu": "thought"
    }

    @classmethod
    def translate(cls, text: str) -> str:
        cleaned = text.strip()
        if not cleaned:
            return ""

        # Step 1: If input contains native Malayalam script, translate with Google Translator (ml -> en)
        if any("MALAYALAM" in unicodedata.name(c, "") for c in cleaned):
            try:
                from deep_translator import GoogleTranslator
                trans = GoogleTranslator(source="ml", target="en").translate(cleaned)
                if trans and trans.strip() and not any("MALAYALAM" in unicodedata.name(c, "") for c in trans):
                    return trans.strip()[:1].upper() + trans.strip()[1:]
            except Exception:
                pass

        # Step 2: Attempt Google Cloud Translation (if official service account key is mounted)
        if "GOOGLE_APPLICATION_CREDENTIALS" in os.environ:
            try:
                from google.cloud import translate_v2 as translate
                client = translate.Client()
                result = client.translate(cleaned, target_language="en")
                if result and "translatedText" in result:
                    res = result["translatedText"].strip()
                    if not any("MALAYALAM" in unicodedata.name(c, "") for c in res) and res.lower() != cleaned.lower():
                        return res[:1].upper() + res[1:]
            except Exception:
                pass

        # Step 3: Idiomatic Phrase Patterns
        lower = cleaned.lower()
        
        # Pattern: "thala vedana eduthu" -> "got a headache"
        if "thala vedana" in lower:
            headache_str = re.sub(r"\bthala\s+vedana\s+(eduthu|aayi)\b", "got a headache", lower)
            tokens = [cls.ENGLISH_SEMANTIC_LEXICON.get(w, w) for w in re.findall(r"[\w']+|[.,!?;:]", headache_str)]
            out = " ".join(tokens)
            out = re.sub(r"\s+([.,!?;:])", r"\1", out)
            return out[:1].upper() + out[1:]

        # Pattern: "theere kollilla" -> "not good at all"
        if "theere kollilla" in lower:
            kollilla_str = re.sub(r"\btheere\s+kollilla\b", "not good at all", lower)
            tokens = [cls.ENGLISH_SEMANTIC_LEXICON.get(w, w) for w in re.findall(r"[\w']+|[.,!?;:]", kollilla_str)]
            out = " ".join(tokens)
            out = re.sub(r"\s+([.,!?;:])", r"\1", out)
            return out[:1].upper() + out[1:]

        # Pattern: "ithu nalla ... aanu" -> "This is a good ..."
        copula_match = re.search(r"\b(ithu|ath)\s+(nalla|super|kidilan)\s+(\w+)\s+aanu\b", lower)
        if copula_match:
            subj = "This" if copula_match.group(1) == "ithu" else "That"
            adj = cls.ENGLISH_SEMANTIC_LEXICON.get(copula_match.group(2), copula_match.group(2))
            noun = cls.ENGLISH_SEMANTIC_LEXICON.get(copula_match.group(3), copula_match.group(3))
            trailing = lower[copula_match.end():].strip()
            trailing_tokens = [cls.ENGLISH_SEMANTIC_LEXICON.get(w, w) for w in re.findall(r"[\w']+|[.,!?;:]", trailing)]
            trailing_str = f" {' '.join(trailing_tokens)}" if trailing_tokens else ""
            out = f"{subj} is a {adj} {noun}{trailing_str}"
            out = re.sub(r"\s+([.,!?;:])", r"\1", out)
            return out

        # Pattern: "super padam visuals pwolichu"
        if "pwolichu" in lower or "polichu" in lower:
            mod = re.sub(r"\bp?wolichu\b", "were awesome", lower)
            tokens = [cls.ENGLISH_SEMANTIC_LEXICON.get(w, w) for w in re.findall(r"[\w']+|[.,!?;:]", mod)]
            out = " ".join(tokens)
            out = re.sub(r"\s+([.,!?;:])", r"\1", out)
            return out[:1].upper() + out[1:]

        # Step 4: Full English Word-by-Word Mapping
        tokens = re.findall(r"[\w']+|[.,!?;:]", lower)
        english_tokens = [cls.ENGLISH_SEMANTIC_LEXICON.get(w, w) for w in tokens]
        reconstructed = " ".join(english_tokens)
        reconstructed = re.sub(r"\s+([.,!?;:])", r"\1", reconstructed)
        return reconstructed[:1].upper() + reconstructed[1:]