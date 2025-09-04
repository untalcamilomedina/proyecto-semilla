"""
Pydantic schemas for role management
"""

from typing import List, Optional
from uuid import UUID
from datetime import datetime

from pydantic import BaseModel


class RoleBase(BaseModel):
    """
    Base role schema
    """
    name: str
    description: Optional[str] = None
    permissions: List[str] = []
    color: str = "#ffffff"
    hierarchy_level: int = 0
    is_default: bool = False
    is_active: bool = True


class RoleCreate(RoleBase):
    """
    Create role request
    """
    pass


class RoleUpdate(BaseModel):
    """
    Update role request
    """
    name: Optional[str] = None
    description: Optional[str] = None
    permissions: Optional[List[str]] = None
    color: Optional[str] = None
    hierarchy_level: Optional[int] = None
    is_default: Optional[bool] = None
    is_active: Optional[bool] = None


class RoleResponse(RoleBase):
    """
    Role response model
    """
    id: UUID
    tenant_id: UUID
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class UserRoleAssignment(BaseModel):
    """
    User role assignment request
    """
    user_id: UUID
    role_id: UUID


class UserRoleResponse(BaseModel):
    """
    User role assignment response
    """
    user_id: UUID
    role_id: UUID
    role_name: str
    assigned_at: datetime

    class Config:
        from_attributes = True