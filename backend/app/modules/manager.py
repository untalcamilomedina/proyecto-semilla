"""
Module Manager for Proyecto Semilla
Central coordinator for module lifecycle management, loading, and execution
"""

import asyncio
import importlib
import sys
from typing import Dict, List, Any, Optional, Set
from uuid import UUID
from datetime import datetime
from pathlib import Path

from app.services.module_service import ModuleService
from app.mcp.client import ModuleMCPClient
from .loader import ModuleLoader
from .registry import ModuleRegistry
from .sandbox import ModuleSandbox


class ModuleManager:
    """
    Central module management system for Proyecto Semilla
    Handles module discovery, loading, execution, and lifecycle management
    """

    def __init__(self):
        self.loader = ModuleLoader()
        self.registry = ModuleRegistry()
        self.sandbox = ModuleSandbox()

        # Active modules cache
        self.active_modules: Dict[str, Any] = {}  # module_name -> module_instance
        self.module_clients: Dict[str, ModuleMCPClient] = {}  # module_name -> MCP client
        self.module_tasks: Dict[str, Set[asyncio.Task]] = {}  # module_name -> background tasks

        # Module directories
        self.modules_dir = Path("backend/app/modules")
        self.modules_dir.mkdir(exist_ok=True)

    async def initialize(self):
        """Initialize the module management system"""
        # Load system modules
        await self._load_system_modules()

        # Start background monitoring
        asyncio.create_task(self._monitor_modules())

    async def install_module(self, tenant_id: UUID, name: str, version: str, config: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Install a module for a tenant
        """
        try:
            # Install via service
            module = await ModuleService.install_module(str(tenant_id), name, version, config)

            # Download and prepare module files
            await self.loader.download_module(name, version, self.modules_dir / name)

            # Validate module structure
            module_path = self.modules_dir / name
            if not await self.loader.validate_module_structure(module_path):
                raise ValueError(f"Invalid module structure for {name}")

            return {
                "success": True,
                "module": self._module_to_dict(module),
                "message": f"Module {name} v{version} installed successfully"
            }

        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }

    async def activate_module(self, tenant_id: UUID, module_id: UUID) -> Dict[str, Any]:
        """
        Activate a module
        """
        try:
            # Get module info
            module = await ModuleService.get_module_by_id(module_id, tenant_id)
            if not module:
                raise ValueError("Module not found")

            # Load module into runtime
            module_instance = await self.loader.load_module(module.name, self.modules_dir / module.name)

            # Initialize MCP client for the module
            client = ModuleMCPClient(module_name=module.name, module_id=str(module_id))
            await client.connect()

            # Register module with MCP server
            config = await ModuleService.get_module_config(str(module_id), str(tenant_id))
            await client.register_module(str(tenant_id), config or {})

            # Start module
            await self._start_module(module.name, module_instance, client)

            # Update status
            activated_module = await ModuleService.activate_module(module_id, tenant_id)

            # Cache active module
            self.active_modules[module.name] = module_instance
            self.module_clients[module.name] = client

            return {
                "success": True,
                "module": self._module_to_dict(activated_module),
                "message": f"Module {module.name} activated successfully"
            }

        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }

    async def deactivate_module(self, tenant_id: UUID, module_id: UUID) -> Dict[str, Any]:
        """
        Deactivate a module
        """
        try:
            # Get module info
            module = await ModuleService.get_module_by_id(module_id, tenant_id)
            if not module:
                raise ValueError("Module not found")

            # Stop module
            await self._stop_module(module.name)

            # Update status
            deactivated_module = await ModuleService.deactivate_module(module_id, tenant_id)

            # Remove from cache
            if module.name in self.active_modules:
                del self.active_modules[module.name]
            if module.name in self.module_clients:
                client = self.module_clients[module.name]
                await client.disconnect()
                del self.module_clients[module.name]

            return {
                "success": True,
                "module": self._module_to_dict(deactivated_module),
                "message": f"Module {module.name} deactivated successfully"
            }

        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }

    async def reload_module(self, tenant_id: UUID, module_id: UUID) -> Dict[str, Any]:
        """
        Hot-reload a module without downtime
        """
        try:
            # Get current module info
            module = await ModuleService.get_module_by_id(module_id, tenant_id)
            if not module:
                raise ValueError("Module not found")

            if module.status != "active":
                raise ValueError("Module must be active to reload")

            # Reload module code
            module_path = self.modules_dir / module.name
            new_instance = await self.loader.reload_module(module.name, module_path)

            # Graceful handover
            old_instance = self.active_modules.get(module.name)
            if old_instance and hasattr(old_instance, 'prepare_handover'):
                await old_instance.prepare_handover()

            # Update instance
            self.active_modules[module.name] = new_instance

            # Initialize new instance
            if hasattr(new_instance, 'initialize'):
                config = await ModuleService.get_module_config(str(module_id), str(tenant_id))
                client = self.module_clients.get(module.name)
                await new_instance.initialize(config or {}, client)

            # Cleanup old instance
            if old_instance and hasattr(old_instance, 'cleanup'):
                await old_instance.cleanup()

            return {
                "success": True,
                "module": self._module_to_dict(module),
                "message": f"Module {module.name} reloaded successfully"
            }

        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }

    async def get_active_modules(self, tenant_id: UUID) -> List[Dict[str, Any]]:
        """
        Get all active modules for a tenant
        """
        modules = await ModuleService.get_active_modules(str(tenant_id))
        return [self._module_to_dict(module) for module in modules]

    async def get_module_health(self, tenant_id: UUID, module_id: UUID) -> Dict[str, Any]:
        """
        Get health status of a module
        """
        return await ModuleService.check_module_health(str(module_id), str(tenant_id))

    async def update_module_config(self, tenant_id: UUID, module_id: UUID, config: Dict[str, Any]) -> Dict[str, Any]:
        """
        Update module configuration
        """
        try:
            config_obj = await ModuleService.update_module_config(str(module_id), str(tenant_id), config)

            # Notify active module of config change
            module = await ModuleService.get_module_by_id(module_id, tenant_id)
            if module and module.status == "active":
                module_instance = self.active_modules.get(module.name)
                if module_instance and hasattr(module_instance, 'on_config_update'):
                    await module_instance.on_config_update(config)

            return {
                "success": True,
                "config": config_obj.config_data,
                "message": "Configuration updated successfully"
            }

        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }

    async def discover_modules(self) -> List[Dict[str, Any]]:
        """
        Discover available modules from registry
        """
        return await ModuleService.discover_available_modules()

    async def _load_system_modules(self):
        """Load system modules that are always available"""
        system_modules = ["health_monitor", "metrics_collector"]

        for module_name in system_modules:
            try:
                module_path = self.modules_dir / module_name
                if module_path.exists():
                    module_instance = await self.loader.load_module(module_name, module_path)
                    self.active_modules[module_name] = module_instance
            except Exception as e:
                print(f"Failed to load system module {module_name}: {e}")

    async def _start_module(self, name: str, instance: Any, client: ModuleMCPClient):
        """Start a module instance"""
        try:
            # Initialize module
            if hasattr(instance, 'initialize'):
                await instance.initialize({}, client)

            # Start background tasks
            if hasattr(instance, 'start_background_tasks'):
                tasks = await instance.start_background_tasks()
                self.module_tasks[name] = tasks

            # Register module capabilities with MCP server
            if hasattr(instance, 'get_capabilities'):
                capabilities = await instance.get_capabilities()
                # Register tools, resources, prompts with MCP server
                # This would integrate with the MCP server to register module capabilities

        except Exception as e:
            print(f"Error starting module {name}: {e}")
            raise

    async def _stop_module(self, name: str):
        """Stop a module instance"""
        try:
            instance = self.active_modules.get(name)
            if instance:
                # Stop background tasks
                if hasattr(instance, 'stop_background_tasks'):
                    await instance.stop_background_tasks()

                tasks = self.module_tasks.get(name, set())
                for task in tasks:
                    task.cancel()
                if tasks:
                    await asyncio.gather(*tasks, return_exceptions=True)

                # Cleanup module
                if hasattr(instance, 'cleanup'):
                    await instance.cleanup()

                # Clean up tasks cache
                if name in self.module_tasks:
                    del self.module_tasks[name]

        except Exception as e:
            print(f"Error stopping module {name}: {e}")

    async def _monitor_modules(self):
        """Background monitoring of active modules"""
        while True:
            try:
                # Check health of active modules
                for name, instance in self.active_modules.items():
                    if hasattr(instance, 'health_check'):
                        try:
                            health = await instance.health_check()
                            if not health.get('healthy', True):
                                print(f"Module {name} health check failed: {health}")
                        except Exception as e:
                            print(f"Health check error for module {name}: {e}")

                await asyncio.sleep(60)  # Check every minute

            except Exception as e:
                print(f"Module monitoring error: {e}")
                await asyncio.sleep(60)

    def _module_to_dict(self, module) -> Dict[str, Any]:
        """Convert module object to dictionary"""
        return {
            "id": str(module.id),
            "tenant_id": str(module.tenant_id),
            "name": module.name,
            "display_name": module.display_name,
            "version": module.version,
            "description": module.description,
            "status": module.status,
            "is_system": module.is_system,
            "installed_at": module.installed_at.isoformat() if module.installed_at else None,
            "activated_at": module.activated_at.isoformat() if module.activated_at else None,
            "last_used_at": module.last_used_at.isoformat() if module.last_used_at else None,
            "created_at": module.created_at.isoformat(),
            "updated_at": module.updated_at.isoformat()
        }


# Global module manager instance
module_manager = ModuleManager()