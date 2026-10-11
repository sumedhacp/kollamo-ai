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
    ID2LABEL = {0: "Positive", 1: "Negative", 2: "Neutral"}
    LABEL2ID = {"Positive": 0, "Negative": 1, "Neutral": 2}

    # Regional, phonetic, and dialectal affective lexicons across Kerala (Malabar, Central, South)
    POSITIVE_WORDS = {
        # Statewide / Universal Slang
        "pwoli", "poli", "adipoli", "kidu", "kidilan", "kiduve", "kidukki", "mass", "mas",
        "super", "superb", "great", "nice", "loved", "hit", "blockbuster", "fire", "theepori",
        "thee", "pori", "romancham", "thooki", "thakarthu", "polichu", "polichadukki",
        "level", "vera level", "veralevel", "marana mass", "maranamass", "mass entry",
        # Emotional & Evaluative
        "nalla", "nalonam", "nallonam", "nannayi", "kollaam", "kollam", "valare nallathu",
        "ishtam", "ishtamayi", "ishtapettu", "ishatayi", "fav", "favourite", "favorite",
        "must watch", "mustwatch", "rakshayilla", "oru rakshayum illa", "rekshayilla",
        # Regional / Local Slang (Malabar & South)
        "chanda", "chandam", "killadi", "vibe", "polappan", "kattakk", "anthas", "anthass",
        "alambilla", "bombastic", "bambal", "scene aahn", "scene aanu", "bhayangara scene"
    }

    NEGATIVE_WORDS = {
        # Statewide Negative & Pacing Critiques
        "bore", "boring", "lag", "full lag", "vallaatha lag", "waste", "waste of money",
        "waste of time", "chali", "chali padam", "durantham", "oro duranthangal",
        "mosham", "valare mosham", "koora", "koora padam", "cringe", "flop", "disaster",
        "churandiyath", "mandan", "mandatharam", "veruthe", "theere", "chavittu",
        "potta padam", "pottatharam", "pothichu", "tholi", "tholinju", "tholvi",
        # Rejection / Dislike Negations
        "kollilla", "kolila", "kolloola", "koloola", "ishtaayilla", "ishtailla", "ishtalla",
        "ishtamilla", "ishtamila", "ishtam ayila", "ishtayla", "venda", "thalkaalam venda",
        "veruppu", "verupikkal", "alambu", "alamb", "kazhappu", "scene contra", "scene dark",
        "oonja", "oanja", "oombiya", "oombiyath", "myru", "mayiru",
        # Loneliness, Absence & Grief (e.g., 'ennik arum ellia')
        "arum illa", "aarum illa", "arum ellia", "arum elia", "arum ila", "aarumilla",
        "arumilla", "arumelia", "aarkkum venda", "ottapettu", "sankadam", "vishamam",
        "karachil", "kannuner", "vedhana", "kashtam", "valare kashtam"
    }

    def __init__(self, model_name_or_path: str = None, device: str = "cpu"):
        if model_name_or_path is None:
            base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
            model_name_or_path = os.path.join(base_dir, "ml", "saved_model")

        self.device = torch.device(device if torch.cuda.is_available() and device == "cuda" else "cpu")
        print(f"[*] Loading Tokenizer & Fine-tuned Model from: {model_name_or_path}")
        self.tokenizer = AutoTokenizer.from_pretrained(model_name_or_path)
        print(f"[*] Initializing MuRIL Classifier on device: {self.device}")
        self.model = AutoModelForSequenceClassification.from_pretrained(
            model_name_or_path,
            num_labels=3,
            id2label=self.ID2LABEL,
            label2id=self.LABEL2ID
        ).to(self.device)
        self.model.eval()

    def _apply_lexical_bias(self, text: str, logits: np.ndarray) -> np.ndarray:
        """Applies calibrated polarity priors for well-known Manglish affective tokens."""
        lower = text.lower()
        pos_hits = sum(1 for w in self.POSITIVE_WORDS if re.search(rf"\b{re.escape(w)}\b", lower))
        neg_hits = sum(1 for w in self.NEGATIVE_WORDS if re.search(rf"\b{re.escape(w)}\b", lower))

        biased_logits = logits.copy()
        if neg_hits > pos_hits:
            # Boost negative logit (index 1), penalize positive (index 0)
            boost = 2.5 * (neg_hits - pos_hits)
            biased_logits[1] += boost
            biased_logits[0] -= boost
        elif pos_hits > neg_hits:
            # Boost positive logit (index 0), penalize negative (index 1)
            boost = 2.5 * (pos_hits - neg_hits)
            biased_logits[0] += boost
            biased_logits[1] -= boost

        return biased_logits

    def _score_clause(self, text: str) -> Tuple[str, Dict[str, float]]:
        inputs = self.tokenizer(
            text,
            padding=True,
            truncation=True,
            max_length=64,
            return_tensors="pt"
        ).to(self.device)

        with torch.no_grad():
            outputs = self.model(**inputs)
            raw_logits = outputs.logits[0].cpu().numpy()

        calibrated_logits = self._apply_lexical_bias(text, raw_logits)
        exp_logits = np.exp(calibrated_logits - np.max(calibrated_logits))
        probs = exp_logits / exp_logits.sum()

        dist = {
            self.ID2LABEL[i]: round(float(probs[i]), 4)
            for i in range(3)
        }
        best = max(dist, key=dist.get)
        return best, dist

    def detect_mixed(self, text: str) -> Tuple[bool, List[Dict[str, Any]]]:
        lower = text.lower()
        conjunction_match = re.search(r"\b(but|pakshe|pakse)\b", lower)
        if conjunction_match:
            spans = re.split(r"\b(?:but|pakshe|pakse)\b", text, flags=re.IGNORECASE)
            if len(spans) >= 2 and spans[0].strip() and spans[1].strip():
                s1, s2 = spans[0].strip(), spans[1].strip()
                l1, d1 = self._score_clause(s1)
                l2, d2 = self._score_clause(s2)
                # Mixed sentiment requires genuine polarity contradiction between clauses
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
            is_mixed = False
            spans = []
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