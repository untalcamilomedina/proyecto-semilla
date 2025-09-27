"""
Main router for API v1
Combines all endpoint routers
"""

from fastapi import APIRouter

from app.api.v1.endpoints import auth, health, tenants, users, roles, dashboard, rate_limiting, analytics, modules
from app.routers.collaboration import router as collaboration_router
# Create main API router
api_router = APIRouter()

# Include endpoint routers
api_router.include_router(
    health.router,
    prefix="",
    tags=["health"]
)

api_router.include_router(
    auth.router,
    prefix="/auth",
    tags=["authentication"]
)

api_router.include_router(
    tenants.router,
    prefix="/tenants",
    tags=["tenants"]
)

api_router.include_router(
    users.router,
    prefix="/users",
    tags=["users"]
)

api_router.include_router(
    roles.router,
    prefix="/roles",
    tags=["roles"]
)


api_router.include_router(
    collaboration_router,
    prefix="",
    tags=["collaboration"]
)

api_router.include_router(
    dashboard.router,
    prefix="/dashboard",
    tags=["dashboard"]
)


api_router.include_router(
    rate_limiting.router,
    prefix="/rate-limiting",
    tags=["rate-limiting"]
)

api_router.include_router(
    analytics.router,
    prefix="/analytics",
    tags=["analytics"]
)

api_router.include_router(
    modules.router,
    prefix="/modules",
    tags=["modules"]
)
