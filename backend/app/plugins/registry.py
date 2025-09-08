"""
Module Registry - Sistema de Registro de Módulos
Registro persistente de módulos disponibles, instalados y su estado
"""

import json
import asyncio
from datetime import datetime
from typing import Dict, List, Any, Optional, Set
from dataclasses import dataclass, field, asdict
from pathlib import Path
import logging
import hashlib

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, delete, and_, or_

from .models import (
    PluginModel, PluginInstanceModel, PluginInstallation,
    PluginStatus, PluginType, EnvironmentType
)

logger = logging.getLogger(__name__)

@dataclass
class ModuleRecord:
    """Registro de un módulo en el sistema"""
    id: str
    name: str
    version: str
    description: str
    author: str
    type: PluginType
    status: PluginStatus
    path: str
    checksum: str
    dependencies: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    created_at: datetime = None
    updated_at: datetime = None
    installed_at: Optional[datetime] = None
    enabled: bool = True

    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.utcnow()
        if self.updated_at is None:
            self.updated_at = datetime.utcnow()

@dataclass
class InstallationRecord:
    """Registro de instalación de un módulo"""
    id: str
    module_id: str
    tenant_id: Optional[str]
    environment: EnvironmentType
    installed_by: str
    version: str
    config: Dict[str, Any] = field(default_factory=dict)
    status: str = "active"
    installed_at: datetime = None
    last_updated: datetime = None

    def __post_init__(self):
        if self.installed_at is None:
            self.installed_at = datetime.utcnow()
        if self.last_updated is None:
            self.last_updated = datetime.utcnow()

class ModuleRegistry:
    """
    Module Registry - Registro central de módulos

    Funcionalidades:
    - Registro de módulos disponibles
    - Tracking de instalaciones
    - Gestión de versiones
    - Búsqueda y filtrado
    - Sincronización con sistema de archivos
    """

    def __init__(self, db_session: AsyncSession = None):
        self.db_session = db_session
        self.cache: Dict[str, ModuleRecord] = {}
        self.installation_cache: Dict[str, List[InstallationRecord]] = {}

    async def register_module(self, module_path: Path, metadata: Dict[str, Any] = None) -> ModuleRecord:
        """
        Registra un módulo en el registro
        """
        if not module_path.exists():
            raise ValueError(f"Module path does not exist: {module_path}")

        # Calcular checksum del módulo
        checksum = await self._calculate_module_checksum(module_path)

        # Extraer información del módulo
        module_info = await self._extract_module_info(module_path, metadata)

        # Crear registro
        record = ModuleRecord(
            id=module_info.get('id', str(module_path.name)),
            name=module_path.name,
            version=module_info.get('version', '1.0.0'),
            description=module_info.get('description', f'Module {module_path.name}'),
            author=module_info.get('author', 'Vibecoding'),
            type=PluginType.MODULE,
            status=PluginStatus.PUBLISHED,
            path=str(module_path),
            checksum=checksum,
            dependencies=module_info.get('dependencies', []),
            metadata=module_info.get('metadata', {})
        )

        # Guardar en base de datos si está disponible
        if self.db_session:
            await self._save_to_database(record)

        # Cachear
        self.cache[record.id] = record

        logger.info(f"Registered module: {record.name} v{record.version}")
        return record

    async def unregister_module(self, module_id: str) -> bool:
        """
        Remueve un módulo del registro
        """
        if module_id not in self.cache:
            return False

        # Verificar si hay instalaciones activas
        installations = await self.get_module_installations(module_id)
        active_installations = [i for i in installations if i.status == 'active']

        if active_installations:
            logger.warning(f"Cannot unregister module {module_id}: has active installations")
            return False

        # Remover de base de datos
        if self.db_session:
            await self._delete_from_database(module_id)

        # Remover del cache
        del self.cache[module_id]

        logger.info(f"Unregistered module: {module_id}")
        return True

    async def get_module(self, module_id: str) -> Optional[ModuleRecord]:
        """
        Obtiene un módulo del registro
        """
        # Buscar en cache primero
        if module_id in self.cache:
            return self.cache[module_id]

        # Buscar en base de datos
        if self.db_session:
            record = await self._load_from_database(module_id)
            if record:
                self.cache[module_id] = record
                return record

        return None

    async def list_modules(self, filters: Dict[str, Any] = None) -> List[ModuleRecord]:
        """
        Lista módulos con filtros opcionales
        """
        modules = list(self.cache.values())

        # Aplicar filtros
        if filters:
            modules = await self._apply_filters(modules, filters)

        return modules

    async def search_modules(self, query: str, filters: Dict[str, Any] = None) -> List[ModuleRecord]:
        """
        Busca módulos por texto
        """
        all_modules = await self.list_modules(filters)
        query_lower = query.lower()

        results = []
        for module in all_modules:
            # Buscar en nombre, descripción y metadata
            searchable_text = f"{module.name} {module.description} {json.dumps(module.metadata)}".lower()

            if query_lower in searchable_text:
                results.append(module)

        return results

    async def install_module(self, module_id: str, tenant_id: str = None,
                           environment: EnvironmentType = EnvironmentType.PRODUCTION,
                           installed_by: str = "system") -> InstallationRecord:
        """
        Registra una instalación de módulo
        """
        module = await self.get_module(module_id)
        if not module:
            raise ValueError(f"Module {module_id} not found")

        # Crear registro de instalación
        installation = InstallationRecord(
            id=f"{module_id}_{tenant_id or 'global'}_{environment.value}_{datetime.utcnow().timestamp()}",
            module_id=module_id,
            tenant_id=tenant_id,
            environment=environment,
            installed_by=installed_by,
            version=module.version
        )

        # Guardar en base de datos
        if self.db_session:
            await self._save_installation_to_database(installation)

        # Cachear
        cache_key = f"{module_id}_{tenant_id or 'global'}"
        if cache_key not in self.installation_cache:
            self.installation_cache[cache_key] = []
        self.installation_cache[cache_key].append(installation)

        # Actualizar estado del módulo
        module.installed_at = installation.installed_at
        module.updated_at = datetime.utcnow()

        logger.info(f"Installed module {module_id} for tenant {tenant_id or 'global'}")
        return installation

    async def uninstall_module(self, module_id: str, tenant_id: str = None,
                             environment: EnvironmentType = None) -> bool:
        """
        Registra una desinstalación de módulo
        """
        cache_key = f"{module_id}_{tenant_id or 'global'}"
        if cache_key not in self.installation_cache:
            return False

        installations = self.installation_cache[cache_key]

        # Filtrar por environment si se especifica
        if environment:
            installations = [i for i in installations if i.environment == environment]

        if not installations:
            return False

        # Marcar como desinstalado
        for installation in installations:
            installation.status = "uninstalled"
            installation.last_updated = datetime.utcnow()

            # Actualizar en base de datos
            if self.db_session:
                await self._update_installation_in_database(installation)

        logger.info(f"Uninstalled module {module_id} for tenant {tenant_id or 'global'}")
        return True

    async def get_module_installations(self, module_id: str, tenant_id: str = None) -> List[InstallationRecord]:
        """
        Obtiene las instalaciones de un módulo
        """
        cache_key = f"{module_id}_{tenant_id or 'global'}"

        # Buscar en cache
        if cache_key in self.installation_cache:
            return self.installation_cache[cache_key]

        # Buscar en base de datos
        if self.db_session:
            installations = await self._load_installations_from_database(module_id, tenant_id)
            self.installation_cache[cache_key] = installations
            return installations

        return []

    async def sync_with_filesystem(self, modules_path: Path):
        """
        Sincroniza el registro con el sistema de archivos
        """
        if not modules_path.exists():
            return

        # Obtener módulos actuales del filesystem
        filesystem_modules = set()
        for item in modules_path.iterdir():
            if item.is_dir() and not item.name.startswith('_'):
                filesystem_modules.add(item.name)

        # Obtener módulos registrados
        registered_modules = set(self.cache.keys())

        # Módulos nuevos para registrar
        new_modules = filesystem_modules - registered_modules
        for module_name in new_modules:
            module_path = modules_path / module_name
            try:
                await self.register_module(module_path)
            except Exception as e:
                logger.error(f"Failed to register module {module_name}: {e}")

        # Módulos para remover (si ya no existen en filesystem)
        removed_modules = registered_modules - filesystem_modules
        for module_id in removed_modules:
            try:
                await self.unregister_module(module_id)
            except Exception as e:
                logger.error(f"Failed to unregister module {module_id}: {e}")

        logger.info(f"Synced registry with filesystem: +{len(new_modules)} -{len(removed_modules)} modules")

    async def get_module_stats(self) -> Dict[str, Any]:
        """
        Obtiene estadísticas del registro de módulos
        """
        modules = list(self.cache.values())

        stats = {
            "total_modules": len(modules),
            "installed_modules": len([m for m in modules if m.installed_at]),
            "enabled_modules": len([m for m in modules if m.enabled]),
            "modules_by_type": {},
            "modules_by_status": {},
            "recently_updated": []
        }

        # Estadísticas por tipo y estado
        for module in modules:
            module_type = module.type.value if hasattr(module.type, 'value') else str(module.type)
            module_status = module.status.value if hasattr(module.status, 'value') else str(module.status)

            stats["modules_by_type"][module_type] = stats["modules_by_type"].get(module_type, 0) + 1
            stats["modules_by_status"][module_status] = stats["modules_by_status"].get(module_status, 0) + 1

        # Módulos actualizados recientemente
        sorted_modules = sorted(modules, key=lambda m: m.updated_at or datetime.min, reverse=True)
        stats["recently_updated"] = [
            {"name": m.name, "updated_at": m.updated_at.isoformat() if m.updated_at else None}
            for m in sorted_modules[:5]
        ]

        return stats

    # Métodos privados de base de datos

    async def _save_to_database(self, record: ModuleRecord):
        """Guarda un registro de módulo en la base de datos"""
        plugin_model = PluginModel(
            id=record.id,
            name=record.name,
            version=record.version,
            description=record.description,
            author=record.author,
            type=record.type.value,
            status=record.status.value,
            manifest={
                "dependencies": record.dependencies,
                "metadata": record.metadata,
                "path": record.path,
                "checksum": record.checksum
            }
        )

        self.db_session.add(plugin_model)
        await self.db_session.commit()

    async def _load_from_database(self, module_id: str) -> Optional[ModuleRecord]:
        """Carga un registro de módulo desde la base de datos"""
        result = await self.db_session.execute(
            select(PluginModel).where(PluginModel.id == module_id)
        )
        plugin_model = result.scalar_one_or_none()

        if not plugin_model:
            return None

        manifest = plugin_model.manifest or {}

        return ModuleRecord(
            id=plugin_model.id,
            name=plugin_model.name,
            version=plugin_model.version,
            description=plugin_model.description,
            author=plugin_model.author,
            type=PluginType(plugin_model.type),
            status=PluginStatus(plugin_model.status),
            path=manifest.get("path", ""),
            checksum=manifest.get("checksum", ""),
            dependencies=manifest.get("dependencies", []),
            metadata=manifest.get("metadata", {}),
            created_at=plugin_model.created_at,
            updated_at=plugin_model.updated_at
        )

    async def _delete_from_database(self, module_id: str):
        """Elimina un registro de módulo de la base de datos"""
        await self.db_session.execute(
            delete(PluginModel).where(PluginModel.id == module_id)
        )
        await self.db_session.commit()

    async def _save_installation_to_database(self, installation: InstallationRecord):
        """Guarda un registro de instalación en la base de datos"""
        instance_model = PluginInstanceModel(
            id=installation.id,
            plugin_id=installation.module_id,
            tenant_id=installation.tenant_id,
            environment=installation.environment.value,
            config=installation.config,
            enabled=(installation.status == "active")
        )

        self.db_session.add(instance_model)
        await self.db_session.commit()

    async def _update_installation_in_database(self, installation: InstallationRecord):
        """Actualiza un registro de instalación en la base de datos"""
        await self.db_session.execute(
            update(PluginInstanceModel)
            .where(PluginInstanceModel.id == installation.id)
            .values(
                config=installation.config,
                enabled=(installation.status == "active")
            )
        )
        await self.db_session.commit()

    async def _load_installations_from_database(self, module_id: str, tenant_id: str = None) -> List[InstallationRecord]:
        """Carga registros de instalación desde la base de datos"""
        query = select(PluginInstanceModel).where(PluginInstanceModel.plugin_id == module_id)

        if tenant_id:
            query = query.where(PluginInstanceModel.tenant_id == tenant_id)

        result = await self.db_session.execute(query)
        instance_models = result.scalars().all()

        installations = []
        for model in instance_models:
            installations.append(InstallationRecord(
                id=model.id,
                module_id=model.plugin_id,
                tenant_id=model.tenant_id,
                environment=EnvironmentType(model.environment),
                installed_by="system",  # TODO: track this properly
                version="1.0.0",  # TODO: track this properly
                config=model.config or {},
                status="active" if model.enabled else "inactive",
                installed_at=model.created_at,
                last_updated=model.updated_at
            ))

        return installations

    # Métodos auxiliares

    async def _calculate_module_checksum(self, module_path: Path) -> str:
        """Calcula el checksum de un módulo"""
        hasher = hashlib.sha256()

        # Incluir archivos importantes
        important_files = ["routes.py", "models.py", "services.py", "README.md"]

        for file_name in important_files:
            file_path = module_path / file_name
            if file_path.exists():
                with open(file_path, 'rb') as f:
                    hasher.update(f.read())

        return hasher.hexdigest()

    async def _extract_module_info(self, module_path: Path, metadata: Dict[str, Any] = None) -> Dict[str, Any]:
        """Extrae información de un módulo"""
        info = {
            "id": str(module_path.name),
            "version": "1.0.0",
            "description": f"Module {module_path.name}",
            "author": "Vibecoding",
            "dependencies": [],
            "metadata": metadata or {}
        }

        # Intentar leer información de archivos
        readme_path = module_path / "README.md"
        if readme_path.exists():
            with open(readme_path, 'r', encoding='utf-8') as f:
                content = f.read()
                # Extraer descripción del README
                lines = content.split('\n')
                if lines:
                    info["description"] = lines[0].strip('# ').strip()

        # Intentar leer requirements.txt para dependencias
        requirements_path = module_path / "requirements.txt"
        if requirements_path.exists():
            with open(requirements_path, 'r', encoding='utf-8') as f:
                deps = []
                for line in f:
                    line = line.strip()
                    if line and not line.startswith('#'):
                        deps.append(line.split('==')[0].strip())
                info["dependencies"] = deps

        return info

    async def _apply_filters(self, modules: List[ModuleRecord], filters: Dict[str, Any]) -> List[ModuleRecord]:
        """Aplica filtros a una lista de módulos"""
        filtered = modules

        if "type" in filters:
            filtered = [m for m in filtered if m.type.value == filters["type"]]

        if "status" in filters:
            filtered = [m for m in filtered if m.status.value == filters["status"]]

        if "enabled" in filters:
            filtered = [m for m in filtered if m.enabled == filters["enabled"]]

        if "author" in filters:
            filtered = [m for m in filtered if m.author == filters["author"]]

        return filtered

# Instancia global del Module Registry
module_registry = ModuleRegistry()

# Funciones de conveniencia
async def get_module_registry() -> ModuleRegistry:
    """Dependency injection para el module registry"""
    return module_registry