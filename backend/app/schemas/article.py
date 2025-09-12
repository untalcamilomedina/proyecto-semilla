# backend/app/schemas/article.py

from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel

from app.models.article import ArticleStatus

class ArticleBase(BaseModel):
    title: str
    content: str
    status: Optional[ArticleStatus] = ArticleStatus.draft

class ArticleCreate(ArticleBase):
    author_id: UUID

class ArticleUpdate(BaseModel):
    title: Optional[str] = None
    content: Optional[str] = None
    status: Optional[ArticleStatus] = None

class ArticleResponse(ArticleBase):
    id: UUID
    author_id: UUID
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True