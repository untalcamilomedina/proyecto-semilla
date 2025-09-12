"""
import jsonMain application file for Proyecto Semilla Backend
FastAPI application with multi-tenant support
"""

from contextlib import asynccontextmanager
import json
import logging
from fastapi import FastAPI, WebSocket
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware

from app.core.config import settings
from app.core.database import create_tables, get_db
from app.core.logging import setup_logging
from app.core.middleware import tenant_context_middleware, rate_limiting_middleware, logging_middleware
from app.core.rate_limiting import RateLimitMiddleware, configure_default_limits
from app.core.audit_logging import init_audit_logging, shutdown_audit_logging, log_request_middleware
from app.middleware.compression import AdvancedCompressionMiddleware, HTTP2ServerPushMiddleware
from app.api.v1.router import api_router
from app.websocket.collaboration import collaboration_manager
from app.plugins import initialize_plugin_system, get_plugin_system_status

# Setup logger
logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Lifespan context manager for FastAPI application
    Handles startup and shutdown events
    """
    # Startup
    print("🚀 Starting Proyecto Semilla Backend...")
    print(f"DATABASE_URL: {settings.DATABASE_URL}")

    # Setup structured logging
    setup_logging()

    # Create database tables
    await create_tables()

    # Initialize audit logging
    # await init_audit_logging()

    # Initialize plugin system
    print("🔌 Initializing Plugin System...")
    db_session = await get_db().__anext__()
    try:
        integration_results = await initialize_plugin_system(app, db_session)
        print(f"✅ Plugin system initialized with {len(integration_results)} modules")
    except Exception as e:
        print(f"⚠️  Plugin system initialization failed: {e}")
    finally:
        await db_session.close()

    print("✅ Backend started successfully!")

    yield

    # Shutdown
    print("🛑 Shutting down Proyecto Semilla Backend...")

    # Shutdown audit logging
    # await shutdown_audit_logging()


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
# app.middleware("http")(log_request_middleware)

# Add performance middleware (Sprint 5)
app.add_middleware(AdvancedCompressionMiddleware, minimum_size=1000)
app.add_middleware(HTTP2ServerPushMiddleware)

# Add security middleware (Sprint 5 Day 5)
app.add_middleware(RateLimitMiddleware)

# Add CORS middleware LAST so it executes FIRST (middleware stack is reversed)
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.BACKEND_CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["DELETE", "GET", "HEAD", "OPTIONS", "PATCH", "POST", "PUT"],
    allow_headers=["*"],
    expose_headers=["*"],
    max_age=600,
)

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


# Plugin Management Endpoints
from fastapi import Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

@app.get("/api/v1/plugins/status")
async def get_plugins_status():
    """
    Get plugin system status
    """
    try:
        status = await get_plugin_system_status()
        return status
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get plugin status: {e}")


@app.get("/api/v1/plugins/")
async def list_plugins():
    """
    List all available plugins
    """
    try:
        from app.plugins import get_plugin_manager
        manager = await get_plugin_manager()
        plugins = manager.list_modules()
        return {"plugins": plugins}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to list plugins: {e}")


@app.post("/api/v1/plugins/{module_name}/install")
async def install_plugin(module_name: str):
    """
    Install and integrate a specific plugin
    """
    try:
        from app.plugins import get_plugin_manager, get_module_registry
        manager = await get_plugin_manager()
        registry = await get_module_registry()

        # Load and integrate module
        loaded = await manager.load_module(module_name)
        if not loaded:
            raise HTTPException(status_code=400, detail=f"Failed to load module {module_name}")

        # Get module metadata
        metadata = manager.modules.get(module_name)
        if not metadata:
            raise HTTPException(status_code=404, detail=f"Module metadata not found for {module_name}")

        # Integrate module
        result = await manager.integrate_module(module_name, app)
        if not result.success:
            raise HTTPException(status_code=400, detail=f"Failed to integrate module {module_name}: {result.errors}")

        # Register in registry
        module_record = await registry.get_module(module_name)
        if not module_record:
            # Create module record if it doesn't exist
            from pathlib import Path
            module_path = Path(f"modules/{module_name}")
            module_record = await registry.register_module(module_path)

        await registry.install_module(module_name)

        return {
            "message": f"Module {module_name} installed successfully",
            "integration_result": {
                "routes_registered": result.routes_registered,
                "models_registered": result.models_registered,
                "services_registered": result.services_registered,
                "migrations_applied": result.migrations_applied
            }
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to install plugin {module_name}: {e}")


@app.post("/api/v1/plugins/{module_name}/test")
async def test_plugin(module_name: str):
    """
    Run integration tests for a specific plugin
    """
    try:
        from app.plugins import get_plugin_manager, run_module_integration_tests
        from fastapi.testclient import TestClient

        manager = await get_plugin_manager()
        metadata = manager.modules.get(module_name)

        if not metadata:
            raise HTTPException(status_code=404, detail=f"Module {module_name} not found")

        # Create test client
        client = TestClient(app)

        # Get module record
        from app.plugins import get_module_registry
        registry = await get_module_registry()
        module_record = await registry.get_module(module_name)

        if not module_record:
            raise HTTPException(status_code=404, detail=f"Module record not found for {module_name}")

        # Run integration tests
        test_suite = await run_module_integration_tests(module_record, metadata)

        return {
            "module_name": module_name,
            "tests_run": test_suite.total_tests,
            "tests_passed": test_suite.passed_tests,
            "tests_failed": test_suite.failed_tests,
            "success_rate": (test_suite.passed_tests / test_suite.total_tests * 100) if test_suite.total_tests > 0 else 0,
            "total_duration": test_suite.total_duration,
            "test_results": [
                {
                    "test_name": test.test_name,
                    "description": test.description,
                    "success": test.success,
                    "duration": test.duration,
                    "error_message": test.error_message,
                    "details": test.details
                }
                for test in test_suite.tests
            ]
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to test plugin {module_name}: {e}")


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
# WebSocket endpoints for real-time collaboration
@app.websocket("/ws/rooms/{room_id}")
async def websocket_room_endpoint(websocket: WebSocket, room_id: str):
    """WebSocket endpoint for real-time collaboration in rooms"""
    try:
        # Extract user info from query parameters (in production, use proper auth)
        user_id = websocket.query_params.get("user_id", "anonymous")
        user_name = websocket.query_params.get("user_name", "Anonymous User")

        await collaboration_manager.connect_to_room(websocket, room_id, user_id, user_name)

        while True:
            try:
                data = await websocket.receive_text()
                message = json.loads(data)
                await collaboration_manager.handle_message(room_id, user_id, message)
            except json.JSONDecodeError:
                await websocket.send_json({"error": "Invalid JSON format"})
            except Exception as e:
                logger.error(f"Error handling message: {e}")
                break

    except Exception as e:
        logger.error(f"WebSocket error: {e}")
    finally:
        await collaboration_manager.disconnect_from_room(room_id, user_id)

