"""
Pydantic schemas for authentication
"""

from typing import Optional
from pydantic import BaseModel, EmailStr, field_validator
import re


class Token(BaseModel):
    """
    JWT token response
    """
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class TokenData(BaseModel):
    """
    JWT token payload data
    """
    user_id: Optional[str] = None


class UserLogin(BaseModel):
    """
    User login request
    """
    email: EmailStr
    password: str


class UserRegister(BaseModel):
    """
    User registration request
    """
    email: EmailStr
    password: str
    first_name: str
    last_name: str
    tenant_id: Optional[str] = None  # For existing tenants

    @field_validator('password')
    @classmethod
    def validate_password_strength(cls, v):
        if len(v) < 8:
            raise ValueError('Password must be at least 8 characters long')
        if not re.search(r'[A-Z]', v):
            raise ValueError('Password must contain at least one uppercase letter')
        if not re.search(r'[a-z]', v):
            raise ValueError('Password must contain at least one lowercase letter')
        if not re.search(r'\d', v):
            raise ValueError('Password must contain at least one digit')
        if not re.search(r'[!@#$%^&*(),.?":{}|<>]', v):
            raise ValueError('Password must contain at least one special character')
        return v

    @field_validator('first_name', 'last_name')
    @classmethod
    def validate_name(cls, v):
        if not v or not v.strip():
            raise ValueError('Name cannot be empty')
        if len(v.strip()) < 2:
            raise ValueError('Name must be at least 2 characters long')
        if not re.match(r'^[a-zA-Z\s\-]+$', v):
            raise ValueError('Name can only contain letters, spaces, and hyphens')
        return v.strip()


class UserCreate(BaseModel):
    """
    Create user request (admin)
    """
    email: EmailStr
    password: str
    first_name: str
    last_name: str
    tenant_id: str
    role_ids: Optional[list[str]] = None


class UserUpdate(BaseModel):
    """
    Update user request
    """
    email: Optional[EmailStr] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    is_active: Optional[bool] = None
    role_ids: Optional[list[str]] = None


class UserResponse(BaseModel):
    """
    User response model
    """
    id: str
    email: EmailStr
    first_name: str
    last_name: str
    full_name: str
    is_active: bool
    is_verified: bool
    tenant_id: str
    role_ids: list[str]
    created_at: str
    updated_at: str

    class Config:
        from_attributes = True


class PasswordResetRequest(BaseModel):
    """
    Password reset request
    """
    email: EmailStr


class PasswordReset(BaseModel):
    """
    Password reset with token
    """
    token: str
    new_password: str


class RefreshTokenRequest(BaseModel):
    """
    Refresh token request
    """
    refresh_token: str


class TokenResponse(BaseModel):
    """
    Complete token response with access and refresh tokens
    """
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int  # seconds