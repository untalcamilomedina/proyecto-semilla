"""
Authentication endpoints
Login, registration, and token management
"""

from datetime import timedelta
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, status, Request
from fastapi.responses import JSONResponse
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from app.core import security
from app.core.database import get_db
from app.core.cookies import get_cookie_manager
from app.schemas.auth import Token, UserLogin, UserRegister, UserResponse, RefreshTokenRequest
from app.models.user import User
from app.models.tenant import Tenant
from app.services.permission_service import PermissionService

router = APIRouter()


@router.get("/test-auth")
async def test_auth_endpoint():
    return {"message": "Auth endpoint is working"}


@router.get("/setup-status")
async def get_setup_status(db: AsyncSession = Depends(get_db)) -> Any:
    """
    Check if the system needs initial setup (no users exist)
    """
    from sqlalchemy import select, func
    user_count_result = await db.execute(select(func.count(User.id)))
    user_count = user_count_result.scalar()

    return {
        "needs_setup": user_count == 0,
        "user_count": user_count,
        "message": "System needs initial setup" if user_count == 0 else "System is already configured"
    }
 
@router.post("/login", response_model=Token)
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: AsyncSession = Depends(get_db)
) -> Any:
    """
    OAuth2 compatible token login, get an access token for future requests
    """
    # Find user by email
    from sqlalchemy import select
    stmt = select(User).where(User.email == form_data.username, User.is_active == True)
    result = await db.execute(stmt)
    user_obj = result.scalar_one_or_none()

    if not user_obj:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Incorrect email or password"
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
        subject=user_obj.id, tenant_id=user_obj.tenant_id, expires_delta=access_token_expires
    )

    # Create refresh token
    refresh_token = security.create_refresh_token(user_obj)

    # Store refresh token in database
    await security.store_refresh_token(
        db,
        user_obj,
        refresh_token,
        user_agent=None,  # Could be extracted from request headers
        ip_address=None   # Could be extracted from request
    )

    # Get tenant name for cookie
    tenant_result = await db.execute(
        text("SELECT name FROM tenants WHERE id = :tenant_id"),
        {"tenant_id": user_obj.tenant_id}
    )
    tenant_name = tenant_result.fetchone()
    tenant_name = tenant_name[0] if tenant_name else "Unknown"

    # Create response with secure cookies
    cookie_manager = get_cookie_manager()
    return cookie_manager.create_login_response(
        access_token=access_token,
        refresh_token=refresh_token,
        tenant_id=str(user_obj.tenant_id),
        tenant_name=tenant_name
    )


@router.post("/register", response_model=UserResponse)
async def register(
    user_data: dict,  # Accept flexible data structure
    db: AsyncSession = Depends(get_db)
) -> Any:
    """
    Register a new user - accepts flexible data structure for frontend compatibility
    """
    # Extract and validate required fields
    email = user_data.get("email")
    password = user_data.get("password")
    nombre_completo = user_data.get("nombre_completo")  # Frontend sends this
    first_name = user_data.get("first_name")  # Alternative format
    last_name = user_data.get("last_name")   # Alternative format

    if not email or not password:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email and password are required"
        )

    # Parse name fields
    if nombre_completo:
        # Split full name into first and last name
        name_parts = nombre_completo.strip().split()
        first_name = name_parts[0] if name_parts else ""
        last_name = " ".join(name_parts[1:]) if len(name_parts) > 1 else ""
    elif not first_name:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Name information is required"
        )

    # Check if user already exists
    from sqlalchemy import select
    stmt = select(User.id).where(User.email == email)
    result = await db.execute(stmt)

    if result.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User with this email already exists"
        )

    # For testing purposes, allow registration without tenant_id
    # Create a default tenant if none provided
    tenant_id = user_data.get("tenant_id")
    if not tenant_id:
        # Check if default tenant exists
        default_tenant = await db.execute(
            text("SELECT id FROM tenants WHERE slug = 'default' LIMIT 1")
        )
        tenant_row = default_tenant.fetchone()

        if tenant_row:
            tenant_id = str(tenant_row[0])
        else:
            # Create default tenant
            from uuid import uuid4
            default_tenant_id = uuid4()
            await db.execute(
                text("INSERT INTO tenants (id, name, slug, description, is_active, created_at, updated_at) VALUES (:id, :name, :slug, :description, :is_active, NOW(), NOW())"),
                {
                    "id": default_tenant_id,
                    "name": "Default Tenant",
                    "slug": "default",
                    "description": "Default tenant for testing",
                    "is_active": True
                }
            )
            await db.commit()
            tenant_id = str(default_tenant_id)
    else:
        # Verify tenant exists if provided
        tenant = await db.get(Tenant, tenant_id)
        if not tenant:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid tenant ID"
            )

    # Hash password
    hashed_password = security.get_password_hash(password)

    # Check if this is the first user in the system
    from sqlalchemy import select, func
    user_count_result = await db.execute(select(func.count(User.id)))
    user_count = user_count_result.scalar()

    # Create user
    from uuid import uuid4
    user_id = uuid4()

    new_user = User(
        id=user_id,
        tenant_id=tenant_id,
        email=email,
        hashed_password=hashed_password,
        first_name=first_name,
        last_name=last_name or "",
        full_name=f"{first_name} {last_name}".strip(),
        is_active=True,
        is_verified=True  # First user is automatically verified
    )

    db.add(new_user)
    await db.commit()
    await db.refresh(new_user)

    # If this is the first user, make them superadmin
    if user_count == 0:
        await _setup_first_superadmin(db, new_user, tenant_id)

    # Return user data
    return {
        "id": str(user_id),
        "email": email,
        "first_name": first_name,
        "last_name": last_name or "",
        "full_name": f"{first_name} {last_name}".strip(),
        "is_active": True,
        "is_verified": True if user_count == 0 else False,
        "tenant_id": tenant_id,
        "role_ids": [],
        "created_at": new_user.created_at.isoformat() if new_user.created_at else None,
        "updated_at": new_user.updated_at.isoformat() if new_user.updated_at else None
    }


@router.post("/refresh", response_model=Token)
async def refresh_access_token(
    refresh_request: RefreshTokenRequest,
    db: AsyncSession = Depends(get_db)
) -> Any:
    """
    Refresh access token using refresh token
    """
    # Verify refresh token
    refresh_token_obj = await security.verify_refresh_token(db, refresh_request.refresh_token)
    if not refresh_token_obj:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired refresh token",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Get user
    user = await db.get(User, refresh_token_obj.user_id)
    if not user or not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found or inactive",
        )

    # Create new access token
    access_token_expires = timedelta(minutes=security.settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = security.create_access_token(
        subject=user.id, tenant_id=user.tenant_id, expires_delta=access_token_expires
    )

    # Create new refresh token
    new_refresh_token = security.create_refresh_token(user)

    # Revoke old refresh token
    await security.revoke_refresh_token(db, refresh_request.refresh_token)

    # Store new refresh token
    await security.store_refresh_token(
        db,
        user,
        new_refresh_token,
        user_agent=None,
        ip_address=None
    )

    return {
        "access_token": access_token,
        "refresh_token": new_refresh_token,
        "token_type": "bearer"
    }


@router.post("/logout")
async def logout(
    refresh_request: RefreshTokenRequest,
    db: AsyncSession = Depends(get_db)
) -> Any:
    """
    Logout by revoking refresh token and clearing cookies
    """
    # Revoke the refresh token
    await security.revoke_refresh_token(db, refresh_request.refresh_token)

    # Create logout response with cleared cookies
    cookie_manager = get_cookie_manager()
    return cookie_manager.create_logout_response()


@router.post("/logout-all")
async def logout_all_devices(
    current_user: User = Depends(security.get_current_user),
    db: AsyncSession = Depends(get_db)
) -> Any:
    """
    Logout from all devices by revoking all refresh tokens for the user
    """
    await security.revoke_all_user_refresh_tokens(db, str(current_user.id))

    # Create logout response with cleared cookies
    cookie_manager = get_cookie_manager()
    return cookie_manager.create_logout_response()


@router.get("/me", response_model=UserResponse)
async def read_users_me(
    current_user: User = Depends(security.get_current_user_from_cookie),
    db: AsyncSession = Depends(get_db)
) -> Any:
    """
    Get current user information
    """

    # Get user roles
    role_ids = []
    if current_user.user_roles:
        role_ids = [str(user_role.role_id) for user_role in current_user.user_roles]

    return {
        "id": str(current_user.id),
        "email": current_user.email,
        "first_name": current_user.first_name,
        "last_name": current_user.last_name,
        "full_name": current_user.full_name,
        "is_active": current_user.is_active,
        "is_verified": current_user.is_verified,
        "tenant_id": str(current_user.tenant_id),
        "role_ids": role_ids,
        "created_at": current_user.created_at.isoformat() if current_user.created_at else None,
        "updated_at": current_user.updated_at.isoformat() if current_user.updated_at else None
    }


@router.get("/permissions")
async def get_user_permissions(
    request: Request,
    db: AsyncSession = Depends(get_db)
) -> Any:
    """
    Get current user's permissions
    """
    # Get user from cookie-based authentication
    current_user = await security.get_current_user_from_cookie(request, db)

    # Get user permissions
    permissions = await PermissionService.get_user_permissions(
        current_user.id, current_user.tenant_id, db
    )

    return {
        "permissions": permissions,
        "user_id": str(current_user.id),
        "tenant_id": str(current_user.tenant_id)
    }


async def _setup_first_superadmin(db: AsyncSession, user: User, tenant_id: str):
    """
    Setup the first user as superadmin with all permissions
    """
    from app.models.role import Role
    from app.models.user_role import UserRole
    from uuid import uuid4

    try:
        # Create superadmin role with all permissions
        superadmin_role = Role(
            id=uuid4(),
            tenant_id=tenant_id,
            name="Super Administrator",
            description="Super administrator with all permissions",
            permissions='["users:*", "roles:*", "tenants:*", "articles:*", "system:*"]',
            color="#FF0000",
            hierarchy_level=100,
            is_default=False,
            is_active=True
        )

        db.add(superadmin_role)
        await db.commit()
        await db.refresh(superadmin_role)

        # Assign role to user
        user_role = UserRole(
            id=uuid4(),
            user_id=user.id,
            role_id=superadmin_role.id
        )

        db.add(user_role)
        await db.commit()

        print(f"✅ First user {user.email} has been set up as superadmin")

    except Exception as e:
        print(f"⚠️  Error setting up first superadmin: {e}")
        # Don't fail registration if role assignment fails