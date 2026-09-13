from pydantic import BaseModel, Field
from typing import List, Dict, Optional

class TokenDetail(BaseModel):
    token: str
    type: str  # 'English', 'Phonetic Manglish', 'Malayalam Script', 'PUNCTUATION'

class SingleTextRequest(BaseModel):
    text: str = Field(..., min_length=1, description="Raw social comment text")

class SingleTextResponse(BaseModel):
    raw_text: str
    cleaned_text: str
    is_supported: bool
    language_type: str  # 'MALAYALAM', 'MANGLISH', 'ENGLISH', 'UNSUPPORTED'
    error_message: Optional[str] = None
    translated_text: Optional[str] = None
    token_breakdown: List[TokenDetail] = []
    label: str
    confidence: float
    probabilities: Dict[str, float]
    latency_ms: float

class BatchItemRequest(BaseModel):
    comment_id: str
    text: str
    author: Optional[str] = "Anonymous"
    like_count: Optional[int] = 0
    published_at: Optional[str] = "Recent"

class BatchAnalyzeRequest(BaseModel):
    comments: List[BatchItemRequest] = Field(..., min_items=1)

class AnalyzedCommentItem(BaseModel):
    comment_id: str
    comment: str
    cleaned_comment: str
    author: str
    like_count: int
    published_at: str
    is_supported: bool
    language_type: str
    error_message: Optional[str] = None
    translated_text: Optional[str] = None
    token_breakdown: List[TokenDetail] = []
    label: str
    confidence: float
    probabilities: Dict[str, float]

class BatchAnalyzeResponse(BaseModel):
    total_analyzed: int
    supported_count: int
    unsupported_count: int
    sentiment_distribution: Dict[str, int]
    sentiment_percentages: Dict[str, float]
    net_sentiment_score: float
    comments: List[AnalyzedCommentItem]