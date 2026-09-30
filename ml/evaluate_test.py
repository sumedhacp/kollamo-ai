# ml/evaluate_test.py
import os
import torch
import pandas as pd
import numpy as np
from transformers import AutoTokenizer, AutoModelForSequenceClassification
from sklearn.metrics import classification_report, confusion_matrix

MODEL_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "saved_model")
TEST_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data", "processed", "test.parquet")

LABEL2ID = {"Positive": 0, "Negative": 1, "Neutral": 2}
TARGET_NAMES = ["Positive", "Negative", "Neutral"]

print(f"[*] Loading model from: {MODEL_DIR}")
tokenizer = AutoTokenizer.from_pretrained(MODEL_DIR)
model = AutoModelForSequenceClassification.from_pretrained(MODEL_DIR)
model.eval()

print(f"[*] Reading held-out test split: {TEST_FILE}")
test_df = pd.read_parquet(TEST_FILE)

y_true = [LABEL2ID[label] for label in test_df["label"]]
y_pred = []

print(f"[*] Generating predictions for {len(test_df)} unseen test samples...")
with torch.no_grad():
    for text in test_df["text"]:
        inputs = tokenizer(text, return_tensors="pt", truncation=True, max_length=64)
        logits = model(**inputs).logits
        pred_idx = torch.argmax(logits, dim=-1).item()
        y_pred.append(pred_idx)

print("\n" + "=" * 60)
print("HELD-OUT TEST SET CLASSIFICATION REPORT")
print("=" * 60)
print(classification_report(y_true, y_pred, target_names=TARGET_NAMES, digits=4))

print("\nCONFUSION MATRIX:")
print(f"{'':>12} | Pred Pos | Pred Neg | Pred Neu |")
print("-" * 45)
cm = confusion_matrix(y_true, y_pred)
for idx, row in enumerate(cm):
    print(f"True {TARGET_NAMES[idx]:>7} | {row[0]:>8} | {row[1]:>8} | {row[2]:>8} |")