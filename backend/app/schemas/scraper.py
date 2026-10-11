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
    url: HttpUrl = Field(..., description="Public social media URL (YouTube, Instagram, X/Twitter)")
    max_comments: int = Field(default=50, ge=1, le=200, description="Volume filter: 20, 50, 100")
    sort_order: str = Field(default="top", description="'top' (Most Liked) or 'newest' (Latest)")

class ScrapeResponse(BaseModel):
    platform: str
    media_id: str
    total_extracted: int
    sort_order: str
    comments: List[CommentItem]