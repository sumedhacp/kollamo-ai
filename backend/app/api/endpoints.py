from fastapi import APIRouter, HTTPException, Depends
from app.core.config import settings
from app.schemas.scraper import ScrapeRequest, ScrapeResponse
from app.schemas.sentiment import (
    SingleTextRequest, SingleTextResponse,
    BatchAnalyzeRequest, BatchAnalyzeResponse, AnalyzedCommentItem
)
from app.services.scraper import SocialScraperService
from app.services.inference import SentimentInferenceEngine

router = APIRouter(prefix=settings.API_V1_PREFIX)

# Module-level singleton to load model once into memory
_inference_engine = None

def get_inference_engine() -> SentimentInferenceEngine:
    global _inference_engine
    if _inference_engine is None:
        _inference_engine = SentimentInferenceEngine(
            model_name_or_path=settings.MODEL_PATH,
            device=settings.DEVICE
        )
    return _inference_engine

@router.post("/analyze-text", response_model=SingleTextResponse, tags=["Zone 1: Single Text Sandbox"])
async def analyze_single_text(
    payload: SingleTextRequest,
    engine: SentimentInferenceEngine = Depends(get_inference_engine)
):
    """
    Instant sentiment inference on an ad-hoc Romanized Malayalam string.
    """
    try:
        result = engine.predict_single(payload.text)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Inference error: {str(e)}")

@router.post("/fetch-comments", response_model=ScrapeResponse, tags=["Zone 2: Social Media Link Ingestion"])
async def fetch_comments(payload: ScrapeRequest):
    """
    Extracts raw comments from a public social media video URL without running inference.
    """
    try:
        video_id, comments = SocialScraperService.get_comments(
            url=str(payload.url),
            api_key=settings.YOUTUBE_API_KEY,
            max_comments=payload.max_comments
        )
        return {
            "platform": "YouTube",
            "video_id": video_id,
            "total_extracted": len(comments),
            "comments": comments
        }
    except ValueError as ve:
        raise HTTPException(status_code=422, detail=str(ve))
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"Failed to extract comments: {str(e)}")

@router.post("/analyze-batch", response_model=BatchAnalyzeResponse, tags=["Zone 3: Batch Analysis & Dashboard"])
async def analyze_batch_comments(
    payload: BatchAnalyzeRequest,
    engine: SentimentInferenceEngine = Depends(get_inference_engine)
):
    """
    Evaluates comments, generating confidence ratings and aggregated distributions.
    """
    if not payload.comments:
        raise HTTPException(status_code=400, detail="Comment list cannot be empty.")

    raw_texts = [item.text for item in payload.comments]
    predictions = engine.predict_batch(raw_texts)

    distribution = {"Positive": 0, "Negative": 0, "Neutral": 0}
    analyzed_items = []

    for item, pred in zip(payload.comments, predictions):
        distribution[pred["label"]] += 1
        analyzed_items.append(
            AnalyzedCommentItem(
                comment_id=item.comment_id,
                comment=item.text,
                cleaned_comment=pred["cleaned_text"],
                author=item.author or "Anonymous",
                like_count=item.like_count or 0,
                published_at=item.published_at or "Recent",
                label=pred["label"],
                confidence=pred["confidence"],
                probabilities=pred["probabilities"]
            )
        )

    total = len(analyzed_items)
    percentages = {
        k: round((v / total) * 100, 2) if total > 0 else 0.0
        for k, v in distribution.items()
    }

    # Net Sentiment Score: (% Positive) - (% Negative), benchmark range: -100 to +100
    net_sentiment_score = round(percentages["Positive"] - percentages["Negative"], 2)

    return {
        "total_analyzed": total,
        "sentiment_distribution": distribution,
        "sentiment_percentages": percentages,
        "net_sentiment_score": net_sentiment_score,
        "comments": analyzed_items
    }