"""
Plugin System - Sistema de Plugins para Proyecto Semilla
Integración automática de módulos Vibecoding
"""

from .manager import PluginManager, get_plugin_manager, auto_discover_and_integrate
from .registry import ModuleRegistry, get_module_registry
from .integration_pipeline import AutoIntegrationPipeline, get_integration_pipeline, integrate_module_automatically
from .integration_testing import IntegrationTestingSystem, get_integration_testing_system, run_module_integration_tests
from .models import (
    PluginManifest, PluginType, PluginStatus, EnvironmentType
)
from .registry import ModuleRecord, InstallationRecord

__all__ = [
    # Plugin Manager
    "PluginManager",
    "get_plugin_manager",
    "auto_discover_and_integrate",

    # Module Registry
    "ModuleRegistry",
    "get_module_registry",

    # Integration Pipeline
    "AutoIntegrationPipeline",
    "get_integration_pipeline",
    "integrate_module_automatically",

    # Integration Testing
    "IntegrationTestingSystem",
    "get_integration_testing_system",
    "run_module_integration_tests",

    # Models
    "PluginManifest",
    "PluginType",
    "PluginStatus",
    "EnvironmentType",
    "ModuleRecord",
    "InstallationRecord"
]

# Sistema de plugins principal
class PluginSystem:
    """
    Sistema de Plugins Principal

    Coordina todos los componentes del sistema de plugins:
    - Plugin Manager: Gestión y carga de módulos
    - Module Registry: Registro de módulos disponibles
    - Integration Pipeline: Integración automática
    - Integration Testing: Validación de integraciones
    """

    def __init__(self):
        self.manager = None
        self.registry = None
        self.pipeline = None
        self.testing = None
        self.initialized = False

    async def initialize(self, db_session=None, test_client=None):
        """Inicializa el sistema de plugins"""
        if self.initialized:
            return

        # Inicializar componentes
        self.registry = ModuleRegistry(db_session)
        self.manager = PluginManager()
        self.pipeline = AutoIntegrationPipeline(db_session)
        self.testing = IntegrationTestingSystem(test_client, db_session)

        self.initialized = True

        return self

    async def auto_setup(self, app=None):
        """Configuración automática del sistema de plugins"""
        if not self.initialized:
            await self.initialize()

        # Auto-descubrir e integrar módulos
        integration_results = await self.manager.load_and_integrate_all(app)

        # Registrar resultados
        for module_name, result in integration_results.items():
            if result.success:
                module_record = await self.registry.get_module(module_name)
                if module_record:
                    await self.registry.install_module(module_name)

        return integration_results

    async def get_system_status(self):
        """Obtiene el estado del sistema de plugins"""
        if not self.initialized:
            return {"status": "not_initialized"}

        # Obtener estadísticas del registro
        stats = await self.registry.get_module_stats()

        # Obtener estado del manager
        modules = self.manager.list_modules()

        return {
            "status": "active",
            "registry_stats": stats,
            "loaded_modules": len([m for m in modules if m["loaded"]]),
            "total_modules": len(modules),
            "components": {
                "manager": "active" if self.manager else "inactive",
                "registry": "active" if self.registry else "inactive",
                "pipeline": "active" if self.pipeline else "inactive",
                "testing": "active" if self.testing else "inactive"
            }
        }

# Instancia global del sistema de plugins
plugin_system = PluginSystem()

# Función de inicialización automática
async def initialize_plugin_system(app=None, db_session=None, test_client=None):
    """
    Inicializa el sistema de plugins automáticamente

    Esta función debe ser llamada durante el startup de la aplicación
    """
    global plugin_system

    await plugin_system.initialize(db_session, test_client)
    results = await plugin_system.auto_setup(app)

    return results

# Función de estado del sistema
async def get_plugin_system_status():
    """Obtiene el estado del sistema de plugins"""
    return await plugin_system.get_system_status()