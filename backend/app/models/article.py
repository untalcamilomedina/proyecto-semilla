"""
Article model for CMS functionality
"""

from datetime import datetime
from typing import Optional
from uuid import uuid4

from sqlalchemy import Boolean, Column, DateTime, Integer, String, Text, UUID, ForeignKey, Index
from sqlalchemy.orm import relationship

from app.core.database import Base


class Article(Base):
    """
    Article model for CMS content management
    """
    __tablename__ = "articles"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    tenant_id = Column(UUID(as_uuid=True), ForeignKey("tenants.id"), nullable=False, index=True)

    # Content
    title = Column(String(200), nullable=False, index=True)
    slug = Column(String(200), nullable=False, unique=True, index=True)
    content = Column(Text, nullable=False)
    excerpt = Column(Text, nullable=True)

    # Metadata
    author_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False, index=True)
    category_id = Column(UUID(as_uuid=True), nullable=True, index=True)

    # SEO
    seo_title = Column(String(60), nullable=True)
    seo_description = Column(String(160), nullable=True)
    featured_image = Column(String(500), nullable=True)

    # Status and workflow
    status = Column(String(20), nullable=False, default="draft", index=True)  # draft, published, review
    is_featured = Column(Boolean, nullable=False, default=False)

    # Statistics
    view_count = Column(Integer, nullable=False, default=0)
    comment_count = Column(Integer, nullable=False, default=0)
    like_count = Column(Integer, nullable=False, default=0)

    # Tags (stored as JSON)
    tags = Column(Text, nullable=True, default="[]")  # JSON array of tag strings

    # Timestamps
    published_at = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime(timezone=True), nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    tenant = relationship("Tenant", back_populates="articles")
    author = relationship("User", back_populates="articles")
    comments = relationship("Comment", back_populates="article", cascade="all, delete-orphan")

    # Indexes for performance
    __table_args__ = (
        Index('idx_articles_tenant_status', 'tenant_id', 'status'),
        Index('idx_articles_tenant_published', 'tenant_id', 'published_at'),
        Index('idx_articles_author', 'author_id'),
    )

    def __repr__(self):
        return f"<Article(id={self.id}, title='{self.title}', status='{self.status}')>"


class Category(Base):
    """
    Category model for organizing articles
    """
    __tablename__ = "categories"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    tenant_id = Column(UUID(as_uuid=True), ForeignKey("tenants.id"), nullable=False, index=True)

    # Category info
    name = Column(String(100), nullable=False, index=True)
    slug = Column(String(100), nullable=False, unique=True, index=True)
    description = Column(Text, nullable=True)
    color = Column(String(7), nullable=True, default="#3B82F6")  # Hex color

    # Hierarchy
    parent_id = Column(UUID(as_uuid=True), nullable=True)
    order_index = Column(Integer, nullable=False, default=0)

    # Status
    is_active = Column(Boolean, nullable=False, default=True)

    # Timestamps
    created_at = Column(DateTime(timezone=True), nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime(timezone=True), nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    tenant = relationship("Tenant", back_populates="categories")
    articles = relationship("Article", backref="category_ref")

    def __repr__(self):
        return f"<Category(id={self.id}, name='{self.name}', slug='{self.slug}')>"


class Comment(Base):
    """
    Comment model for article discussions
    """
    __tablename__ = "comments"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    tenant_id = Column(UUID(as_uuid=True), ForeignKey("tenants.id"), nullable=False, index=True)
    article_id = Column(UUID(as_uuid=True), ForeignKey("articles.id"), nullable=False, index=True)

    # Comment content
    author_name = Column(String(100), nullable=False)
    author_email = Column(String(255), nullable=True)
    content = Column(Text, nullable=False)

    # User association (if registered user)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)

    # Moderation
    is_approved = Column(Boolean, nullable=False, default=False)
    is_spam = Column(Boolean, nullable=False, default=False)

    # Hierarchy for threaded comments
    parent_id = Column(UUID(as_uuid=True), nullable=True)

    # Timestamps
    created_at = Column(DateTime(timezone=True), nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime(timezone=True), nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    tenant = relationship("Tenant", back_populates="comments")
    article = relationship("Article", back_populates="comments")
    user = relationship("User", back_populates="comments")

    def __repr__(self):
        return f"<Comment(id={self.id}, article_id={self.article_id}, author='{self.author_name}')>"