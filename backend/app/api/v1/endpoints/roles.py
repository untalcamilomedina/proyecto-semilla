"""
Role CRUD endpoints
Role management with tenant isolation
"""

from typing import Any, List
from uuid import UUID, uuid4

import json
from fastapi import APIRouter, Depends, HTTPException, Query, Request, status
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.models.role import Role
from app.models.user import User
from app.models.user_role import UserRole
from app.schemas.role import (
    RoleCreate,
    RoleResponse,
    RoleUpdate,
)

router = APIRouter()


@router.get("/", response_model=List[RoleResponse])
async def read_roles(
    request: Request,
    db: AsyncSession = Depends(get_db),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000)
) -> Any:
    """
    Retrieve roles with pagination
    """
    # Check authentication
    user_id = getattr(request.state, 'user_id', None)
    tenant_id = getattr(request.state, 'tenant_id', None)

    if not user_id or not tenant_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required",
            headers={"WWW-Authenticate": "Bearer"},
        )

    stmt = (
        select(Role)
        .where(Role.tenant_id == tenant_id)
        .order_by(Role.hierarchy_level.desc(), Role.created_at.desc())
        .offset(skip)
        .limit(limit)
    )
    result = await db.execute(stmt)
    roles = result.scalars().all()

    return [_serialize_role(role) for role in roles]


@router.post("/", response_model=RoleResponse)
async def create_role(
    request: Request,
    role_in: RoleCreate,
    db: AsyncSession = Depends(get_db)
) -> Any:
    """
    Create new role
    """
    # Check authentication
    user_id = getattr(request.state, 'user_id', None)
    tenant_id = getattr(request.state, 'tenant_id', None)

    if not user_id or not tenant_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required",
            headers={"WWW-Authenticate": "Bearer"},
        )

    existing = await db.execute(
        select(func.count(Role.id)).where(
            Role.tenant_id == tenant_id, Role.name == role_in.name
        )
    )
    if (existing.scalar() or 0) > 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Role with this name already exists in your tenant"
        )

    role = Role(
        id=uuid4(),
        tenant_id=tenant_id,
        name=role_in.name,
        description=role_in.description,
        permissions=json.dumps(role_in.permissions or []),
        color=role_in.color or "#ffffff",
        hierarchy_level=role_in.hierarchy_level,
        is_default=role_in.is_default,
        is_active=role_in.is_active,
    )

    db.add(role)
    await db.commit()
    await db.refresh(role)

    return _serialize_role(role)


@router.get("/{role_id}", response_model=RoleResponse)
async def read_role(
    request: Request,
    role_id: UUID,
    db: AsyncSession = Depends(get_db)
) -> Any:
    """
    Get role by ID
    """
    # Check authentication
    user_id = getattr(request.state, 'user_id', None)
    tenant_id = getattr(request.state, 'tenant_id', None)

    if not user_id or not tenant_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Get role
    stmt = select(Role).where(Role.id == role_id, Role.tenant_id == tenant_id)
    result = await db.execute(stmt)
    role = result.scalar_one_or_none()

    if not role:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Role not found"
        )

    return _serialize_role(role)


@router.put("/{role_id}", response_model=RoleResponse)
async def update_role(
    request: Request,
    role_id: UUID,
    role_in: RoleUpdate,
    db: AsyncSession = Depends(get_db)
) -> Any:
    """
    Update role
    """
    # Check authentication
    user_id = getattr(request.state, 'user_id', None)
    tenant_id = getattr(request.state, 'tenant_id', None)

    if not user_id or not tenant_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Check if role exists and belongs to tenant
    stmt = select(Role).where(Role.id == role_id, Role.tenant_id == tenant_id)
    result = await db.execute(stmt)
    role = result.scalar_one_or_none()

    if not role:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Role not found"
        )

    if role_in.name and role_in.name != role.name:
        name_check = await db.execute(
            select(func.count(Role.id)).where(
                Role.tenant_id == tenant_id,
                Role.name == role_in.name,
                Role.id != role_id,
            )
        )
        if (name_check.scalar() or 0) > 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Role with this name already exists in your tenant",
            )

    if role_in.name is not None:
        role.name = role_in.name

    if role_in.description is not None:
        role.description = role_in.description

    if role_in.permissions is not None:
        role.permissions = json.dumps(role_in.permissions)

    if role_in.color is not None:
        role.color = role_in.color

    if role_in.hierarchy_level is not None:
        role.hierarchy_level = role_in.hierarchy_level

    if role_in.is_default is not None:
        role.is_default = role_in.is_default

    if role_in.is_active is not None:
        role.is_active = role_in.is_active

    await db.commit()
    await db.refresh(role)

    return _serialize_role(role)


@router.delete("/{role_id}")
async def delete_role(
    request: Request,
    role_id: UUID,
    db: AsyncSession = Depends(get_db)
) -> Any:
    """
    Delete role (soft delete - mark as inactive)
    """
    # Check authentication
    user_id = getattr(request.state, 'user_id', None)
    tenant_id = getattr(request.state, 'tenant_id', None)

    if not user_id or not tenant_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Check if role exists and belongs to tenant
    stmt = select(Role).where(Role.id == role_id, Role.tenant_id == tenant_id)
    result = await db.execute(stmt)
    role = result.scalar_one_or_none()

    if not role:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Role not found"
        )

    role.is_active = False
    await db.commit()

    return {"message": "Role deleted successfully"}


@router.post("/users/{user_id}/roles/{role_id}")
async def assign_role_to_user(
    request: Request,
    user_id: UUID,
    role_id: UUID,
    db: AsyncSession = Depends(get_db)
) -> Any:
    """
    Assign role to user
    """
    # Check authentication
    auth_user_id = getattr(request.state, 'user_id', None)
    tenant_id = getattr(request.state, 'tenant_id', None)

    if not auth_user_id or not tenant_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required",
            headers={"WWW-Authenticate": "Bearer"},
        )

    user_stmt = select(User).where(User.id == user_id, User.tenant_id == tenant_id)
    user_result = await db.execute(user_stmt)
    user = user_result.scalar_one_or_none()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found in your tenant"
        )

    role_stmt = select(Role).where(Role.id == role_id, Role.tenant_id == tenant_id)
    role_result = await db.execute(role_stmt)
    role = role_result.scalar_one_or_none()

    if not role:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Role not found in your tenant"
        )

    assignment_stmt = select(UserRole).where(
        UserRole.user_id == user_id, UserRole.role_id == role_id
    )
    existing = await db.execute(assignment_stmt)
    if existing.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User already has this role"
        )

    assignment = UserRole(user_id=user_id, role_id=role_id)
    db.add(assignment)
    await db.commit()

    return {
        "message": "Role assigned successfully",
        "user_id": str(user_id),
        "role_id": str(role_id),
        "role_name": role.name,
    }


@router.delete("/users/{user_id}/roles/{role_id}")
async def remove_role_from_user(
    request: Request,
    user_id: UUID,
    role_id: UUID,
    db: AsyncSession = Depends(get_db)
) -> Any:
    """
    Remove role from user
    """
    # Check authentication
    auth_user_id = getattr(request.state, 'user_id', None)
    tenant_id = getattr(request.state, 'tenant_id', None)

    if not auth_user_id or not tenant_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Verify user and role belong to tenant
    assignment_stmt = (
        select(UserRole)
        .join(User, User.id == UserRole.user_id)
        .join(Role, Role.id == UserRole.role_id)
        .where(
            UserRole.user_id == user_id,
            UserRole.role_id == role_id,
            User.tenant_id == tenant_id,
            Role.tenant_id == tenant_id,
        )
    )
    assignment_result = await db.execute(assignment_stmt)
    assignment = assignment_result.scalar_one_or_none()

    if not assignment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Role assignment not found"
        )

    await db.delete(assignment)
    await db.commit()

    return {"message": "Role removed successfully"}


def _serialize_role(role: Role) -> dict[str, Any]:
    """Serializa un rol de SQLAlchemy al formato de respuesta esperado."""

    try:
        permissions = json.loads(role.permissions) if role.permissions else []
    except (json.JSONDecodeError, TypeError):
        permissions = []

    return {
        "id": str(role.id),
        "tenant_id": str(role.tenant_id),
        "name": role.name,
        "description": role.description,
        "permissions": permissions,
        "color": role.color,
        "hierarchy_level": role.hierarchy_level,
        "is_default": role.is_default,
        "is_active": role.is_active,
        "created_at": role.created_at.isoformat() if role.created_at else None,
        "updated_at": role.updated_at.isoformat() if role.updated_at else None,
    }
