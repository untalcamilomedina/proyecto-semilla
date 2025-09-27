"""
Module schemas for API validation and serialization
"""

from datetime import datetime
from typing import Dict, List, Any, Optional
from uuid import UUID

from pydantic import BaseModel, Field, validator


class ModuleBase(BaseModel):
    """Base module schema"""
    name: str = Field(..., min_length=1, max_length=255, description="Module name")
    display_name: str = Field(..., min_length=1, max_length=255, description="Display name")
    version: str = Field(..., min_length=1, max_length=50, description="Module version")
    description: Optional[str] = Field(None, description="Module description")
    author: Optional[str] = Field(None, description="Module author")
    homepage: Optional[str] = Field(None, description="Module homepage URL")
    repository: Optional[str] = Field(None, description="Module repository URL")


class ModuleCreate(ModuleBase):
    """Schema for creating a new module"""
    config_schema: Optional[Dict[str, Any]] = Field(None, description="Configuration schema")
    default_config: Optional[Dict[str, Any]] = Field(None, description="Default configuration")
    dependencies: Optional[List[Dict[str, Any]]] = Field(None, description="Module dependencies")
    min_core_version: Optional[str] = Field(None, description="Minimum core version required")
    max_core_version: Optional[str] = Field(None, description="Maximum core version supported")
    is_system: bool = Field(False, description="Whether this is a system module")


class ModuleUpdate(BaseModel):
    """Schema for updating a module"""
    display_name: Optional[str] = Field(None, description="Display name")
    description: Optional[str] = Field(None, description="Module description")
    author: Optional[str] = Field(None, description="Module author")
    homepage: Optional[str] = Field(None, description="Module homepage URL")
    repository: Optional[str] = Field(None, description="Module repository URL")
    config_schema: Optional[Dict[str, Any]] = Field(None, description="Configuration schema")
    default_config: Optional[Dict[str, Any]] = Field(None, description="Default configuration")
    dependencies: Optional[List[Dict[str, Any]]] = Field(None, description="Module dependencies")
    min_core_version: Optional[str] = Field(None, description="Minimum core version required")
    max_core_version: Optional[str] = Field(None, description="Maximum core version supported")


class ModuleResponse(ModuleBase):
    """Schema for module response"""
    id: UUID
    tenant_id: UUID
    status: str
    is_system: bool
    config_schema: Optional[Dict[str, Any]]
    default_config: Optional[Dict[str, Any]]
    dependencies: Optional[List[Dict[str, Any]]]
    min_core_version: Optional[str]
    max_core_version: Optional[str]
    installed_at: Optional[datetime]
    activated_at: Optional[datetime]
    last_used_at: Optional[datetime]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class ModuleConfigurationBase(BaseModel):
    """Base module configuration schema"""
    config_data: Dict[str, Any] = Field(..., description="Configuration data")
    is_active: bool = Field(True, description="Whether configuration is active")


class ModuleConfigurationCreate(ModuleConfigurationBase):
    """Schema for creating module configuration"""
    pass


class ModuleConfigurationUpdate(BaseModel):
    """Schema for updating module configuration"""
    config_data: Optional[Dict[str, Any]] = Field(None, description="Configuration data")
    is_active: Optional[bool] = Field(None, description="Whether configuration is active")


class ModuleConfigurationResponse(ModuleConfigurationBase):
    """Schema for module configuration response"""
    id: UUID
    module_id: UUID
    tenant_id: UUID
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class ModuleVersionBase(BaseModel):
    """Base module version schema"""
    version: str = Field(..., description="Version string")
    changelog: Optional[str] = Field(None, description="Version changelog")
    download_url: Optional[str] = Field(None, description="Download URL")
    checksum: Optional[str] = Field(None, description="File checksum")


class ModuleVersionCreate(ModuleVersionBase):
    """Schema for creating module version"""
    pass


class ModuleVersionResponse(ModuleVersionBase):
    """Schema for module version response"""
    id: UUID
    module_id: UUID
    is_available: bool
    is_compatible: bool
    released_at: Optional[datetime]
    created_at: datetime

    class Config:
        from_attributes = True


class ModuleRegistryBase(BaseModel):
    """Base module registry schema"""
    name: str = Field(..., unique=True, description="Module name")
    display_name: str = Field(..., description="Display name")
    description: Optional[str] = Field(None, description="Description")
    author: Optional[str] = Field(None, description="Author")
    homepage: Optional[str] = Field(None, description="Homepage URL")
    repository: Optional[str] = Field(None, description="Repository URL")
    latest_version: str = Field(..., description="Latest version")
    total_downloads: int = Field(0, description="Total downloads")
    is_official: bool = Field(False, description="Whether it's an official module")


class ModuleRegistryCreate(ModuleRegistryBase):
    """Schema for creating registry entry"""
    pass


class ModuleRegistryResponse(ModuleRegistryBase):
    """Schema for registry response"""
    last_updated: datetime
    created_at: datetime

    class Config:
        from_attributes = True


class ModuleInstallRequest(BaseModel):
    """Schema for module installation request"""
    name: str = Field(..., description="Module name")
    version: str = Field(..., description="Module version")
    config: Optional[Dict[str, Any]] = Field(None, description="Initial configuration")


class ModuleActionResponse(BaseModel):
    """Schema for module action responses"""
    success: bool
    message: str
    module: Optional[ModuleResponse] = None
    error: Optional[str] = None


class ModuleHealthResponse(BaseModel):
    """Schema for module health check response"""
    status: str
    name: str
    version: str
    last_used: Optional[str]
    config_valid: bool
    dependencies_satisfied: bool
    details: Optional[Dict[str, Any]] = None


class ModuleDiscoveryResponse(BaseModel):
    """Schema for module discovery response"""
    name: str
    display_name: str
    description: Optional[str]
    latest_version: str
    author: Optional[str]
    total_downloads: int
    is_official: bool
    categories: Optional[List[str]] = None


class ModuleListResponse(BaseModel):
    """Schema for module list response"""
    modules: List[ModuleResponse]
    total: int
    skip: int
    limit: int


class ModuleConfigUpdateRequest(BaseModel):
    """Schema for module configuration update"""
    config: Dict[str, Any] = Field(..., description="New configuration")


class ModuleReloadResponse(BaseModel):
    """Schema for module reload response"""
    success: bool
    message: str
    reloaded_at: datetime
    changes_detected: bool