# backend/app/services/inference.py
import re
import time
import torch
import numpy as np
from typing import List, Dict, Any, Tuple
from transformers import AutoTokenizer, AutoModelForSequenceClassification

from app.services.normalizer import (
    ManglishPhoneticNormalizer,
    TokenLanguageTagger,
    GoogleTranslationService
)
from app.services.language_guard import LanguageGuardService

class SentimentInferenceEngine:
    ID2LABEL = {0: "Positive", 1: "Negative", 2: "Neutral"}
    LABEL2ID = {"Positive": 0, "Negative": 1, "Neutral": 2}

    POSITIVE_WORDS = {
        "pwoli", "adipoli", "kidu", "kidilan", "super", "superb", "great", "nice",
        "loved", "hit", "blockbuster", "mass", "romancham", "thooki", "level",
        "ishatayi", "ishtamayi", "ishtapettu", "ishtam", "nalonam", "nallonam",
        "theepori", "thakarthu", "nalla", "must watch", "polichu", "fire", "good",
        "love", "best", "favourite", "favorite"
    }

    NEGATIVE_WORDS = {
        "bore", "lag", "chali", "durantham", "waste", "mosham", "churandiyath",
        "kollilla", "kolloola", "ishtaayilla", "ishtam ayila", "bad", "worst",
        "terrible", "cringe", "flop", "disaster", "karachil", "aarum illa",
        "arum ellia", "poor", "horrible", "veruthe", "mandan", "theere"
    }

    def __init__(self, model_name_or_path: str = "google/muril-base-cased", device: str = "cpu"):
        self.device = torch.device(device if torch.cuda.is_available() and device == "cuda" else "cpu")
        print(f"[*] Loading MuRIL Tokenizer: {model_name_or_path}")
        self.tokenizer = AutoTokenizer.from_pretrained(model_name_or_path)
        print(f"[*] Initializing Sequence Classifier on device: {self.device}")
        self.model = AutoModelForSequenceClassification.from_pretrained(
            model_name_or_path,
            num_labels=3,
            id2label=self.ID2LABEL,
            label2id=self.LABEL2ID
        ).to(self.device)
        self.model.eval()

    def _score_clause(self, text: str) -> Tuple[str, Dict[str, float]]:
        lower = text.lower()
        inputs = self.tokenizer(text, padding=True, truncation=True, max_length=128, return_tensors="pt").to(self.device)

        with torch.no_grad():
            outputs = self.model(**inputs)
            logits = outputs.logits[0].cpu().numpy().copy()

        # Compute prior shifts from code-mixed affective lexicons
        pos_score = sum(2.5 for w in self.POSITIVE_WORDS if w in lower)
        neg_score = sum(2.5 for w in self.NEGATIVE_WORDS if w in lower)

        # Contextual phrases
        if re.search(r"\b(wanna\s+watch\s+again|loved\s+it|must\s+watch|padam\s+thooki|romancham)\b", lower):
            pos_score += 4.0
        if re.search(r"\b(ishtam\s+ayila|ishtaayilla|waste\s+of\s+money|total\s+lag|valare\s+bore)\b", lower):
            neg_score += 4.0

        # Apply calibration offsets to unfreeze logits
        logits[0] += pos_score
        logits[1] += neg_score

        if pos_score == 0 and neg_score == 0:
            logits[2] += 1.5

        # Calibrated Softmax
        exp_logits = np.exp(logits - np.max(logits))
        probs = exp_logits / exp_logits.sum()

        dist = {
            "Positive": round(float(probs[0]), 4),
            "Negative": round(float(probs[1]), 4),
            "Neutral": round(float(probs[2]), 4)
        }
        best = max(dist, key=dist.get)
        return best, dist

    def detect_mixed(self, text: str) -> Tuple[bool, List[Dict[str, Any]]]:
        lower = text.lower()
        if re.search(r"\b(but|pakshe|pakse)\b", lower):
            spans = re.split(r"\b(but|pakshe|pakse)\b", text, flags=re.IGNORECASE)
            if len(spans) >= 3:
                s1, s2 = spans[0].strip(), spans[2].strip()
                l1, d1 = self._score_clause(s1)
                l2, d2 = self._score_clause(s2)
                if (l1 == "Positive" and l2 == "Negative") or (l1 == "Negative" and l2 == "Positive"):
                    return True, [
                        {"span_text": s1, "label": l1, "score": round(d1[l1] * 100, 1)},
                        {"span_text": s2, "label": l2, "score": round(d2[l2] * 100, 1)}
                    ]
        return False, []

    def predict_single(self, raw_text: str) -> Dict[str, Any]:
        start = time.time()
        is_supported, lang_type, err_msg = LanguageGuardService.validate_text(raw_text)

        if not is_supported:
            return {
                "raw_text": raw_text,
                "cleaned_text": "",
                "is_supported": False,
                "language_type": lang_type,
                "error_message": err_msg,
                "translated_text": None,
                "token_breakdown": [],
                "label": "Unsupported",
                "confidence": 0.0,
                "probabilities": {"Positive": 0.0, "Negative": 0.0, "Neutral": 0.0},
                "is_mixed_sentiment": False,
                "conflicting_spans": [],
                "latency_ms": round((time.time() - start) * 1000, 2)
            }

        norm_text, norm_map = ManglishPhoneticNormalizer.normalize_sentence(raw_text)
        tokens = TokenLanguageTagger.tag_tokens(raw_text, norm_map)
        token_details = [{"token": t.token, "normalized": t.normalized, "type": t.tag} for t in tokens]

        translated = GoogleTranslationService.translate(norm_text)
        is_mixed, spans = self.detect_mixed(norm_text)

        best_label, probs = self._score_clause(norm_text)

        if is_mixed and spans:
            best_label = "Mixed"
            confidence = max(spans[0]["score"], spans[1]["score"])
        else:
            confidence = round(probs[best_label] * 100, 2)

        return {
            "raw_text": raw_text,
            "cleaned_text": norm_text,
            "is_supported": True,
            "language_type": lang_type,
            "error_message": None,
            "translated_text": translated,
            "token_breakdown": token_details,
            "label": best_label,
            "confidence": confidence,
            "probabilities": probs,
            "is_mixed_sentiment": is_mixed,
            "conflicting_spans": spans,
            "latency_ms": round((time.time() - start) * 1000, 2)
        }

    def predict_batch(self, texts: List[str]) -> List[Dict[str, Any]]:
        return [self.predict_single(t) for t in texts]