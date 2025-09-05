"""
Pydantic schemas for CMS articles, categories, and comments
"""

from datetime import datetime
from typing import List, Optional
from uuid import UUID

from pydantic import BaseModel, Field


# Category schemas
class CategoryBase(BaseModel):
    name: str = Field(..., max_length=100)
    slug: str = Field(..., max_length=100)
    description: Optional[str] = None
    color: Optional[str] = Field("#3B82F6", max_length=7)
    parent_id: Optional[UUID] = None
    order_index: int = 0
    is_active: bool = True


class CategoryCreate(CategoryBase):
    pass


class CategoryUpdate(BaseModel):
    name: Optional[str] = Field(None, max_length=100)
    slug: Optional[str] = Field(None, max_length=100)
    description: Optional[str] = None
    color: Optional[str] = Field(None, max_length=7)
    parent_id: Optional[UUID] = None
    order_index: Optional[int] = None
    is_active: Optional[bool] = None


class CategoryResponse(CategoryBase):
    id: UUID
    tenant_id: UUID
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# Article schemas
class ArticleBase(BaseModel):
    title: str = Field(..., max_length=200)
    slug: str = Field(..., max_length=200)
    content: str
    excerpt: Optional[str] = None
    category_id: Optional[UUID] = None
    seo_title: Optional[str] = Field(None, max_length=60)
    seo_description: Optional[str] = Field(None, max_length=160)
    featured_image: Optional[str] = Field(None, max_length=500)
    status: str = Field("draft", pattern="^(draft|published|review)$")
    is_featured: bool = False
    tags: List[str] = Field(default_factory=list)


class ArticleCreate(ArticleBase):
    pass


class ArticleUpdate(BaseModel):
    title: Optional[str] = Field(None, max_length=200)
    slug: Optional[str] = Field(None, max_length=200)
    content: Optional[str] = None
    excerpt: Optional[str] = None
    category_id: Optional[UUID] = None
    seo_title: Optional[str] = Field(None, max_length=60)
    seo_description: Optional[str] = Field(None, max_length=160)
    featured_image: Optional[str] = Field(None, max_length=500)
    status: Optional[str] = Field(None, pattern="^(draft|published|review)$")
    is_featured: Optional[bool] = None
    tags: Optional[List[str]] = None


class ArticleResponse(ArticleBase):
    id: UUID
    tenant_id: UUID
    author_id: UUID
    view_count: int
    comment_count: int
    like_count: int
    published_at: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime

    # Related data
    author_name: Optional[str] = None
    category_name: Optional[str] = None

    class Config:
        from_attributes = True


class ArticleWithContent(ArticleResponse):
    """Article with full content for editing"""
    pass


# Comment schemas
class CommentBase(BaseModel):
    content: str
    author_name: Optional[str] = Field(None, max_length=100)
    author_email: Optional[str] = Field(None, max_length=255)


class CommentCreate(CommentBase):
    pass


class CommentUpdate(BaseModel):
    content: Optional[str] = None
    is_approved: Optional[bool] = None
    is_spam: Optional[bool] = None


class CommentResponse(CommentBase):
    id: UUID
    tenant_id: UUID
    article_id: UUID
    user_id: Optional[UUID] = None
    is_approved: bool
    is_spam: bool
    parent_id: Optional[UUID] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# Statistics schemas
class ArticleStats(BaseModel):
    total_articles: int
    published_articles: int
    draft_articles: int
    total_views: int
    total_comments: int
    total_likes: int


class CategoryStats(BaseModel):
    total_categories: int
    active_categories: int
    articles_per_category: List[dict]


# Bulk operations
class BulkArticleUpdate(BaseModel):
    article_ids: List[UUID]
    status: Optional[str] = Field(None, pattern="^(draft|published|review)$")
    category_id: Optional[UUID] = None
    is_featured: Optional[bool] = None


class BulkCategoryUpdate(BaseModel):
    category_ids: List[UUID]
    is_active: Optional[bool] = None
    color: Optional[str] = Field(None, max_length=7)