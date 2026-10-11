# backend/test_milestone_4.py
import sys
import os
from fastapi.testclient import TestClient

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.main import app

client = TestClient(app)

def run_tests():
    print("=" * 80)
    print("KOLLAMO.AI - MILESTONE 4: FASTAPI ENDPOINTS & SUMMARY GENERATOR VERIFICATION")
    print("=" * 80)

    # 1. Health Check
    res = client.get("/health")
    assert res.status_code == 200, f"Health check failed: {res.text}"
    print(f"[TEST 1] GET /health -> Status 200 OK | Response: {res.json()['system']}")

    # 2. Single Analysis Route
    single_payload = {"text": "Padam thooki! Climax scene romancham aayirunnu 🔥🔥"}
    res = client.post("/api/analyze-single", json=single_payload)
    assert res.status_code == 200, f"Analyze-single failed: {res.text}"
    data = res.json()
    print(f"\n[TEST 2] POST /api/analyze-single -> Status 200 OK")
    print(f" -> Label: {data['label']} ({data['confidence']}%)")
    print(f" -> English: \"{data['translated_text']}\"")
    print(f" -> Probs: {data['probabilities']}")

    # 3. Social Scraper Route
    scrape_payload = {
        "url": "https://www.youtube.com/watch?v=2hAfg4tjc-s",
        "max_comments": 4,
        "sort_order": "top"
    }
    res = client.post("/api/scrape-comments", json=scrape_payload)
    assert res.status_code == 200, f"Scrape-comments failed: {res.text}"
    scrape_data = res.json()
    print(f"\n[TEST 3] POST /api/scrape-comments -> Status 200 OK")
    print(f" -> Platform: {scrape_data['platform']} | Media ID: {scrape_data['media_id']}")
    print(f" -> Extracted: {scrape_data['total_extracted']} comments")

    # 4. Batch Analysis Route
    batch_payload = {
        "comments": [
            {"comment_id": "c1", "text": "Padam adipoli aayittund! Visuals super", "author": "@user1", "like_count": 50},
            {"comment_id": "c2", "text": "Valare bore aayi poyi, full lag waste of money", "author": "@user2", "like_count": 12},
            {"comment_id": "c3", "text": "First half pwoli, but second half valare bore", "author": "@user3", "like_count": 8},
            {"comment_id": "c4", "text": "यह फिल्म बहुत अच्छी है", "author": "@user4", "like_count": 2}
        ]
    }
    res = client.post("/api/analyze-batch", json=batch_payload)
    assert res.status_code == 200, f"Analyze-batch failed: {res.text}"
    batch_data = res.json()
    print(f"\n[TEST 4] POST /api/analyze-batch -> Status 200 OK")
    print(f" -> Total Analyzed: {batch_data['total_analyzed']} (Supported: {batch_data['supported_count']}, Unsupported: {batch_data['unsupported_count']})")
    print(f" -> Distribution: {batch_data['sentiment_distribution']}")
    print(f" -> Net Sentiment Score (NSS): {batch_data['net_sentiment_score']}")

    # 5. Executive Review Summary Generation
    res = client.post("/api/generate-summary", json=batch_data["comments"])
    assert res.status_code == 200, f"Generate-summary failed: {res.text}"
    summary = res.json()
    print(f"\n[TEST 5] POST /api/generate-summary -> Status 200 OK")
    print(f" -> Headline: {summary['headline']}")
    print(f" -> Narrative: \"{summary['narrative']}\"")
    print(f" -> Net Sentiment Score: {summary['net_sentiment_score']}")

    print("\n" + "=" * 80)
    print("[SUCCESS] Milestone 4 FastAPI Endpoints & Summary Generation fully operational!")
    print("=" * 80)

if __name__ == "__main__":
    run_tests()