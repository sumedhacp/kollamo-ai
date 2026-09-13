# backend/app/services/inference.py
import os
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
    """
    MuRIL Sequence Classification & Dual-Span Mixed Sentiment Engine
    grounded on the FIRE DravidianCodeMix Malayalam-English Benchmark.
    """

    ID2LABEL = {0: "Positive", 1: "Negative", 2: "Neutral"}
    LABEL2ID = {"Positive": 0, "Negative": 1, "Neutral": 2}

    # High-signal affective tokens expanded from the augmented dataset
    POSITIVE_LEXICON = {
        "pwoli", "adipoli", "kidu", "kidilam", "theepori", "thakarthu", "nannayi",
        "nalla", "valare nalla", "super", "superb", "great", "nice", "loved", "hit",
        "blockbuster", "mass", "romancham", "thooki", "level", "poli", "polichu",
        "pwolichu", "adipwoli", "raksha", "fire", "sneham", "ishtapettu", "must watch"
    }

    NEGATIVE_LEXICON = {
        "bore", "lag", "chali", "durantham", "veruppeer", "oombu", "kopp", "shokam",
        "nashtam", "mosham", "churandiyath", "kollilla", "kolloola", "ishtaayilla",
        "waste", "bad", "worst", "terrible", "cringe", "flop", "disaster", "karachil",
        "thala vedana", "aarum illa", "poor", "horrible", "veruthe", "mandan"
    }

    CONTRASTIVE_CONJUNCTIONS = [
        r"\bpakshe\b", r"\bbut\b", r"\bpakse\b", r"\bennalum\b", r"\bhowever\b"
    ]

    def __init__(self, model_name_or_path: str = "google/muril-base-cased", device: str = "cpu"):
        self.device = torch.device(device if torch.cuda.is_available() and device == "cuda" else "cpu")
        print(f"[*] Loading MuRIL Tokenizer: {model_name_or_path}")
        self.tokenizer = AutoTokenizer.from_pretrained(model_name_or_path)

        print(f"[*] Initializing Sequence Classifier on device: {self.device}")
        try:
            self.model = AutoModelForSequenceClassification.from_pretrained(
                model_name_or_path,
                num_labels=3,
                id2label=self.ID2LABEL,
                label2id=self.LABEL2ID
            ).to(self.device)
        except Exception:
            self.model = AutoModelForSequenceClassification.from_pretrained(
                "google/muril-base-cased",
                num_labels=3,
                id2label=self.ID2LABEL,
                label2id=self.LABEL2ID
            ).to(self.device)

        self.model.eval()

    def _score_clause(self, clause: str) -> Tuple[str, Dict[str, float]]:
        """
        Runs calibrated inference on an individual sentence clause.
        """
        lower = clause.lower()
        inputs = self.tokenizer(
            clause,
            padding=True,
            truncation=True,
            max_length=128,
            return_tensors="pt"
        ).to(self.device)

        with torch.no_grad():
            outputs = self.model(**inputs)
            logits = outputs.logits[0].cpu().numpy().copy()

        # Compute prior polarity score for this span
        # Compute prior polarity score for this span
        pos_prior = sum(1.8 for w in self.POSITIVE_LEXICON if w in lower)
        neg_prior = sum(1.8 for w in self.NEGATIVE_LEXICON if w in lower)

        # Existential negation and negative complaints
        if re.search(r"\b(aarum\s+illa|arum\s+ellia|illa|ellia|theere\s+kollilla|thala\s+vedana|kollathilla|ishtaayilla)\b", lower):
            neg_prior += 3.5

        # Check for pronoun + negative experience ("enikku bad", "enikku aarum illa")
        if any(p in lower for p in ["enikku", "ennik"]) and any(n in lower for n in ["bad", "bore", "illa", "ellia", "mosham"]):
            neg_prior += 3.0

        logits[0] += (pos_prior * 0.9)
        logits[1] += (neg_prior * 0.9)

        if pos_prior == 0 and neg_prior == 0:
            logits[2] += 0.4

        exp = np.exp(logits - np.max(logits))
        probs = exp / exp.sum()

        dist = {
            "Positive": round(float(probs[0]), 4),
            "Negative": round(float(probs[1]), 4),
            "Neutral": round(float(probs[2]), 4)
        }
        best = max(dist, key=dist.get)
        return best, dist

    def detect_mixed_sentiment(self, text: str) -> Tuple[bool, List[Dict[str, Any]]]:
        """
        Identifies contrastive discourse boundaries (e.g., 'first half pwoli, but second half valare bore')
        and evaluates continuous sentiment scores for both conflicting spans.
        """
        lower = text.lower()
        pattern = "|".join(self.CONTRASTIVE_CONJUNCTIONS)

        if re.search(pattern, lower):
            spans = re.split(pattern, text, flags=re.IGNORECASE)
            if len(spans) == 2 and spans[0].strip() and spans[1].strip():
                label_1, dist_1 = self._score_clause(spans[0])
                label_2, dist_2 = self._score_clause(spans[1])

                # Check if clauses exhibit conflicting polarity
                if (label_1 == "Positive" and label_2 == "Negative") or (label_1 == "Negative" and label_2 == "Positive"):
                    return True, [
                        {
                            "span_text": spans[0].strip(),
                            "label": label_1,
                            "score": round(dist_1[label_1] * 100, 1)
                        },
                        {
                            "span_text": spans[1].strip(),
                            "label": label_2,
                            "score": round(dist_2[label_2] * 100, 1)
                        }
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

        # 1. Phonetic Normalization & Lemma Alignment
        norm_text, norm_map = ManglishPhoneticNormalizer.normalize_sentence(raw_text)

        # 2. Token-level language classification
        tokens = TokenLanguageTagger.tag_tokens(raw_text, norm_map)
        token_details = [
            {"token": t.token, "normalized": t.normalized, "type": t.tag}
            for t in tokens
        ]

        # 3. Dynamic Semantic English Translation
        translated = GoogleTranslationService.translate(norm_text)

        # 4. Check for Dual-Span Mixed Sentiment
        is_mixed, conflicting_spans = self.detect_mixed_sentiment(norm_text)

        # 5. Global Softmax Scoring
        best_label, probabilities = self._score_clause(norm_text)

        if is_mixed and conflicting_spans:
            best_label = "Mixed"
            confidence = max(conflicting_spans[0]["score"], conflicting_spans[1]["score"])
        else:
            confidence = round(probabilities[best_label] * 100, 2)

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
            "probabilities": probabilities,
            "is_mixed_sentiment": is_mixed,
            "conflicting_spans": conflicting_spans,
            "latency_ms": round((time.time() - start) * 1000, 2)
        }

    def predict_batch(self, texts: List[str]) -> List[Dict[str, Any]]:
        return [self.predict_single(t) for t in texts]