"""
Tenant CRUD endpoints
Multi-tenant management with proper authorization
"""

from typing import Any, List
from uuid import UUID, uuid4
from datetime import datetime, timedelta

from fastapi import APIRouter, Depends, HTTPException, Query, status, Request
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text

from app.core.database import get_db
from app.core.security import get_current_user, get_current_user_from_cookie, create_access_token
from app.core.cookies import get_cookie_manager
from app.models.user import User
from app.models.tenant import Tenant
from app.schemas.tenant import (
    TenantCreate,
    TenantResponse,
    TenantUpdate,
    TenantWithUsers
)
from app.schemas.auth import TokenResponse

router = APIRouter()


@router.get("/", response_model=List[TenantResponse])
async def read_tenants(
    request: Request,
    db: AsyncSession = Depends(get_db),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000)
) -> Any:
    """
    Retrieve tenants with pagination
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

    # For now, return all tenants (will be filtered by RLS later)
    result = await db.execute(
        text("SELECT * FROM tenants ORDER BY created_at DESC LIMIT :limit OFFSET :skip"),
        {"limit": limit, "skip": skip}
    )
    tenants = result.fetchall()

    # Convert to response format
    tenant_list = []
    for row in tenants:
        tenant_list.append({
            "id": str(row[0]),
            "name": row[1],
            "slug": row[2],
            "description": row[3],
            "parent_tenant_id": str(row[4]) if row[4] else None,
            "settings": row[5] or "{}",
            "is_active": row[6],
            "created_at": row[7].isoformat() if row[7] else None,
            "updated_at": row[8].isoformat() if row[8] else None
        })

    return tenant_list


@router.post("/", response_model=TenantResponse)
async def create_tenant(
    tenant_in: TenantCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> Any:
    """
    Create new tenant
    """
    # Check if slug already exists
    existing = await db.execute(
        text("SELECT id FROM tenants WHERE slug = :slug"),
        {"slug": tenant_in.slug}
    )

    if existing.fetchone():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Tenant with this slug already exists"
        )

    # Create tenant
    tenant_id = uuid4()
    from datetime import datetime
    now = datetime.utcnow()

    await db.execute(
        text("""
        INSERT INTO tenants (id, name, slug, description, parent_tenant_id, settings, is_active, created_at, updated_at)
        VALUES (:id, :name, :slug, :description, :parent_tenant_id, :settings, :is_active, :created_at, :updated_at)
        """),
        {
            "id": tenant_id,
            "name": tenant_in.name,
            "slug": tenant_in.slug,
            "description": tenant_in.description,
            "parent_tenant_id": tenant_in.parent_tenant_id,
            "settings": tenant_in.settings,
            "is_active": tenant_in.is_active,
            "created_at": now,
            "updated_at": now
        }
    )

    await db.commit()

    # Return created tenant
    return {
        "id": str(tenant_id),
        "name": tenant_in.name,
        "slug": tenant_in.slug,
        "description": tenant_in.description,
        "parent_tenant_id": tenant_in.parent_tenant_id,
        "settings": tenant_in.settings,
        "is_active": tenant_in.is_active,
        "created_at": now.isoformat(),
        "updated_at": now.isoformat()
    }


@router.get("/{tenant_id}", response_model=TenantWithUsers)
async def read_tenant(
    tenant_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> Any:
    """
    Get tenant by ID with user count
    """
    # Get tenant
    result = await db.execute(
        text("SELECT * FROM tenants WHERE id = :tenant_id"),
        {"tenant_id": tenant_id}
    )
    tenant_data = result.fetchone()

    if not tenant_data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Tenant not found"
        )

    # Get user count
    user_count_result = await db.execute(
        text("SELECT COUNT(*) FROM users WHERE tenant_id = :tenant_id"),
        {"tenant_id": tenant_id}
    )
    user_count = user_count_result.fetchone()[0]

    # Get role count
    role_count_result = await db.execute(
        text("SELECT COUNT(*) FROM roles WHERE tenant_id = :tenant_id"),
        {"tenant_id": tenant_id}
    )
    role_count = role_count_result.fetchone()[0]

    return {
        "id": str(tenant_data[0]),
        "name": tenant_data[1],
        "slug": tenant_data[2],
        "description": tenant_data[3],
        "parent_tenant_id": tenant_data[4],
        "settings": tenant_data[5],
        "is_active": tenant_data[6],
        "created_at": tenant_data[7].isoformat() if tenant_data[7] else None,
        "updated_at": tenant_data[8].isoformat() if tenant_data[8] else None,
        "user_count": user_count,
        "role_count": role_count
    }


@router.put("/{tenant_id}", response_model=TenantResponse)
async def update_tenant(
    tenant_id: UUID,
    tenant_in: TenantUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> Any:
    """
    Update tenant
    """
    # Check if tenant exists
    existing = await db.execute(
        text("SELECT * FROM tenants WHERE id = :tenant_id"),
        {"tenant_id": tenant_id}
    )

    if not existing.fetchone():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Tenant not found"
        )

    # Build update query dynamically
    update_fields = []
    params = {"tenant_id": tenant_id}

    if tenant_in.name is not None:
        update_fields.append("name = :name")
        params["name"] = tenant_in.name

    if tenant_in.description is not None:
        update_fields.append("description = :description")
        params["description"] = tenant_in.description

    if tenant_in.settings is not None:
        update_fields.append("settings = :settings")
        params["settings"] = tenant_in.settings

    if tenant_in.is_active is not None:
        update_fields.append("is_active = :is_active")
        params["is_active"] = tenant_in.is_active

    if not update_fields:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No fields to update"
        )

    # Execute update
    update_query = f"""
    UPDATE tenants
    SET {', '.join(update_fields)}, updated_at = NOW()
    WHERE id = :tenant_id
    """

    await db.execute(text(update_query), params)
    await db.commit()

    # Return updated tenant
    result = await db.execute(
        text("SELECT * FROM tenants WHERE id = :tenant_id"),
        {"tenant_id": tenant_id}
    )
    updated_data = result.fetchone()

    return {
        "id": str(updated_data[0]),
        "name": updated_data[1],
        "slug": updated_data[2],
        "description": updated_data[3],
        "parent_tenant_id": updated_data[4],
        "settings": updated_data[5],
        "is_active": updated_data[6],
        "created_at": updated_data[7].isoformat() if updated_data[7] else None,
        "updated_at": updated_data[8].isoformat() if updated_data[8] else None
    }


@router.delete("/{tenant_id}")
async def delete_tenant(
    tenant_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> Any:
    """
    Delete tenant (soft delete - mark as inactive)
    """
    # Check if tenant exists
    existing = await db.execute(
        text("SELECT * FROM tenants WHERE id = :tenant_id"),
        {"tenant_id": tenant_id}
    )

    if not existing.fetchone():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Tenant not found"
        )

    # Soft delete - mark as inactive
    await db.execute(
        text("UPDATE tenants SET is_active = false, updated_at = NOW() WHERE id = :tenant_id"),
        {"tenant_id": tenant_id}
    )

    await db.commit()

    return {"message": "Tenant deleted successfully"}


@router.post("/switch/{tenant_id}", response_model=TokenResponse)
async def switch_tenant(
    tenant_id: UUID,
    request: Request,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> Any:
    """
    Switch user to a different tenant
    Creates new access token with updated tenant context
    """
    # Verify tenant exists and is active
    tenant_result = await db.execute(
        text("SELECT id, name, is_active FROM tenants WHERE id = :tenant_id"),
        {"tenant_id": tenant_id}
    )
    tenant_data = tenant_result.fetchone()

    if not tenant_data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Tenant not found"
        )

    if not tenant_data[2]:  # is_active
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Tenant is not active"
        )

    # Verify user has access to this tenant
    # For now, allow access to all tenants (this can be restricted based on user permissions)
    # In production, you might want to check user_tenant_permissions table

    # Create new access token with updated tenant_id
    access_token = create_access_token(
        subject=current_user.id,
        tenant_id=str(tenant_id)
    )

    # Create response with updated cookies
    cookie_manager = get_cookie_manager()
    response = cookie_manager.create_login_response(
        access_token=access_token,
        refresh_token="",  # Keep existing refresh token
        tenant_id=str(tenant_id),
        tenant_name=tenant_data[1]
    )

    # Update response body
    response_data = {
        "access_token": access_token,
        "token_type": "bearer",
        "expires_in": 60 * 24 * 8,  # 8 days in seconds
        "tenant_id": str(tenant_id),
        "tenant_name": tenant_data[1]
    }

    response.body = response.render(response_data)
    response.headers["Content-Type"] = "application/json"

    return response


@router.get("/user-tenants", response_model=List[TenantResponse])
async def get_user_tenants(
    request: Request,
    db: AsyncSession = Depends(get_db)
) -> Any:
    """
    Get all tenants available to the current user
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

    # For now, return all active tenants
    # In production, filter based on user permissions
    result = await db.execute(
        text("SELECT * FROM tenants WHERE is_active = true ORDER BY name")
    )
    tenants = result.fetchall()

    # Convert to response format
    tenant_list = []
    for row in tenants:
        tenant_list.append({
            "id": str(row[0]),
            "name": row[1],
            "slug": row[2],
            "description": row[3],
            "parent_tenant_id": str(row[4]) if row[4] else None,
            "settings": row[5] or "{}",
            "is_active": row[6],
            "created_at": row[7].isoformat() if row[7] else None,
            "updated_at": row[8].isoformat() if row[8] else None
        })

    return tenant_list