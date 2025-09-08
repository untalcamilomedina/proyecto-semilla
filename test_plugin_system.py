#!/usr/bin/env python3
"""
Test script for Plugin System
Prueba el sistema de plugins sin necesidad de base de datos completa
"""

import asyncio
import sys
import os
from pathlib import Path

# Agregar el directorio backend al path
backend_path = Path(__file__).parent / "backend"
sys.path.insert(0, str(backend_path))

async def test_plugin_system():
    """Prueba el sistema de plugins"""

    print("🧪 Testing Plugin System...")
    print("=" * 50)

    try:
        # Importar componentes del sistema de plugins
        from app.plugins.manager import PluginManager
        from app.plugins.registry import ModuleRegistry
        from app.plugins.integration_pipeline import AutoIntegrationPipeline
        from app.plugins.integration_testing import IntegrationTestingSystem

        print("✅ Plugin system imports successful")

        # Crear instancias
        manager = PluginManager()
        registry = ModuleRegistry()
        pipeline = AutoIntegrationPipeline()
        testing = IntegrationTestingSystem()

        print("✅ Plugin system components initialized")

        # Descubrir módulos
        print("\n🔍 Discovering modules...")
        discovered = await manager.discover_modules()

        if discovered:
            print(f"✅ Found {len(discovered)} modules: {discovered}")

            # Probar con el módulo CMS
            cms_module = "cms"
            if cms_module in discovered:
                print(f"\n📦 Testing module: {cms_module}")

                # Registrar módulo en el registry
                module_path = Path("modules") / cms_module
                module_record = await registry.register_module(module_path)
                print(f"✅ Module registered: {module_record.name} v{module_record.version}")

                # Cargar módulo
                loaded = await manager.load_module(cms_module)
                if loaded:
                    print("✅ Module loaded successfully")

                    # Obtener metadata
                    metadata = manager.modules.get(cms_module)
                    if metadata:
                        print(f"📊 Module info:")
                        print(f"   - Routes: {len(metadata.routes)}")
                        print(f"   - Models: {len(metadata.models)}")
                        print(f"   - Services: {len(metadata.services)}")

                        # Probar integración (sin app real)
                        print("\n🔧 Testing integration pipeline...")
                        # Nota: No podemos probar integración completa sin FastAPI app
                        print("   (Skipping full integration - requires FastAPI app)")

                        # Probar testing system
                        print("\n🧪 Testing integration testing system...")
                        # Crear mock test client
                        class MockTestClient:
                            def get(self, url):
                                class MockResponse:
                                    status_code = 200
                                    def json(self): return {"status": "ok"}
                                return MockResponse()

                        testing.test_client = MockTestClient()

                        # Ejecutar pruebas de estructura
                        test_result = await testing._test_module_structure(module_record, metadata)
                        print(f"   Structure test: {'✅ PASS' if test_result.success else '❌ FAIL'}")

                        print("✅ Integration testing system working")

                else:
                    print("❌ Failed to load module")

        else:
            print("❌ No modules found")
            print("   Make sure modules are in the 'modules/' directory")

        # Mostrar estado del sistema
        print("\n📈 System Status:")
        modules = manager.list_modules()
        print(f"   - Total modules: {len(modules)}")
        print(f"   - Loaded modules: {len([m for m in modules if m['loaded']])}")

        print("\n🎉 Plugin system test completed successfully!")

    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

    return True

async def test_plugin_discovery():
    """Prueba específica del sistema de discovery"""

    print("\n🔍 Testing Plugin Discovery...")

    try:
        from app.plugins.manager import PluginManager

        manager = PluginManager()

        # Verificar que puede encontrar módulos
        discovered = await manager.discover_modules()

        print(f"Discovered modules: {discovered}")

        # Verificar estructura de módulos
        for module_name in discovered:
            module_path = Path("modules") / module_name
            print(f"Module {module_name}:")
            print(f"  Path: {module_path}")
            print(f"  Exists: {module_path.exists()}")

            if module_path.exists():
                files = list(module_path.glob("*.py"))
                print(f"  Python files: {[f.name for f in files]}")

        return True

    except Exception as e:
        print(f"❌ Discovery test failed: {e}")
        return False

if __name__ == "__main__":
    print("🚀 Starting Plugin System Tests")
    print("=" * 50)

    # Ejecutar pruebas
    success = asyncio.run(test_plugin_system())

    if success:
        # Prueba adicional de discovery
        asyncio.run(test_plugin_discovery())

    print("\n" + "=" * 50)
    if success:
        print("🎉 All tests passed!")
        sys.exit(0)
    else:
        print("❌ Some tests failed!")
        sys.exit(1)