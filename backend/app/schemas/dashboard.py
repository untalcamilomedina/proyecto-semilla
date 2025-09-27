"""Schemas para endpoints del dashboard administrativo"""

from typing import List

from pydantic import BaseModel


class DashboardMetrics(BaseModel):
    """Resumen de métricas principales para el dashboard."""

    user_count: int
    tenant_count: int
    role_count: int


class UsersOverTimeEntry(BaseModel):
    """Entrada con conteo de usuarios agrupados por fecha."""

    date: str
    count: int


class RecentUserEntry(BaseModel):
    """Información simplificada de usuarios recientes."""

    id: str
    tenant_id: str
    email: str
    first_name: str | None = None
    last_name: str | None = None
    full_name: str | None = None
    is_active: bool
    role_ids: List[str]
    created_at: str | None = None
    updated_at: str | None = None

