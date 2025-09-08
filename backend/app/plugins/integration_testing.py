"""
Integration Testing System - Sistema de Pruebas de Integración
Valida que módulos integrados funcionen correctamente
"""

import asyncio
import json
import time
from typing import Dict, List, Any, Optional, Callable
from dataclasses import dataclass, field
import logging
from datetime import datetime
import requests
from pathlib import Path

from fastapi.testclient import TestClient
from sqlalchemy.ext.asyncio import AsyncSession

from .manager import ModuleMetadata
from .registry import ModuleRecord

logger = logging.getLogger(__name__)

@dataclass
class TestResult:
    """Resultado de una prueba"""
    test_name: str
    description: str
    success: bool
    duration: float
    error_message: str = ""
    details: Dict[str, Any] = field(default_factory=dict)

@dataclass
class IntegrationTestSuite:
    """Suite de pruebas de integración"""
    module_name: str
    tests: List[TestResult] = field(default_factory=list)
    start_time: datetime = None
    end_time: datetime = None
    total_tests: int = 0
    passed_tests: int = 0
    failed_tests: int = 0
    total_duration: float = 0.0

    def add_test(self, result: TestResult):
        """Agrega un resultado de prueba"""
        self.tests.append(result)
        self.total_tests += 1
        if result.success:
            self.passed_tests += 1
        else:
            self.failed_tests += 1

    def complete(self):
        """Completa la suite de pruebas"""
        self.end_time = datetime.utcnow()
        if self.start_time:
            self.total_duration = (self.end_time - self.start_time).total_seconds()

class IntegrationTestingSystem:
    """
    Integration Testing System

    Sistema que valida automáticamente:
    - APIs del módulo funcionan correctamente
    - Base de datos se creó correctamente
    - Integración con otros módulos
    - Frontend se integra correctamente
    - Documentación está actualizada
    """

    def __init__(self, test_client: TestClient = None, db_session: AsyncSession = None):
        self.test_client = test_client
        self.db_session = db_session
        self.project_root = Path(__file__).parent.parent.parent.parent

    async def run_integration_tests(self, module_record: ModuleRecord,
                                  module_metadata: ModuleMetadata) -> IntegrationTestSuite:
        """
        Ejecuta todas las pruebas de integración para un módulo
        """
        suite = IntegrationTestSuite(module_name=module_record.name)
        suite.start_time = datetime.utcnow()

        logger.info(f"Starting integration tests for module {module_record.name}")

        try:
            # Prueba 1: Validar estructura del módulo
            result = await self._test_module_structure(module_record, module_metadata)
            suite.add_test(result)

            # Prueba 2: Validar APIs
            result = await self._test_module_apis(module_record, module_metadata)
            suite.add_test(result)

            # Prueba 3: Validar base de datos
            result = await self._test_database_integration(module_record, module_metadata)
            suite.add_test(result)

            # Prueba 4: Validar integración frontend
            result = await self._test_frontend_integration(module_record, module_metadata)
            suite.add_test(result)

            # Prueba 5: Validar documentación
            result = await self._test_documentation_integration(module_record, module_metadata)
            suite.add_test(result)

            # Prueba 6: Validar dependencias
            result = await self._test_dependencies_integration(module_record, module_metadata)
            suite.add_test(result)

            # Prueba 7: Validar configuración
            result = await self._test_configuration_integration(module_record, module_metadata)
            suite.add_test(result)

            # Prueba 8: Pruebas de carga básicas
            result = await self._test_basic_load(module_record, module_metadata)
            suite.add_test(result)

        except Exception as e:
            logger.error(f"Integration testing failed for {module_record.name}: {e}")
            error_result = TestResult(
                test_name="integration_test_suite",
                description="Integration test suite execution",
                success=False,
                duration=0.0,
                error_message=str(e)
            )
            suite.add_test(error_result)

        suite.complete()

        success_rate = (suite.passed_tests / suite.total_tests * 100) if suite.total_tests > 0 else 0
        logger.info(f"Integration tests completed for {module_record.name}: "
                   f"{suite.passed_tests}/{suite.total_tests} passed ({success_rate:.1f}%) "
                   f"in {suite.total_duration:.2f}s")

        return suite

    async def _test_module_structure(self, module_record: ModuleRecord,
                                   module_metadata: ModuleMetadata) -> TestResult:
        """Prueba la estructura del módulo"""
        start_time = time.time()

        try:
            module_path = Path(module_record.path)

            # Verificar archivos requeridos
            required_files = ["routes.py", "models.py"]
            missing_files = []

            for file_name in required_files:
                if not (module_path / file_name).exists():
                    missing_files.append(file_name)

            if missing_files:
                return TestResult(
                    test_name="module_structure",
                    description="Validate module file structure",
                    success=False,
                    duration=time.time() - start_time,
                    error_message=f"Missing required files: {missing_files}",
                    details={"missing_files": missing_files}
                )

            # Verificar que se pueda importar
            try:
                __import__(module_record.name)
            except ImportError as e:
                return TestResult(
                    test_name="module_structure",
                    description="Validate module import",
                    success=False,
                    duration=time.time() - start_time,
                    error_message=f"Cannot import module: {e}",
                    details={"import_error": str(e)}
                )

            return TestResult(
                test_name="module_structure",
                description="Validate module file structure and import",
                success=True,
                duration=time.time() - start_time,
                details={"files_present": required_files}
            )

        except Exception as e:
            return TestResult(
                test_name="module_structure",
                description="Validate module file structure",
                success=False,
                duration=time.time() - start_time,
                error_message=str(e)
            )

    async def _test_module_apis(self, module_record: ModuleRecord,
                              module_metadata: ModuleMetadata) -> TestResult:
        """Prueba las APIs del módulo"""
        start_time = time.time()

        if not self.test_client:
            return TestResult(
                test_name="module_apis",
                description="Test module API endpoints",
                success=False,
                duration=time.time() - start_time,
                error_message="Test client not available"
            )

        try:
            base_url = f"/api/v1/{module_record.name}"

            # Probar endpoint de listado
            response = self.test_client.get(base_url)
            api_tests = []

            if response.status_code == 200:
                api_tests.append({"endpoint": base_url, "method": "GET", "status": "PASS"})
            else:
                api_tests.append({
                    "endpoint": base_url,
                    "method": "GET",
                    "status": "FAIL",
                    "status_code": response.status_code
                })

            # Probar endpoint de creación (si existe)
            create_response = self.test_client.post(base_url, json={})
            if create_response.status_code in [200, 201, 400, 422]:  # 400/422 son errores de validación esperados
                api_tests.append({"endpoint": base_url, "method": "POST", "status": "PASS"})
            else:
                api_tests.append({
                    "endpoint": base_url,
                    "method": "POST",
                    "status": "FAIL",
                    "status_code": create_response.status_code
                })

            # Verificar que al menos un endpoint funciona
            passed_tests = [t for t in api_tests if t["status"] == "PASS"]

            return TestResult(
                test_name="module_apis",
                description="Test module API endpoints",
                success=len(passed_tests) > 0,
                duration=time.time() - start_time,
                details={
                    "api_tests": api_tests,
                    "passed_count": len(passed_tests),
                    "total_count": len(api_tests)
                }
            )

        except Exception as e:
            return TestResult(
                test_name="module_apis",
                description="Test module API endpoints",
                success=False,
                duration=time.time() - start_time,
                error_message=str(e)
            )

    async def _test_database_integration(self, module_record: ModuleRecord,
                                       module_metadata: ModuleMetadata) -> TestResult:
        """Prueba la integración con la base de datos"""
        start_time = time.time()

        if not self.db_session:
            return TestResult(
                test_name="database_integration",
                description="Test database integration",
                success=False,
                duration=time.time() - start_time,
                error_message="Database session not available"
            )

        try:
            # Verificar que las tablas del módulo existen
            tables_created = 0
            tables_missing = []

            # Obtener nombres de tablas esperadas desde los modelos
            expected_tables = await self._get_expected_tables(module_record, module_metadata)

            for table_name in expected_tables:
                try:
                    # Intentar hacer una consulta simple
                    result = await self.db_session.execute(f"SELECT 1 FROM {table_name} LIMIT 1")
                    tables_created += 1
                except Exception:
                    tables_missing.append(table_name)

            success = len(tables_missing) == 0

            return TestResult(
                test_name="database_integration",
                description="Test database table creation",
                success=success,
                duration=time.time() - start_time,
                details={
                    "expected_tables": expected_tables,
                    "tables_created": tables_created,
                    "tables_missing": tables_missing
                }
            )

        except Exception as e:
            return TestResult(
                test_name="database_integration",
                description="Test database integration",
                success=False,
                duration=time.time() - start_time,
                error_message=str(e)
            )

    async def _test_frontend_integration(self, module_record: ModuleRecord,
                                       module_metadata: ModuleMetadata) -> TestResult:
        """Prueba la integración del frontend"""
        start_time = time.time()

        try:
            # Verificar que los archivos frontend existen
            frontend_path = self.project_root / "frontend" / "src" / "modules" / module_record.name

            if not frontend_path.exists():
                return TestResult(
                    test_name="frontend_integration",
                    description="Test frontend component integration",
                    success=False,
                    duration=time.time() - start_time,
                    error_message="Frontend components not found",
                    details={"frontend_path": str(frontend_path)}
                )

            # Verificar archivos principales
            main_files = ["index.tsx", "components", "pages"]
            files_present = []

            for file_name in main_files:
                if (frontend_path / file_name).exists():
                    files_present.append(file_name)

            # Verificar configuración de Next.js
            next_config = self.project_root / "frontend" / "next.config.js"
            config_updated = False

            if next_config.exists():
                with open(next_config, 'r', encoding='utf-8') as f:
                    config_content = f.read()
                    if module_record.name in config_content:
                        config_updated = True

            return TestResult(
                test_name="frontend_integration",
                description="Test frontend component integration",
                success=len(files_present) > 0,
                duration=time.time() - start_time,
                details={
                    "frontend_path": str(frontend_path),
                    "files_present": files_present,
                    "next_config_updated": config_updated
                }
            )

        except Exception as e:
            return TestResult(
                test_name="frontend_integration",
                description="Test frontend component integration",
                success=False,
                duration=time.time() - start_time,
                error_message=str(e)
            )

    async def _test_documentation_integration(self, module_record: ModuleRecord,
                                            module_metadata: ModuleMetadata) -> TestResult:
        """Prueba la integración de documentación"""
        start_time = time.time()

        try:
            # Verificar documentación API
            api_docs = self.project_root / "docs" / "api-documentation.md"

            if not api_docs.exists():
                return TestResult(
                    test_name="documentation_integration",
                    description="Test API documentation integration",
                    success=False,
                    duration=time.time() - start_time,
                    error_message="API documentation file not found"
                )

            with open(api_docs, 'r', encoding='utf-8') as f:
                docs_content = f.read()

            # Verificar que el módulo esté documentado
            module_documented = module_record.name.upper() in docs_content

            return TestResult(
                test_name="documentation_integration",
                description="Test API documentation integration",
                success=module_documented,
                duration=time.time() - start_time,
                details={
                    "api_docs_path": str(api_docs),
                    "module_documented": module_documented
                }
            )

        except Exception as e:
            return TestResult(
                test_name="documentation_integration",
                description="Test API documentation integration",
                success=False,
                duration=time.time() - start_time,
                error_message=str(e)
            )

    async def _test_dependencies_integration(self, module_record: ModuleRecord,
                                           module_metadata: ModuleMetadata) -> TestResult:
        """Prueba la integración de dependencias"""
        start_time = time.time()

        try:
            dependencies_ok = True
            dependency_status = []

            for dep in module_metadata.dependencies:
                try:
                    __import__(dep)
                    dependency_status.append({"name": dep, "status": "OK"})
                except ImportError:
                    dependency_status.append({"name": dep, "status": "MISSING"})
                    dependencies_ok = False

            return TestResult(
                test_name="dependencies_integration",
                description="Test module dependencies",
                success=dependencies_ok,
                duration=time.time() - start_time,
                details={"dependency_status": dependency_status}
            )

        except Exception as e:
            return TestResult(
                test_name="dependencies_integration",
                description="Test module dependencies",
                success=False,
                duration=time.time() - start_time,
                error_message=str(e)
            )

    async def _test_configuration_integration(self, module_record: ModuleRecord,
                                            module_metadata: ModuleMetadata) -> TestResult:
        """Prueba la integración de configuración"""
        start_time = time.time()

        try:
            # Verificar configuración del módulo
            config_ok = True
            config_checks = []

            # Verificar que el módulo esté en la configuración principal
            main_config = self.project_root / "backend" / "app" / "core" / "config.py"
            if main_config.exists():
                with open(main_config, 'r', encoding='utf-8') as f:
                    config_content = f.read()
                    if module_record.name in config_content:
                        config_checks.append({"check": "main_config", "status": "OK"})
                    else:
                        config_checks.append({"check": "main_config", "status": "MISSING"})
                        config_ok = False

            return TestResult(
                test_name="configuration_integration",
                description="Test module configuration",
                success=config_ok,
                duration=time.time() - start_time,
                details={"config_checks": config_checks}
            )

        except Exception as e:
            return TestResult(
                test_name="configuration_integration",
                description="Test module configuration",
                success=False,
                duration=time.time() - start_time,
                error_message=str(e)
            )

    async def _test_basic_load(self, module_record: ModuleRecord,
                             module_metadata: ModuleMetadata) -> TestResult:
        """Prueba de carga básica"""
        start_time = time.time()

        if not self.test_client:
            return TestResult(
                test_name="basic_load",
                description="Test basic load handling",
                success=False,
                duration=time.time() - start_time,
                error_message="Test client not available"
            )

        try:
            base_url = f"/api/v1/{module_record.name}"

            # Hacer múltiples requests para probar carga básica
            request_count = 5
            successful_requests = 0

            for i in range(request_count):
                try:
                    response = self.test_client.get(base_url)
                    if response.status_code == 200:
                        successful_requests += 1
                except Exception:
                    pass  # Ignorar errores individuales

            success_rate = successful_requests / request_count
            success = success_rate >= 0.8  # Al menos 80% de éxito

            return TestResult(
                test_name="basic_load",
                description="Test basic load handling",
                success=success,
                duration=time.time() - start_time,
                details={
                    "total_requests": request_count,
                    "successful_requests": successful_requests,
                    "success_rate": success_rate
                }
            )

        except Exception as e:
            return TestResult(
                test_name="basic_load",
                description="Test basic load handling",
                success=False,
                duration=time.time() - start_time,
                error_message=str(e)
            )

    async def _get_expected_tables(self, module_record: ModuleRecord,
                                 module_metadata: ModuleMetadata) -> List[str]:
        """Obtiene las tablas esperadas para el módulo"""
        expected_tables = []

        # Inferir nombres de tablas desde los modelos
        for model in module_metadata.models:
            if hasattr(model, '__tablename__'):
                expected_tables.append(model.__tablename__)

        # Si no hay modelos con __tablename__, intentar inferir
        if not expected_tables:
            # Asumir tabla en plural
            expected_tables.append(f"{module_record.name}s")

        return expected_tables

# Instancia global del Integration Testing System
integration_testing = IntegrationTestingSystem()

# Funciones de conveniencia
async def get_integration_testing_system() -> IntegrationTestingSystem:
    """Dependency injection para el integration testing system"""
    return integration_testing

async def run_module_integration_tests(module_record: ModuleRecord,
                                     module_metadata: ModuleMetadata) -> IntegrationTestSuite:
    """Función de conveniencia para ejecutar pruebas de integración"""
    return await integration_testing.run_integration_tests(module_record, module_metadata)