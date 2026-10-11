import os
from fastapi import APIRouter, HTTPException, Query
from typing import Optional, List

from app.schemas.sentiment import (
    SingleTextRequest,
    SingleTextResponse,
    BatchAnalyzeRequest,
    BatchAnalyzeResponse,
    AnalyzedCommentItem
)
from app.schemas.scraper import ScrapeRequest, ScrapeResponse
from app.services.inference import SentimentInferenceEngine
from app.services.scraper import SocialScraperService
from app.services.summary_generator import ExecutiveReviewGenerator

router = APIRouter()

# Dynamically locate ml/saved_model directory
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
DEFAULT_MODEL_PATH = os.path.join(BASE_DIR, "ml", "saved_model")
MODEL_PATH = os.getenv("SENTIMENT_MODEL_PATH", DEFAULT_MODEL_PATH)

# Instantiate fine-tuned pipeline once on startup
inference_engine = SentimentInferenceEngine(model_name_or_path=MODEL_PATH, device="cpu")

@router.post("/analyze-single", response_model=SingleTextResponse, tags=["Inference"])
def analyze_single_comment(request: SingleTextRequest):
    try:
        result = inference_engine.predict_single(request.text)
        return SingleTextResponse(**result)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Inference error: {str(e)}")

@router.post("/scrape-comments", response_model=ScrapeResponse, tags=["Scraper"])
def scrape_social_comments(request: ScrapeRequest):
    try:
        platform, media_id, comments = SocialScraperService.get_comments(
            url=str(request.url),
            max_comments=request.max_comments,
            sort_order=request.sort_order
        )
        return ScrapeResponse(
            platform=platform,
            media_id=media_id,
            total_extracted=len(comments),
            requested_limit=request.max_comments,
            sort_order=request.sort_order,
            comments=comments
        )
    except ValueError as ve:
        raise HTTPException(status_code=400, detail=str(ve))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Scraper error: {str(e)}")

@router.post("/analyze-batch", response_model=BatchAnalyzeResponse, tags=["Batch Analytics"])
def analyze_batch_comments(request: BatchAnalyzeRequest):
    if not request.comments:
        raise HTTPException(status_code=400, detail="Comments payload cannot be empty.")

    analyzed_items: List[AnalyzedCommentItem] = []
    distribution = {"Positive": 0, "Negative": 0, "Neutral": 0, "Mixed": 0, "Unsupported": 0}

    for item in request.comments:
        pred = inference_engine.predict_single(item.text)
        label = pred["label"]
        distribution[label] = distribution.get(label, 0) + 1

        analyzed_items.append(
            AnalyzedCommentItem(
                comment_id=item.comment_id,
                comment=item.text,
                cleaned_comment=pred["cleaned_text"],
                author=item.author or "Anonymous",
                like_count=item.like_count or 0,
                published_at=item.published_at or "Recent",
                is_supported=pred["is_supported"],
                language_type=pred["language_type"],
                error_message=pred["error_message"],
                translated_text=pred["translated_text"],
                token_breakdown=pred["token_breakdown"],
                label=pred["label"],
                confidence=pred["confidence"],
                probabilities=pred["probabilities"],
                is_mixed_sentiment=pred["is_mixed_sentiment"],
                conflicting_spans=pred["conflicting_spans"]
            )
        )

    total = len(analyzed_items)
    supported_items = [c for c in analyzed_items if c.is_supported]
    supported_count = len(supported_items)
    unsupported_count = total - supported_count

    percentages = {
        k: round((v / supported_count) * 100, 1) if supported_count > 0 else 0.0
        for k, v in distribution.items()
        if k != "Unsupported"
    }

    nss = round(percentages.get("Positive", 0.0) - percentages.get("Negative", 0.0), 1)

    return BatchAnalyzeResponse(
        total_analyzed=total,
        supported_count=supported_count,
        unsupported_count=unsupported_count,
        sentiment_distribution=distribution,
        sentiment_percentages=percentages,
        net_sentiment_score=nss,
        comments=analyzed_items
    )

@router.post("/generate-summary", tags=["Analytics Summary"])
def generate_executive_summary(comments: List[AnalyzedCommentItem]):
    dict_items = [c.dict() for c in comments]
    summary = ExecutiveReviewGenerator.generate_summary(dict_items)
    return summary