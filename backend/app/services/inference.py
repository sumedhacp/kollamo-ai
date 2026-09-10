import re
import time
import torch
import torch.nn.functional as F
from typing import List, Dict, Any
from transformers import AutoTokenizer, AutoModelForSequenceClassification
from app.services.preprocessor import ManglishPreprocessor

class SentimentInferenceEngine:
    LABELS = ["Positive", "Negative", "Neutral"]

    # High-signal colloquial Manglish lexicon for calibrating zero-shot representations
    POSITIVE_SLANG = {
        "adipoli", "adipwoli", "pwoli", "polichu", "pwolichu", "kollam", "kidilam", 
        "kidu", "super", "polii", "poli", "level", "blockbuster", "heavy", 
        "mass", "theepori", "raksha", "thakarthu", "fire", "love", "ishtapettu"
    }
    
    NEGATIVE_SLANG = {
        "bore", "kopp", "koothara", "oombu", "lag", "durantham", "veruppeer", 
        "chali", "nashtam", "waste", "disaster", "mosham", "shokam", "karachil", 
        "kuduthal", "kandilla", "thripthikaramalla", "valare bore", "pakshe bore"
    }

    def __init__(self, model_name_or_path: str = "google/muril-base-cased", device: str = "cpu"):
        self.device = torch.device(device if torch.cuda.is_available() and device == "cuda" else "cpu")
        print(f"[*] Initializing MuRIL sentiment tokenizer from: {model_name_or_path}")
        self.tokenizer = AutoTokenizer.from_pretrained(model_name_or_path)
        
        print(f"[*] Loading model weights on device: {self.device}")
        try:
            self.model = AutoModelForSequenceClassification.from_pretrained(
                model_name_or_path, 
                num_labels=3
            ).to(self.device)
        except Exception:
            self.model = AutoModelForSequenceClassification.from_pretrained(
                "google/muril-base-cased", 
                num_labels=3
            ).to(self.device)
            
        self.model.eval()
        self.preprocessor = ManglishPreprocessor()

    def _lexicon_prior(self, cleaned_text: str) -> Dict[str, float]:
        """
        Calculates lexical priors based on regional Manglish morphemes and sentiment tokens.
        """
        lower = cleaned_text.lower()
        pos_hits = sum(1 for token in self.POSITIVE_SLANG if token in lower)
        neg_hits = sum(1 for token in self.NEGATIVE_SLANG if token in lower)

        # Contrastive conjunction handling ('pakshe' / 'but')
        if "pakshe" in lower or " but " in lower:
            parts = re.split(r"\bpakshe\b|\bbut\b", lower)
            if len(parts) > 1:
                after_conjunction = parts[1]
                if any(w in after_conjunction for w in self.NEGATIVE_SLANG):
                    neg_hits += 2
                elif any(w in after_conjunction for w in self.POSITIVE_SLANG):
                    pos_hits += 2

        # Check positive/negative emojis
        if ":fire:" in lower or ":heart:" in lower or ":thumbs_up:" in lower or ":smiling_face:" in lower:
            pos_hits += 2
        if ":disappointed_face:" in lower or ":poop:" in lower or ":thumbs_down:" in lower:
            neg_hits += 2

        return {"pos": pos_hits, "neg": neg_hits}

    def predict_single(self, raw_text: str) -> Dict[str, Any]:
        """
        Infers sentiment label and distribution for a single string.
        """
        start_time = time.time()
        cleaned = self.preprocessor.clean_text(raw_text)
        
        if not cleaned.strip():
            return {
                "raw_text": raw_text,
                "cleaned_text": "",
                "label": "Neutral",
                "confidence": 50.0,
                "probabilities": {"Positive": 0.25, "Negative": 0.25, "Neutral": 0.50},
                "latency_ms": round((time.time() - start_time) * 1000, 2)
            }

        inputs = self.tokenizer(
            cleaned,
            padding=True,
            truncation=True,
            max_length=128,
            return_tensors="pt"
        ).to(self.device)

        with torch.no_grad():
            outputs = self.model(**inputs)
            logits = outputs.logits[0]
            probs = F.softmax(logits, dim=-1).cpu().numpy()

        # Hybrid calibration using regional code-mixed morphemes
        prior = self._lexicon_prior(cleaned)
        pos_boost = prior["pos"] * 0.25
        neg_boost = prior["neg"] * 0.25

        adj_pos = max(0.01, float(probs[0]) + pos_boost)
        adj_neg = max(0.01, float(probs[1]) + neg_boost)
        adj_neu = max(0.01, float(probs[2]) if len(probs) > 2 else 0.2)

        # Normalize into proper probability distribution
        total = adj_pos + adj_neg + adj_neu
        norm_pos = adj_pos / total
        norm_neg = adj_neg / total
        norm_neu = adj_neu / total

        prob_dict = {
            "Positive": round(norm_pos, 4),
            "Negative": round(norm_neg, 4),
            "Neutral": round(norm_neu, 4)
        }

        best_label = max(prob_dict, key=prob_dict.get)
        confidence = round(prob_dict[best_label] * 100, 2)
        latency = round((time.time() - start_time) * 1000, 2)

        return {
            "raw_text": raw_text,
            "cleaned_text": cleaned,
            "label": best_label,
            "confidence": confidence,
            "probabilities": prob_dict,
            "latency_ms": latency
        }

    def predict_batch(self, texts: List[str]) -> List[Dict[str, Any]]:
        """
        Performs batch inference on a list of comment strings.
        """
        return [self.predict_single(t) for t in texts]