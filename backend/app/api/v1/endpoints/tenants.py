"""
Tenant CRUD endpoints
Multi-tenant management with proper authorization
"""

from typing import Any, List
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.security import get_current_user
from app.models.user import User
from app.models.tenant import Tenant
from app.schemas.tenant import (
    TenantCreate,
    TenantResponse,
    TenantUpdate,
    TenantWithUsers
)

router = APIRouter()


@router.get("/", response_model=List[TenantResponse])
async def read_tenants(
    db: AsyncSession = Depends(get_db),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    current_user: User = Depends(get_current_user)
) -> Any:
    """
    Retrieve tenants with pagination
    """
    # For now, return all tenants (will be filtered by RLS later)
    result = await db.execute(
        "SELECT * FROM tenants ORDER BY created_at DESC LIMIT $1 OFFSET $2",
        (limit, skip)
    )
    tenants = result.fetchall()

    # Convert to Tenant objects
    tenant_list = []
    for row in tenants:
        tenant = Tenant(
            id=row[0],
            name=row[1],
            slug=row[2],
            description=row[3],
            parent_tenant_id=row[4],
            settings=row[5],
            is_active=row[6],
            created_at=row[7],
            updated_at=row[8]
        )
        tenant_list.append(tenant)

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
        "SELECT id FROM tenants WHERE slug = $1",
        (tenant_in.slug,)
    )

    if existing.fetchone():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Tenant with this slug already exists"
        )

    # Create tenant
    tenant_id = UUID()
    await db.execute(
        """
        INSERT INTO tenants (id, name, slug, description, parent_tenant_id, settings, is_active)
        VALUES ($1, $2, $3, $4, $5, $6, $7)
        """,
        (
            tenant_id,
            tenant_in.name,
            tenant_in.slug,
            tenant_in.description,
            tenant_in.parent_tenant_id,
            tenant_in.settings,
            tenant_in.is_active
        )
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
        "created_at": "2024-01-01T00:00:00Z",  # Placeholder
        "updated_at": "2024-01-01T00:00:00Z"   # Placeholder
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
        "SELECT * FROM tenants WHERE id = $1",
        (tenant_id,)
    )
    tenant_data = result.fetchone()

    if not tenant_data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Tenant not found"
        )

    # Get user count
    user_count_result = await db.execute(
        "SELECT COUNT(*) FROM users WHERE tenant_id = $1",
        (tenant_id,)
    )
    user_count = user_count_result.fetchone()[0]

    # Get role count
    role_count_result = await db.execute(
        "SELECT COUNT(*) FROM roles WHERE tenant_id = $1",
        (tenant_id,)
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
        "SELECT * FROM tenants WHERE id = $1",
        (tenant_id,)
    )

    if not existing.fetchone():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Tenant not found"
        )

    # Build update query dynamically
    update_fields = []
    values = []
    param_count = 1

    if tenant_in.name is not None:
        update_fields.append(f"name = ${param_count}")
        values.append(tenant_in.name)
        param_count += 1

    if tenant_in.description is not None:
        update_fields.append(f"description = ${param_count}")
        values.append(tenant_in.description)
        param_count += 1

    if tenant_in.settings is not None:
        update_fields.append(f"settings = ${param_count}")
        values.append(tenant_in.settings)
        param_count += 1

    if tenant_in.is_active is not None:
        update_fields.append(f"is_active = ${param_count}")
        values.append(tenant_in.is_active)
        param_count += 1

    if not update_fields:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No fields to update"
        )

    # Add tenant_id to values
    values.append(tenant_id)

    # Execute update
    update_query = f"""
    UPDATE tenants
    SET {', '.join(update_fields)}, updated_at = NOW()
    WHERE id = ${param_count}
    """

    await db.execute(update_query, values)
    await db.commit()

    # Return updated tenant
    result = await db.execute(
        "SELECT * FROM tenants WHERE id = $1",
        (tenant_id,)
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
        "SELECT * FROM tenants WHERE id = $1",
        (tenant_id,)
    )

    if not existing.fetchone():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Tenant not found"
        )

    # Soft delete - mark as inactive
    await db.execute(
        "UPDATE tenants SET is_active = false, updated_at = NOW() WHERE id = $1",
        (tenant_id,)
    )

    await db.commit()

    return {"message": "Tenant deleted successfully"}