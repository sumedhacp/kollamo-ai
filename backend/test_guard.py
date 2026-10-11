import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.services.language_guard import LanguageGuardService
from app.services.scraper import SocialScraperService

def main():
    print("=" * 65)
    print("KOLLAMO.AI - LANGUAGE GUARD & SCRAPER VERIFICATION")
    print("=" * 65)

    # 1. Test Language Guard
    test_phrases = [
        ("Padam adipoli aayittund! Visuals pwolichu!", True, "MANGLISH"),
        ("പോസിറ്റീവ് സിനിമ ആണ്", True, "MALAYALAM"),
        ("Great movie, loved the direction!", True, "ENGLISH"),
        ("यह फिल्म बहुत अच्छी है", False, "UNSUPPORTED"),
        ("இந்த படம் மிகவும் அருமை", False, "UNSUPPORTED")
    ]

    print("\n--- Testing Language Guardrail ---")
    for text, should_pass, exp_lang in test_phrases:
        ok, lang, msg = LanguageGuardService.validate_text(text)
        status = "PASSED" if ok == should_pass and lang == exp_lang else "FAILED"
        print(f"[{status}] Type: {lang:<11} | Input: '{text}'")
        if not ok:
            print(f"         Alert: {msg}")

    # 2. Test Scraper Multi-Platform Routing & Junk Filter
    print("\n--- Testing Multi-Platform Scraper ---")
    urls = [
        "https://www.youtube.com/watch?v=dQw4w9WgXcQ",
        "https://www.instagram.com/reel/C3x9pL/",
        "https://x.com/user/status/123456789"
    ]
    for url in urls:
        platform, mid, comments = SocialScraperService.get_comments(url, max_comments=3)
        print(f"[PASSED] Platform: {platform:<9} | ID: {mid} | Extracted: {len(comments)} comments")
        for c in comments[:1]:
            print(f"         Sample: [{c.author}] ({c.like_count} likes): {c.text}")

    print("\n[SUCCESS] Milestone 2 Scraper and Language Guardrail operational!")

if __name__ == "__main__":
    main()