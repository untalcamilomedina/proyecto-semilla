"""
User CRUD endpoints
User management with tenant isolation
"""

from typing import Any, List
from uuid import UUID
import math

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.security import get_current_user
from app.core.permissions import Permission, PermissionChecker
from app.models.user import User
from app.schemas.user import UserCreate, UserUpdate, UserResponse
from app.schemas.pagination import PaginatedResponse, PaginationMetadata
from app.crud import crud_user

router = APIRouter()


@router.get(
    "/",
    response_model=PaginatedResponse[UserResponse],
    dependencies=[Depends(PermissionChecker(Permission.USER_READ))]
)
async def read_users(
    db: AsyncSession = Depends(get_db),
    page: int = Query(1, ge=1, description="Page number (1-indexed)"),
    page_size: int = Query(20, ge=1, le=100, description="Number of items per page"),
    current_user: User = Depends(get_current_user),
) -> Any:
    """
    Retrieve users with pagination.
    Returns paginated list of users with metadata.
    Requires: user:read permission
    """
    # Calculate skip based on page
    skip = (page - 1) * page_size

    # Get total count and users
    total = await crud_user.count_users(db)
    users = await crud_user.get_users(db, skip=skip, limit=page_size)

    # Calculate pagination metadata
    total_pages = math.ceil(total / page_size) if total > 0 else 0

    metadata = PaginationMetadata(
        total=total,
        page=page,
        page_size=page_size,
        total_pages=total_pages,
        has_next=page < total_pages,
        has_previous=page > 1
    )

    return PaginatedResponse(items=users, metadata=metadata)


@router.post(
    "/",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(PermissionChecker(Permission.USER_CREATE))]
)
async def create_user(
    *,
    db: AsyncSession = Depends(get_db),
    user_in: UserCreate,
    current_user: User = Depends(get_current_user),
) -> Any:
    """
    Create new user.
    Requires: user:create permission
    """
    user = await crud_user.get_user_by_email(db, email=user_in.email)
    if user:
        raise HTTPException(
            status_code=400,
            detail="The user with this email already exists in the system.",
        )
    user = await crud_user.create_user(db, obj_in=user_in)
    return user


@router.get(
    "/{user_id}",
    response_model=UserResponse,
    dependencies=[Depends(PermissionChecker(Permission.USER_READ))]
)
async def read_user(
    *,
    db: AsyncSession = Depends(get_db),
    user_id: UUID,
    current_user: User = Depends(get_current_user),
) -> Any:
    """
    Get user by ID.
    Requires: user:read permission
    """
    user = await crud_user.get_user(db, user_id=user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user


@router.put(
    "/{user_id}",
    response_model=UserResponse,
    dependencies=[Depends(PermissionChecker(Permission.USER_UPDATE))]
)
async def update_user(
    *,
    db: AsyncSession = Depends(get_db),
    user_id: UUID,
    user_in: UserUpdate,
    current_user: User = Depends(get_current_user),
) -> Any:
    """
    Update a user.
    Requires: user:update permission
    """
    user = await crud_user.get_user(db, user_id=user_id)
    if not user:
        raise HTTPException(
            status_code=404,
            detail="The user with this ID does not exist in the system",
        )
    user = await crud_user.update_user(db, db_obj=user, obj_in=user_in)
    return user


@router.delete(
    "/{user_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    dependencies=[Depends(PermissionChecker(Permission.USER_DELETE))]
)
async def delete_user(
    *,
    db: AsyncSession = Depends(get_db),
    user_id: UUID,
    current_user: User = Depends(get_current_user),
) -> None:
    """
    Delete a user.
    Requires: user:delete permission
    """
    user = await crud_user.get_user(db, user_id=user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    await crud_user.delete_user(db, db_obj=user)