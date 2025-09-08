#!/usr/bin/env python3
"""
Test API Integration for Plugin System
Prueba la integración de módulos con la API
"""

import asyncio
import sys
import os
from pathlib import Path
import requests

# Agregar el directorio backend al path
backend_path = Path(__file__).parent / "backend"
sys.path.insert(0, str(backend_path))

async def test_api_integration():
    """Prueba la integración de la API con el sistema de plugins"""

    print("🔌 Testing API Integration...")
    print("=" * 50)

    try:
        # Verificar que podemos importar el sistema
        from app.plugins.manager import PluginManager
        from app.plugins.registry import ModuleRegistry

        print("✅ Plugin system imports successful")

        # Crear instancias
        manager = PluginManager()
        registry = ModuleRegistry()

        # Descubrir módulos
        discovered = await manager.discover_modules()
        print(f"✅ Discovered modules: {discovered}")

        # Probar integración del módulo CMS
        if "cms" in discovered:
            print("\n📦 Integrating CMS module...")

            # Registrar módulo
            module_path = Path("modules/cms")
            module_record = await registry.register_module(module_path)
            print(f"✅ Module registered: {module_record.name}")

            # Cargar módulo
            loaded = await manager.load_module("cms")
            print(f"✅ Module loaded: {loaded}")

            # Verificar que el módulo tiene rutas
            metadata = manager.modules.get("cms")
            if metadata:
                print(f"📊 Module metadata:")
                print(f"   - Routes: {len(metadata.routes)}")
                print(f"   - Models: {len(metadata.models)}")
                print(f"   - Services: {len(metadata.services)}")

                # Intentar acceder al router del módulo
                try:
                    import importlib
                    cms_module = importlib.import_module("cms")
                    print(f"✅ CMS module imported successfully")

                    if hasattr(cms_module, 'router'):
                        print(f"✅ CMS router found: {type(cms_module.router)}")
                        print(f"   Router routes: {len(cms_module.router.routes) if hasattr(cms_module.router, 'routes') else 'N/A'}")
                    else:
                        print("⚠️  CMS router not found")

                except ImportError as e:
                    print(f"❌ Failed to import CMS module: {e}")

        # Probar endpoints de gestión de plugins (si el servidor está corriendo)
        print("\n🌐 Testing plugin management endpoints...")

        try:
            # Verificar si el servidor está corriendo en el puerto 7778
            response = requests.get("http://localhost:7778/api/v1/plugins/status", timeout=5)
            if response.status_code == 200:
                status_data = response.json()
                print("✅ Plugin status endpoint working")
                print(f"   Status: {status_data.get('status', 'unknown')}")

                # Listar plugins
                response = requests.get("http://localhost:7778/api/v1/plugins/", timeout=5)
                if response.status_code == 200:
                    plugins_data = response.json()
                    print("✅ Plugin list endpoint working")
                    print(f"   Plugins: {len(plugins_data.get('plugins', []))}")

                    # Intentar instalar el módulo CMS
                    install_response = requests.post(
                        "http://localhost:7778/api/v1/plugins/cms/install",
                        timeout=10
                    )
                    if install_response.status_code == 200:
                        install_data = install_response.json()
                        print("✅ Plugin install endpoint working")
                        print(f"   Install result: {install_data.get('message', 'unknown')}")
                    else:
                        print(f"⚠️  Plugin install failed: {install_response.status_code}")
                        print(f"   Error: {install_response.text}")

            else:
                print(f"⚠️  Server not responding on port 7778: {response.status_code}")

        except requests.exceptions.RequestException as e:
            print(f"⚠️  Cannot connect to server: {e}")
            print("   Make sure the backend server is running on port 7778")

        print("\n🎉 API integration test completed!")

    except Exception as e:
        print(f"❌ API integration test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

    return True

async def test_module_structure():
    """Prueba la estructura de módulos"""

    print("\n🔍 Testing Module Structure...")

    try:
        from app.plugins.manager import PluginManager

        manager = PluginManager()

        # Verificar módulos disponibles
        discovered = await manager.discover_modules()

        for module_name in discovered:
            print(f"\n📁 Module: {module_name}")
            module_path = Path("modules") / module_name

            # Verificar archivos requeridos
            required_files = ["routes.py", "models.py", "services.py"]
            for file_name in required_files:
                file_path = module_path / file_name
                exists = file_path.exists()
                print(f"   {file_name}: {'✅' if exists else '❌'}")

            # Verificar si se puede importar
            try:
                import importlib
                module = importlib.import_module(module_name)
                print(f"   Import: ✅")

                # Verificar componentes principales
                has_router = hasattr(module, 'router')
                print(f"   Router: {'✅' if has_router else '❌'}")

            except ImportError as e:
                print(f"   Import: ❌ ({e})")

        return True

    except Exception as e:
        print(f"❌ Module structure test failed: {e}")
        return False

if __name__ == "__main__":
    print("🚀 Starting API Integration Tests")
    print("=" * 50)

    # Ejecutar pruebas
    success = asyncio.run(test_api_integration())

    if success:
        # Prueba adicional de estructura
        asyncio.run(test_module_structure())

    print("\n" + "=" * 50)
    if success:
        print("🎉 API integration tests completed!")
        sys.exit(0)
    else:
        print("❌ Some API integration tests failed!")
        sys.exit(1)