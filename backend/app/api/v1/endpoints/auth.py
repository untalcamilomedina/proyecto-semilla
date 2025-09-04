"""
Authentication endpoints
Login, registration, and token management
"""

from datetime import timedelta
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession

from app.core import security
from app.core.database import get_db
from app.schemas.auth import Token, UserLogin, UserRegister, UserResponse
from app.models.user import User
from app.models.tenant import Tenant

router = APIRouter()


@router.post("/login", response_model=Token)
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: AsyncSession = Depends(get_db)
) -> Any:
    """
    OAuth2 compatible token login, get an access token for future requests
    """
    # Find user by email
    user = await db.execute(
        "SELECT * FROM users WHERE email = $1 AND is_active = true",
        (form_data.username,)
    )
    user_data = user.fetchone()

    if not user_data:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Incorrect email or password"
        )

    # Convert to User object (simplified for now)
    user_obj = User(
        id=user_data[0],
        tenant_id=user_data[1],
        email=user_data[2],
        hashed_password=user_data[3],
        first_name=user_data[4],
        last_name=user_data[5],
        is_active=user_data[6],
        is_verified=user_data[7]
    )

    # Verify password
    if not security.verify_password(form_data.password, user_obj.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Incorrect email or password"
        )

    # Create access token
    access_token_expires = timedelta(minutes=security.settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = security.create_access_token(
        subject=user_obj.id, expires_delta=access_token_expires
    )

    return {"access_token": access_token, "token_type": "bearer"}


@router.post("/register", response_model=UserResponse)
async def register(
    user_in: UserRegister,
    db: AsyncSession = Depends(get_db)
) -> Any:
    """
    Register a new user
    """
    # Check if user already exists
    existing_user = await db.execute(
        "SELECT id FROM users WHERE email = $1",
        (user_in.email,)
    )

    if existing_user.fetchone():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User with this email already exists"
        )

    # For now, require tenant_id (will be improved later)
    if not user_in.tenant_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Tenant ID is required for registration"
        )

    # Verify tenant exists
    tenant = await db.get(Tenant, user_in.tenant_id)
    if not tenant:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid tenant ID"
        )

    # Hash password
    hashed_password = security.get_password_hash(user_in.password)

    # Create user
    from uuid import uuid4
    user_id = uuid4()

    await db.execute(
        """
        INSERT INTO users (id, tenant_id, email, hashed_password, first_name, last_name, full_name, is_active, is_verified)
        VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9)
        """,
        (
            user_id,
            user_in.tenant_id,
            user_in.email,
            hashed_password,
            user_in.first_name,
            user_in.last_name,
            f"{user_in.first_name} {user_in.last_name}",
            True,
            False
        )
    )

    await db.commit()

    # Return user data
    return {
        "id": str(user_id),
        "email": user_in.email,
        "first_name": user_in.first_name,
        "last_name": user_in.last_name,
        "full_name": f"{user_in.first_name} {user_in.last_name}",
        "is_active": True,
        "is_verified": False,
        "tenant_id": user_in.tenant_id,
        "role_ids": [],
        "created_at": "2024-01-01T00:00:00Z",  # Placeholder
        "updated_at": "2024-01-01T00:00:00Z"   # Placeholder
    }


@router.post("/refresh-token", response_model=Token)
async def refresh_access_token(
    current_user: User = Depends(security.get_current_user)
) -> Any:
    """
    Refresh access token
    """
    access_token = security.create_user_token(current_user)
    return {"access_token": access_token, "token_type": "bearer"}


@router.get("/me", response_model=UserResponse)
async def read_users_me(
    current_user: User = Depends(security.get_current_user)
) -> Any:
    """
    Get current user information
    """
    return {
        "id": str(current_user.id),
        "email": current_user.email,
        "first_name": current_user.first_name,
        "last_name": current_user.last_name,
        "full_name": current_user.full_name,
        "is_active": current_user.is_active,
        "is_verified": current_user.is_verified,
        "tenant_id": str(current_user.tenant_id),
        "role_ids": [str(role.id) for role in current_user.roles],
        "created_at": current_user.created_at.isoformat(),
        "updated_at": current_user.updated_at.isoformat()
    }