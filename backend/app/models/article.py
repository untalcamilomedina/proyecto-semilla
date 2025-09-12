# backend/app/models/article.py

import enum
from datetime import datetime
from uuid import uuid4

from sqlalchemy import Column, DateTime, Enum as SQLAlchemyEnum, ForeignKey, String, Text, UUID
from sqlalchemy.orm import relationship

from app.core.database import Base

class ArticleStatus(enum.Enum):
    draft = "draft"
    published = "published"
    archived = "archived"

class Article(Base):
    __tablename__ = "articles"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    title = Column(String(255), nullable=False)
    content = Column(Text, nullable=False)
    author_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False, index=True)
    status = Column(SQLAlchemyEnum(ArticleStatus), nullable=False, default=ArticleStatus.draft)

    created_at = Column(DateTime(timezone=True), nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime(timezone=True), nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)

    author = relationship("User")

    def __repr__(self):
        return f"<Article(id={self.id}, title='{self.title}')>"