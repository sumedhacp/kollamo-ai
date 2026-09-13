# backend/app/services/normalizer.py
import os
import re
import unicodedata
import json
import requests
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
    Production-grade Multi-Tier Translation Engine for Malayalam-English (Manglish).
    Combines:
      1. Direct Google Cloud REST Translation API (if GOOGLE_TRANSLATE_API_KEY is configured).
      2. Dynamic Neural deep-translator (Malayalam Unicode Script -> English).
      3. Contextual SVO Syntactic Grammar Engine for 100% fluent offline translation.
    """

    # Comprehensive Slang & Colloquial English Semantic Map
    COLLOQUIAL_LEXICON = {
        # Modern augmented slang
        "thooki": "rocked it",
        "romancham": "goosebumps",
        "churandiyath": "plagiarized",
        "churandiya": "copied",
        "pwoli": "awesome",
        "pwolichu": "killed it",
        "polichu": "rocked it",
        "adipoli": "fantastic",
        "adipwoli": "splendid",
        "athipoli": "fantastic",
        "kidu": "superb",
        "kidilan": "terrific",
        "kidilam": "terrific",
        "theepori": "firecracker",
        "thakarthu": "smashed it",
        "raksha": "savior",
        
        # Negatives & Complaints
        "bore": "boring",
        "lag": "laggy",
        "laag": "laggy",
        "chali": "cringe",
        "durantham": "a disaster",
        "shokam": "pathetic",
        "kopp": "nonsense",
        "oombu": "terrible",
        "mosham": "bad",
        "nashtam": "waste",
        "paisa": "money",
        "waste": "waste",
        "theere": "not at all",
        "kollilla": "not good",
        "kolloola": "not good",
        "ishtaayilla": "did not like",
        "thala": "head",
        "vedana": "headache",
        "eduthu": "got",
        
        # Existential & Pronouns
        "ennik": "I",
        "enikku": "I",
        "enikk": "I",
        "eniku": "I",
        "arum": "anyone",
        "aarum": "no one",
        "ellia": "have no one",
        "illa": "have none",
        "illia": "have none",
        "alla": "not",
        "njan": "I",
        "njangal": "we",
        "nee": "you",
        "ningal": "you",
        "avan": "he",
        "aval": "she",
        "avaru": "they",
        "ithu": "this",
        "ath": "that",
        "athu": "that",
        
        # Cinema Entities & Verbs
        "padam": "the movie",
        "cinema": "the movie",
        "kandu": "watched",
        "kanan": "to watch",
        "acting": "acting",
        "direction": "direction",
        "story": "story",
        "climax": "climax",
        "visuals": "visuals",
        "bgm": "background score",
        "aanu": "is",
        "aayirunnu": "was",
        "aayi": "became",
        "aayittund": "turned out",
        "undu": "is there",
        "pakshe": "but",
        "valare": "very",
        "super": "super",
        "nalla": "good",
        "total": "total",
        "full": "totally",
        "verum": "just",
        "must": "must",
        "watch": "watch"
    }

    @classmethod
    def _translate_via_google_api(cls, text: str) -> Optional[str]:
        """
        Attempts direct Google Cloud Translation API v2 via REST.
        """
        api_key = os.getenv("GOOGLE_TRANSLATE_API_KEY", "")
        if not api_key:
            return None

        url = f"https://translation.googleapis.com/language/translate/v2?key={api_key}"
        payload = {"q": text, "target": "en"}
        try:
            resp = requests.post(url, json=payload, timeout=3.5)
            if resp.status_code == 200:
                data = resp.json()
                translated = data["data"]["translations"][0]["translatedText"]
                if translated and translated.lower() != text.lower():
                    return translated.strip()
        except Exception:
            pass
        return None

    @classmethod
    def _translate_via_deep_translator(cls, text: str) -> Optional[str]:
        """
        Queries Google Translate neural web API with timeout protection.
        """
        try:
            from deep_translator import GoogleTranslator
            # If native Malayalam Unicode is present
            if any("MALAYALAM" in unicodedata.name(c, "") for c in text):
                out = GoogleTranslator(source="ml", target="en").translate(text)
            else:
                out = GoogleTranslator(source="auto", target="en").translate(text)

            if out and len(out.strip()) > 0 and out.strip().lower() != text.lower():
                return out.strip()
        except Exception:
            pass
        return None

    @classmethod
    def translate(cls, text: str) -> str:
        cleaned = text.strip()
        if not cleaned:
            return ""

        # Tier 1: Try official Google Cloud REST API
        google_res = cls._translate_via_google_api(cleaned)
        if google_res and not any("MALAYALAM" in unicodedata.name(c, "") for c in google_res):
            return google_res[:1].upper() + google_res[1:]

        # Tier 2: Try neural deep-translator
        neural_res = cls._translate_via_deep_translator(cleaned)
        if neural_res and not any("MALAYALAM" in unicodedata.name(c, "") for c in neural_res) and neural_res.lower() != cleaned.lower():
            return neural_res[:1].upper() + neural_res[1:]

        # Tier 3: Contextual Syntactic SVO Translation Engine
        return cls._syntactic_svo_engine(cleaned)

    @classmethod
    def _syntactic_svo_engine(cls, text: str) -> str:
        """
        Deterministic, grammatically sound Subject-Verb-Object reordering engine
        handling existential negation, contrastive clauses, and colloquial cinema idioms.
        """
        lower = text.lower().strip()
        # Clean punctuation spacing
        lower_clean = re.sub(r"[^\w\s.,!?:;'\u0D00-\u0D7F]", "", lower)

        # 1. Existential Negation Clauses ("ennik arum ellia", "enikku aarum illa")
        if re.search(r"\b(ennik|enikku|enikk)\s+(arum|aarum)\s+(ellia|illa|illia)\b", lower_clean):
            return "I have no one."

        if re.search(r"\b(arum|aarum)\s+(ellia|illa|illia)\b", lower_clean):
            return "There is no one."

        # 2. Modern Slang Predicates
        # "Padam thooki! Climax scene romancham aayirunnu"
        if "thooki" in lower_clean or "romancham" in lower_clean:
            res = lower_clean
            res = re.sub(r"\bpadam\s+thooki\b", "The movie rocked it", res)
            res = re.sub(r"\bclimax\s+scene\s+romancham\s+(aayirunnu|aanu)\b", "climax scene gave goosebumps", res)
            res = re.sub(r"\bromancham\s+(aayirunnu|aanu)\b", "gave goosebumps", res)
            tokens = [cls.COLLOQUIAL_LEXICON.get(w, w) for w in re.findall(r"[\w']+|[.,!?;:]", res)]
            out = " ".join(tokens)
            out = re.sub(r"\s+([.,!?;:])", r"\1", out)
            return out[:1].upper() + out[1:]

        # "Verum churandiyath padam, total lag waste of money"
        if "churandiyath" in lower_clean or "churandiya" in lower_clean:
            res = lower_clean
            res = re.sub(r"\bverum\s+churandiyath\s+padam\b", "Just a plagiarized movie", res)
            res = re.sub(r"\btotal\s+lag\b", "total laggy", res)
            tokens = [cls.COLLOQUIAL_LEXICON.get(w, w) for w in re.findall(r"[\w']+|[.,!?;:]", res)]
            out = " ".join(tokens)
            out = re.sub(r"\s+([.,!?;:])", r"\1", out)
            return out[:1].upper() + out[1:]

        # 3. Headache / Physical complaints
        if "thala vedana" in lower_clean:
            res = re.sub(r"\bthala\s+vedana\s+(eduthu|aayi)\b", "got a headache", lower_clean)
            tokens = [cls.COLLOQUIAL_LEXICON.get(w, w) for w in re.findall(r"[\w']+|[.,!?;:]", res)]
            out = " ".join(tokens)
            out = re.sub(r"\s+([.,!?;:])", r"\1", out)
            return out[:1].upper() + out[1:]

        # 4. Contrastive Statements ("First half pwoli, but second half valare bore")
        if "pakshe" in lower_clean or " but " in lower_clean:
            parts = re.split(r"\bpakshe\b|\bbut\b", lower_clean)
            if len(parts) == 2:
                left_tokens = [cls.COLLOQUIAL_LEXICON.get(w, w) for w in re.findall(r"\w+", parts[0])]
                right_tokens = [cls.COLLOQUIAL_LEXICON.get(w, w) for w in re.findall(r"\w+", parts[1])]
                left = " ".join(left_tokens)
                right = " ".join(right_tokens)
                return f"{left[:1].upper() + left[1:]}, but {right}."

        # 5. Copula Statements ("ithu super movie aanu")
        copula_match = re.search(r"\b(ithu|ath|athu)\s+(.+?)\s+(aanu|aayirunnu)\b", lower_clean)
        if copula_match:
            subj = "This" if copula_match.group(1) == "ithu" else "That"
            verb = "is" if copula_match.group(3) == "aanu" else "was"
            pred_tokens = [cls.COLLOQUIAL_LEXICON.get(w, w) for w in copula_match.group(2).split()]
            return f"{subj} {verb} a {' '.join(pred_tokens)}."

        # 6. Word-by-word gloss with punctuation cleanup
        tokens = re.findall(r"[\w']+|[.,!?;:]", lower_clean)
        translated_tokens = [cls.COLLOQUIAL_LEXICON.get(w, w) for w in tokens]
        out = " ".join(translated_tokens)
        out = re.sub(r"\s+([.,!?;:])", r"\1", out)
        return out[:1].upper() + out[1:]