from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime


class NewsArticleBase(BaseModel):
    title: str
    content: Optional[str] = None
    source: str
    url: str
    publish_date: Optional[datetime] = None
    authors: Optional[List[str]] = []
    keywords: Optional[List[str]] = []
    summary: Optional[str] = None
    top_image: Optional[str] = None


class NewsArticleCreate(NewsArticleBase):
    pass


class NewsArticleResponse(NewsArticleBase):
    id: int
    created_at: datetime
    updated_at: datetime
    is_processed: bool = False

    class Config:
        from_attributes = True