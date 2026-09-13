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
    url: HttpUrl = Field(..., description="Public video or post URL")
    max_comments: int = Field(default=50, ge=1, le=200, description="Comment volume")
    sort_order: str = Field(default="top", description="'top' or 'newest'")

class ScrapeResponse(BaseModel):
    platform: str
    video_id: str
    total_extracted: int
    comments: List[CommentItem]