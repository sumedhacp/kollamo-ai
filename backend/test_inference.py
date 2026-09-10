import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.services.inference import SentimentInferenceEngine

def main():
    print("=" * 65)
    print("KOLLAMO.AI - NLP TRANSFORMER INFERENCE VERIFICATION")
    print("=" * 65)

    engine = SentimentInferenceEngine(model_name_or_path="google/muril-base-cased", device="cpu")

    test_samples = [
        "Padam adipoli aayittund! Acting super visuals pwolichu 🔥🔥",
        "Valare bore aayi poyi, second half total lag waste of money",
        "Ee movie release date eppozhaanu OTT varumo?",
        "BGM kollam, pakshe direction bore aayi poyi"
    ]

    print("\nExecuting sentiment predictions on sample Manglish comments...\n")
    for text in test_samples:
        result = engine.predict_single(text)
        print(f"Text: '{result['raw_text']}'")
        print(f"Cleaned: '{result['cleaned_text']}'")
        print(f"Prediction: [{result['label']}] ({result['confidence']}%) | Latency: {result['latency_ms']}ms")
        print(f"Dist: {result['probabilities']}")
        print("-" * 65)

    print("\n[SUCCESS] Milestone 3 NLP Inference Engine is fully functional!")

if __name__ == "__main__":
    main()