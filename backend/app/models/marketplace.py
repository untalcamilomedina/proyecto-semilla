"""
Marketplace models for MCP modules
Extends the module system with marketplace functionality including reviews, ratings, and categories
"""

from datetime import datetime
from typing import List, Optional, Dict, Any
from uuid import uuid4

from sqlalchemy import Boolean, Column, DateTime, Integer, String, Text, UUID, ForeignKey, Float, JSON
from sqlalchemy.orm import relationship

from app.core.database import Base


class ModuleCategory(Base):
    """
    Categories for organizing modules in the marketplace
    """
    __tablename__ = "module_categories"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    name = Column(String(100), nullable=False, unique=True)
    display_name = Column(String(100), nullable=False)
    description = Column(Text, nullable=True)
    icon = Column(String(50), nullable=True)  # Icon identifier (emoji or icon name)
    color = Column(String(7), nullable=True)  # Hex color code
    parent_id = Column(UUID(as_uuid=True), ForeignKey("module_categories.id"), nullable=True)

    # Hierarchy
    parent = relationship("ModuleCategory", remote_side=[id], backref="subcategories")

    # Metadata
    is_active = Column(Boolean, nullable=False, default=True)
    sort_order = Column(Integer, nullable=False, default=0)

    # Timestamps
    created_at = Column(DateTime(timezone=True), nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime(timezone=True), nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self):
        return f"<ModuleCategory(id={self.id}, name='{self.name}')>"


class ModuleMarketplaceEntry(Base):
    """
    Marketplace entry for modules available in the public catalog
    """
    __tablename__ = "module_marketplace_entries"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    module_registry_id = Column(UUID(as_uuid=True), ForeignKey("module_registry.id"), nullable=False, index=True)

    # Marketplace metadata
    category_id = Column(UUID(as_uuid=True), ForeignKey("module_categories.id"), nullable=False)
    tags = Column(JSON, nullable=False, default=list)  # List of tags
    screenshots = Column(JSON, nullable=False, default=list)  # List of screenshot URLs
    demo_url = Column(String(500), nullable=True)
    documentation_url = Column(String(500), nullable=True)
    support_email = Column(String(255), nullable=True)
    repository_url = Column(String(500), nullable=True)

    # Pricing and licensing
    pricing_model = Column(String(50), nullable=False, default="free")  # free, freemium, paid, subscription
    price = Column(Float, nullable=True)  # Price in USD, null for free
    currency = Column(String(3), nullable=False, default="USD")
    license_type = Column(String(100), nullable=True)  # MIT, GPL, Commercial, etc.

    # Marketplace status
    is_featured = Column(Boolean, nullable=False, default=False)
    is_verified = Column(Boolean, nullable=False, default=False)  # Verified by platform
    is_deprecated = Column(Boolean, nullable=False, default=False)
    moderation_status = Column(String(50), nullable=False, default="pending")  # pending, approved, rejected

    # Statistics
    total_downloads = Column(Integer, nullable=False, default=0)
    total_ratings = Column(Integer, nullable=False, default=0)
    average_rating = Column(Float, nullable=False, default=0.0)
    total_reviews = Column(Integer, nullable=False, default=0)

    # Publisher information
    publisher_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)  # User who published
    publisher_name = Column(String(255), nullable=False)
    publisher_email = Column(String(255), nullable=False)

    # Timestamps
    published_at = Column(DateTime(timezone=True), nullable=True)
    last_updated = Column(DateTime(timezone=True), nullable=False, default=datetime.utcnow)
    created_at = Column(DateTime(timezone=True), nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime(timezone=True), nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    category = relationship("ModuleCategory")
    module_registry = relationship("ModuleRegistry", back_populates="marketplace_entry")
    reviews = relationship("ModuleReview", back_populates="marketplace_entry", cascade="all, delete-orphan")
    ratings = relationship("ModuleRating", back_populates="marketplace_entry", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<ModuleMarketplaceEntry(id={self.id}, module_registry_id={self.module_registry_id})>"


class ModuleReview(Base):
    """
    User reviews for marketplace modules
    """
    __tablename__ = "module_reviews"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    marketplace_entry_id = Column(UUID(as_uuid=True), ForeignKey("module_marketplace_entries.id"), nullable=False, index=True)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False, index=True)
    tenant_id = Column(UUID(as_uuid=True), ForeignKey("tenants.id"), nullable=True, index=True)  # Optional tenant context

    # Review content
    title = Column(String(200), nullable=False)
    content = Column(Text, nullable=False)
    pros = Column(JSON, nullable=False, default=list)  # List of positive points
    cons = Column(JSON, nullable=False, default=list)  # List of negative points

    # Rating (1-5 stars, separate from ModuleRating for detailed reviews)
    rating = Column(Integer, nullable=False)

    # Review metadata
    is_verified_purchase = Column(Boolean, nullable=False, default=False)  # User has installed this module
    is_featured = Column(Boolean, nullable=False, default=False)  # Featured review
    helpful_votes = Column(Integer, nullable=False, default=0)
    total_votes = Column(Integer, nullable=False, default=0)

    # Moderation
    moderation_status = Column(String(50), nullable=False, default="approved")  # approved, pending, rejected
    moderated_by = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)
    moderated_at = Column(DateTime(timezone=True), nullable=True)

    # Timestamps
    created_at = Column(DateTime(timezone=True), nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime(timezone=True), nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    marketplace_entry = relationship("ModuleMarketplaceEntry", back_populates="reviews")
    user = relationship("User")
    tenant = relationship("Tenant")

    def __repr__(self):
        return f"<ModuleReview(id={self.id}, marketplace_entry_id={self.marketplace_entry_id}, rating={self.rating})>"


class ModuleRating(Base):
    """
    Simple star ratings for modules (separate from detailed reviews)
    """
    __tablename__ = "module_ratings"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    marketplace_entry_id = Column(UUID(as_uuid=True), ForeignKey("module_marketplace_entries.id"), nullable=False, index=True)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False, index=True)
    tenant_id = Column(UUID(as_uuid=True), ForeignKey("tenants.id"), nullable=True, index=True)

    # Rating
    rating = Column(Integer, nullable=False)  # 1-5 stars

    # Metadata
    is_verified_purchase = Column(Boolean, nullable=False, default=False)

    # Timestamps
    created_at = Column(DateTime(timezone=True), nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime(timezone=True), nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    marketplace_entry = relationship("ModuleMarketplaceEntry", back_populates="ratings")
    user = relationship("User")
    tenant = relationship("Tenant")

    def __repr__(self):
        return f"<ModuleRating(id={self.id}, marketplace_entry_id={self.marketplace_entry_id}, rating={self.rating})>"


class ModuleDownload(Base):
    """
    Track module downloads for analytics
    """
    __tablename__ = "module_downloads"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    marketplace_entry_id = Column(UUID(as_uuid=True), ForeignKey("module_marketplace_entries.id"), nullable=False, index=True)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True, index=True)  # Anonymous downloads allowed
    tenant_id = Column(UUID(as_uuid=True), ForeignKey("tenants.id"), nullable=True, index=True)

    # Download info
    version = Column(String(50), nullable=False)
    ip_address = Column(String(45), nullable=True)  # IPv4/IPv6
    user_agent = Column(Text, nullable=True)

    # Metadata
    download_source = Column(String(50), nullable=False, default="marketplace")  # marketplace, api, direct

    # Timestamps
    created_at = Column(DateTime(timezone=True), nullable=False, default=datetime.utcnow)

    # Relationships
    marketplace_entry = relationship("ModuleMarketplaceEntry")
    user = relationship("User")
    tenant = relationship("Tenant")

    def __repr__(self):
        return f"<ModuleDownload(id={self.id}, marketplace_entry_id={self.marketplace_entry_id}, version='{self.version}')>"


class ModuleUpdate(Base):
    """
    Track module update notifications and installations
    """
    __tablename__ = "module_updates"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    module_id = Column(UUID(as_uuid=True), ForeignKey("modules.id"), nullable=False, index=True)
    tenant_id = Column(UUID(as_uuid=True), ForeignKey("tenants.id"), nullable=False, index=True)

    # Update info
    current_version = Column(String(50), nullable=False)
    available_version = Column(String(50), nullable=False)
    update_type = Column(String(50), nullable=False, default="minor")  # major, minor, patch, security

    # Update status
    is_notified = Column(Boolean, nullable=False, default=False)
    is_installed = Column(Boolean, nullable=False, default=False)
    installed_at = Column(DateTime(timezone=True), nullable=True)

    # Update metadata
    changelog = Column(Text, nullable=True)
    breaking_changes = Column(Boolean, nullable=False, default=False)
    requires_restart = Column(Boolean, nullable=False, default=False)

    # Timestamps
    notified_at = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime(timezone=True), nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    module = relationship("Module")
    tenant = relationship("Tenant")

    def __repr__(self):
        return f"<ModuleUpdate(id={self.id}, module_id={self.module_id}, current='{self.current_version}', available='{self.available_version}')>"


class ModuleLicense(Base):
    """
    License management for paid modules
    """
    __tablename__ = "module_licenses"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    marketplace_entry_id = Column(UUID(as_uuid=True), ForeignKey("module_marketplace_entries.id"), nullable=False, index=True)
    tenant_id = Column(UUID(as_uuid=True), ForeignKey("tenants.id"), nullable=False, index=True)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False, index=True)

    # License info
    license_key = Column(String(255), nullable=False, unique=True)
    license_type = Column(String(50), nullable=False)  # perpetual, subscription, trial
    max_users = Column(Integer, nullable=True)  # Maximum users allowed
    max_tenants = Column(Integer, nullable=True)  # Maximum tenants allowed

    # Validity
    is_active = Column(Boolean, nullable=False, default=True)
    expires_at = Column(DateTime(timezone=True), nullable=True)
    auto_renew = Column(Boolean, nullable=False, default=False)

    # Payment info
    purchase_price = Column(Float, nullable=False)
    currency = Column(String(3), nullable=False, default="USD")
    payment_method = Column(String(50), nullable=True)
    transaction_id = Column(String(255), nullable=True)

    # Timestamps
    purchased_at = Column(DateTime(timezone=True), nullable=False, default=datetime.utcnow)
    created_at = Column(DateTime(timezone=True), nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime(timezone=True), nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    marketplace_entry = relationship("ModuleMarketplaceEntry")
    tenant = relationship("Tenant")
    user = relationship("User")

    def __repr__(self):
        return f"<ModuleLicense(id={self.id}, marketplace_entry_id={self.marketplace_entry_id}, license_key='{self.license_key}')>"


# Update existing ModuleRegistry to include marketplace relationship
# This would be done via migration, but we add the relationship here for clarity
# ModuleRegistry.marketplace_entry = relationship("ModuleMarketplaceEntry", back_populates="module_registry", uselist=False)