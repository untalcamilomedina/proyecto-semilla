"""
Main router for API v1
Combines all endpoint routers
"""

from fastapi import APIRouter

from app.api.v1.endpoints import auth, health, tenants, users, roles

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