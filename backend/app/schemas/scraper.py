from pydantic import BaseModel, HttpUrl, Field
from typing import List, Optional

class CommentItem(BaseModel):
    comment_id: str
    text: str
    author: str
    author_avatar: Optional[str] = None
    like_count: int = 0
    published_at: str

class ScrapeRequest(BaseModel):
    url: HttpUrl = Field(..., description="Public YouTube video URL")
    max_comments: int = Field(default=50, ge=1, le=500, description="Number of comments to fetch")

class ScrapeResponse(BaseModel):
    platform: str
    video_id: str
    total_extracted: int
    comments: List[CommentItem]