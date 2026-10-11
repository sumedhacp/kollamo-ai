# backend/app/services/summary_generator.py
import re
from typing import List, Dict, Any

class ExecutiveReviewGenerator:
    """
    Synthesizes multi-comment analytics into an executive-level audience summary.
    Calculates Net Sentiment Score (NSS = % Positive - % Negative) and surfaces key discussion themes.
    """

    ASPECT_LEXICON = {
        "visuals": ["visual", "visuals", "cinematography", "camera", "frame", "vfx", "color"],
        "acting": ["acting", "actor", "actress", "performance", "tovino", "mammookka", "mohanlal"],
        "music": ["music", "bgm", "score", "song", "songs", "soundtrack"],
        "pacing": ["lag", "pacing", "slow", "length", "drag", "second half"],
        "story": ["story", "screenplay", "script", "direction", "climax", "plot"]
    }

    @classmethod
    def generate_summary(cls, analyzed_comments: List[Dict[str, Any]]) -> Dict[str, Any]:
        supported = [c for c in analyzed_comments if c.get("is_supported", True)]
        total = len(supported)

        if total == 0:
            return {
                "headline": "Insufficient Supported Comments",
                "narrative": "No supported Malayalam, Manglish, or English comments were available to generate an executive review summary.",
                "net_sentiment_score": 0.0,
                "aspect_breakdown": {}
            }

        pos_count = sum(1 for c in supported if c.get("label") == "Positive")
        neg_count = sum(1 for c in supported if c.get("label") == "Negative")
        neu_count = sum(1 for c in supported if c.get("label") == "Neutral")
        mix_count = sum(1 for c in supported if c.get("label") == "Mixed" or c.get("is_mixed_sentiment", False))

        pos_pct = round((pos_count / total) * 100, 1)
        neg_pct = round((neg_count / total) * 100, 1)
        neu_pct = round((neu_count / total) * 100, 1)

        # Net Sentiment Score (NSS ranges from -100 to +100)
        nss = round(pos_pct - neg_pct, 1)

        # Determine overall tone headline
        if pos_pct >= 70:
            headline = f"Strongly Positive Reception ({pos_pct}%)"
        elif pos_pct >= 50:
            headline = f"Favorable Reception ({pos_pct}%)"
        elif neg_pct >= 50:
            headline = f"Predominantly Critical Reception ({neg_pct}%)"
        elif nss >= 15:
            headline = f"Moderately Positive Reception (NSS: +{nss})"
        elif nss <= -15:
            headline = f"Mixed-to-Negative Reception (NSS: {nss})"
        else:
            headline = "Balanced / Neutral Audience Response"

        # Aspect & theme frequency extraction
        aspect_feedback: Dict[str, Dict[str, int]] = {k: {"pos": 0, "neg": 0} for k in cls.ASPECT_LEXICON}
        for c in supported:
            text = (c.get("cleaned_comment") or c.get("comment", "")).lower()
            label = c.get("label", "Neutral")

            for aspect, keywords in cls.ASPECT_LEXICON.items():
                if any(kw in text for kw in keywords):
                    if label in ["Positive", "Mixed"]:
                        aspect_feedback[aspect]["pos"] += 1
                    elif label == "Negative":
                        aspect_feedback[aspect]["neg"] += 1

        praised = [asp for asp, counts in aspect_feedback.items() if counts["pos"] > counts["neg"] and counts["pos"] > 0]
        critiqued = [asp for asp, counts in aspect_feedback.items() if counts["neg"] >= counts["pos"] and counts["neg"] > 0]

        # Construct analytical narrative
        praised_str = ", ".join(praised) if praised else "the core creative direction"
        narrative_parts = [f"Audience response across {total} analyzed comments reflects a {headline.lower()}."]

        if praised:
            narrative_parts.append(f"Viewers frequently highlighted and praised {praised_str}.")
        if critiqued:
            critiqued_str = ", ".join(critiqued)
            narrative_parts.append(f"Criticism centered primarily on {critiqued_str} ({neg_pct}% negative sentiments).")
        if mix_count > 0:
            narrative_parts.append(f"{mix_count} comments expressed mixed sentiments, often contrasting strong opening acts with slower pacing in later halves.")

        return {
            "headline": headline,
            "narrative": " ".join(narrative_parts),
            "net_sentiment_score": nss,
            "sentiment_split": {
                "positive_pct": pos_pct,
                "negative_pct": neg_pct,
                "neutral_pct": neu_pct
            },
            "aspect_breakdown": aspect_feedback
        }