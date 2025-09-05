"""
Proyecto Semilla SDK Models - Type-safe data structures
"""

from pydantic import BaseModel, Field, validator
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum


class Tenant(BaseModel):
    """Tenant model for multi-tenant operations"""
    id: str
    name: str = Field(..., min_length=1, max_length=100)
    slug: str = Field(..., regex=r'^[a-z0-9-]+$', min_length=1, max_length=50)
    settings: Dict[str, Any] = Field(default_factory=dict)
    is_active: bool = True
    created_at: datetime
    updated_at: datetime

    @validator('slug')
    def slug_must_be_valid(cls, v):
        if not v.replace('-', '').replace('_', '').isalnum():
            raise ValueError('Slug must contain only letters, numbers, hyphens, and underscores')
        return v


class User(BaseModel):
    """User model with tenant association"""
    id: str
    tenant_id: str
    email: str = Field(..., regex=r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$')
    first_name: Optional[str] = Field(None, max_length=50)
    last_name: Optional[str] = Field(None, max_length=50)
    is_active: bool = True
    is_verified: bool = False
    role_ids: List[str] = Field(default_factory=list)
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    @property
    def full_name(self) -> str:
        """Get user's full name"""
        if self.first_name and self.last_name:
            return f"{self.first_name} {self.last_name}"
        return self.first_name or self.last_name or self.email


class ModuleCategory(str, Enum):
    """Available module categories"""
    CMS = "cms"
    INVENTORY = "inventory"
    CRM = "crm"
    FINANCE = "finance"
    ANALYTICS = "analytics"
    COMMUNICATION = "communication"
    ECOMMERCE = "ecommerce"
    CUSTOM = "custom"


class EntityField(BaseModel):
    """Field definition for module entities"""
    name: str = Field(..., regex=r'^[a-z_][a-z0-9_]*$')
    type: str = Field(..., regex=r'^(string|text|integer|float|boolean|date|datetime|json)$')
    required: bool = False
    default: Optional[Any] = None
    max_length: Optional[int] = None
    choices: Optional[List[str]] = None
    description: Optional[str] = None


class ModuleEntity(BaseModel):
    """Entity definition for modules"""
    name: str = Field(..., regex=r'^[A-Z][a-zA-Z0-9]*$')
    description: Optional[str] = None
    fields: List[EntityField] = Field(default_factory=list)

    @validator('fields')
    def validate_fields(cls, v):
        if not v:
            raise ValueError('Entity must have at least one field')
        field_names = [f.name for f in v]
        if len(field_names) != len(set(field_names)):
            raise ValueError('Field names must be unique')
        return v


class APIEndpoint(BaseModel):
    """API endpoint definition"""
    path: str = Field(..., regex=r'^/')
    method: str = Field(..., regex=r'^(GET|POST|PUT|DELETE|PATCH)$')
    description: Optional[str] = None
    parameters: List[Dict[str, Any]] = Field(default_factory=list)
    responses: Dict[str, Dict[str, Any]] = Field(default_factory=dict)


class UIComponent(str, Enum):
    """Available UI components"""
    DASHBOARD = "dashboard"
    LIST_VIEW = "list_view"
    FORM = "form"
    DETAIL_VIEW = "detail_view"
    NAVIGATION = "navigation"
    SIDEBAR = "sidebar"


class ModuleSpec(BaseModel):
    """Complete module specification for generation"""
    name: str = Field(..., regex=r'^[a-z_][a-z0-9_]*$', min_length=1, max_length=50)
    display_name: str = Field(..., min_length=1, max_length=100)
    description: str = Field(..., min_length=10, max_length=500)
    version: str = Field(default="1.0.0", regex=r'^\d+\.\d+\.\d+$')
    category: ModuleCategory
    features: List[str] = Field(default_factory=list, max_items=20)
    entities: List[ModuleEntity] = Field(default_factory=list, max_items=10)
    apis: List[APIEndpoint] = Field(default_factory=list, max_items=20)
    ui_components: List[UIComponent] = Field(default_factory=list, max_items=10)
    dependencies: List[str] = Field(default_factory=list)
    tags: List[str] = Field(default_factory=list, max_items=10)

    @validator('features')
    def validate_features(cls, v):
        if len(set(v)) != len(v):
            raise ValueError('Features must be unique')
        return v

    @validator('tags')
    def validate_tags(cls, v):
        if len(set(v)) != len(v):
            raise ValueError('Tags must be unique')
        return v


class ModuleStatus(BaseModel):
    """Status of a generated module"""
    name: str
    status: str = Field(..., regex=r'^(generating|ready|deployed|error)$')
    description: str
    files_count: Optional[int] = None
    api_endpoints_count: Optional[int] = None
    ui_components_count: Optional[int] = None
    created_at: datetime
    updated_at: datetime
    error_message: Optional[str] = None


class GenerationResult(BaseModel):
    """Result of module generation"""
    module_name: str
    success: bool
    files_created: int
    apis_generated: int
    ui_components_created: int
    documentation_updated: bool
    execution_time_seconds: float
    generated_files: List[str] = Field(default_factory=list)
    warnings: List[str] = Field(default_factory=list)
    errors: List[str] = Field(default_factory=list)


class APIResponse(BaseModel):
    """Standard API response wrapper"""
    success: bool
    data: Optional[Any] = None
    message: Optional[str] = None
    errors: Optional[List[str]] = Field(default_factory=list)
    meta: Optional[Dict[str, Any]] = Field(default_factory=dict)


class AuthTokens(BaseModel):
    """Authentication tokens response"""
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int
    user: User


class TenantCreate(BaseModel):
    """Data for creating a new tenant"""
    name: str = Field(..., min_length=1, max_length=100)
    slug: str = Field(..., regex=r'^[a-z0-9-]+$', min_length=1, max_length=50)
    settings: Optional[Dict[str, Any]] = Field(default_factory=dict)


class UserCreate(BaseModel):
    """Data for creating a new user"""
    email: str = Field(..., regex=r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$')
    password: str = Field(..., min_length=8, max_length=128)
    first_name: Optional[str] = Field(None, max_length=50)
    last_name: Optional[str] = Field(None, max_length=50)
    tenant_id: str


class LoginRequest(BaseModel):
    """Login request data"""
    email: str = Field(..., regex=r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$')
    password: str = Field(..., min_length=1)


class ModuleGenerationRequest(BaseModel):
    """Request to generate a new module"""
    spec: ModuleSpec
    auto_deploy: bool = False
    update_documentation: bool = True
    generate_tests: bool = True