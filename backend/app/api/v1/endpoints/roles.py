"""
Role CRUD endpoints
Role management with tenant isolation
"""

from typing import Any, List
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status, Request
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text

from app.core.database import get_db
from app.models.role import Role
from app.models.user_role import UserRole
from app.schemas.role import (
    RoleCreate,
    RoleResponse,
    RoleUpdate,
    UserRoleAssignment,
    UserRoleResponse
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

    # Get roles for current tenant
    result = await db.execute(
        text("SELECT * FROM roles WHERE tenant_id = :tenant_id ORDER BY hierarchy_level DESC, created_at DESC LIMIT :limit OFFSET :skip"),
        {"tenant_id": tenant_id, "limit": limit, "skip": skip}
    )
    roles = result.fetchall()

    # Convert to response format
    role_list = []
    for row in roles:
        # Parse permissions JSON string to list
        import json
        try:
            permissions = json.loads(row[5]) if row[5] else []
        except (json.JSONDecodeError, TypeError):
            permissions = []

        role_list.append({
            "id": str(row[0]),
            "tenant_id": str(row[1]),
            "name": row[2],
            "description": row[3],
            "permissions": permissions,      # parsed JSON to list
            "color": row[4],               # color is at index 4
            "hierarchy_level": row[6],
            "is_default": row[7],
            "is_active": row[8],
            "created_at": row[9].isoformat() if row[9] else None,
            "updated_at": row[10].isoformat() if row[10] else None
        })

    return role_list


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

    # Check if role name already exists in tenant
    existing = await db.execute(
        text("SELECT id FROM roles WHERE tenant_id = :tenant_id AND name = :name"),
        {"tenant_id": tenant_id, "name": role_in.name}
    )

    if existing.fetchone():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Role with this name already exists in your tenant"
        )

    # Create role
    import json
    role_id = UUID()
    await db.execute(
        text("""
        INSERT INTO roles (id, tenant_id, name, description, permissions, color, hierarchy_level, is_default, is_active)
        VALUES (:id, :tenant_id, :name, :description, :permissions, :color, :hierarchy_level, :is_default, :is_active)
        """),
        {
            "id": role_id,
            "tenant_id": tenant_id,
            "name": role_in.name,
            "description": role_in.description,
            "permissions": json.dumps(role_in.permissions),
            "color": role_in.color,
            "hierarchy_level": role_in.hierarchy_level,
            "is_default": role_in.is_default,
            "is_active": role_in.is_active
        }
    )

    await db.commit()

    # Return created role
    return {
        "id": str(role_id),
        "tenant_id": str(tenant_id),
        "name": role_in.name,
        "description": role_in.description,
        "permissions": role_in.permissions,
        "color": role_in.color,
        "hierarchy_level": role_in.hierarchy_level,
        "is_default": role_in.is_default,
        "is_active": role_in.is_active,
        "created_at": "2024-01-01T00:00:00Z",  # Placeholder
        "updated_at": "2024-01-01T00:00:00Z"   # Placeholder
    }


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
    result = await db.execute(
        text("SELECT * FROM roles WHERE id = :role_id AND tenant_id = :tenant_id"),
        {"role_id": role_id, "tenant_id": tenant_id}
    )
    role_data = result.fetchone()

    if not role_data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Role not found"
        )

    # Parse permissions JSON string to list
    import json
    try:
        permissions = json.loads(role_data[4]) if role_data[4] else []
    except (json.JSONDecodeError, TypeError):
        permissions = []

    return {
        "id": str(role_data[0]),
        "tenant_id": str(role_data[1]),
        "name": role_data[2],
        "description": role_data[3],
        "permissions": permissions,
        "color": role_data[5],
        "hierarchy_level": role_data[6],
        "is_default": role_data[7],
        "is_active": role_data[8],
        "created_at": role_data[9].isoformat() if role_data[9] else None,
        "updated_at": role_data[10].isoformat() if role_data[10] else None
    }


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
    existing = await db.execute(
        text("SELECT * FROM roles WHERE id = :role_id AND tenant_id = :tenant_id"),
        {"role_id": role_id, "tenant_id": tenant_id}
    )

    if not existing.fetchone():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Role not found"
        )

    # Check name uniqueness if name is being updated
    if role_in.name is not None:
        name_check = await db.execute(
            text("SELECT id FROM roles WHERE tenant_id = :tenant_id AND name = :name AND id != :role_id"),
            {"tenant_id": tenant_id, "name": role_in.name, "role_id": role_id}
        )
        if name_check.fetchone():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Role with this name already exists in your tenant"
            )

    # Build update query
    update_fields = []
    values = []
    param_count = 1

    if role_in.name is not None:
        update_fields.append(f"name = ${param_count}")
        values.append(role_in.name)
        param_count += 1

    if role_in.description is not None:
        update_fields.append(f"description = ${param_count}")
        values.append(role_in.description)
        param_count += 1

    if role_in.permissions is not None:
        import json
        update_fields.append(f"permissions = ${param_count}")
        values.append(json.dumps(role_in.permissions))
        param_count += 1

    if role_in.color is not None:
        update_fields.append(f"color = ${param_count}")
        values.append(role_in.color)
        param_count += 1

    if role_in.hierarchy_level is not None:
        update_fields.append(f"hierarchy_level = ${param_count}")
        values.append(role_in.hierarchy_level)
        param_count += 1

    if role_in.is_default is not None:
        update_fields.append(f"is_default = ${param_count}")
        values.append(role_in.is_default)
        param_count += 1

    if role_in.is_active is not None:
        update_fields.append(f"is_active = ${param_count}")
        values.append(role_in.is_active)
        param_count += 1

    if not update_fields:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No fields to update"
        )

    # Add role_id to values
    values.append(role_id)

    # Execute update
    update_query = f"""
    UPDATE roles
    SET {', '.join(update_fields)}, updated_at = NOW()
    WHERE id = ${param_count}
    """

    await db.execute(text(update_query), values)
    await db.commit()

    # Return updated role
    return await read_role(request, role_id, db)


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
    existing = await db.execute(
        text("SELECT * FROM roles WHERE id = $1 AND tenant_id = $2"),
        (role_id, tenant_id)
    )

    if not existing.fetchone():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Role not found"
        )

    # Soft delete - mark as inactive
    await db.execute(
        text("UPDATE roles SET is_active = false, updated_at = NOW() WHERE id = $1"),
        (role_id,)
    )

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

    # Verify user belongs to tenant
    user_check = await db.execute(
        text("SELECT id FROM users WHERE id = $1 AND tenant_id = $2"),
        (user_id, tenant_id)
    )

    if not user_check.fetchone():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found in your tenant"
        )

    # Verify role belongs to tenant
    role_check = await db.execute(
        text("SELECT name FROM roles WHERE id = $1 AND tenant_id = $2"),
        (role_id, tenant_id)
    )

    role_data = role_check.fetchone()
    if not role_data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Role not found in your tenant"
        )

    # Check if assignment already exists
    existing = await db.execute(
        text("SELECT id FROM user_roles WHERE user_id = $1 AND role_id = $2"),
        (user_id, role_id)
    )

    if existing.fetchone():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User already has this role"
        )

    # Create assignment
    assignment_id = UUID()
    await db.execute(
        text("INSERT INTO user_roles (id, user_id, role_id) VALUES ($1, $2, $3)"),
        (assignment_id, user_id, role_id)
    )

    await db.commit()

    return {
        "message": "Role assigned successfully",
        "user_id": str(user_id),
        "role_id": str(role_id),
        "role_name": role_data[0]
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
    assignment_check = await db.execute(
        text("""
        SELECT ur.id FROM user_roles ur
        JOIN users u ON ur.user_id = u.id
        JOIN roles r ON ur.role_id = r.id
        WHERE ur.user_id = $1 AND ur.role_id = $2
        AND u.tenant_id = $3 AND r.tenant_id = $3
        """),
        (user_id, role_id, tenant_id)
    )

    if not assignment_check.fetchone():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Role assignment not found"
        )

    # Remove assignment
    await db.execute(
        text("DELETE FROM user_roles WHERE user_id = $1 AND role_id = $2"),
        (user_id, role_id)
    )

    await db.commit()

    return {"message": "Role removed successfully"}