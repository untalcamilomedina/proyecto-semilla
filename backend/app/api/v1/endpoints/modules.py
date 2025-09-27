"""
Module management API endpoints
Provides REST API for MCP module lifecycle management
"""

from typing import Any, List
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.security import get_current_user
from app.models.user import User
from app.services.module_service import ModuleService
from app.modules.manager import module_manager
from app.schemas.module import (
    ModuleResponse, ModuleInstallRequest, ModuleActionResponse,
    ModuleHealthResponse, ModuleDiscoveryResponse, ModuleListResponse,
    ModuleConfigUpdateRequest, ModuleReloadResponse
)

router = APIRouter()


@router.get("/", response_model=ModuleListResponse)
async def list_modules(
    db: AsyncSession = Depends(get_db),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    status_filter: str = Query(None, description="Filter by status"),
    current_user: User = Depends(get_current_user),
) -> Any:
    """
    List modules for the current tenant.
    """
    modules = await ModuleService.get_modules(str(current_user.tenant_id), db, skip, limit)

    # Apply status filter if provided
    if status_filter:
        modules = [m for m in modules if m.status == status_filter]

    return ModuleListResponse(
        modules=[ModuleResponse.from_orm(module) for module in modules],
        total=len(modules),
        skip=skip,
        limit=limit
    )


@router.post("/install", response_model=ModuleActionResponse)
async def install_module(
    *,
    db: AsyncSession = Depends(get_db),
    install_request: ModuleInstallRequest,
    current_user: User = Depends(get_current_user),
) -> Any:
    """
    Install a module for the current tenant.
    """
    result = await module_manager.install_module(
        current_user.tenant_id,
        install_request.name,
        install_request.version,
        install_request.config
    )

    if not result["success"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=result.get("error", "Installation failed")
        )

    return ModuleActionResponse(
        success=True,
        message=result["message"],
        module=ModuleResponse.from_orm(result["module"]) if result.get("module") else None
    )


@router.post("/{module_id}/activate", response_model=ModuleActionResponse)
async def activate_module(
    *,
    db: AsyncSession = Depends(get_db),
    module_id: UUID,
    current_user: User = Depends(get_current_user),
) -> Any:
    """
    Activate a module.
    """
    result = await module_manager.activate_module(current_user.tenant_id, module_id)

    if not result["success"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=result.get("error", "Activation failed")
        )

    return ModuleActionResponse(
        success=True,
        message=result["message"],
        module=ModuleResponse.from_orm(result["module"]) if result.get("module") else None
    )


@router.post("/{module_id}/deactivate", response_model=ModuleActionResponse)
async def deactivate_module(
    *,
    db: AsyncSession = Depends(get_db),
    module_id: UUID,
    current_user: User = Depends(get_current_user),
) -> Any:
    """
    Deactivate a module.
    """
    result = await module_manager.deactivate_module(current_user.tenant_id, module_id)

    if not result["success"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=result.get("error", "Deactivation failed")
        )

    return ModuleActionResponse(
        success=True,
        message=result["message"],
        module=ModuleResponse.from_orm(result["module"]) if result.get("module") else None
    )


@router.delete("/{module_id}", response_model=ModuleActionResponse)
async def uninstall_module(
    *,
    db: AsyncSession = Depends(get_db),
    module_id: UUID,
    current_user: User = Depends(get_current_user),
) -> Any:
    """
    Uninstall a module.
    """
    # Check if module exists and belongs to tenant
    module = await ModuleService.get_module_by_id(module_id, current_user.tenant_id, db)
    if not module:
        raise HTTPException(status_code=404, detail="Module not found")

    result = await module_manager.deactivate_module(current_user.tenant_id, module_id)
    if not result["success"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Deactivation failed: {result.get('error')}"
        )

    # Uninstall via service
    success = await ModuleService.uninstall_module(module_id, current_user.tenant_id, db)

    if not success:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Uninstallation failed"
        )

    return ModuleActionResponse(
        success=True,
        message=f"Module {module.name} uninstalled successfully"
    )


@router.put("/{module_id}/config", response_model=ModuleActionResponse)
async def update_module_config(
    *,
    db: AsyncSession = Depends(get_db),
    module_id: UUID,
    config_request: ModuleConfigUpdateRequest,
    current_user: User = Depends(get_current_user),
) -> Any:
    """
    Update module configuration.
    """
    result = await module_manager.update_module_config(
        current_user.tenant_id,
        module_id,
        config_request.config
    )

    if not result["success"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=result.get("error", "Configuration update failed")
        )

    return ModuleActionResponse(
        success=True,
        message=result["message"]
    )


@router.post("/{module_id}/reload", response_model=ModuleReloadResponse)
async def reload_module(
    *,
    db: AsyncSession = Depends(get_db),
    module_id: UUID,
    current_user: User = Depends(get_current_user),
) -> Any:
    """
    Hot-reload a module.
    """
    from datetime import datetime

    result = await module_manager.reload_module(current_user.tenant_id, module_id)

    if not result["success"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=result.get("error", "Reload failed")
        )

    return ModuleReloadResponse(
        success=True,
        message=result["message"],
        reloaded_at=datetime.utcnow(),
        changes_detected=result.get("changes_detected", False)
    )


@router.get("/{module_id}/health", response_model=ModuleHealthResponse)
async def get_module_health(
    *,
    db: AsyncSession = Depends(get_db),
    module_id: UUID,
    current_user: User = Depends(get_current_user),
) -> Any:
    """
    Get module health status.
    """
    health = await module_manager.get_module_health(current_user.tenant_id, module_id)

    if not health:
        raise HTTPException(status_code=404, detail="Module not found")

    return ModuleHealthResponse(**health)


@router.get("/discovery", response_model=List[ModuleDiscoveryResponse])
async def discover_modules(
    category: str = Query(None, description="Filter by category"),
    limit: int = Query(50, ge=1, le=200),
    current_user: User = Depends(get_current_user),
) -> Any:
    """
    Discover available modules from registry.
    """
    modules = await module_manager.discover_modules()

    # Apply category filter if provided
    if category:
        modules = [m for m in modules if category in m.get("categories", [])]

    return [ModuleDiscoveryResponse(**module) for module in modules[:limit]]


@router.get("/active", response_model=List[ModuleResponse])
async def get_active_modules(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> Any:
    """
    Get all active modules for the current tenant.
    """
    modules = await module_manager.get_active_modules(current_user.tenant_id)
    return [ModuleResponse.from_orm(module) for module in modules]


@router.get("/{module_id}", response_model=ModuleResponse)
async def get_module(
    *,
    db: AsyncSession = Depends(get_db),
    module_id: UUID,
    current_user: User = Depends(get_current_user),
) -> Any:
    """
    Get a specific module by ID.
    """
    module = await ModuleService.get_module_by_id(module_id, current_user.tenant_id, db)
    if not module:
        raise HTTPException(status_code=404, detail="Module not found")

    return ModuleResponse.from_orm(module)


@router.get("/by-name/{name}", response_model=ModuleResponse)
async def get_module_by_name(
    *,
    db: AsyncSession = Depends(get_db),
    name: str,
    current_user: User = Depends(get_current_user),
) -> Any:
    """
    Get a module by name.
    """
    module = await ModuleService.get_module_by_name(name, str(current_user.tenant_id), db)
    if not module:
        raise HTTPException(status_code=404, detail="Module not found")

    return ModuleResponse.from_orm(module)