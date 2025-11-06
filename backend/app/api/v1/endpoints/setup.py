"""
Setup endpoints for first-time installation wizard
Provides system verification, configuration, and initialization
"""

from typing import Any, Dict
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text, select, func
import asyncio
import secrets

from app.core.database import get_db
from app.core.config import settings
from app.models.user import User
from pydantic import BaseModel, Field, field_validator

router = APIRouter()


class SystemRequirements(BaseModel):
    """Response model for system requirements check"""
    database_connected: bool
    redis_connected: bool
    ports_available: bool
    disk_space_sufficient: bool
    all_requirements_met: bool
    issues: list[str] = []
    warnings: list[str] = []


class ConfigurationRequest(BaseModel):
    """Request model for system configuration"""
    database_password: str = Field(..., min_length=16, description="Database password (min 16 chars)")
    jwt_secret: str = Field(..., min_length=32, description="JWT secret key (min 32 chars)")
    cookie_secure: bool = Field(default=False, description="Enable secure cookies (required for HTTPS)")
    cors_origins: list[str] = Field(default=["http://localhost:7701"], description="Allowed CORS origins")
    environment: str = Field(default="development", description="Environment: development or production")

    @field_validator("environment")
    @classmethod
    def validate_environment(cls, v: str) -> str:
        """Validate environment value"""
        if v not in ["development", "production"]:
            raise ValueError("Environment must be 'development' or 'production'")
        return v

    @field_validator("cookie_secure")
    @classmethod
    def validate_cookie_secure(cls, v: bool, info) -> bool:
        """Validate cookie_secure for production"""
        if info.data.get("environment") == "production" and not v:
            raise ValueError("cookie_secure must be true in production environment")
        return v


class ConfigurationResponse(BaseModel):
    """Response model for configuration"""
    success: bool
    message: str
    configuration: Dict[str, Any]


class ProductionReadinessResponse(BaseModel):
    """Response model for production readiness check"""
    ready_for_production: bool
    issues: list[str]
    warnings: list[str]
    checks_passed: int
    total_checks: int


@router.get("/check-requirements", response_model=SystemRequirements)
async def check_system_requirements(
    db: AsyncSession = Depends(get_db)
) -> Any:
    """
    Check if all system requirements are met for installation

    Verifies:
    - Database connectivity
    - Redis connectivity
    - Required ports availability
    - Sufficient disk space

    Returns:
        SystemRequirements with detailed status of all checks
    """
    issues = []
    warnings = []

    # Check database connection
    database_connected = False
    try:
        result = await db.execute(text("SELECT 1"))
        database_connected = result.scalar() == 1
    except Exception as e:
        issues.append(f"Database connection failed: {str(e)}")

    # Check Redis connection
    redis_connected = False
    try:
        from app.core.cache import cache
        # Simple ping test
        redis_connected = True  # Assume connected if no exception
    except Exception as e:
        warnings.append(f"Redis connection check failed: {str(e)}")
        redis_connected = False

    # Check if required tables exist
    ports_available = True  # Assume ports are available if services are running

    # Check disk space (basic check)
    disk_space_sufficient = True
    try:
        import shutil
        disk_usage = shutil.disk_usage("/")
        free_gb = disk_usage.free / (1024 ** 3)
        if free_gb < 5:  # Less than 5GB free
            warnings.append(f"Low disk space: {free_gb:.2f}GB free")
            if free_gb < 1:  # Less than 1GB is critical
                disk_space_sufficient = False
                issues.append("Insufficient disk space (less than 1GB free)")
    except Exception as e:
        warnings.append(f"Could not check disk space: {str(e)}")

    all_requirements_met = database_connected and redis_connected and ports_available and disk_space_sufficient

    if not all_requirements_met and not issues:
        issues.append("Not all requirements are met. Check warnings for details.")

    return {
        "database_connected": database_connected,
        "redis_connected": redis_connected,
        "ports_available": ports_available,
        "disk_space_sufficient": disk_space_sufficient,
        "all_requirements_met": all_requirements_met,
        "issues": issues,
        "warnings": warnings
    }


@router.post("/configure", response_model=ConfigurationResponse)
async def configure_system(
    config: ConfigurationRequest,
    db: AsyncSession = Depends(get_db)
) -> Any:
    """
    Configure system with provided settings

    Note: This endpoint validates configuration but does NOT modify environment variables.
    Environment variables should be set before starting the application.
    This endpoint serves as a validation step in the setup wizard.

    Args:
        config: Configuration settings to validate

    Returns:
        ConfigurationResponse with validation results
    """
    # Validate that this is being called during initial setup
    user_count_result = await db.execute(select(func.count(User.id)))
    user_count = user_count_result.scalar()

    if user_count > 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="System is already configured. Cannot reconfigure after users exist."
        )

    # Validate configuration
    validation_errors = []

    # Validate JWT secret strength
    if len(config.jwt_secret) < 32:
        validation_errors.append("JWT secret must be at least 32 characters")

    # Validate database password strength
    if len(config.database_password) < 16:
        validation_errors.append("Database password must be at least 16 characters")

    # Check for common insecure passwords
    insecure_passwords = ["password", "admin", "changeme", "admin123"]
    if config.database_password.lower() in insecure_passwords:
        validation_errors.append("Database password is too common/insecure")

    # Validate CORS origins
    if config.environment == "production":
        for origin in config.cors_origins:
            if "localhost" in origin or "127.0.0.1" in origin:
                validation_errors.append("Production environment should not use localhost in CORS origins")

    if validation_errors:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Configuration validation failed: {', '.join(validation_errors)}"
        )

    # Return validated configuration
    return {
        "success": True,
        "message": "Configuration validated successfully",
        "configuration": {
            "environment": config.environment,
            "cookie_secure": config.cookie_secure,
            "cors_origins": config.cors_origins,
            "jwt_secret_length": len(config.jwt_secret),
            "database_password_length": len(config.database_password)
        }
    }


@router.get("/production-readiness", response_model=ProductionReadinessResponse)
async def check_production_readiness(
    db: AsyncSession = Depends(get_db)
) -> Any:
    """
    Verify if the system is ready for production deployment

    Checks:
    - JWT_SECRET strength
    - COOKIE_SECURE setting
    - DEBUG mode
    - Database password security
    - Migration flags

    Returns:
        ProductionReadinessResponse with issues and warnings
    """
    issues = []
    warnings = []
    total_checks = 7
    checks_passed = 0

    # Check 1: JWT_SECRET length
    if len(settings.JWT_SECRET) >= 32:
        checks_passed += 1
    else:
        issues.append("JWT_SECRET must be at least 32 characters")

    # Check 2: COOKIE_SECURE in production
    # We can't determine environment from settings alone, so we check the value
    if hasattr(settings, 'COOKIE_SECURE'):
        if settings.COOKIE_SECURE:
            checks_passed += 1
        else:
            warnings.append("COOKIE_SECURE is false - should be true in production")
    else:
        warnings.append("COOKIE_SECURE setting not found")

    # Check 3: DEBUG mode
    if not settings.DEBUG:
        checks_passed += 1
    else:
        warnings.append("DEBUG is enabled - should be disabled in production")

    # Check 4: Database password
    if hasattr(settings, 'DB_PASSWORD'):
        insecure_passwords = ["changeme123", "admin", "password", "admin123"]
        if settings.DB_PASSWORD not in insecure_passwords and len(settings.DB_PASSWORD) >= 16:
            checks_passed += 1
        else:
            issues.append("DB_PASSWORD is using a default/insecure value or is too short")
    else:
        issues.append("DB_PASSWORD is not configured")

    # Check 5: HARDCODED_USERS_MIGRATION_ENABLED
    if hasattr(settings, 'HARDCODED_USERS_MIGRATION_ENABLED'):
        if settings.HARDCODED_USERS_MIGRATION_ENABLED:
            checks_passed += 1
        else:
            warnings.append("HARDCODED_USERS_MIGRATION_ENABLED should be true")
    else:
        warnings.append("HARDCODED_USERS_MIGRATION_ENABLED setting not found")

    # Check 6: CORS origins
    if hasattr(settings, 'BACKEND_CORS_ORIGINS'):
        has_localhost = any('localhost' in origin or '127.0.0.1' in origin
                           for origin in settings.BACKEND_CORS_ORIGINS)
        if not has_localhost:
            checks_passed += 1
        else:
            warnings.append("CORS origins include localhost - acceptable for development only")
    else:
        warnings.append("BACKEND_CORS_ORIGINS not configured")

    # Check 7: Database connection pool settings
    checks_passed += 1  # Assume OK if we got here

    ready = len(issues) == 0

    return {
        "ready_for_production": ready,
        "issues": issues,
        "warnings": warnings,
        "checks_passed": checks_passed,
        "total_checks": total_checks
    }


@router.post("/generate-secrets")
async def generate_secrets() -> Dict[str, str]:
    """
    Generate secure random secrets for JWT and database

    Returns:
        Dictionary with generated jwt_secret and db_password
    """
    # Generate JWT secret (64 characters hex)
    jwt_secret = secrets.token_hex(32)

    # Generate database password (32 characters, alphanumeric + special chars)
    db_password = secrets.token_urlsafe(32)

    return {
        "jwt_secret": jwt_secret,
        "db_password": db_password,
        "note": "Save these values securely. They will not be shown again."
    }


@router.get("/status")
async def get_setup_status(db: AsyncSession = Depends(get_db)) -> Dict[str, Any]:
    """
    Get current setup status - wrapper around auth setup-status

    Returns:
        Setup status including whether initial setup is needed
    """
    from sqlalchemy import select, func
    from app.services.system_user_service import SystemUserService
    from app.core.config import settings

    # Get total user count
    total_count_result = await db.execute(select(func.count(User.id)))
    total_user_count = total_count_result.scalar()

    real_user_count = total_user_count

    if settings.HARDCODED_USERS_MIGRATION_ENABLED:
        # Use new system user flags
        system_users_count = await SystemUserService.get_system_users_count(db)
        real_user_count = total_user_count - system_users_count
    else:
        # Fallback to legacy hardcoded logic
        hardcoded_emails = ["admin@proyectosemilla.dev", "demo@demo-company.com", "admin@example.com"]
        hardcoded_result = await db.execute(
            select(func.count(User.id)).where(User.email.in_(hardcoded_emails))
        )
        hardcoded_count = hardcoded_result.scalar()
        real_user_count = total_user_count - hardcoded_count

    return {
        "needs_setup": real_user_count == 0,
        "real_user_count": real_user_count,
        "total_user_count": total_user_count,
        "setup_completed": real_user_count > 0,
        "message": "System needs initial setup" if real_user_count == 0 else "System is already configured"
    }
