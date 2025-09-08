"""
Plugin Manager System - Sistema de Gestión de Plugins para Proyecto Semilla
Gestión automática de módulos Vibecoding con integración dinámica
"""

import importlib
import inspect
import os
import sys
from pathlib import Path
from typing import Dict, List, Any, Optional, Set, Type, Callable
from dataclasses import dataclass, field
import logging
from datetime import datetime
import asyncio
import json

from fastapi import APIRouter, FastAPI
from sqlalchemy.ext.declarative import DeclarativeMeta

from .models import PluginManifest, PluginType, PluginStatus
from .discovery import plugin_discoverer

logger = logging.getLogger(__name__)

@dataclass
class ModuleMetadata:
    """Metadata de un módulo Vibecoding"""
    name: str
    version: str
    description: str
    author: str
    dependencies: List[str] = field(default_factory=list)
    entry_points: Dict[str, str] = field(default_factory=dict)
    models: List[Type] = field(default_factory=list)
    routes: List[APIRouter] = field(default_factory=list)
    services: Dict[str, Any] = field(default_factory=dict)
    frontend_components: Dict[str, str] = field(default_factory=dict)
    migrations: List[str] = field(default_factory=list)
    tests: List[Callable] = field(default_factory=list)
    path: Path = None
    loaded: bool = False
    enabled: bool = True
    load_time: datetime = None

@dataclass
class IntegrationResult:
    """Resultado de integración de un módulo"""
    success: bool
    module_name: str
    routes_registered: int = 0
    models_registered: int = 0
    services_registered: int = 0
    migrations_applied: int = 0
    errors: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)

class PluginManager:
    """
    Plugin Manager - Sistema central para gestión de módulos Vibecoding

    Características:
    - Auto-discovery de módulos
    - Carga dinámica
    - Integración automática (rutas, modelos, servicios)
    - Gestión de dependencias
    - Hot reload en desarrollo
    """

    def __init__(self, modules_path: str = "modules"):
        self.modules_path = Path(modules_path)
        self.modules: Dict[str, ModuleMetadata] = {}
        self.loaded_modules: Dict[str, Any] = {}
        self.dependency_graph: Dict[str, Set[str]] = {}
        self.integration_results: Dict[str, IntegrationResult] = {}

        # Asegurar que la carpeta de módulos existe
        self.modules_path.mkdir(exist_ok=True)

        # Agregar modules_path al sys.path para imports dinámicos
        if str(self.modules_path) not in sys.path:
            sys.path.insert(0, str(self.modules_path))

    async def discover_modules(self) -> List[str]:
        """
        Descubre módulos disponibles en la carpeta modules/
        """
        discovered = []

        if not self.modules_path.exists():
            logger.warning(f"Modules path {self.modules_path} does not exist")
            return discovered

        for item in self.modules_path.iterdir():
            if item.is_dir() and not item.name.startswith('_'):
                # Verificar si es un módulo válido
                if self._is_valid_module(item):
                    module_name = item.name
                    discovered.append(module_name)

                    # Crear metadata básica si no existe
                    if module_name not in self.modules:
                        self.modules[module_name] = ModuleMetadata(
                            name=module_name,
                            version="1.0.0",
                            description=f"Module {module_name}",
                            author="Vibecoding",
                            path=item
                        )

        logger.info(f"Discovered {len(discovered)} modules: {discovered}")
        return discovered

    async def load_module(self, module_name: str) -> bool:
        """
        Carga un módulo específico dinámicamente
        """
        if module_name not in self.modules:
            logger.error(f"Module {module_name} not found in registry")
            return False

        module_meta = self.modules[module_name]

        try:
            # Verificar dependencias
            if not await self._check_dependencies(module_name):
                logger.error(f"Dependencies not satisfied for module {module_name}")
                return False

            # Importar el módulo
            module = importlib.import_module(module_name)

            # Analizar el módulo y extraer componentes
            await self._analyze_module(module, module_meta)

            # Marcar como cargado
            module_meta.loaded = True
            module_meta.load_time = datetime.utcnow()
            self.loaded_modules[module_name] = module

            logger.info(f"Successfully loaded module: {module_name}")
            return True

        except Exception as e:
            logger.error(f"Failed to load module {module_name}: {e}")
            return False

    async def integrate_module(self, module_name: str, app: FastAPI = None) -> IntegrationResult:
        """
        Integra un módulo al sistema principal
        """
        if module_name not in self.modules:
            return IntegrationResult(
                success=False,
                module_name=module_name,
                errors=[f"Module {module_name} not found"]
            )

        module_meta = self.modules[module_name]

        if not module_meta.loaded:
            return IntegrationResult(
                success=False,
                module_name=module_name,
                errors=[f"Module {module_name} not loaded"]
            )

        result = IntegrationResult(success=True, module_name=module_name)

        try:
            # 1. Registrar rutas
            routes_registered = await self._integrate_routes(module_meta, app)
            result.routes_registered = routes_registered

            # 2. Registrar modelos
            models_registered = await self._integrate_models(module_meta)
            result.models_registered = models_registered

            # 3. Registrar servicios
            services_registered = await self._integrate_services(module_meta)
            result.services_registered = services_registered

            # 4. Aplicar migraciones
            migrations_applied = await self._integrate_migrations(module_meta)
            result.migrations_applied = migrations_applied

            # 5. Integrar frontend (si aplica)
            await self._integrate_frontend(module_meta)

            logger.info(f"Successfully integrated module: {module_name}")

        except Exception as e:
            result.success = False
            result.errors.append(str(e))
            logger.error(f"Failed to integrate module {module_name}: {e}")

        self.integration_results[module_name] = result
        return result

    async def load_and_integrate_all(self, app: FastAPI = None) -> Dict[str, IntegrationResult]:
        """
        Descubre, carga e integra todos los módulos disponibles
        """
        # Descubrir módulos
        discovered = await self.discover_modules()

        # Resolver dependencias
        await self._resolve_dependencies(discovered)

        # Cargar módulos en orden de dependencias
        load_order = await self._get_load_order(discovered)

        results = {}

        for module_name in load_order:
            # Cargar módulo
            loaded = await self.load_module(module_name)

            if loaded:
                # Integrar módulo
                result = await self.integrate_module(module_name, app)
                results[module_name] = result
            else:
                results[module_name] = IntegrationResult(
                    success=False,
                    module_name=module_name,
                    errors=["Failed to load module"]
                )

        return results

    async def reload_module(self, module_name: str, app: FastAPI = None) -> bool:
        """
        Recarga un módulo (útil para desarrollo)
        """
        if module_name not in self.loaded_modules:
            return False

        try:
            # Remover del sys.modules
            module_path = f"{module_name}"
            if module_path in sys.modules:
                del sys.modules[module_path]

            # Limpiar metadata
            if module_name in self.modules:
                self.modules[module_name].loaded = False
                self.modules[module_name].load_time = None

            # Recargar
            return await self.load_module(module_name) and \
                   (await self.integrate_module(module_name, app)).success

        except Exception as e:
            logger.error(f"Failed to reload module {module_name}: {e}")
            return False

    def get_module_info(self, module_name: str) -> Optional[ModuleMetadata]:
        """Obtiene información de un módulo"""
        return self.modules.get(module_name)

    def list_modules(self) -> List[Dict[str, Any]]:
        """Lista todos los módulos con su estado"""
        return [
            {
                "name": name,
                "version": meta.version,
                "description": meta.description,
                "loaded": meta.loaded,
                "enabled": meta.enabled,
                "load_time": meta.load_time.isoformat() if meta.load_time else None,
                "dependencies": meta.dependencies,
                "routes_count": len(meta.routes),
                "models_count": len(meta.models),
                "services_count": len(meta.services)
            }
            for name, meta in self.modules.items()
        ]

    # Métodos privados de apoyo

    def _is_valid_module(self, module_path: Path) -> bool:
        """Verifica si una carpeta contiene un módulo válido"""
        # Verificar archivos requeridos
        required_files = ["routes.py", "models.py"]
        return all((module_path / file).exists() for file in required_files)

    async def _check_dependencies(self, module_name: str) -> bool:
        """Verifica que las dependencias del módulo estén satisfechas"""
        if module_name not in self.modules:
            return False

        deps = self.modules[module_name].dependencies
        for dep in deps:
            if dep not in self.modules or not self.modules[dep].loaded:
                return False

        return True

    async def _analyze_module(self, module: Any, metadata: ModuleMetadata):
        """Analiza un módulo cargado y extrae sus componentes"""

        # Extraer rutas
        if hasattr(module, 'router') or hasattr(module, 'routes'):
            if hasattr(module, 'router'):
                metadata.routes.append(module.router)
            elif hasattr(module, 'routes'):
                metadata.routes.extend(module.routes)

        # Extraer modelos
        if hasattr(module, 'models'):
            models_module = module.models
            for name, obj in inspect.getmembers(models_module):
                if inspect.isclass(obj) and hasattr(obj, '__tablename__'):
                    metadata.models.append(obj)

        # Extraer servicios
        if hasattr(module, 'services'):
            services_module = module.services
            for name, obj in inspect.getmembers(services_module):
                if not name.startswith('_'):
                    metadata.services[name] = obj

        # Extraer información adicional del módulo
        if hasattr(module, '__version__'):
            metadata.version = module.__version__
        if hasattr(module, '__description__'):
            metadata.description = module.__description__
        if hasattr(module, '__author__'):
            metadata.author = module.__author__

    async def _integrate_routes(self, metadata: ModuleMetadata, app: FastAPI = None) -> int:
        """Integra las rutas del módulo al sistema principal"""
        if not app:
            return 0

        routes_registered = 0

        for router in metadata.routes:
            # Crear prefijo para el módulo
            prefix = f"/api/v1/{metadata.name}"

            # Incluir el router en la app principal
            app.include_router(router, prefix=prefix, tags=[metadata.name])
            routes_registered += 1

        return routes_registered

    async def _integrate_models(self, metadata: ModuleMetadata) -> int:
        """Integra los modelos del módulo (crea tablas si no existen)"""
        # Nota: En un sistema real, aquí aplicaríamos migraciones
        # Por ahora solo contamos los modelos
        return len(metadata.models)

    async def _integrate_services(self, metadata: ModuleMetadata) -> int:
        """Integra los servicios del módulo al sistema de DI"""
        # Aquí podríamos registrar servicios en un contenedor de DI
        return len(metadata.services)

    async def _integrate_migrations(self, metadata: ModuleMetadata) -> int:
        """Aplica las migraciones del módulo"""
        # Aquí ejecutaríamos las migraciones de base de datos
        return len(metadata.migrations)

    async def _integrate_frontend(self, metadata: ModuleMetadata):
        """Integra componentes frontend del módulo"""
        # Aquí podríamos copiar archivos frontend o registrar rutas
        pass

    async def _resolve_dependencies(self, modules: List[str]):
        """Resuelve el grafo de dependencias entre módulos"""
        for module_name in modules:
            module_path = self.modules_path / module_name
            deps = await self._extract_dependencies(module_path)
            self.modules[module_name].dependencies = deps
            self.dependency_graph[module_name] = set(deps)

    async def _extract_dependencies(self, module_path: Path) -> List[str]:
        """Extrae dependencias de un módulo desde su código"""
        # Simplificado: buscar imports de otros módulos
        deps = []

        # Verificar requirements.txt o setup.py
        requirements_file = module_path / "requirements.txt"
        if requirements_file.exists():
            with open(requirements_file) as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith('#'):
                        # Extraer nombre del paquete
                        dep_name = line.split('==')[0].split('>=')[0].split('<')[0].strip()
                        if dep_name in self.modules:
                            deps.append(dep_name)

        return deps

    async def _get_load_order(self, modules: List[str]) -> List[str]:
        """Determina el orden de carga considerando dependencias"""
        # Algoritmo simplificado de ordenamiento topológico
        load_order = []
        visited = set()
        visiting = set()

        def visit(module_name: str):
            if module_name in visiting:
                raise ValueError(f"Circular dependency detected: {module_name}")
            if module_name in visited:
                return

            visiting.add(module_name)

            for dep in self.dependency_graph.get(module_name, set()):
                visit(dep)

            visiting.remove(module_name)
            visited.add(module_name)
            load_order.append(module_name)

        for module_name in modules:
            if module_name not in visited:
                visit(module_name)

        return load_order

# Instancia global del Plugin Manager
plugin_manager = PluginManager()

# Funciones de conveniencia
async def get_plugin_manager() -> PluginManager:
    """Dependency injection para el plugin manager"""
    return plugin_manager

async def auto_discover_and_integrate(app: FastAPI = None) -> Dict[str, IntegrationResult]:
    """Función de conveniencia para auto-descubrimiento e integración"""
    return await plugin_manager.load_and_integrate_all(app)