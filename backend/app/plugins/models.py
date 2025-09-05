"""
Plugin System Models for Proyecto Semilla
Extensible plugin architecture with isolated testing environments
"""

from datetime import datetime
from typing import Dict, List, Any, Optional, Union
from dataclasses import dataclass, asdict
from enum import Enum
import json
import uuid

from sqlalchemy import Column, Integer, String, DateTime, Text, Float, Boolean, JSON, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

Base = declarative_base()

class PluginStatus(Enum):
    """Plugin lifecycle status"""
    DEVELOPMENT = "development"
    TESTING = "testing"
    PUBLISHED = "published"
    DEPRECATED = "deprecated"
    DISABLED = "disabled"

class PluginType(Enum):
    """Types of plugins"""
    MODULE = "module"  # Business logic modules
    INTEGRATION = "integration"  # External service integrations
    THEME = "theme"  # UI/UX themes
    WORKFLOW = "workflow"  # Business process automation
    ANALYTICS = "analytics"  # Analytics and reporting
    SECURITY = "security"  # Security enhancements

class EnvironmentType(Enum):
    """Plugin environment types"""
    PRODUCTION = "production"
    STAGING = "staging"
    DEVELOPMENT = "development"
    TESTING = "testing"

@dataclass
class PluginManifest:
    """Plugin manifest configuration"""
    id: str
    name: str
    version: str
    description: str
    author: str
    type: PluginType
    dependencies: List[str] = None
    permissions: List[str] = None
    config_schema: Dict[str, Any] = None
    entry_points: Dict[str, str] = None
    metadata: Dict[str, Any] = None

    def __post_init__(self):
        if not self.id:
            self.id = str(uuid.uuid4())
        if self.dependencies is None:
            self.dependencies = []
        if self.permissions is None:
            self.permissions = []
        if self.config_schema is None:
            self.config_schema = {}
        if self.entry_points is None:
            self.entry_points = {}
        if self.metadata is None:
            self.metadata = {}

@dataclass
class PluginInstance:
    """Plugin instance configuration"""
    id: str
    plugin_id: str
    tenant_id: Optional[str]
    environment: EnvironmentType
    config: Dict[str, Any]
    enabled: bool = True
    installed_at: datetime = None
    last_updated: datetime = None

    def __post_init__(self):
        if not self.id:
            self.id = str(uuid.uuid4())
        if self.installed_at is None:
            self.installed_at = datetime.utcnow()
        if self.last_updated is None:
            self.last_updated = datetime.utcnow()

@dataclass
class PluginEnvironment:
    """Isolated plugin testing environment"""
    id: str
    name: str
    tenant_id: str
    creator_id: str
    plugin_id: str
    base_environment: EnvironmentType
    config: Dict[str, Any]
    status: str = "active"
    created_at: datetime = None
    expires_at: Optional[datetime] = None

    def __post_init__(self):
        if not self.id:
            self.id = str(uuid.uuid4())
        if self.created_at is None:
            self.created_at = datetime.utcnow()

@dataclass
class PluginReview:
    """Plugin review and rating"""
    id: str
    plugin_id: str
    user_id: str
    tenant_id: Optional[str]
    rating: int  # 1-5 stars
    title: str
    comment: str
    pros: List[str] = None
    cons: List[str] = None
    verified: bool = False
    created_at: datetime = None

    def __post_init__(self):
        if not self.id:
            self.id = str(uuid.uuid4())
        if self.pros is None:
            self.pros = []
        if self.cons is None:
            self.cons = []
        if self.created_at is None:
            self.created_at = datetime.utcnow()

@dataclass
class PluginAnalytics:
    """Plugin usage analytics"""
    plugin_id: str
    tenant_id: Optional[str]
    environment: EnvironmentType
    metric_name: str
    value: Union[int, float]
    timestamp: datetime
    metadata: Dict[str, Any] = None

    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}

# SQLAlchemy Models

class PluginModel(Base):
    """Database model for plugins"""
    __tablename__ = "plugins"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    name = Column(String(100), nullable=False)
    version = Column(String(20), nullable=False)
    description = Column(Text)
    author = Column(String(100), nullable=False)
    type = Column(String(20), nullable=False)
    status = Column(String(20), nullable=False, default=PluginStatus.DEVELOPMENT.value)
    manifest = Column(JSON, nullable=False)
    downloads = Column(Integer, default=0)
    rating = Column(Float, default=0.0)
    review_count = Column(Integer, default=0)

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class PluginInstanceModel(Base):
    """Database model for plugin instances"""
    __tablename__ = "plugin_instances"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    plugin_id = Column(String(36), ForeignKey("plugins.id"), nullable=False)
    tenant_id = Column(String(36), index=True)
    environment = Column(String(20), nullable=False)
    config = Column(JSON, nullable=False)
    enabled = Column(Boolean, default=True)

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    plugin = relationship("PluginModel")

class PluginEnvironmentModel(Base):
    """Database model for plugin testing environments"""
    __tablename__ = "plugin_environments"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    name = Column(String(100), nullable=False)
    tenant_id = Column(String(36), nullable=False, index=True)
    creator_id = Column(String(36), nullable=False)
    plugin_id = Column(String(36), ForeignKey("plugins.id"), nullable=False)
    base_environment = Column(String(20), nullable=False)
    config = Column(JSON, nullable=False)
    status = Column(String(20), nullable=False, default="active")
    expires_at = Column(DateTime)

    created_at = Column(DateTime, default=datetime.utcnow)

    plugin = relationship("PluginModel")

class PluginReviewModel(Base):
    """Database model for plugin reviews"""
    __tablename__ = "plugin_reviews"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    plugin_id = Column(String(36), ForeignKey("plugins.id"), nullable=False)
    user_id = Column(String(36), nullable=False)
    tenant_id = Column(String(36), index=True)
    rating = Column(Integer, nullable=False)
    title = Column(String(200), nullable=False)
    comment = Column(Text)
    pros = Column(JSON)
    cons = Column(JSON)
    verified = Column(Boolean, default=False)

    created_at = Column(DateTime, default=datetime.utcnow)

    plugin = relationship("PluginModel")

class PluginAnalyticsModel(Base):
    """Database model for plugin analytics"""
    __tablename__ = "plugin_analytics"

    id = Column(Integer, primary_key=True)
    plugin_id = Column(String(36), nullable=False, index=True)
    tenant_id = Column(String(36), index=True)
    environment = Column(String(20), nullable=False)
    metric_name = Column(String(100), nullable=False)
    value = Column(Float, nullable=False)
    timestamp = Column(DateTime, nullable=False, index=True)
    metadata = Column(JSON)

    created_at = Column(DateTime, default=datetime.utcnow)

# Plugin Registry and Marketplace Models

@dataclass
class PluginCategory:
    """Plugin marketplace category"""
    id: str
    name: str
    description: str
    icon: str
    parent_id: Optional[str] = None
    subcategories: List['PluginCategory'] = None

    def __post_init__(self):
        if not self.id:
            self.id = str(uuid.uuid4())
        if self.subcategories is None:
            self.subcategories = []

@dataclass
class PluginMarketplaceEntry:
    """Plugin marketplace entry"""
    id: str
    plugin_id: str
    category_id: str
    tags: List[str]
    screenshots: List[str] = None
    demo_url: Optional[str] = None
    documentation_url: Optional[str] = None
    support_email: Optional[str] = None
    pricing: Dict[str, Any] = None
    featured: bool = False

    def __post_init__(self):
        if not self.id:
            self.id = str(uuid.uuid4())
        if self.screenshots is None:
            self.screenshots = []
        if self.pricing is None:
            self.pricing = {"type": "free"}

@dataclass
class PluginInstallation:
    """Plugin installation record"""
    id: str
    plugin_id: str
    tenant_id: str
    environment: EnvironmentType
    installed_by: str
    status: str = "completed"
    version: str = ""
    config_backup: Dict[str, Any] = None
    installed_at: datetime = None

    def __post_init__(self):
        if not self.id:
            self.id = str(uuid.uuid4())
        if self.config_backup is None:
            self.config_backup = {}
        if self.installed_at is None:
            self.installed_at = datetime.utcnow()

# Plugin Development Environment Configuration

@dataclass
class DevelopmentEnvironment:
    """Plugin development environment configuration"""
    id: str
    name: str
    tenant_id: str
    creator_id: str
    plugin_id: str
    database_url: str
    redis_url: str
    api_base_url: str
    environment_variables: Dict[str, str] = None
    resource_limits: Dict[str, Any] = None
    auto_cleanup: bool = True
    cleanup_after_hours: int = 24

    def __post_init__(self):
        if not self.id:
            self.id = str(uuid.uuid4())
        if self.environment_variables is None:
            self.environment_variables = {}
        if self.resource_limits is None:
            self.resource_limits = {
                "max_cpu": 0.5,
                "max_memory": "512MB",
                "max_storage": "1GB"
            }

# Utility functions

def create_plugin_manifest(name: str, version: str, description: str, author: str,
                          plugin_type: PluginType, **kwargs) -> PluginManifest:
    """Create a new plugin manifest"""
    return PluginManifest(
        id=str(uuid.uuid4()),
        name=name,
        version=version,
        description=description,
        author=author,
        type=plugin_type,
        **kwargs
    )

def create_plugin_environment(tenant_id: str, creator_id: str, plugin_id: str,
                             name: str, base_environment: EnvironmentType) -> PluginEnvironment:
    """Create a new plugin testing environment"""
    return PluginEnvironment(
        id=str(uuid.uuid4()),
        name=name,
        tenant_id=tenant_id,
        creator_id=creator_id,
        plugin_id=plugin_id,
        base_environment=base_environment,
        config={},
        status="active",
        created_at=datetime.utcnow()
    )

def create_development_environment(tenant_id: str, creator_id: str, plugin_id: str,
                                  name: str) -> DevelopmentEnvironment:
    """Create a new development environment for plugin testing"""
    return DevelopmentEnvironment(
        id=str(uuid.uuid4()),
        name=name,
        tenant_id=tenant_id,
        creator_id=creator_id,
        plugin_id=plugin_id,
        database_url=f"postgresql://test_{tenant_id}_{plugin_id}@localhost:5432/test_{plugin_id}",
        redis_url="redis://localhost:6379/1",
        api_base_url=f"http://localhost:8000/api/v1/tenants/{tenant_id}/plugins/{plugin_id}"
    )

# Plugin system configuration
PLUGIN_SYSTEM_CONFIG = {
    "max_environments_per_tenant": 5,
    "environment_lifetime_hours": 24,
    "max_plugins_per_tenant": 50,
    "auto_cleanup_enabled": True,
    "development_mode_enabled": True,
    "marketplace_enabled": True,
    "review_system_enabled": True
}