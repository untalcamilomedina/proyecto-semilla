"""
Pydantic schemas for tenant management
"""

from typing import Optional
from pydantic import BaseModel


class TenantBase(BaseModel):
    """
    Base tenant schema
    """
    name: str
    slug: str
    description: Optional[str] = None
    parent_tenant_id: Optional[str] = None
    settings: Optional[str] = "{}"  # JSON string
    is_active: bool = True


class TenantCreate(TenantBase):
    """
    Create tenant request
    """
    pass


class TenantUpdate(BaseModel):
    """
    Update tenant request
    """
    name: Optional[str] = None
    description: Optional[str] = None
    settings: Optional[str] = None
    is_active: Optional[bool] = None


class TenantResponse(TenantBase):
    """
    Tenant response model
    """
    id: str
    created_at: str
    updated_at: str

    class Config:
        from_attributes = True


class TenantWithUsers(TenantResponse):
    """
    Tenant response with user count
    """
    user_count: int = 0
    role_count: int = 0