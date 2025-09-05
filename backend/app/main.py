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
from app.core.logging import setup_logging
from app.core.middleware import tenant_context_middleware, rate_limiting_middleware, logging_middleware
from app.core.rate_limiting import RateLimitMiddleware, configure_default_limits
from app.core.audit_logging import init_audit_logging, shutdown_audit_logging, log_request_middleware
from app.middleware.compression import AdvancedCompressionMiddleware, HTTP2ServerPushMiddleware
from app.api.v1.router import api_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Lifespan context manager for FastAPI application
    Handles startup and shutdown events
    """
    # Startup
    print("🚀 Starting Proyecto Semilla Backend...")

    # Setup structured logging
    setup_logging()

    # Create database tables
    await create_tables()

    # Initialize audit logging
    await init_audit_logging()

    print("✅ Backend started successfully!")

    yield

    # Shutdown
    print("🛑 Shutting down Proyecto Semilla Backend...")

    # Shutdown audit logging
    await shutdown_audit_logging()


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

# Add custom middleware
app.middleware("http")(logging_middleware)
app.middleware("http")(rate_limiting_middleware)
app.middleware("http")(tenant_context_middleware)
app.middleware("http")(log_request_middleware)

# Add performance middleware (Sprint 5)
app.add_middleware(AdvancedCompressionMiddleware, minimum_size=1000)
app.add_middleware(HTTP2ServerPushMiddleware)

# Add security middleware (Sprint 5 Day 5)
app.add_middleware(RateLimitMiddleware)

# Configure default rate limits
configure_default_limits()

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
        port=7777,
        reload=True,
        log_level="info"
    )