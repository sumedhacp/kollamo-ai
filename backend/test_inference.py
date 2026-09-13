import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.services.inference import SentimentInferenceEngine

def main():
    print("=" * 70)
    print("KOLLAMO.AI - CALIBRATED MURIL INFERENCE TEST")
    print("=" * 70)

    engine = SentimentInferenceEngine(model_name_or_path="google/muril-base-cased", device="cpu")

    test_corpus = [
        ("ithu super movie aanu", "Positive"),
        ("Padam adipoli aayittund! Acting super visuals pwolichu 🔥🔥", "Positive"),
        ("Valare bore aayi poyi, second half full lag waste of money 💩", "Negative"),
        ("Padam kandu, waste of time", "Negative"),
        ("Padam kollam ennu vicharichu, pakshe climax bore aayi", "Negative"),
        ("Ee movie release date eppozhaanu OTT release?", "Neutral")
    ]

    print("\nExecuting predictions across representative Manglish sentences...\n")
    all_passed = True
    for text, expected in test_corpus:
        res = engine.predict_single(text)
        is_match = res["label"] == expected
        status = "PASSED" if is_match else "FAILED"
        if not is_match:
            all_passed = False
        print(f"[{status}] Expected: {expected:<8} | Got: {res['label']:<8} ({res['confidence']}%)")
        print(f"  Input:   '{res['raw_text']}'")
        print(f"  Cleaned: '{res['cleaned_text']}'")
        print(f"  Dist:    {res['probabilities']} | Latency: {res['latency_ms']}ms")
        print("-" * 70)

    if all_passed:
        print("\n[SUCCESS] All Manglish calibration benchmarks passed with high accuracy!")
    else:
        print("\n[WARNING] Some sentences deviated from expected targets.")

if __name__ == "__main__":
    main()