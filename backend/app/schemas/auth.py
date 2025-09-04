"""
Pydantic schemas for authentication
"""

from typing import Optional
from pydantic import BaseModel, EmailStr


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