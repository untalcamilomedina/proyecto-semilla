"""
Module models for MCP (Model Context Protocol) system
"""

from datetime import datetime
from typing import List, Optional
from uuid import uuid4

from sqlalchemy import Boolean, Column, DateTime, Integer, String, Text, UUID, ForeignKey, JSON
from sqlalchemy.orm import relationship

from app.core.database import Base


class Module(Base):
    """
    Module model representing MCP modules in the system
    """
    __tablename__ = "modules"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    tenant_id = Column(UUID(as_uuid=True), ForeignKey("tenants.id"), nullable=False, index=True)

    # Module metadata
    name = Column(String(255), nullable=False, index=True)
    display_name = Column(String(255), nullable=False)
    version = Column(String(50), nullable=False)
    description = Column(Text, nullable=True)
    author = Column(String(255), nullable=True)
    homepage = Column(String(500), nullable=True)
    repository = Column(String(500), nullable=True)

    # Module status
    status = Column(String(50), nullable=False, default="inactive")  # inactive, installing, active, error
    is_system = Column(Boolean, nullable=False, default=False)  # System modules cannot be uninstalled

    # Module configuration
    config_schema = Column(JSON, nullable=True)  # JSON schema for configuration
    default_config = Column(JSON, nullable=True)  # Default configuration values

    # Dependencies and compatibility
    dependencies = Column(JSON, nullable=True)  # List of required dependencies
    min_core_version = Column(String(50), nullable=True)  # Minimum core version required
    max_core_version = Column(String(50), nullable=True)  # Maximum core version supported

    # Module files and paths
    module_path = Column(String(500), nullable=True)  # Path to module files
    entry_point = Column(String(255), nullable=True)  # Main entry point file

    # Activity tracking
    installed_at = Column(DateTime(timezone=True), nullable=True)
    activated_at = Column(DateTime(timezone=True), nullable=True)
    last_used_at = Column(DateTime(timezone=True), nullable=True)

    # Timestamps
    created_at = Column(DateTime(timezone=True), nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime(timezone=True), nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    tenant = relationship("Tenant", back_populates="modules")
    configurations = relationship("ModuleConfiguration", back_populates="module", cascade="all, delete-orphan")
    versions = relationship("ModuleVersion", back_populates="module", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Module(id={self.id}, name='{self.name}', version='{self.version}', status='{self.status}')>"


class ModuleConfiguration(Base):
    """
    Module configuration per tenant
    """
    __tablename__ = "module_configurations"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    module_id = Column(UUID(as_uuid=True), ForeignKey("modules.id"), nullable=False, index=True)
    tenant_id = Column(UUID(as_uuid=True), ForeignKey("tenants.id"), nullable=False, index=True)

    # Configuration data
    config_data = Column(JSON, nullable=False, default=dict)  # Configuration values
    is_active = Column(Boolean, nullable=False, default=True)

    # Timestamps
    created_at = Column(DateTime(timezone=True), nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime(timezone=True), nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    module = relationship("Module", back_populates="configurations")
    tenant = relationship("Tenant", back_populates="module_configurations")

    def __repr__(self):
        return f"<ModuleConfiguration(id={self.id}, module_id={self.module_id}, tenant_id={self.tenant_id})>"


class ModuleVersion(Base):
    """
    Module version history
    """
    __tablename__ = "module_versions"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    module_id = Column(UUID(as_uuid=True), ForeignKey("modules.id"), nullable=False, index=True)

    # Version information
    version = Column(String(50), nullable=False)
    changelog = Column(Text, nullable=True)
    download_url = Column(String(500), nullable=True)
    checksum = Column(String(128), nullable=True)  # SHA256 checksum

    # Version status
    is_available = Column(Boolean, nullable=False, default=True)
    is_compatible = Column(Boolean, nullable=False, default=True)

    # Timestamps
    released_at = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), nullable=False, default=datetime.utcnow)

    # Relationships
    module = relationship("Module", back_populates="versions")

    def __repr__(self):
        return f"<ModuleVersion(id={self.id}, module_id={self.module_id}, version='{self.version}')>"


class ModuleRegistry(Base):
    """
    Registry of available modules for discovery
    """
    __tablename__ = "module_registry"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)

    # Module metadata
    name = Column(String(255), nullable=False, unique=True, index=True)
    display_name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    author = Column(String(255), nullable=True)
    homepage = Column(String(500), nullable=True)
    repository = Column(String(500), nullable=True)

    # Latest version info
    latest_version = Column(String(50), nullable=False)
    total_downloads = Column(Integer, nullable=False, default=0)

    # Registry metadata
    registry_url = Column(String(500), nullable=True)  # URL of the registry
    is_official = Column(Boolean, nullable=False, default=False)

    # Timestamps
    last_updated = Column(DateTime(timezone=True), nullable=False, default=datetime.utcnow)
    created_at = Column(DateTime(timezone=True), nullable=False, default=datetime.utcnow)

    def __repr__(self):
        return f"<ModuleRegistry(id={self.id}, name='{self.name}', latest_version='{self.latest_version}')>"