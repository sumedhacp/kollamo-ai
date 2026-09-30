# ml/download_dataset.py
import os
import glob
import pandas as pd
from sklearn.model_selection import train_test_split

# Label standard mapping for 3-class sentiment model:
# 0: Positive, 1: Negative, 2: Neutral
LABEL_MAP = {
    "positive": "Positive",
    "negative": "Negative",
    "neutral": "Neutral",
    "unknown_state": "Neutral",
    "mixed_feelings": "Neutral"  # Merged into Neutral for 3-class base training
}

def process_tsv():
    base_dir = os.path.dirname(os.path.abspath(__file__))
    dataset_dir = os.path.join(base_dir, "dataset")
    target_csv = os.path.join(dataset_dir, "dravidian_manglish_sentiment.csv")

    tsv_files = glob.glob(os.path.join(dataset_dir, "*sentiment*.tsv"))
    if not tsv_files:
        tsv_files = glob.glob(os.path.join(dataset_dir, "*.tsv"))

    if not tsv_files:
        print("[!] No TSV file found in ml/dataset/")
        return

    filepath = tsv_files[0]
    print(f"[*] Ingesting: {os.path.basename(filepath)}")

    records = []
    skipped_not_ml = 0

    with open(filepath, "r", encoding="utf-8", errors="replace") as f:
        for line in f:
            parts = line.strip().split("\t", 1)
            if len(parts) == 2:
                raw_label = parts[0].strip().lower()
                text = parts[1].strip()

                if raw_label == "not-malayalam":
                    skipped_not_ml += 1
                    continue

                if raw_label in LABEL_MAP and len(text) > 1:
                    records.append({
                        "text": text,
                        "label": LABEL_MAP[raw_label]
                    })

    df = pd.DataFrame(records)
    print(f"[+] Extracted {len(df)} sentiment records (Filtered out {skipped_not_ml} 'not-malayalam' rows).")

    # Drop duplicate text rows
    df = df.drop_duplicates(subset=["text"]).reset_index(drop=True)
    print(f"[+] Unique comments after deduplication: {len(df)}")
    print("\nClass Distribution:")
    print(df["label"].value_counts())

    # Stratified Train (80%), Validation (10%), Test (10%)
    train_df, temp_df = train_test_split(
        df,
        test_size=0.2,
        random_state=42,
        stratify=df["label"]
    )
    val_df, test_df = train_test_split(
        temp_df,
        test_size=0.5,
        random_state=42,
        stratify=temp_df["label"]
    )

    train_df = train_df.copy()
    val_df = val_df.copy()
    test_df = test_df.copy()

    train_df["split"] = "train"
    val_df["split"] = "validation"
    test_df["split"] = "test"

    final_df = pd.concat([train_df, val_df, test_df], ignore_index=True)
    final_df = final_df[["split", "text", "label"]]
    final_df.to_csv(target_csv, index=False, encoding="utf-8")

    # Save individual parquet files for fast PyTorch DataLoader streaming
    processed_dir = os.path.join(base_dir, "data", "processed")
    os.makedirs(processed_dir, exist_ok=True)
    train_df.to_parquet(os.path.join(processed_dir, "train.parquet"), index=False)
    val_df.to_parquet(os.path.join(processed_dir, "validation.parquet"), index=False)
    test_df.to_parquet(os.path.join(processed_dir, "test.parquet"), index=False)

    print(f"\n[SUCCESS] Datasets compiled and saved to:")
    print(f"  -> {target_csv}")
    print(f"  -> {processed_dir}\\train.parquet ({len(train_df)} rows)")
    print(f"  -> {processed_dir}\\validation.parquet ({len(val_df)} rows)")
    print(f"  -> {processed_dir}\\test.parquet ({len(test_df)} rows)")

if __name__ == "__main__":
    process_tsv()