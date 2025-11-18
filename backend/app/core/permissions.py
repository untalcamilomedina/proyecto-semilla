"""
Permission validation system
Centralized permission checking for endpoints
"""

from enum import Enum
from typing import List, Optional
from fastapi import Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text

from app.core.database import get_db
from app.core.security import get_current_user
from app.models.user import User


class Permission(str, Enum):
    """Available permissions in the system"""
    # User permissions
    USER_CREATE = "user:create"
    USER_READ = "user:read"
    USER_UPDATE = "user:update"
    USER_DELETE = "user:delete"

    # Tenant permissions
    TENANT_CREATE = "tenant:create"
    TENANT_READ = "tenant:read"
    TENANT_UPDATE = "tenant:update"
    TENANT_DELETE = "tenant:delete"

    # Role permissions
    ROLE_CREATE = "role:create"
    ROLE_READ = "role:read"
    ROLE_UPDATE = "role:update"
    ROLE_DELETE = "role:delete"
    ROLE_ASSIGN = "role:assign"

    # Admin permissions
    ADMIN_ALL = "admin:*"


async def get_user_permissions(
    db: AsyncSession,
    user_id: str
) -> List[str]:
    """
    Get all permissions for a user based on their roles.
    Returns list of permission strings.
    """
    query = text("""
        SELECT DISTINCT r.permissions
        FROM user_roles ur
        JOIN roles r ON ur.role_id = r.id
        WHERE ur.user_id = :user_id AND r.is_active = true
    """)

    result = await db.execute(query, {"user_id": user_id})
    rows = result.fetchall()

    # Flatten permissions from all roles
    all_permissions = []
    import json
    for row in rows:
        if row[0]:
            try:
                permissions = json.loads(row[0]) if isinstance(row[0], str) else row[0]
                if isinstance(permissions, list):
                    all_permissions.extend(permissions)
            except (json.JSONDecodeError, TypeError):
                continue

    return list(set(all_permissions))  # Remove duplicates


async def has_permission(
    db: AsyncSession,
    user: User,
    required_permission: Permission
) -> bool:
    """
    Check if user has a specific permission.
    Users with admin:* permission have all permissions.
    """
    user_permissions = await get_user_permissions(db, str(user.id))

    # Check if user has admin wildcard
    if Permission.ADMIN_ALL.value in user_permissions:
        return True

    # Check for specific permission
    return required_permission.value in user_permissions


async def require_permission(
    required_permission: Permission,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> User:
    """
    Dependency to require a specific permission.
    Raises 403 if user doesn't have the permission.

    Usage:
        @router.post("/")
        async def create_user(
            user: User = Depends(require_permission(Permission.USER_CREATE))
        ):
            ...
    """
    if not await has_permission(db, current_user, required_permission):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"Permission denied. Required permission: {required_permission.value}"
        )

    return current_user


def PermissionChecker(required_permission: Permission):
    """
    Factory function to create permission dependency.

    Usage:
        @router.post("/", dependencies=[Depends(PermissionChecker(Permission.USER_CREATE))])
        async def create_user(...):
            ...
    """
    async def check_permission(
        db: AsyncSession = Depends(get_db),
        current_user: User = Depends(get_current_user)
    ):
        if not await has_permission(db, current_user, required_permission):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Permission denied. Required permission: {required_permission.value}"
            )
        return True

    return check_permission


async def require_any_permission(
    required_permissions: List[Permission],
    db: AsyncSession,
    current_user: User
) -> bool:
    """
    Check if user has ANY of the required permissions.
    Returns True if user has at least one permission.
    """
    user_permissions = await get_user_permissions(db, str(current_user.id))

    # Check admin wildcard
    if Permission.ADMIN_ALL.value in user_permissions:
        return True

    # Check if user has any of the required permissions
    for perm in required_permissions:
        if perm.value in user_permissions:
            return True

    return False


async def require_all_permissions(
    required_permissions: List[Permission],
    db: AsyncSession,
    current_user: User
) -> bool:
    """
    Check if user has ALL of the required permissions.
    Returns True only if user has all permissions.
    """
    user_permissions = await get_user_permissions(db, str(current_user.id))

    # Check admin wildcard
    if Permission.ADMIN_ALL.value in user_permissions:
        return True

    # Check if user has all required permissions
    for perm in required_permissions:
        if perm.value not in user_permissions:
            return False

    return True
