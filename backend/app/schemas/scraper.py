# backend/app/schemas/scraper.py
from pydantic import BaseModel, HttpUrl, Field
from typing import List, Optional

class CommentItem(BaseModel):
    comment_id: str
    text: str
    author: str
    author_avatar: Optional[str] = None
    like_count: int = 0
    published_at: str
    platform: str

class ScrapeRequest(BaseModel):
    url: HttpUrl = Field(..., description="Public social media URL")
    max_comments: int = Field(default=50, ge=0, description="0 for ALL comments, or any positive number (1, 2, 3...)")
    sort_order: str = Field(default="top", description="'top', 'newest', or 'oldest'")

class ScrapeResponse(BaseModel):
    platform: str
    media_id: str
    total_extracted: int
    requested_limit: int = 0
    sort_order: str
    comments: List[CommentItem]
