"""
CRUD operations for User model
"""
from typing import Any, Dict, List, Optional, Union
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload

from app.models.user import User
from app.schemas.user import UserCreate, UserUpdate
from app.core.security import get_password_hash


async def get_user(db: AsyncSession, user_id: UUID) -> Optional[User]:
    """Get a user by ID"""
    result = await db.execute(select(User).filter(User.id == user_id))
    return result.scalars().first()

async def get_user_by_email(db: AsyncSession, email: str) -> Optional[User]:
    """Get a user by email"""
    result = await db.execute(select(User).filter(User.email == email))
    return result.scalars().first()

async def get_users(db: AsyncSession, skip: int = 0, limit: int = 100) -> List[User]:
    """Get all users"""
    result = await db.execute(
        select(User)
        .order_by(User.created_at.desc())
        .offset(skip)
        .limit(limit)
    )
    return result.scalars().all()

async def create_user(db: AsyncSession, *, obj_in: UserCreate) -> User:
    """Create a new user"""
    hashed_password = get_password_hash(obj_in.password)
    db_obj = User(
        email=obj_in.email,
        hashed_password=hashed_password,
        first_name=obj_in.first_name,
        last_name=obj_in.last_name,
        full_name=f"{obj_in.first_name} {obj_in.last_name}",
        tenant_id=obj_in.tenant_id,
        is_active=True,
        is_verified=False, # Or based on your logic, e.g., email verification
    )
    db.add(db_obj)
    await db.commit()
    await db.refresh(db_obj)
    return db_obj

async def update_user(db: AsyncSession, *, db_obj: User, obj_in: Union[UserUpdate, Dict[str, Any]]) -> User:
    """Update a user"""
    if isinstance(obj_in, dict):
        update_data = obj_in
    else:
        update_data = obj_in.dict(exclude_unset=True)

    for field in update_data:
        if hasattr(db_obj, field):
            setattr(db_obj, field, update_data[field])
    
    if "first_name" in update_data or "last_name" in update_data:
        db_obj.full_name = f"{db_obj.first_name} {db_obj.last_name}"

    db.add(db_obj)
    await db.commit()
    await db.refresh(db_obj)
    return db_obj

async def delete_user(db: AsyncSession, *, db_obj: User) -> User:
    """Delete a user (soft delete)"""
    db_obj.is_active = False
    db.add(db_obj)
    await db.commit()
    await db.refresh(db_obj)
    return db_obj