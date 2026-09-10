import sys
import os

# Add backend directory to sys.path so imports work directly
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.core.config import settings
from app.services.scraper import SocialScraperService

def main():
    test_url = "https://www.youtube.com/watch?v=dQw4w9WgXcQ"
    print(f"[*] Testing scraper extraction for URL: {test_url}")
    
    try:
        video_id, comments = SocialScraperService.get_comments(
            url=test_url,
            api_key=settings.YOUTUBE_API_KEY,
            max_comments=5
        )
        print(f"[+] Successfully extracted Video ID: {video_id}")
        print(f"[+] Total comments extracted: {len(comments)}")
        print("\n--- Sample Extracted Comments ---")
        for idx, c in enumerate(comments, 1):
            print(f"{idx}. [{c.author}] ({c.like_count} likes): {c.text}")
        print("\n[SUCCESS] Milestone 2 Scraper Module is operational!")
    except Exception as e:
        print(f"[!] Scraper failed with error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
    