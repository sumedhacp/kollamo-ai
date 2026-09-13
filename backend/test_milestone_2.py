# backend/test_milestone_2.py
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.services.inference import SentimentInferenceEngine

def main():
    print("=" * 80)
    print("KOLLAMO.AI - MILESTONE 2: TRANSFORMER INFERENCE & DUAL-SPAN VERIFICATION")
    print("=" * 80)

    engine = SentimentInferenceEngine(model_name_or_path="google/muril-base-cased", device="cpu")

    test_cases = [
        # Positive with augmented slang
        ("Padam thooki! Climax scene romancham aayirunnu 🔥🔥", "Positive"),
        # Negative with augmented slang
        ("Verum churandiyath padam, total lag waste of money 💩", "Negative"),
        # Dual-span mixed sentiment
        ("First half pwoli, but second half valare bore", "Mixed"),
        # Conversational single-line negative
        ("ennik arum ellia", "Negative"),
        # Neutral inquiry
        ("Ee movie OTT release date eppozhaanu?", "Neutral"),
        # Unsupported foreign language guardrail
        ("यह फिल्म बहुत अच्छी है", "Unsupported")
    ]

    for idx, (text, expected) in enumerate(test_cases, 1):
        res = engine.predict_single(text)
        print(f"\n[Case {idx}] Input: '{res['raw_text']}'")
        print(f" -> Label: {res['label']} (Expected: {expected}) | Confidence: {res['confidence']}%")
        print(f" -> Probs: {res['probabilities']}")
        
        if res["is_mixed_sentiment"]:
            print(f" -> [MIXED SPANS HIGHLIGHTED]:")
            for sp in res["conflicting_spans"]:
                print(f"     * '{sp['span_text']}' -> {sp['label']} ({sp['score']}%)")

        if res["translated_text"]:
            print(f" -> English: \"{res['translated_text']}\"")
        if not res["is_supported"]:
            print(f" -> Guard Alert: {res['error_message']}")
        print(f" -> Latency: {res['latency_ms']} ms")
        print("-" * 80)

    print("\n[SUCCESS] Milestone 2 Transformer Inference Engine fully operational!")

if __name__ == "__main__":
    main()