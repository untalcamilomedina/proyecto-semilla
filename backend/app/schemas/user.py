"""
Pydantic schemas for user management
"""

from typing import List, Optional
from uuid import UUID
from pydantic import BaseModel, EmailStr
from datetime import datetime

# Base User Schema
class UserBase(BaseModel):
    email: EmailStr
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    is_active: bool = True

# Schema for creating a user
class UserCreate(UserBase):
    password: str
    tenant_id: UUID
    role_ids: List[UUID] = []

# Schema for updating a user
class UserUpdate(BaseModel):
    email: Optional[EmailStr] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    is_active: Optional[bool] = None
    role_ids: Optional[List[UUID]] = None

# Schema for user response
class UserResponse(UserBase):
    id: UUID
    tenant_id: UUID
    full_name: Optional[str] = None
    is_verified: bool
    role_ids: List[UUID] = []
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True