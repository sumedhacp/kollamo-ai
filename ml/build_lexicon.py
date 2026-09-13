# ml/build_lexicon.py
import os
import re
import json
import pandas as pd
from collections import Counter
from typing import Dict, List, Set

DATASET_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "dataset", "dravidian_manglish_sentiment.csv")
LEXICON_OUTPUT_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "dataset", "manglish_lexicon.json")

# Master multi-domain seed clusters
SEED_CLUSTERS: Dict[str, List[str]] = {
    # -------------------------------------------------------------------------
    # 1. POSITIVE / HYPE / PRAISE / VIRAL REACTION (Insta Reels, Shorts, Drops)
    # -------------------------------------------------------------------------
    "pwoli": [
        "poli", "pwoli", "pwoly", "poly", "polii", "pwolii", "polichu", "pwolichu",
        "polich", "pwolich", "pwolisanam", "polisaname", "pwolichallo", "policheee",
        "polikkuka", "polikkanu", "pwolichadukki", "poliche", "pwolichittund", "pwolye"
    ],
    "adipoli": [
        "adipoli", "adipwoli", "athipoli", "athipwoli", "adipoly", "adipwoly",
        "adhipoli", "adhypoly", "adipolii", "adbwoli", "adipwolii", "adhypwoli",
        "athipoly", "athipwolii", "adipoliyayittund"
    ],
    "kidilam": [
        "kidu", "kidilam", "kidhilan", "kidilan", "kiddilam", "kidukidu",
        "kidukkachi", "kidilann", "kiduve", "kiduveee", "kidilamaayittund",
        "kidilanaayi", "kidukki", "kidukkiyittund"
    ],
    "kollam": [
        "kollam", "kolam", "kollaam", "kollamm", "kollallo", "kollaalo",
        "kollamallo", "kollameda", "kollamparayanilla", "kollaamayirunnu", "kollutto"
    ],
    "theepori": [
        "theepori", "theepwori", "thee", "theeporiye", "theeppori", "theepic",
        "fire", "theeyaane", "theeyanu", "theeppori_item", "theeporii"
    ],
    "thakarthu": [
        "thakarthu", "thakartu", "thakathu", "thakarthallo", "thakarthirikkunnu",
        "thakarthe", "thakartha", "thakarthittund", "thakarthekkunnu"
    ],
    "thooki": [
        "thooki", "thookii", "thookk", "thookiyallo", "thooki_chuvanna",
        "thookipparathi", "thookikkoottu"
    ],
    "mass": [
        "mass", "maas", "massu", "massaa", "massaanu", "massmaram", "masskidu",
        "marana_mass", "paka_mass", "masskaatt", "masslevel", "swag", "aura"
    ],
    "romancham": [
        "romancham", "romanjam", "romanchamm", "romancha", "romaancham",
        "goosebumps", "romanchamvannu", "romanchified", "mayirkalchuma"
    ],
    "raksha": [
        "rakshayilla", "rakshayillatha", "rakshilla", "rekshayilla", "no_words",
        "oru_rakshayumilla", "rakshayilathathu", "speechless"
    ],
    "uyir": [
        "uyir", "uyire", "uyiraanu", "uyiranu", "uyirrrr", "life", "uyir_item"
    ],
    "level": [
        "level", "leval", "levil", "vere_level", "next_level", "veralevel",
        "veraleval", "verelevelaanu", "vera_level"
    ],
    "sambhavam": [
        "sambavam", "sambavamthanne", "sambhavam", "sambhavamaan",
        "sambhavamaayi", "valiya_sambhavam", "sambhavam_set"
    ],
    "idivettu": [
        "idivett", "idivettu", "idivette", "saadhanam", "sadhanam", "idivett_item"
    ],
    "ijjathi": [
        "ijjathi", "eejathi", "ejjathi", "e_jathi", "ijjathi_twist", "ijjathi_mass"
    ],
    "ponno": [
        "ponno", "ponnoo", "nte_ponno", "nte_ponnoo", "ente_ponno", "ente_daivame", "daivameee"
    ],
    "nannayi": [
        "nannayi", "nannaayi", "nannaytund", "nannayittund", "nanayi",
        "nannaayittund", "nannay", "nannayitt", "nannavunnu", "nannayirikunnu"
    ],
    "nalla": [
        "nalla", "nala", "nallath", "nallatha", "nallathaanu", "nallathanu",
        "nallavan", "nallathum", "nallapole", "nalloru", "nallathre"
    ],
    "ishtam": [
        "ishtam", "ishttam", "istam", "isttam", "ishtapettu", "ishtappettu",
        "ishtaayi", "ishtaayilla", "ishtamaayi", "ishtamayi", "ishtamaan"
    ],

    # -------------------------------------------------------------------------
    # 2. NEGATIVE / CRITICAL / TROLLS / DISAPPOINTMENT (Movies & Social Media)
    # -------------------------------------------------------------------------
    "bore": [
        "bore", "bor", "boar", "boring", "boradichu", "boradi",
        "boreadipichu", "borayi", "boratharam", "boradichu_chathu"
    ],
    "lag": [
        "lag", "laag", "lagg", "lagging", "valipp", "lagged",
        "valichuneetti", "valichu_neetti", "drag", "valip", "lag_adi"
    ],
    "chali": [
        "chali", "chaly", "chaali", "ocha", "chalipperu", "pachachali",
        "chalikal", "chalis", "verum_chali"
    ],
    "durantham": [
        "durantham", "durantam", "duranthamm", "durandham", "duranthama",
        "duranthamanu", "tholi", "tholvi", "maha_durantham"
    ],
    "veruppeer": [
        "veruppir", "veruppeer", "veruppikkal", "verupichu", "veruppichu",
        "veruthu", "verupp", "verupaanu", "verupikkunnu"
    ],
    "shokam": [
        "shokam", "sokam", "shokama", "sokama", "shokamthanne",
        "sokamthanne", "valare_shokam"
    ],
    "nashtam": [
        "nashtam", "nastam", "nashttam", "kashtam", "kashtamthanne",
        "waste", "samayam_poyi", "kashtapadu", "kaashu_poyi"
    ],
    "mosham": [
        "mosham", "mosam", "moosham", "moshamayi", "moshamayittund",
        "moshamanu", "valare_mosham"
    ],
    "potta": [
        "potta", "potte", "pottan", "potten", "pottatharam", "mandan",
        "potatharam", "ooola", "oohlam", "oohlatharam", "koora", "mandatharam"
    ],
    "alamb": [
        "alamb", "alambu", "alambaanu", "aalamb", "elamb", "alambacting", "alambpadam"
    ],
    "thallu": [
        "thallu", "thal", "thallal", "thallukal", "over_hype", "fake_hype",
        "thallimaari", "thallu_vandi"
    ],
    "kopp": [
        "kopp", "kop", "koppu", "kopile", "kopilathe", "oombu", "oombi",
        "oombiya", "oombiko", "oombiyath"
    ],
    "churandiyath": [
        "churandiyath", "churandi", "copypaste", "copy_adi", "swaha", "freemake"
    ],

    # -------------------------------------------------------------------------
    # 3. POLITICAL DEBATE, NEWS & TWITTER/X TROLL SPAN
    # -------------------------------------------------------------------------
    "capsule": [
        "capsule", "kapsule", "capsul", "capsule_irakki", "kapsule_theernnu", "capsules"
    ],
    "nyayeekaranam": [
        "nyayeekaranam", "nyayikaranam", "nyayeekarikka", "nyayikarichu", "nyayamilla"
    ],
    "antham": [
        "antham", "andham", "anthams", "anthamfanz", "fanole", "fanzoli", "kammi", "kammikal",
        "sanghi", "sanghikal", "sudappi", "congi", "congikal"
    ],
    "troll": [
        "troll", "trolls", "trollan", "trollmaar", "chappa", "chaappa", "kalippan"
    ],
    "thettanu": [
        "thettanu", "thett", "thettaayi", "thettaanu", "abaddham", "abatham"
    ],

    # -------------------------------------------------------------------------
    # 4. INSTAGRAM & YOUTUBE CREATOR ADDRESSING SLANG
    # -------------------------------------------------------------------------
    "machane": [
        "machan", "machane", "macha", "machaan", "machanee", "bro", "bhai",
        "aliya", "aliyan", "broye", "chunk", "chunke", "mwonu", "mwone",
        "muthmane", "muth", "muthe", "chettan", "chettane", "chetta"
    ],
    "settu": [
        "settu", "set", "settanu", "setaane", "settaan", "scene_set",
        "pakka_set", "set_aakki", "paripadi_set"
    ],
    "scene": [
        "scene", "scen", "seen", "seene", "sceneaanu", "sceneda",
        "sceneconttra", "ghora_scene"
    ],
    "chumma": [
        "chumma", "chuma", "chummaa", "veruthe", "veruthey", "chumma_show", "show_kaanikalle"
    ],

    # -------------------------------------------------------------------------
    # 5. AUDIO-VISUAL & MEDIA PRODUCTION TERMS
    # -------------------------------------------------------------------------
    "padam": [
        "padam", "paadam", "padamm", "padaam", "cinema", "sinima", "sinma", "movie", "film"
    ],
    "song": [
        "song", "paattu", "pattu", "ganam", "track", "music", "audio", "bgm", "score"
    ],
    "acting": [
        "acting", "abhinayam", "performance", "cast", "role", "character", "overacting"
    ],
    "making": [
        "direction", "making", "director", "screenplay", "script", "visuals",
        "cinematography", "vfx", "editing", "cut"
    ],

    # -------------------------------------------------------------------------
    # 6. GRAMMATICAL CONNECTORS, NEGATIONS & PARTICLES
    # -------------------------------------------------------------------------
    "aanu": ["aan", "aane", "aann", "aannu", "aanu", "anu", "aakunnu", "aanedo", "aanuith"],
    "aayi": ["aay", "aaye", "aayi", "ay", "aye", "ayi"],
    "aayirunnu": ["aarnu", "aarnnu", "aayirnu", "aayirnnu", "aayirunnu", "aayrnn", "arnnu", "ayirnu", "ayirunnu"],
    "aayittund": ["aayittund", "aayittundallo", "aaytund", "ayittund", "aytund"],
    "alla": ["allaa", "alla", "allada", "allallo", "allathe", "allla"],
    "illa": ["ila", "illa", "illaa", "illada", "illallo", "illathe", "illla"],
    "undu": ["und", "undallo", "undayirunnu", "undarnnu", "undd", "undu"],
    "enikku": ["enik", "enikk", "enikku", "enikm", "eniku", "ennik", "ennikku"],
    "njan": ["nammal", "nammall", "njaan", "njan", "njann", "njanum", "njn"],
    "pakshe": ["but", "enkilum", "pakse", "pakseh", "pakshe", "pakshehh"],
    "ithu": ["eethu", "idhu", "ith", "ithaa", "ithaanu", "ithokke", "ithu"],
    "cheythu": ["cheydhu", "cheythu", "cheyithu", "cheytha", "cheydhilla", "cheythilla", "cheythittilla", "cheythittund"],
    "kandu": ["kandu", "kand", "kanditt", "kandittilla", "kanditilla", "kandathinu", "kandathinushesham"],
    "thanne": ["thanne", "thanney", "thannae", "thanneyaanu", "thanneaanu"],
    "kurachu": ["korach", "korachu", "kore", "kurach", "kurachu", "koreokke"],
    "valare": ["kooduthal", "valare", "valareadhikam", "valareyere", "valarre", "bhayankara", "bhayankaram"],
    "athe": ["athe", "athey", "athae", "atheeda", "athaanu", "athaan"],
    "pinne": ["pinne", "pinneyum", "pinnee"],
    "mathram": ["maathram", "mathram", "mathrame"]
}


def clean_raw_token(token: str) -> str:
    token = token.lower().strip()
    token = re.sub(r"[^\w]", "", token)
    return token


def soundex_canonical_signature(word: str) -> str:
    w = word.lower()
    w = re.sub(r"\bpw", "p", w)
    w = re.sub(r"\bbw", "b", w)
    w = re.sub(r"zh", "l", w)
    w = re.sub(r"th", "t", w)
    w = re.sub(r"dh", "d", w)
    w = re.sub(r"sh", "s", w)
    w = re.sub(r"aa", "a", w)
    w = re.sub(r"ee", "i", w)
    w = re.sub(r"oo", "u", w)
    w = re.sub(r"y\b", "i", w)
    w = re.sub(r"(.)\1+", r"\1", w)
    return w


def find_comment_column(df: pd.DataFrame) -> str:
    possible_names = ["comment", "text", "comments", "sentence", "sentences", "tweet", "data"]
    for col in df.columns:
        if str(col).lower().strip() in possible_names:
            return col
    col_lengths = {col: df[col].astype(str).str.len().mean() for col in df.columns}
    return max(col_lengths, key=col_lengths.get)


def build_lexicon():
    if not os.path.exists(DATASET_PATH):
        raise FileNotFoundError(f"Missing {DATASET_PATH}. Please run ml/download_dataset.py first.")

    print(f"[*] Reading DravidianCodeMix corpus from: {DATASET_PATH}")
    df = pd.read_csv(DATASET_PATH)
    comment_col = find_comment_column(df)
    print(f"[+] Using text column: '{comment_col}'")

    token_counter = Counter()
    for comment in df[comment_col].dropna():
        words = str(comment).split()
        for w in words:
            cleaned = clean_raw_token(w)
            if cleaned and not cleaned.isnumeric() and len(cleaned) > 1:
                token_counter[cleaned] += 1

    print(f"[+] Parsed {len(token_counter)} unique tokens from corpus.")

    lexicon_map: Dict[str, Set[str]] = {}
    canonical_signatures: Dict[str, str] = {}

    for canonical, variants in SEED_CLUSTERS.items():
        lexicon_map[canonical] = set(variants)
        canonical_signatures[canonical] = soundex_canonical_signature(canonical)

    matched_tokens = 0
    for token, freq in token_counter.items():
        if freq < 2:
            continue
        token_sig = soundex_canonical_signature(token)
        for canonical, sig in canonical_signatures.items():
            if token_sig == sig:
                lexicon_map[canonical].add(token)
                matched_tokens += 1
                break

    final_output = {k: sorted(list(v)) for k, v in sorted(lexicon_map.items())}

    with open(LEXICON_OUTPUT_PATH, "w", encoding="utf-8") as f:
        json.dump(final_output, f, indent=2, ensure_ascii=False)

    total_variants = sum(len(v) for v in final_output.values())
    print(f"\n[SUCCESS] Synthesized {len(final_output)} canonical lemmas covering {total_variants} phonetic variations.")
    print(f"[+] Clustered {matched_tokens} authentic social tokens into lexicon.")
    print(f"[+] Output written to: {LEXICON_OUTPUT_PATH}")


if __name__ == "__main__":
    build_lexicon()