"""
Main application file for Proyecto Semilla Backend
FastAPI application with multi-tenant support
"""

from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware

from app.core.config import settings
from app.core.database import create_tables
from app.api.v1.router import api_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Lifespan context manager for FastAPI application
    Handles startup and shutdown events
    """
    # Startup
    print("🚀 Starting Proyecto Semilla Backend...")

    # Create database tables
    await create_tables()

    print("✅ Backend started successfully!")

    yield

    # Shutdown
    print("🛑 Shutting down Proyecto Semilla Backend...")


# Create FastAPI application
app = FastAPI(
    title="Proyecto Semilla API",
    description="Backend API for Proyecto Semilla - Multi-tenant SaaS platform",
    version="0.1.0",
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan,
)

# Set up CORS
if settings.BACKEND_CORS_ORIGINS:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=[str(origin) for origin in settings.BACKEND_CORS_ORIGINS],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

# Add trusted host middleware
if not settings.DEBUG:
    app.add_middleware(
        TrustedHostMiddleware,
        allowed_hosts=settings.ALLOWED_HOSTS,
    )

# Include API routers
app.include_router(api_router, prefix=settings.API_V1_STR)


@app.get("/health")
async def health_check():
    """
    Health check endpoint
    """
    return {"status": "healthy", "version": "0.1.0"}


@app.get("/")
async def root():
    """
    Root endpoint
    """
    return {
        "message": "Welcome to Proyecto Semilla API",
        "version": "0.1.0",
        "docs": "/docs",
        "health": "/health"
    }


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )