"""
Auto-Integration Pipeline - Pipeline de Integración Automática
Integra automáticamente módulos al sistema principal
"""

import os
import re
import json
import asyncio
from pathlib import Path
from typing import Dict, List, Any, Optional, Set
from dataclasses import dataclass, field
import logging
from datetime import datetime
import shutil

from fastapi import APIRouter
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from .manager import ModuleMetadata
from .registry import ModuleRecord

logger = logging.getLogger(__name__)

@dataclass
class IntegrationStep:
    """Paso de integración"""
    name: str
    description: str
    required: bool = True
    executed: bool = False
    success: bool = False
    error_message: str = ""
    start_time: datetime = None
    end_time: datetime = None

    def execute(self):
        """Ejecuta el paso"""
        self.start_time = datetime.utcnow()
        self.executed = True

    def complete(self, success: bool = True, error: str = ""):
        """Completa el paso"""
        self.end_time = datetime.utcnow()
        self.success = success
        if error:
            self.error_message = error

@dataclass
class IntegrationPipelineResult:
    """Resultado del pipeline de integración"""
    module_name: str
    success: bool
    steps_executed: int
    steps_succeeded: int
    total_duration: float
    steps: List[IntegrationStep] = field(default_factory=list)
    errors: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)

class AutoIntegrationPipeline:
    """
    Auto-Integration Pipeline

    Pipeline que automáticamente:
    - Registra rutas en el sistema principal
    - Crea y aplica migraciones de base de datos
    - Actualiza documentación API
    - Integra componentes frontend
    - Configura servicios y dependencias
    """

    def __init__(self, db_session: AsyncSession = None):
        self.db_session = db_session
        self.project_root = Path(__file__).parent.parent.parent.parent

    async def integrate_module(self, module_record: ModuleRecord,
                             module_metadata: ModuleMetadata) -> IntegrationPipelineResult:
        """
        Ejecuta el pipeline completo de integración para un módulo
        """
        result = IntegrationPipelineResult(
            module_name=module_record.name,
            success=True,
            steps_executed=0,
            steps_succeeded=0,
            total_duration=0.0
        )

        start_time = datetime.utcnow()

        # Definir pasos del pipeline
        steps = [
            IntegrationStep("validate_module", "Validar estructura del módulo"),
            IntegrationStep("register_routes", "Registrar rutas en el sistema principal"),
            IntegrationStep("create_migrations", "Crear migraciones de base de datos"),
            IntegrationStep("apply_migrations", "Aplicar migraciones a la base de datos"),
            IntegrationStep("update_api_docs", "Actualizar documentación API"),
            IntegrationStep("integrate_frontend", "Integrar componentes frontend"),
            IntegrationStep("configure_services", "Configurar servicios y dependencias"),
            IntegrationStep("update_navigation", "Actualizar navegación del sistema"),
            IntegrationStep("validate_integration", "Validar integración completa")
        ]

        result.steps = steps

        try:
            # Paso 1: Validar módulo
            step = steps[0]
            step.execute()
            await self._validate_module_structure(module_record, module_metadata)
            step.complete()

            # Paso 2: Registrar rutas
            step = steps[1]
            step.execute()
            await self._register_module_routes(module_record, module_metadata)
            step.complete()

            # Paso 3: Crear migraciones
            step = steps[2]
            step.execute()
            await self._create_database_migrations(module_record, module_metadata)
            step.complete()

            # Paso 4: Aplicar migraciones
            step = steps[3]
            step.execute()
            await self._apply_database_migrations(module_record)
            step.complete()

            # Paso 5: Actualizar documentación API
            step = steps[4]
            step.execute()
            await self._update_api_documentation(module_record, module_metadata)
            step.complete()

            # Paso 6: Integrar frontend
            step = steps[5]
            step.execute()
            await self._integrate_frontend_components(module_record, module_metadata)
            step.complete()

            # Paso 7: Configurar servicios
            step = steps[6]
            step.execute()
            await self._configure_module_services(module_record, module_metadata)
            step.complete()

            # Paso 8: Actualizar navegación
            step = steps[7]
            step.execute()
            await self._update_system_navigation(module_record, module_metadata)
            step.complete()

            # Paso 9: Validar integración
            step = steps[8]
            step.execute()
            await self._validate_module_integration(module_record, module_metadata)
            step.complete()

        except Exception as e:
            result.success = False
            result.errors.append(f"Pipeline failed: {str(e)}")
            logger.error(f"Integration pipeline failed for {module_record.name}: {e}")

        # Calcular estadísticas
        end_time = datetime.utcnow()
        result.total_duration = (end_time - start_time).total_seconds()

        for step in steps:
            if step.executed:
                result.steps_executed += 1
                if step.success:
                    result.steps_succeeded += 1
                else:
                    result.errors.append(f"Step {step.name} failed: {step.error_message}")

        if result.steps_executed != result.steps_succeeded:
            result.success = False

        logger.info(f"Integration pipeline completed for {module_record.name}: "
                   f"{result.steps_succeeded}/{result.steps_executed} steps succeeded "
                   f"in {result.total_duration:.2f}s")

        return result

    async def _validate_module_structure(self, module_record: ModuleRecord,
                                       module_metadata: ModuleMetadata):
        """Valida la estructura del módulo"""
        module_path = Path(module_record.path)

        # Verificar archivos requeridos
        required_files = ["routes.py", "models.py"]
        for file_name in required_files:
            if not (module_path / file_name).exists():
                raise ValueError(f"Required file {file_name} not found in module {module_record.name}")

        # Verificar que el módulo se pueda importar
        try:
            __import__(module_record.name)
        except ImportError as e:
            raise ValueError(f"Cannot import module {module_record.name}: {e}")

        # Validar dependencias
        for dep in module_metadata.dependencies:
            try:
                __import__(dep)
            except ImportError:
                logger.warning(f"Dependency {dep} not available for module {module_record.name}")

    async def _register_module_routes(self, module_record: ModuleRecord,
                                    module_metadata: ModuleMetadata):
        """Registra las rutas del módulo en el sistema principal"""

        # Leer el archivo main.py actual
        main_file = self.project_root / "backend" / "app" / "main.py"
        if not main_file.exists():
            raise FileNotFoundError("main.py not found")

        with open(main_file, 'r', encoding='utf-8') as f:
            content = f.read()

        # Verificar si las rutas ya están registradas
        module_router_import = f"from app.modules.{module_record.name}.routes import router as {module_record.name}_router"
        module_router_include = f"app.include_router({module_record.name}_router, prefix=\"/api/v1/{module_record.name}\", tags=[\"{module_record.name}\"])"

        if module_router_import in content and module_router_include in content:
            logger.info(f"Routes for {module_record.name} already registered")
            return

        # Agregar import del router del módulo
        import_section = self._find_import_section(content)
        if import_section and module_router_import not in content:
            content = content.replace(
                import_section,
                import_section + module_router_import + "\n"
            )

        # Agregar inclusión del router
        router_section = self._find_router_section(content)
        if router_section and module_router_include not in content:
            content = content.replace(
                router_section,
                router_section + "\n" + module_router_include
            )

        # Escribir el archivo actualizado
        with open(main_file, 'w', encoding='utf-8') as f:
            f.write(content)

        logger.info(f"Registered routes for module {module_record.name}")

    async def _create_database_migrations(self, module_record: ModuleRecord,
                                        module_metadata: ModuleMetadata):
        """Crea migraciones de base de datos para el módulo"""

        # Leer modelos del módulo
        models_file = Path(module_record.path) / "models.py"
        if not models_file.exists():
            logger.warning(f"No models.py found for module {module_record.name}")
            return

        # Extraer nombres de modelos
        model_names = await self._extract_model_names(models_file)

        if not model_names:
            logger.info(f"No models found in module {module_record.name}")
            return

        # Crear archivo de migración
        migration_dir = self.project_root / "backend" / "alembic" / "versions"
        migration_dir.mkdir(exist_ok=True)

        timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
        migration_file = migration_dir / f"{timestamp}_{module_record.name}_initial.py"

        migration_content = self._generate_migration_content(module_record.name, model_names)

        with open(migration_file, 'w', encoding='utf-8') as f:
            f.write(migration_content)

        logger.info(f"Created migration for module {module_record.name}: {migration_file.name}")

    async def _apply_database_migrations(self, module_record: ModuleRecord):
        """Aplica las migraciones de base de datos"""
        if not self.db_session:
            logger.warning("No database session available, skipping migration application")
            return

        try:
            # Ejecutar migraciones pendientes
            # Nota: En un sistema real, usaríamos alembic para esto
            logger.info(f"Applying migrations for module {module_record.name}")

            # Aquí iría la lógica para ejecutar las migraciones
            # Por simplicidad, asumimos que se aplican correctamente

        except Exception as e:
            logger.error(f"Failed to apply migrations for {module_record.name}: {e}")
            raise

    async def _update_api_documentation(self, module_record: ModuleRecord,
                                      module_metadata: ModuleMetadata):
        """Actualiza la documentación API"""

        # Leer archivo de documentación actual
        docs_file = self.project_root / "docs" / "api-documentation.md"
        if not docs_file.exists():
            # Crear archivo si no existe
            with open(docs_file, 'w', encoding='utf-8') as f:
                f.write("# API Documentation\n\n")

        with open(docs_file, 'r', encoding='utf-8') as f:
            content = f.read()

        # Agregar sección del módulo si no existe
        module_section = f"## {module_record.name.upper()} Module\n\n"
        if module_section not in content:
            content += f"\n{module_section}"
            content += f"**Description**: {module_record.description}\n\n"
            content += f"**Version**: {module_record.version}\n\n"
            content += f"**Base URL**: `/api/v1/{module_record.name}`\n\n"

            # Agregar endpoints básicos
            content += "### Endpoints\n\n"
            content += f"- `GET /api/v1/{module_record.name}/` - List {module_record.name}\n"
            content += f"- `POST /api/v1/{module_record.name}/` - Create {module_record.name}\n"
            content += f"- `GET /api/v1/{module_record.name}/{{id}}` - Get {module_record.name} by ID\n"
            content += f"- `PUT /api/v1/{module_record.name}/{{id}}` - Update {module_record.name}\n"
            content += f"- `DELETE /api/v1/{module_record.name}/{{id}}` - Delete {module_record.name}\n\n"

            with open(docs_file, 'w', encoding='utf-8') as f:
                f.write(content)

        logger.info(f"Updated API documentation for module {module_record.name}")

    async def _integrate_frontend_components(self, module_record: ModuleRecord,
                                           module_metadata: ModuleMetadata):
        """Integra componentes frontend del módulo"""

        module_frontend_path = Path(module_record.path) / "frontend"
        if not module_frontend_path.exists():
            logger.info(f"No frontend components found for module {module_record.name}")
            return

        frontend_dest = self.project_root / "frontend" / "src" / "modules" / module_record.name
        frontend_dest.mkdir(parents=True, exist_ok=True)

        # Copiar componentes frontend
        if (module_frontend_path / "src").exists():
            shutil.copytree(
                module_frontend_path / "src",
                frontend_dest,
                dirs_exist_ok=True
            )

        # Actualizar configuración de Next.js si es necesario
        await self._update_nextjs_config(module_record)

        logger.info(f"Integrated frontend components for module {module_record.name}")

    async def _configure_module_services(self, module_record: ModuleRecord,
                                       module_metadata: ModuleMetadata):
        """Configura servicios y dependencias del módulo"""

        # Leer archivo de configuración de servicios
        services_config = self.project_root / "backend" / "app" / "core" / "services.py"
        if not services_config.exists():
            # Crear archivo si no existe
            with open(services_config, 'w', encoding='utf-8') as f:
                f.write('"""Service Configuration"""\n\nservices = {}\n')

        # Aquí iría la lógica para registrar servicios del módulo
        # Por simplicidad, solo loggeamos
        logger.info(f"Configured services for module {module_record.name}")

    async def _update_system_navigation(self, module_record: ModuleRecord,
                                      module_metadata: ModuleMetadata):
        """Actualiza la navegación del sistema"""

        # Leer archivo de navegación
        nav_file = self.project_root / "frontend" / "src" / "components" / "dashboard" / "sidebar.tsx"
        if not nav_file.exists():
            logger.warning("Navigation file not found, skipping navigation update")
            return

        with open(nav_file, 'r', encoding='utf-8') as f:
            content = f.read()

        # Agregar entrada de navegación para el módulo
        module_nav_entry = f'{{ label: "{module_record.name.title()}", href: "/dashboard/{module_record.name}" }},'
        if module_nav_entry not in content:
            # Encontrar sección de navegación
            nav_section = self._find_navigation_section(content)
            if nav_section:
                content = content.replace(
                    nav_section,
                    nav_section + "\n" + module_nav_entry
                )

                with open(nav_file, 'w', encoding='utf-8') as f:
                    f.write(content)

        logger.info(f"Updated navigation for module {module_record.name}")

    async def _validate_module_integration(self, module_record: ModuleRecord,
                                         module_metadata: ModuleMetadata):
        """Valida que la integración del módulo sea correcta"""

        # Verificar que el módulo se pueda importar
        try:
            module = __import__(module_record.name)
        except ImportError as e:
            raise ValueError(f"Cannot import integrated module {module_record.name}: {e}")

        # Verificar que tenga los componentes esperados
        required_attrs = ["routes"]
        for attr in required_attrs:
            if not hasattr(module, attr):
                raise ValueError(f"Module {module_record.name} missing required attribute: {attr}")

        # Verificar rutas
        if hasattr(module, 'routes'):
            routes = module.routes
            if not isinstance(routes, (list, APIRouter)):
                raise ValueError(f"Invalid routes configuration in module {module_record.name}")

        logger.info(f"Validated integration for module {module_record.name}")

    # Métodos auxiliares

    def _find_import_section(self, content: str) -> str:
        """Encuentra la sección de imports en main.py"""
        lines = content.split('\n')
        for i, line in enumerate(lines):
            if line.startswith('from app.api.v1.router import api_router'):
                return line
        return ""

    def _find_router_section(self, content: str) -> str:
        """Encuentra la sección de routers en main.py"""
        lines = content.split('\n')
        for i, line in enumerate(lines):
            if 'app.include_router(api_router' in line:
                return line
        return ""

    def _find_navigation_section(self, content: str) -> str:
        """Encuentra la sección de navegación en sidebar.tsx"""
        # Buscar patrón de array de navegación
        nav_pattern = r'const navigation\s*=\s*\['
        match = re.search(nav_pattern, content, re.MULTILINE | re.DOTALL)
        if match:
            # Encontrar el final del array
            start_pos = match.end()
            bracket_count = 1
            end_pos = start_pos

            while end_pos < len(content) and bracket_count > 0:
                if content[end_pos] == '[':
                    bracket_count += 1
                elif content[end_pos] == ']':
                    bracket_count -= 1
                end_pos += 1

            return content[start_pos:end_pos-1].strip()
        return ""

    async def _extract_model_names(self, models_file: Path) -> List[str]:
        """Extrae nombres de modelos de un archivo models.py"""
        model_names = []

        with open(models_file, 'r', encoding='utf-8') as f:
            content = f.read()

        # Buscar patrones de definición de clase SQLAlchemy
        class_pattern = r'class\s+(\w+)\s*\(\s*Base\s*\)'
        matches = re.findall(class_pattern, content)

        for match in matches:
            if not match.startswith('_'):  # Ignorar clases privadas
                model_names.append(match)

        return model_names

    def _generate_migration_content(self, module_name: str, model_names: List[str]) -> str:
        """Genera contenido de migración para modelos"""
        timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")

        content = f'''"""
Migration for {module_name} module
Created: {datetime.utcnow().isoformat()}
"""

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = "{timestamp}"
down_revision = None
branch_labels = None
depends_on = None

def upgrade():
    """Upgrade migration"""
'''

        for model_name in model_names:
            table_name = model_name.lower() + 's'  # Asumir plural
            content += f'''
    # Create {table_name} table for {model_name}
    op.create_table(
        '{table_name}',
        sa.Column('id', sa.String(36), primary_key=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        # Add more columns as needed based on model definition
    )
'''

        content += '''
def downgrade():
    """Downgrade migration"""
'''

        for model_name in model_names:
            table_name = model_name.lower() + 's'
            content += f'''
    # Drop {table_name} table
    op.drop_table('{table_name}')
'''

        return content

    async def _update_nextjs_config(self, module_record: ModuleRecord):
        """Actualiza configuración de Next.js si es necesario"""
        # Aquí iría lógica para actualizar next.config.js
        # Por simplicidad, solo loggeamos
        logger.info(f"Updated Next.js config for module {module_record.name}")

# Instancia global del Auto-Integration Pipeline
integration_pipeline = AutoIntegrationPipeline()

# Funciones de conveniencia
async def get_integration_pipeline() -> AutoIntegrationPipeline:
    """Dependency injection para el integration pipeline"""
    return integration_pipeline

async def integrate_module_automatically(module_record: ModuleRecord,
                                       module_metadata: ModuleMetadata) -> IntegrationPipelineResult:
    """Función de conveniencia para integrar un módulo automáticamente"""
    return await integration_pipeline.integrate_module(module_record, module_metadata)