"""
User CRUD endpoints
User management with tenant isolation
"""

from typing import Any, List
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.security import get_current_user
from app.models.user import User
from app.schemas.auth import UserCreate, UserUpdate, UserResponse

router = APIRouter()


@router.get("/", response_model=List[UserResponse])
async def read_users(
    db: AsyncSession = Depends(get_db),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    tenant_id: UUID = None,
    current_user: User = Depends(get_current_user)
) -> Any:
    """
    Retrieve users with optional tenant filtering
    """
    # Build query based on tenant filter
    if tenant_id:
        result = await db.execute(
            "SELECT * FROM users WHERE tenant_id = $1 ORDER BY created_at DESC LIMIT $2 OFFSET $3",
            (tenant_id, limit, skip)
        )
    else:
        # For now, return all users (will be filtered by RLS later)
        result = await db.execute(
            "SELECT * FROM users ORDER BY created_at DESC LIMIT $1 OFFSET $2",
            (limit, skip)
        )

    users = result.fetchall()

    # Convert to UserResponse format
    user_list = []
    for row in users:
        user_response = {
            "id": str(row[0]),
            "email": row[2],
            "first_name": row[4],
            "last_name": row[5],
            "full_name": f"{row[4]} {row[5]}",
            "is_active": row[6],
            "is_verified": row[7],
            "tenant_id": str(row[1]),
            "role_ids": [],  # Will be populated with actual roles
            "created_at": row[11].isoformat() if row[11] else None,
            "updated_at": row[12].isoformat() if row[12] else None
        }
        user_list.append(user_response)

    return user_list


@router.post("/", response_model=UserResponse)
async def create_user(
    user_in: UserCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> Any:
    """
    Create new user
    """
    # Check if user already exists
    existing = await db.execute(
        "SELECT id FROM users WHERE email = $1",
        (user_in.email,)
    )

    if existing.fetchone():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User with this email already exists"
        )

    # Verify tenant exists
    tenant_result = await db.execute(
        "SELECT id FROM tenants WHERE id = $1",
        (user_in.tenant_id,)
    )

    if not tenant_result.fetchone():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid tenant ID"
        )

    # Hash password
    from app.core.security import get_password_hash
    hashed_password = get_password_hash(user_in.password)

    # Create user
    user_id = UUID()
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

    # Return created user
    return {
        "id": str(user_id),
        "email": user_in.email,
        "first_name": user_in.first_name,
        "last_name": user_in.last_name,
        "full_name": f"{user_in.first_name} {user_in.last_name}",
        "is_active": True,
        "is_verified": False,
        "tenant_id": user_in.tenant_id,
        "role_ids": user_in.role_ids or [],
        "created_at": "2024-01-01T00:00:00Z",  # Placeholder
        "updated_at": "2024-01-01T00:00:00Z"   # Placeholder
    }


@router.get("/{user_id}", response_model=UserResponse)
async def read_user(
    user_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> Any:
    """
    Get user by ID
    """
    result = await db.execute(
        "SELECT * FROM users WHERE id = $1",
        (user_id,)
    )
    user_data = result.fetchone()

    if not user_data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    # Get user roles
    roles_result = await db.execute(
        """
        SELECT r.id FROM roles r
        JOIN user_roles ur ON r.id = ur.role_id
        WHERE ur.user_id = $1
        """,
        (user_id,)
    )
    role_ids = [str(row[0]) for row in roles_result.fetchall()]

    return {
        "id": str(user_data[0]),
        "email": user_data[2],
        "first_name": user_data[4],
        "last_name": user_data[5],
        "full_name": user_data[6],
        "is_active": user_data[7],
        "is_verified": user_data[8],
        "tenant_id": str(user_data[1]),
        "role_ids": role_ids,
        "created_at": user_data[11].isoformat() if user_data[11] else None,
        "updated_at": user_data[12].isoformat() if user_data[12] else None
    }


@router.put("/{user_id}", response_model=UserResponse)
async def update_user(
    user_id: UUID,
    user_in: UserUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> Any:
    """
    Update user
    """
    # Check if user exists
    existing = await db.execute(
        "SELECT * FROM users WHERE id = $1",
        (user_id,)
    )

    if not existing.fetchone():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    # Build update query dynamically
    update_fields = []
    values = []
    param_count = 1

    if user_in.email is not None:
        # Check if email is already taken by another user
        email_check = await db.execute(
            "SELECT id FROM users WHERE email = $1 AND id != $2",
            (user_in.email, user_id)
        )
        if email_check.fetchone():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already taken"
            )
        update_fields.append(f"email = ${param_count}")
        values.append(user_in.email)
        param_count += 1

    if user_in.first_name is not None:
        update_fields.append(f"first_name = ${param_count}")
        values.append(user_in.first_name)
        param_count += 1

    if user_in.last_name is not None:
        update_fields.append(f"last_name = ${param_count}")
        values.append(user_in.last_name)
        param_count += 1

    if user_in.is_active is not None:
        update_fields.append(f"is_active = ${param_count}")
        values.append(user_in.is_active)
        param_count += 1

    # Update full_name if first_name or last_name changed
    if user_in.first_name or user_in.last_name:
        # Get current user data to build full name
        current_data = await db.execute(
            "SELECT first_name, last_name FROM users WHERE id = $1",
            (user_id,)
        )
        current_row = current_data.fetchone()
        new_first = user_in.first_name or current_row[0]
        new_last = user_in.last_name or current_row[1]
        update_fields.append(f"full_name = ${param_count}")
        values.append(f"{new_first} {new_last}")
        param_count += 1

    if not update_fields:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No fields to update"
        )

    # Add user_id to values
    values.append(user_id)

    # Execute update
    update_query = f"""
    UPDATE users
    SET {', '.join(update_fields)}, updated_at = NOW()
    WHERE id = ${param_count}
    """

    await db.execute(update_query, values)
    await db.commit()

    # Return updated user
    return await read_user(user_id, db, current_user)


@router.delete("/{user_id}")
async def delete_user(
    user_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> Any:
    """
    Delete user (soft delete - mark as inactive)
    """
    # Check if user exists
    existing = await db.execute(
        "SELECT * FROM users WHERE id = $1",
        (user_id,)
    )

    if not existing.fetchone():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    # Soft delete - mark as inactive
    await db.execute(
        "UPDATE users SET is_active = false, updated_at = NOW() WHERE id = $1",
        (user_id,)
    )

    await db.commit()

    return {"message": "User deleted successfully"}