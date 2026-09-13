from fastapi import APIRouter, HTTPException, Depends
from app.core.config import settings
from app.schemas.scraper import ScrapeRequest, ScrapeResponse
from app.schemas.sentiment import (
    SingleTextRequest, SingleTextResponse,
    BatchAnalyzeRequest, BatchAnalyzeResponse, AnalyzedCommentItem
)
from app.services.scraper import SocialScraperService
from app.services.inference import SentimentInferenceEngine
from app.services.language_guard import LanguageGuardService
from app.services.translator import ManglishTranslatorService

router = APIRouter(prefix=settings.API_V1_PREFIX)

_inference_engine = None

def get_inference_engine() -> SentimentInferenceEngine:
    global _inference_engine
    if _inference_engine is None:
        _inference_engine = SentimentInferenceEngine(
            model_name_or_path=settings.MODEL_PATH,
            device=settings.DEVICE
        )
    return _inference_engine

@router.post("/analyze-text", response_model=SingleTextResponse, tags=["Single Text Sandbox"])
async def analyze_single_text(
    payload: SingleTextRequest,
    engine: SentimentInferenceEngine = Depends(get_inference_engine)
):
    """
    Evaluates a single comment: runs language guardrail, token breakdown,
    semantic translation, and calibrated MuRIL sentiment inference.
    """
    raw_text = payload.text.strip()
    is_supported, lang_type, err_msg = LanguageGuardService.validate_text(raw_text)

    if not is_supported:
        return SingleTextResponse(
            raw_text=raw_text,
            cleaned_text="",
            is_supported=False,
            language_type=lang_type,
            error_message=err_msg,
            translated_text=None,
            token_breakdown=[],
            label="Unsupported",
            confidence=0.0,
            probabilities={"Positive": 0.0, "Negative": 0.0, "Neutral": 0.0},
            latency_ms=1.5
        )

    tokens = ManglishTranslatorService.get_token_breakdown(raw_text)
    translation = ManglishTranslatorService.translate_manglish_to_english(raw_text)
    prediction = engine.predict_single(raw_text)

    return SingleTextResponse(
        raw_text=raw_text,
        cleaned_text=prediction["cleaned_text"],
        is_supported=True,
        language_type=lang_type,
        error_message=None,
        translated_text=translation,
        token_breakdown=tokens,
        label=prediction["label"],
        confidence=prediction["confidence"],
        probabilities=prediction["probabilities"],
        latency_ms=prediction["latency_ms"]
    )

@router.post("/fetch-comments", response_model=ScrapeResponse, tags=["Social Link Studio"])
async def fetch_comments(payload: ScrapeRequest):
    """
    Extracts authentic comments from YouTube, Instagram, or X without capturing UI button artifacts.
    """
    try:
        platform, video_id, comments = SocialScraperService.get_comments(
            url=str(payload.url),
            api_key=settings.YOUTUBE_API_KEY,
            max_comments=payload.max_comments,
            sort_order=payload.sort_order
        )
        return {
            "platform": platform,
            "video_id": video_id,
            "total_extracted": len(comments),
            "comments": comments
        }
    except ValueError as ve:
        raise HTTPException(status_code=422, detail=str(ve))
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"Extraction failure: {str(e)}")

@router.post("/analyze-batch", response_model=BatchAnalyzeResponse, tags=["Batch Analytics"])
async def analyze_batch_comments(
    payload: BatchAnalyzeRequest,
    engine: SentimentInferenceEngine = Depends(get_inference_engine)
):
    """
    Batch evaluates comments: filters unsupported languages, executes MuRIL inference,
    translates Manglish to English, and computes global KPI metrics.
    """
    if not payload.comments:
        raise HTTPException(status_code=400, detail="Comment payload list is empty.")

    analyzed_items = []
    distribution = {"Positive": 0, "Negative": 0, "Neutral": 0}
    supported_count = 0
    unsupported_count = 0
    valid_items_to_predict = []

    # Step 1: Language Guardrail Partitioning
    for item in payload.comments:
        is_supported, lang_type, err_msg = LanguageGuardService.validate_text(item.text)
        if not is_supported:
            unsupported_count += 1
            analyzed_items.append(
                AnalyzedCommentItem(
                    comment_id=item.comment_id,
                    comment=item.text,
                    cleaned_comment="",
                    author=item.author or "Anonymous",
                    like_count=item.like_count or 0,
                    published_at=item.published_at or "Recent",
                    is_supported=False,
                    language_type=lang_type,
                    error_message=err_msg,
                    translated_text=None,
                    token_breakdown=[],
                    label="Unsupported",
                    confidence=0.0,
                    probabilities={"Positive": 0.0, "Negative": 0.0, "Neutral": 0.0}
                )
            )
        else:
            supported_count += 1
            valid_items_to_predict.append(item)

    # Step 2: Inference & Translation for Supported Items
    if valid_items_to_predict:
        texts = [c.text for c in valid_items_to_predict]
        predictions = engine.predict_batch(texts)

        for c, pred in zip(valid_items_to_predict, predictions):
            distribution[pred["label"]] += 1
            tokens = ManglishTranslatorService.get_token_breakdown(c.text)
            trans = ManglishTranslatorService.translate_manglish_to_english(c.text)

            analyzed_items.append(
                AnalyzedCommentItem(
                    comment_id=c.comment_id,
                    comment=c.text,
                    cleaned_comment=pred["cleaned_text"],
                    author=c.author or "Anonymous",
                    like_count=c.like_count or 0,
                    published_at=c.published_at or "Recent",
                    is_supported=True,
                    language_type="MANGLISH",
                    error_message=None,
                    translated_text=trans,
                    token_breakdown=tokens,
                    label=pred["label"],
                    confidence=pred["confidence"],
                    probabilities=pred["probabilities"]
                )
            )

    total = len(analyzed_items)
    percentages = {
        k: round((v / supported_count) * 100, 2) if supported_count > 0 else 0.0
        for k, v in distribution.items()
    }
    net_score = round(percentages["Positive"] - percentages["Negative"], 2)

    return {
        "total_analyzed": total,
        "supported_count": supported_count,
        "unsupported_count": unsupported_count,
        "sentiment_distribution": distribution,
        "sentiment_percentages": percentages,
        "net_sentiment_score": net_score,
        "comments": analyzed_items
    }