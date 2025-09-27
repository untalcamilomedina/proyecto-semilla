"""Endpoints para métricas del dashboard administrativo"""

from datetime import datetime, timedelta

from fastapi import APIRouter, Depends
from sqlalchemy import asc, func, select, text
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.core.database import get_db
from app.core.security import get_current_user_from_cookie
from app.models.role import Role
from app.models.user import User
from app.schemas.dashboard import (
    DashboardMetrics,
    RecentUserEntry,
    UsersOverTimeEntry,
)

router = APIRouter()


@router.get("/metrics", response_model=DashboardMetrics)
async def get_dashboard_metrics(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user_from_cookie),
) -> DashboardMetrics:
    """Devuelve métricas principales para tarjetas del dashboard."""

    del current_user  # Autenticación ya verificada

    user_count_result = await db.execute(select(func.count(User.id)))
    user_count = int(user_count_result.scalar() or 0)

    tenant_count_result = await db.execute(text("SELECT COUNT(*) FROM tenants"))
    tenant_count = int(tenant_count_result.scalar() or 0)

    role_count_result = await db.execute(select(func.count(Role.id)))
    role_count = int(role_count_result.scalar() or 0)

    return DashboardMetrics(
        user_count=user_count,
        tenant_count=tenant_count,
        role_count=role_count,
    )


@router.get("/users-over-time", response_model=list[UsersOverTimeEntry])
async def get_users_over_time(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user_from_cookie),
) -> list[UsersOverTimeEntry]:
    """Devuelve conteo de usuarios creados por día (últimos 30 días)."""

    del current_user

    since = datetime.utcnow() - timedelta(days=30)
    stmt = (
        select(func.date_trunc("day", User.created_at).label("day"), func.count(User.id))
        .where(User.created_at >= since)
        .group_by("day")
        .order_by(asc("day"))
    )

    result = await db.execute(stmt)
    entries: list[UsersOverTimeEntry] = []
    for day, count in result.all():
        # Convierte fecha a cadena ISO (solo fecha)
        day_str = day.date().isoformat() if isinstance(day, datetime) else str(day)
        entries.append(UsersOverTimeEntry(date=day_str, count=int(count or 0)))

    return entries


@router.get("/recent-users", response_model=list[RecentUserEntry])
async def get_recent_users(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user_from_cookie),
) -> list[RecentUserEntry]:
    """Devuelve usuarios creados recientemente."""

    del current_user

    stmt = (
        select(User)
        .options(selectinload(User.user_roles))
        .order_by(User.created_at.desc())
        .limit(10)
    )

    result = await db.execute(stmt)
    users = result.scalars().all()

    recent_users: list[RecentUserEntry] = []
    for user in users:
        role_ids = [str(user_role.role_id) for user_role in (user.user_roles or [])]
        recent_users.append(
            RecentUserEntry(
                id=str(user.id),
                tenant_id=str(user.tenant_id),
                email=user.email,
                first_name=user.first_name,
                last_name=user.last_name,
                full_name=user.full_name,
                is_active=user.is_active,
                role_ids=role_ids,
                created_at=user.created_at.isoformat() if user.created_at else None,
                updated_at=user.updated_at.isoformat() if user.updated_at else None,
            )
        )

    return recent_users
