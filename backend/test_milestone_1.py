# backend/test_milestone_1.py
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.services.normalizer import (
    ManglishPhoneticNormalizer,
    TokenLanguageTagger,
    GoogleTranslationService
)

def run_verification():
    print("=" * 80)
    print("KOLLAMO.AI - MILESTONE 1 VERIFICATION SUITE")
    print("PHONETIC NORMALIZER, TOKEN TAGGER & GOOGLE TRANSLATION ENGINE")
    print("=" * 80)

    test_cases = [
        "padam kandu enikku thala vedana eduthu",
        "super padam visuals pwolichu",
        "theere kollilla valare bore aayirunnu",
        "ithu nalla cinema aanu must watch",
        "ennik arum ellia"
    ]
    for idx, raw in enumerate(test_cases, 1):
        print(f"\n[Case {idx}] Raw Input: '{raw}'")
        
        # 1. Phonetic Normalization
        norm_text, norm_map = ManglishPhoneticNormalizer.normalize_sentence(raw)
        print(f" -> Normalized: '{norm_text}'")
        if norm_map:
            print(f"    Syllable Transformations: {norm_map}")

        # 2. Token Language Tagging
        tagged = TokenLanguageTagger.tag_tokens(raw, norm_map)
        tag_str = " | ".join([f"{t.token} {t.tag}" for t in tagged])
        print(f" -> Token Tags: {tag_str}")

        # 3. Google Translation (Translating clean normalized text)
        translation = GoogleTranslationService.translate(norm_text)
        print(f" -> English Translation: \"{translation}\"")
        print("-" * 80)

    print("\n[SUCCESS] Milestone 1 verification suite completed.")

if __name__ == "__main__":
    run_verification()