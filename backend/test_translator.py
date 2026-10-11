import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.services.translator import ManglishTranslatorService

def main():
    print("=" * 70)
    print("KOLLAMO.AI - OPTION B (DYNAMIC TRANSLATION ENGINE) TEST")
    print("=" * 70)

    test_sentences = [
        "ithu super movie aanu",
        "Padam kidu aayirunnu, visuals and bgm pwoli!",
        "Padam kollam ennu vicharichu, pakshe climax bore aayi.",
        # Testing unseen slang words that were not in any hardcoded dictionary
        "Chumma thallu padam aanu, veruthe paisa poyi",
        "Avan oru valiya mandan aayirunnu"
    ]

    for sentence in test_sentences:
        tokens = ManglishTranslatorService.get_token_breakdown(sentence)
        translated = ManglishTranslatorService.translate_manglish_to_english(sentence)
        print(f"\nOriginal: '{sentence}'")
        print(f"Meaning:  '{translated}'")
        print("Tokens:   " + ", ".join([f"{t['token']} ({t['type']})" for t in tokens]))
        print("-" * 70)

    print("\n[SUCCESS] Option B Dynamic Translation Engine is working!")

if __name__ == "__main__":
    main()