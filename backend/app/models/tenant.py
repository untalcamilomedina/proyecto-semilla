"""
Tenant model for multi-tenant architecture
"""

from datetime import datetime
from typing import Optional
from uuid import uuid4

from sqlalchemy import Boolean, Column, DateTime, String, Text, UUID
from sqlalchemy.orm import relationship

from app.core.database import Base


class Tenant(Base):
    """
    Tenant model representing organizations/companies in the multi-tenant system
    """
    __tablename__ = "tenants"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    name = Column(String(100), nullable=False, index=True)
    slug = Column(String(50), nullable=False, unique=True, index=True)
    description = Column(Text, nullable=True)

    # Parent tenant for hierarchical structure (sub-tenants)
    parent_tenant_id = Column(UUID(as_uuid=True), nullable=True)

    # Configuration and settings
    settings = Column(Text, nullable=True, default="{}")  # JSON string

    # Status
    is_active = Column(Boolean, nullable=False, default=True)

    # Timestamps
    created_at = Column(DateTime(timezone=True), nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime(timezone=True), nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    users = relationship("User", back_populates="tenant", cascade="all, delete-orphan")
    roles = relationship("Role", back_populates="tenant", cascade="all, delete-orphan")
    modules = relationship("Module", back_populates="tenant", cascade="all, delete-orphan")
    module_configurations = relationship("ModuleConfiguration", back_populates="tenant", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Tenant(id={self.id}, name='{self.name}', slug='{self.slug}')>"