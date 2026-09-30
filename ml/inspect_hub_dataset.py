import os
from datasets import load_dataset

# Keep Hugging Face cache on D: drive
os.environ["HF_HOME"] = r"D:\Projects\kollamo-ai\.cache\huggingface"

# Paste your active token here
token = "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"

print("[*] Inspecting IsaacRodgz/DravidianCodeMix-Dataset...")
try:
    # Check dataset info/configs
    ds = load_dataset("IsaacRodgz/DravidianCodeMix-Dataset", token=token)
    print("[+] Successfully connected!")
    print("Available splits:", list(ds.keys()))
    sample_split = list(ds.keys())[0]
    print(f"Sample from '{sample_split}':")
    print(ds[sample_split][0])
except Exception as e:
    print("[!] Error loading dataset:", e)