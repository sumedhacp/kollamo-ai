# ml/test_inference.py
import os
import torch
import torch.nn.functional as F
from transformers import AutoTokenizer, AutoModelForSequenceClassification

MODEL_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "saved_model")

print(f"[*] Loading fine-tuned Kollamo.ai model from:\n    {MODEL_DIR}")
tokenizer = AutoTokenizer.from_pretrained(MODEL_DIR)
model = AutoModelForSequenceClassification.from_pretrained(MODEL_DIR)
model.eval()

# Test cases: Pure Malayalam script, code-mixed Manglish positive, negative, and neutral
test_phrases = [
    "Padam super aayirunnu, kidu acting and direction!",           # Manglish Positive
    "Kollilla, waste of money and time. Valare mosham cinema.",     # Manglish Negative
    "Trailer kandu, let's see how the movie turns out.",           # Manglish Neutral
    "ഇത് വളരെ മികച്ച ഒരു ചിത്രമാണ്, എല്ലാവരും കാണണം",               # Malayalam Script Positive
    "വളരെ മോശം അനുഭവം, വെറുതെ സമയം കളഞ്ഞു",                         # Malayalam Script Negative
    "Ettan fans ivide like adikkuka"                               # YouTube neutral/social
]

print("\n" + "=" * 70)
print(f"{'Comment':<45} | {'Prediction':<10} | {'Confidence':<10}")
print("=" * 70)

with torch.no_grad():
    for text in test_phrases:
        inputs = tokenizer(text, return_tensors="pt", truncation=True, max_length=64)
        outputs = model(**inputs)
        probs = F.softmax(outputs.logits, dim=-1)[0]
        
        pred_idx = torch.argmax(probs).item()
        pred_label = model.config.id2label[pred_idx]
        confidence = probs[pred_idx].item()
        
        display_text = text if len(text) <= 42 else text[:39] + "..."
        print(f"{display_text:<45} | {pred_label:<10} | {confidence:>8.2%}")

print("=" * 70)