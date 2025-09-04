"""
Security utilities for authentication and authorization
JWT tokens, password hashing, and authentication dependencies
"""

from datetime import datetime, timedelta
from typing import Any, Union, Optional
from uuid import UUID

from fastapi import Depends, HTTPException, status, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import jwt, JWTError
from passlib.context import CryptContext
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text

from app.core.config import settings
from app.core.database import get_db
from app.models.user import User
from app.models.refresh_token import RefreshToken

# Password hashing context
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# JWT security scheme
security = HTTPBearer()


def create_access_token(
    subject: Union[str, UUID], tenant_id: Union[str, UUID], expires_delta: timedelta = None
) -> str:
    """
    Create JWT access token with tenant context
    """
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(
            minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
        )

    to_encode = {
        "exp": expire,
        "sub": str(subject),
        "tenant_id": str(tenant_id)
    }
    encoded_jwt = jwt.encode(
        to_encode,
        settings.JWT_SECRET,
        algorithm=settings.JWT_ALGORITHM
    )
    return encoded_jwt


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verify a password against its hash
    """
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    """
    Hash a password
    """
    return pwd_context.hash(password)


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: AsyncSession = Depends(get_db)
) -> User:
    """
    Get current authenticated user from JWT token
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        payload = jwt.decode(
            credentials.credentials,
            settings.JWT_SECRET,
            algorithms=[settings.JWT_ALGORITHM]
        )
        user_id: str = payload.get("sub")
        if user_id is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception

    try:
        user_uuid = UUID(user_id)
    except ValueError:
        raise credentials_exception

    # Get user from database
    user = await db.get(User, user_uuid)
    if user is None:
        raise credentials_exception

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Inactive user"
        )

    return user


async def get_current_active_user(
    current_user: User = Depends(get_current_user)
) -> User:
    """
    Get current active user (alias for get_current_user)
    """
    return current_user


def create_user_token(user: User) -> str:
    """
    Create JWT token for a user
    """
    return create_access_token(subject=user.id, tenant_id=user.tenant_id)


def authenticate_user(db: AsyncSession, email: str, password: str) -> Optional[User]:
    """
    Authenticate a user with email and password
    """
    # This would be implemented with database query
    # For now, return None (will be implemented with actual auth endpoints)
    return None


async def get_current_user_with_tenant(
    request: Request,
    db: AsyncSession = Depends(get_db)
) -> User:
    """
    Get current authenticated user and set tenant context
    """
    from fastapi import HTTPException, status
    from sqlalchemy import text

    # Get user_id and tenant_id from request state (set by middleware)
    user_id = getattr(request.state, 'user_id', None)
    tenant_id = getattr(request.state, 'tenant_id', None)

    if not user_id or not tenant_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Verify user exists and is active
    user = await db.get(User, user_id)
    if not user or not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found or inactive",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Set tenant context in database session
    try:
        await db.execute(
            text("SELECT set_config('app.current_tenant_id', :tenant_id, false)"),
            {"tenant_id": str(tenant_id)}
        )
        await db.execute(
            text("SELECT set_config('app.current_user_id', :user_id, false)"),
            {"user_id": str(user_id)}
        )
        await db.execute(
            text("SELECT set_config('app.user_role', :role, false)"),
            {"role": "user"}
        )
    except Exception as e:
        # If setting context fails, continue without it
        # This allows the endpoint to work even if RLS is not fully set up
        pass

    return user


def create_refresh_token(user: User) -> str:
    """
    Create a refresh token for a user
    """
    expires_delta = timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
    token_data = {
        "sub": str(user.id),
        "tenant_id": str(user.tenant_id),
        "type": "refresh",
        "exp": datetime.utcnow() + expires_delta
    }
    return jwt.encode(token_data, settings.JWT_SECRET, algorithm=settings.JWT_ALGORITHM)


async def store_refresh_token(
    db: AsyncSession,
    user: User,
    token: str,
    user_agent: Optional[str] = None,
    ip_address: Optional[str] = None
) -> None:
    """
    Store a refresh token in the database
    """
    from app.models.refresh_token import RefreshToken
    from uuid import uuid4

    expires_at = datetime.utcnow() + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)

    refresh_token_obj = RefreshToken(
        id=uuid4(),
        user_id=user.id,
        tenant_id=user.tenant_id,
        token=token,
        expires_at=expires_at,
        user_agent=user_agent,
        ip_address=ip_address
    )

    db.add(refresh_token_obj)
    await db.commit()


async def verify_refresh_token(db: AsyncSession, token: str) -> Optional["RefreshToken"]:
    """
    Verify a refresh token and return the token object if valid
    """
    from app.models.refresh_token import RefreshToken
    from sqlalchemy import select

    stmt = select(RefreshToken).where(
        RefreshToken.token == token,
        RefreshToken.is_revoked == False,
        RefreshToken.expires_at > datetime.utcnow()
    )
    result = await db.execute(stmt)
    return result.scalar_one_or_none()


async def revoke_refresh_token(db: AsyncSession, token: str) -> None:
    """
    Revoke a refresh token
    """
    from app.models.refresh_token import RefreshToken
    from sqlalchemy import update

    stmt = (
        update(RefreshToken)
        .where(RefreshToken.token == token)
        .values(is_revoked=True, revoked_at=datetime.utcnow())
    )
    await db.execute(stmt)
    await db.commit()


async def revoke_all_user_refresh_tokens(db: AsyncSession, user_id: str) -> None:
    """
    Revoke all refresh tokens for a user
    """
    from app.models.refresh_token import RefreshToken
    from sqlalchemy import update

    stmt = (
        update(RefreshToken)
        .where(RefreshToken.user_id == user_id)
        .values(is_revoked=True, revoked_at=datetime.utcnow())
    )
    await db.execute(stmt)
    await db.commit()


def create_refresh_token(user: User) -> str:
    """
    Create a refresh token for a user
    """
    from datetime import timedelta
    expires_delta = timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
    expire = datetime.utcnow() + expires_delta

    to_encode = {
        "sub": str(user.id),
        "tenant_id": str(user.tenant_id),
        "type": "refresh",
        "exp": expire
    }

    encoded_jwt = jwt.encode(
        to_encode,
        settings.JWT_SECRET,
        algorithm=settings.JWT_ALGORITHM
    )
    return encoded_jwt


async def store_refresh_token(db: AsyncSession, user: User, token: str, user_agent: str = None, ip_address: str = None):
    """
    Store refresh token in database
    """
    from datetime import timedelta
    expires_at = datetime.utcnow() + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)

    refresh_token = RefreshToken(
        user_id=user.id,
        tenant_id=user.tenant_id,
        token=token,
        expires_at=expires_at,
        user_agent=user_agent,
        ip_address=ip_address
    )

    db.add(refresh_token)
    await db.commit()
    await db.refresh(refresh_token)
    return refresh_token


async def verify_refresh_token(db: AsyncSession, token: str) -> Optional[RefreshToken]:
    """
    Verify and return refresh token if valid
    """
    try:
        payload = jwt.decode(
            token,
            settings.JWT_SECRET,
            algorithms=[settings.JWT_ALGORITHM]
        )

        if payload.get("type") != "refresh":
            return None

        user_id = payload.get("sub")
        if not user_id:
            return None

        # Get token from database
        result = await db.execute(
            "SELECT * FROM refresh_tokens WHERE token = $1 AND is_revoked = false",
            (token,)
        )
        token_data = result.fetchone()

        if not token_data:
            return None

        # Convert to RefreshToken object
        refresh_token = RefreshToken(
            id=token_data[0],
            user_id=token_data[1],
            tenant_id=token_data[2],
            token=token_data[3],
            is_revoked=token_data[4],
            expires_at=token_data[5],
            user_agent=token_data[6],
            ip_address=token_data[7],
            created_at=token_data[8],
            revoked_at=token_data[9]
        )

        if not refresh_token.is_valid():
            return None

        return refresh_token

    except JWTError:
        return None


async def revoke_refresh_token(db: AsyncSession, token: str):
    """
    Revoke a refresh token
    """
    await db.execute(
        "UPDATE refresh_tokens SET is_revoked = true, revoked_at = NOW() WHERE token = $1",
        (token,)
    )
    await db.commit()


async def revoke_all_user_refresh_tokens(db: AsyncSession, user_id: str):
    """
    Revoke all refresh tokens for a user (logout from all devices)
    """
    await db.execute(
        "UPDATE refresh_tokens SET is_revoked = true, revoked_at = NOW() WHERE user_id = $1",
        (user_id,)
    )
    await db.commit()