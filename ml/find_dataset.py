import os
from huggingface_hub import HfApi

# Paste your new read token here or read from environment
token = os.environ.get("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", "")

api = HfApi(token=token if token else None)

print("[*] Searching Hugging Face Hub for Dravidian datasets...")
try:
    results = list(api.list_datasets(search="dravidian", limit=50))
    print(f"[+] Found {len(results)} matches for 'dravidian':")
    for r in results:
        rid = r.id.lower()
        if any(term in rid for term in ["malayalam", "codemix", "sentiment"]):
            print("  ->", r.id)
except Exception as e:
    print("[!] Error searching for dravidian:", e)

print("\n[*] Searching Hugging Face Hub for Malayalam sentiment datasets...")
try:
    mal_results = list(api.list_datasets(search="malayalam sentiment", limit=50))
    print(f"[+] Found {len(mal_results)} matches for 'malayalam sentiment':")
    for r in mal_results:
        print("  ->", r.id)
except Exception as e:
    print("[!] Error searching for malayalam sentiment:", e)