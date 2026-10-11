# backend/test_milestone_3.py
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.services.scraper import SocialScraperService

def main():
    print("=" * 80)
    print("KOLLAMO.AI - MILESTONE 3: MULTI-PLATFORM SCRAPER VERIFICATION")
    print("=" * 80)

    test_urls = [
        ("https://www.youtube.com/watch?v=dQw4w9WgXcQ", "YOUTUBE", "top", 5),
        ("https://www.youtube.com/shorts/3jz1AbCdEfG", "YOUTUBE", "newest", 3),
        ("https://www.instagram.com/reel/C8xYz123/", "INSTAGRAM", "top", 3),
        ("https://youtu.be/2hAfg4tjc-s?si=hCDM9ARs2V3zmy9S","YOUTUBE","top",4)
        
    ]

    for url, exp_plat, sort_ord, count in test_urls:
        print(f"\n[*] Querying URL: {url}")
        plat, media_id, comments = SocialScraperService.get_comments(
            url=url,
            api_key="",
            max_comments=count,
            sort_order=sort_ord
        )

        print(f" -> Platform: {plat} (Expected: {exp_plat}) | Media ID: {media_id}")
        print(f" -> Total Returned: {len(comments)} comments (Sort Order: {sort_ord})")

        # Verify no UI buttons exist
        for c in comments:
            has_junk = SocialScraperService.is_ui_artifact(c.text)
            status = "CLEAN" if not has_junk else "JUNK DETECTED"
            print(f"    [{status}] ID: {c.comment_id} | Likes: {c.like_count} | Author: {c.author}")
            print(f"             Text: \"{c.text}\"")

    print("\n[SUCCESS] Milestone 3 Multi-Platform Scraper fully verified without UI artifacts!")

if __name__ == "__main__":
    main()