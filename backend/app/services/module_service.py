"""
Module service for MCP (Model Context Protocol) system
Handles module lifecycle management, configuration, and discovery
"""

import asyncio
import importlib
import json
import os
import sys
from typing import Dict, List, Optional, Any
from uuid import UUID
from datetime import datetime

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text, select, update, delete
from sqlalchemy.orm import selectinload

from app.models.module import Module, ModuleConfiguration, ModuleVersion, ModuleRegistry
from app.core.config import settings


class ModuleService:
    """
    Service for handling MCP module operations
    """

    @staticmethod
    async def get_modules(tenant_id: UUID, db: AsyncSession, skip: int = 0, limit: int = 100) -> List[Module]:
        """
        Get all modules for a tenant
        """
        result = await db.execute(
            select(Module)
            .where(Module.tenant_id == tenant_id)
            .offset(skip)
            .limit(limit)
            .options(selectinload(Module.configurations))
        )
        return result.scalars().all()

    @staticmethod
    async def get_module_by_id(module_id: UUID, tenant_id: UUID, db: AsyncSession) -> Optional[Module]:
        """
        Get a specific module by ID
        """
        result = await db.execute(
            select(Module)
            .where(Module.id == module_id, Module.tenant_id == tenant_id)
            .options(selectinload(Module.configurations), selectinload(Module.versions))
        )
        return result.scalar_one_or_none()

    @staticmethod
    async def get_module_by_name(name: str, tenant_id: UUID, db: AsyncSession) -> Optional[Module]:
        """
        Get a module by name
        """
        result = await db.execute(
            select(Module)
            .where(Module.name == name, Module.tenant_id == tenant_id)
            .options(selectinload(Module.configurations))
        )
        return result.scalar_one_or_none()

    @staticmethod
    async def install_module(
        tenant_id: UUID,
        name: str,
        version: str,
        config_data: Optional[Dict[str, Any]] = None,
        db: AsyncSession = None
    ) -> Module:
        """
        Install a module for a tenant
        """
        # Check if module already exists
        existing = await ModuleService.get_module_by_name(name, tenant_id, db)
        if existing:
            if existing.status == "active":
                raise ValueError(f"Module {name} is already installed and active")
            elif existing.status == "installing":
                raise ValueError(f"Module {name} is currently being installed")

        # Get module info from registry
        registry_info = await ModuleService.get_module_from_registry(name, db)
        if not registry_info:
            raise ValueError(f"Module {name} not found in registry")

        # Validate version compatibility
        if not await ModuleService.validate_version_compatibility(name, version, db):
            raise ValueError(f"Version {version} is not compatible with current system")

        # Create or update module record
        if existing:
            module = existing
            module.version = version
            module.status = "installing"
            module.updated_at = datetime.utcnow()
        else:
            module = Module(
                tenant_id=tenant_id,
                name=name,
                display_name=registry_info.display_name,
                version=version,
                description=registry_info.description,
                author=registry_info.author,
                status="installing",
                config_schema=registry_info.config_schema,
                default_config=registry_info.default_config,
                dependencies=registry_info.dependencies,
                min_core_version=registry_info.min_core_version,
                max_core_version=registry_info.max_core_version
            )
            db.add(module)
            await db.flush()

        # Perform installation
        try:
            await ModuleService._perform_module_installation(module, db)

            # Create default configuration
            default_config = config_data or registry_info.default_config or {}
            config = ModuleConfiguration(
                module_id=module.id,
                tenant_id=tenant_id,
                config_data=default_config
            )
            db.add(config)

            module.status = "inactive"
            module.installed_at = datetime.utcnow()
            await db.commit()

            return module

        except Exception as e:
            module.status = "error"
            await db.commit()
            raise ValueError(f"Failed to install module {name}: {str(e)}")

    @staticmethod
    async def activate_module(module_id: UUID, tenant_id: UUID, db: AsyncSession) -> Module:
        """
        Activate a module
        """
        module = await ModuleService.get_module_by_id(module_id, tenant_id, db)
        if not module:
            raise ValueError("Module not found")

        if module.status != "inactive":
            raise ValueError(f"Module is not in inactive state (current: {module.status})")

        try:
            # Load and initialize module
            await ModuleService._load_module_runtime(module, db)

            module.status = "active"
            module.activated_at = datetime.utcnow()
            module.last_used_at = datetime.utcnow()
            await db.commit()

            return module

        except Exception as e:
            module.status = "error"
            await db.commit()
            raise ValueError(f"Failed to activate module {module.name}: {str(e)}")

    @staticmethod
    async def deactivate_module(module_id: UUID, tenant_id: UUID, db: AsyncSession) -> Module:
        """
        Deactivate a module
        """
        module = await ModuleService.get_module_by_id(module_id, tenant_id, db)
        if not module:
            raise ValueError("Module not found")

        if module.status != "active":
            raise ValueError(f"Module is not active (current: {module.status})")

        try:
            # Unload module
            await ModuleService._unload_module_runtime(module, db)

            module.status = "inactive"
            await db.commit()

            return module

        except Exception as e:
            module.status = "error"
            await db.commit()
            raise ValueError(f"Failed to deactivate module {module.name}: {str(e)}")

    @staticmethod
    async def uninstall_module(module_id: UUID, tenant_id: UUID, db: AsyncSession) -> bool:
        """
        Uninstall a module
        """
        module = await ModuleService.get_module_by_id(module_id, tenant_id, db)
        if not module:
            raise ValueError("Module not found")

        if module.is_system:
            raise ValueError("System modules cannot be uninstalled")

        if module.status == "active":
            await ModuleService.deactivate_module(module_id, tenant_id, db)

        # Remove configurations
        await db.execute(
            delete(ModuleConfiguration)
            .where(ModuleConfiguration.module_id == module_id)
        )

        # Remove versions
        await db.execute(
            delete(ModuleVersion)
            .where(ModuleVersion.module_id == module_id)
        )

        # Remove module
        await db.delete(module)
        await db.commit()

        return True

    @staticmethod
    async def update_module_config(
        module_id: UUID,
        tenant_id: UUID,
        config_data: Dict[str, Any],
        db: AsyncSession
    ) -> ModuleConfiguration:
        """
        Update module configuration
        """
        config = await db.execute(
            select(ModuleConfiguration)
            .where(
                ModuleConfiguration.module_id == module_id,
                ModuleConfiguration.tenant_id == tenant_id
            )
        )
        config = config.scalar_one_or_none()

        if not config:
            config = ModuleConfiguration(
                module_id=module_id,
                tenant_id=tenant_id,
                config_data=config_data
            )
            db.add(config)
        else:
            config.config_data = config_data
            config.updated_at = datetime.utcnow()

        await db.commit()
        return config

    @staticmethod
    async def get_module_config(module_id: UUID, tenant_id: UUID, db: AsyncSession) -> Optional[Dict[str, Any]]:
        """
        Get module configuration
        """
        config = await db.execute(
            select(ModuleConfiguration)
            .where(
                ModuleConfiguration.module_id == module_id,
                ModuleConfiguration.tenant_id == tenant_id,
                ModuleConfiguration.is_active == True
            )
        )
        config = config.scalar_one_or_none()
        return config.config_data if config else None

    @staticmethod
    async def discover_available_modules(db: AsyncSession) -> List[Dict[str, Any]]:
        """
        Discover available modules from registry
        """
        result = await db.execute(
            select(ModuleRegistry)
            .where(ModuleRegistry.is_available == True)
            .order_by(ModuleRegistry.total_downloads.desc())
        )
        modules = result.scalars().all()

        return [{
            "name": m.name,
            "display_name": m.display_name,
            "description": m.description,
            "latest_version": m.latest_version,
            "author": m.author,
            "total_downloads": m.total_downloads,
            "is_official": m.is_official
        } for m in modules]

    @staticmethod
    async def validate_version_compatibility(module_name: str, version: str, db: AsyncSession) -> bool:
        """
        Validate if a module version is compatible with the current system
        """
        # Get module registry info
        registry = await db.execute(
            select(ModuleRegistry)
            .where(ModuleRegistry.name == module_name)
        )
        registry = registry.scalar_one_or_none()

        if not registry:
            return False

        # Check core version compatibility
        # This would need to be implemented based on actual version checking logic
        return True

    @staticmethod
    async def get_module_from_registry(name: str, db: AsyncSession) -> Optional[ModuleRegistry]:
        """
        Get module information from registry
        """
        result = await db.execute(
            select(ModuleRegistry)
            .where(ModuleRegistry.name == name)
        )
        return result.scalar_one_or_none()

    @staticmethod
    async def _perform_module_installation(module: Module, db: AsyncSession) -> None:
        """
        Perform the actual module installation
        """
        # This would handle downloading, extracting, and setting up the module
        # For now, just simulate the process
        await asyncio.sleep(0.1)  # Simulate installation time

        # In a real implementation, this would:
        # 1. Download module from registry
        # 2. Extract to modules directory
        # 3. Install dependencies
        # 4. Validate installation
        pass

    @staticmethod
    async def _load_module_runtime(module: Module, db: AsyncSession) -> None:
        """
        Load module into runtime
        """
        # This would dynamically import and initialize the module
        # For now, just simulate the process
        await asyncio.sleep(0.1)

        # In a real implementation, this would:
        # 1. Import module dynamically
        # 2. Initialize module with configuration
        # 3. Register module endpoints/services
        # 4. Start background tasks if needed
        pass

    @staticmethod
    async def _unload_module_runtime(module: Module, db: AsyncSession) -> None:
        """
        Unload module from runtime
        """
        # This would clean up module resources
        # For now, just simulate the process
        await asyncio.sleep(0.1)

        # In a real implementation, this would:
        # 1. Stop background tasks
        # 2. Unregister endpoints/services
        # 3. Clean up resources
        # 4. Remove from sys.modules if needed
        pass

    @staticmethod
    async def check_module_health(module_id: UUID, tenant_id: UUID, db: AsyncSession) -> Dict[str, Any]:
        """
        Check the health status of a module
        """
        module = await ModuleService.get_module_by_id(module_id, tenant_id, db)
        if not module:
            return {"status": "not_found"}

        # Basic health checks
        health_info = {
            "status": module.status,
            "name": module.name,
            "version": module.version,
            "last_used": module.last_used_at.isoformat() if module.last_used_at else None,
            "config_valid": True,  # Would validate config against schema
            "dependencies_satisfied": True,  # Would check dependencies
        }

        return health_info

    @staticmethod
    async def get_active_modules(tenant_id: UUID, db: AsyncSession) -> List[Module]:
        """
        Get all active modules for a tenant
        """
        result = await db.execute(
            select(Module)
            .where(Module.tenant_id == tenant_id, Module.status == "active")
            .options(selectinload(Module.configurations))
        )
        return result.scalars().all()

    @staticmethod
    async def check_for_updates(tenant_id: UUID, db: AsyncSession) -> List[Dict[str, Any]]:
        """
        Check for available updates for tenant's modules
        """
        from app.models.marketplace import ModuleUpdate

        # Get all active modules for the tenant
        active_modules = await ModuleService.get_active_modules(tenant_id, db)

        updates = []
        for module in active_modules:
            # Check if there's a newer version available
            registry_info = await ModuleService.get_module_from_registry(module.name, db)
            if registry_info and registry_info.latest_version != module.version:
                # Check if update already exists
                existing_update = await db.execute(
                    select(ModuleUpdate)
                    .where(
                        ModuleUpdate.module_id == module.id,
                        ModuleUpdate.tenant_id == tenant_id,
                        ModuleUpdate.available_version == registry_info.latest_version
                    )
                )
                existing_update = existing_update.scalar_one_or_none()

                if not existing_update:
                    # Create update notification
                    update = ModuleUpdate(
                        module_id=module.id,
                        tenant_id=tenant_id,
                        current_version=module.version,
                        available_version=registry_info.latest_version,
                        update_type=ModuleService._determine_update_type(module.version, registry_info.latest_version)
                    )
                    db.add(update)
                    await db.commit()
                    await db.refresh(update)

                    updates.append({
                        "module_id": str(module.id),
                        "module_name": module.name,
                        "current_version": module.version,
                        "available_version": registry_info.latest_version,
                        "update_type": update.update_type,
                        "created_at": update.created_at.isoformat()
                    })
                elif existing_update and not existing_update.is_notified:
                    # Mark as notified
                    existing_update.is_notified = True
                    existing_update.notified_at = datetime.utcnow()
                    await db.commit()

                    updates.append({
                        "module_id": str(module.id),
                        "module_name": module.name,
                        "current_version": module.version,
                        "available_version": registry_info.latest_version,
                        "update_type": existing_update.update_type,
                        "created_at": existing_update.created_at.isoformat()
                    })

        return updates

    @staticmethod
    async def apply_update(module_id: UUID, tenant_id: UUID, target_version: str, db: AsyncSession) -> Dict[str, Any]:
        """
        Apply an update to a module
        """
        from app.models.marketplace import ModuleUpdate

        module = await ModuleService.get_module_by_id(module_id, tenant_id, db)
        if not module:
            raise ValueError("Module not found")

        if module.status != "active":
            raise ValueError(f"Module is not active (current status: {module.status})")

        # Validate target version
        if not await ModuleService.validate_version_compatibility(module.name, target_version, db):
            raise ValueError(f"Version {target_version} is not compatible")

        # Create or update update record
        update = await db.execute(
            select(ModuleUpdate)
            .where(
                ModuleUpdate.module_id == module_id,
                ModuleUpdate.tenant_id == tenant_id,
                ModuleUpdate.available_version == target_version
            )
        )
        update = update.scalar_one_or_none()

        if not update:
            update = ModuleUpdate(
                module_id=module_id,
                tenant_id=tenant_id,
                current_version=module.version,
                available_version=target_version,
                update_type=ModuleService._determine_update_type(module.version, target_version)
            )
            db.add(update)

        try:
            # Perform update
            update.is_installed = True
            update.installed_at = datetime.utcnow()

            # Update module version
            module.version = target_version
            module.updated_at = datetime.utcnow()

            await db.commit()

            return {
                "success": True,
                "module_id": str(module_id),
                "old_version": update.current_version,
                "new_version": target_version,
                "update_type": update.update_type
            }

        except Exception as e:
            update.is_installed = False
            await db.rollback()
            raise ValueError(f"Failed to apply update: {str(e)}")

    @staticmethod
    def _determine_update_type(current_version: str, new_version: str) -> str:
        """
        Determine the type of update (major, minor, patch)
        """
        try:
            current_parts = [int(x) for x in current_version.split('.')]
            new_parts = [int(x) for x in new_version.split('.')]

            if len(current_parts) >= 3 and len(new_parts) >= 3:
                if new_parts[0] > current_parts[0]:
                    return "major"
                elif new_parts[1] > current_parts[1]:
                    return "minor"
                elif new_parts[2] > current_parts[2]:
                    return "patch"
                else:
                    return "patch"  # Same version or build update
            else:
                return "minor"  # Fallback
        except (ValueError, IndexError):
            return "minor"  # Fallback for non-standard versioning

    @staticmethod
    async def get_update_history(module_id: UUID, tenant_id: UUID, db: AsyncSession) -> List[Dict[str, Any]]:
        """
        Get update history for a module
        """
        from app.models.marketplace import ModuleUpdate

        result = await db.execute(
            select(ModuleUpdate)
            .where(
                ModuleUpdate.module_id == module_id,
                ModuleUpdate.tenant_id == tenant_id
            )
            .order_by(ModuleUpdate.created_at.desc())
        )
        updates = result.scalars().all()

        return [{
            "id": str(update.id),
            "current_version": update.current_version,
            "available_version": update.available_version,
            "update_type": update.update_type,
            "is_installed": update.is_installed,
            "installed_at": update.installed_at.isoformat() if update.installed_at else None,
            "notified_at": update.notified_at.isoformat() if update.notified_at else None,
            "created_at": update.created_at.isoformat()
        } for update in updates]