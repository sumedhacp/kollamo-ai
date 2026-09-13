import re
import emoji

class ManglishPreprocessor:
    """
    Normalizes code-mixed Malayalam-English social media text.
    Handles character elongations, colloquial contractions, and maps emojis
    directly to affective sentiment tokens rather than unknown tokens.
    """

    EMOJI_SENTIMENT_MAP = {
        ":fire:": " adipoli_positive ",
        ":red_heart:": " sneham_positive ",
        ":sparkling_heart:": " sneham_positive ",
        ":thumbs_up:": " super_positive ",
        ":clapping_hands:": " kidilan_positive ",
        ":smiling_face_with_heart-eyes:": " ishtapettu_positive ",
        ":grinning_face_with_smiling_eyes:": " chirichu_positive ",
        ":face_with_tears_of_joy:": " chiri_positive ",
        ":pile_of_poo:": " chali_negative ",
        ":thumbs_down:": " mosham_negative ",
        ":disappointed_face:": " shokam_negative ",
        ":face_vomiting:": " durantham_negative ",
        ":sleeping_face:": " lag_negative ",
        ":yawning_face:": " bore_negative ",
        ":crying_face:": " vishamam_negative "
    }

    @classmethod
    def clean_text(cls, text: str) -> str:
        if not text or not isinstance(text, str):
            return ""

        # 1. Translate emojis into textual tags
        demojized = emoji.demojize(text, delimiters=(":", ":"))
        for emo_tag, sentiment_sub in cls.EMOJI_SENTIMENT_MAP.items():
            demojized = demojized.replace(emo_tag, sentiment_sub)
        
        # Strip any remaining unmapped emoji tags
        demojized = re.sub(r":[\w_]+:", " ", demojized)

        # 2. Strip URLs, mentions, and HTML tags
        cleaned = re.sub(r"https?://\S+|www\.\S+", " ", demojized)
        cleaned = re.sub(r"@[\w_]+", " ", cleaned)
        cleaned = re.sub(r"<.*?>", " ", cleaned)
        cleaned = cleaned.replace("#", " ")

        # 3. Collapse elongated characters beyond 2 repetitions (e.g., 'poliiiiiii' -> 'polii')
        cleaned = re.sub(r"(.)\1{2,}", r"\1\1", cleaned)

        # 4. Collapse redundant spacing
        cleaned = re.sub(r"\s+", " ", cleaned).strip()

        return cleaned