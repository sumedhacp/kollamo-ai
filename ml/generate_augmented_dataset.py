# ml/generate_augmented_dataset.py
import os
import random
import pandas as pd

OUTPUT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "dataset")
OUTPUT_FILE = os.path.join(OUTPUT_DIR, "augmented_social_comments.csv")
BENCHMARK_FILE = os.path.join(OUTPUT_DIR, "dravidian_manglish_sentiment.csv")

# Synthetic comment templates covering YouTube shorts, Instagram reels, and Twitter
TEMPLATES = [
    # Positive / Hype / Praise
    ("{subject} {praise_adj} aayittund machane, {aspect} vere level!", "Positive"),
    ("Climax {praise_verb}.. {aspect} kanditt romancham vannu!", "Positive"),
    ("{aspect} idivett saadhanam.. {subject} thakarthu!", "Positive"),
    ("Ijjathi twist aayippoyi, {subject} pakka mass and clean making.", "Positive"),
    ("Oru rakshayumillaatha item! {aspect} koodi aayappol kidilam aayi.", "Positive"),
    ("{subject} swag and aura vere level, haters enthelum paranjotte!", "Positive"),
    ("First half nalla entertainment, second half climax thooki!", "Positive"),
    ("Nte ponnoo.. ithra nalla {aspect} ee aduthonnum kandittillaa!", "Positive"),

    # Negative / Critical / Disappointment
    ("{subject} valare bore aayirunnu, full lag mathram.", "Negative"),
    ("Kore thallu kettu vannatha, verum chali padam.", "Negative"),
    ("{aspect} total durantham.. samayam poyi kaashum poyi.", "Negative"),
    ("Overacting kandu veruppeer vannu, oola direction.", "Negative"),
    ("Trailer kanditt hype ketti, final product shokam thanne!", "Negative"),
    ("Freemake aanu bro, vere cinemel ninnu motham churandiyath.", "Negative"),
    ("Chumma show kaanikkan vendi mathram undakkiya {subject}.", "Negative"),
    ("Second half valichuneetti alamb aakki kalanju.", "Negative"),

    # Neutral / Balanced / Informational
    ("Instayil reel kand vannavar undo ivide?", "Neutral"),
    ("15:30 timeline il ulla bgm ethu song aanu?", "Neutral"),
    ("Next part eppozhaanu release aakunnath?", "Neutral"),
    ("Story average aanu, pakshe visuals kollam.", "Neutral"),
    ("First half pwoli pakshe second half valare bore aayi.", "Mixed_feelings"),
    ("Acting nannayittund enkilum pacing kurachu lag aanu.", "Mixed_feelings")
]

SUBJECTS = ["Short film", "Padam", "Teaser", "Trailer", "Acting", "Movie", "Scene", "Character", "Content", "Making"]
ASPECTS = ["Background music", "BGM", "Visuals", "Cinematography", "Direction", "Color grading", "Script", "Acting"]
PRAISE_ADJ = ["adipoli", "kidilam", "theepori", "pwoli", "mass", "marana mass", "pakka set"]
PRAISE_VERB = ["thooki", "polichadukki", "thakarthu", "kidukki"]

def generate_synthetic_samples(num_samples: int = 4000) -> pd.DataFrame:
    records = []
    for _ in range(num_samples):
        template, sentiment = random.choice(TEMPLATES)
        comment = template.format(
            subject=random.choice(SUBJECTS),
            aspect=random.choice(ASPECTS),
            praise_adj=random.choice(PRAISE_ADJ),
            praise_verb=random.choice(PRAISE_VERB)
        )
        records.append({"comment": comment, "sentiment": sentiment})
    return pd.DataFrame(records)

def create_master_dataset():
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    
    synthetic_df = generate_synthetic_samples(4000)
    print(f"[+] Generated {len(synthetic_df)} augmented modern social media samples.")

    if os.path.exists(BENCHMARK_FILE):
        print(f"[*] Merging with existing DravidianCodeMix corpus: {BENCHMARK_FILE}")
        benchmark_df = pd.read_csv(BENCHMARK_FILE)
        
        # Standardize column names
        text_col = "comment" if "comment" in benchmark_df.columns else benchmark_df.columns[0]
        label_col = "sentiment" if "sentiment" in benchmark_df.columns else benchmark_df.columns[1]
        
        benchmark_clean = pd.DataFrame({
            "comment": benchmark_df[text_col].astype(str),
            "sentiment": benchmark_df[label_col].astype(str)
        })
        
        master_df = pd.concat([benchmark_clean, synthetic_df], ignore_index=True)
    else:
        print("[!] Benchmark file not found. Outputting synthetic corpus only.")
        master_df = synthetic_df

    master_df.drop_duplicates(subset=["comment"], inplace=True)
    master_df.to_csv(OUTPUT_FILE, index=False, encoding="utf-8")
    
    print(f"[SUCCESS] Master augmented dataset written to: {OUTPUT_FILE}")
    print(f"[+] Total samples available for training/evaluation: {len(master_df)}")

if __name__ == "__main__":
    create_master_dataset()