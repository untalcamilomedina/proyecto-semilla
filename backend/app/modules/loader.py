"""
Module Loader for Proyecto Semilla
Handles dynamic loading, reloading, and validation of MCP modules
"""

import asyncio
import importlib
import importlib.util
import sys
from typing import Dict, List, Any, Optional
from pathlib import Path
import hashlib
import json


class ModuleLoader:
    """
    Dynamic module loader with hot-reload capabilities
    """

    def __init__(self):
        self.loaded_modules: Dict[str, Any] = {}
        self.module_specs: Dict[str, Any] = {}
        self.module_checksums: Dict[str, str] = {}

    async def download_module(self, name: str, version: str, target_path: Path) -> bool:
        """
        Download and extract a module from registry
        """
        try:
            # Create module directory
            target_path.mkdir(parents=True, exist_ok=True)

            # In a real implementation, this would:
            # 1. Fetch module from registry
            # 2. Download archive
            # 3. Extract to target_path
            # 4. Install dependencies

            # For now, create a basic module structure
            await self._create_basic_module_structure(name, version, target_path)

            return True

        except Exception as e:
            print(f"Failed to download module {name}: {e}")
            return False

    async def validate_module_structure(self, module_path: Path) -> bool:
        """
        Validate that a module has the required structure
        """
        required_files = ["__init__.py", "module.json"]
        required_dirs = ["handlers", "schemas"]

        # Check required files
        for file in required_files:
            if not (module_path / file).exists():
                print(f"Missing required file: {file}")
                return False

        # Check required directories
        for dir_name in required_dirs:
            if not (module_path / dir_name).exists():
                print(f"Missing required directory: {dir_name}")
                return False

        # Validate module.json
        try:
            with open(module_path / "module.json", 'r') as f:
                metadata = json.load(f)

            required_fields = ["name", "version", "description", "main"]
            for field in required_fields:
                if field not in metadata:
                    print(f"Missing required field in module.json: {field}")
                    return False

        except Exception as e:
            print(f"Invalid module.json: {e}")
            return False

        return True

    async def load_module(self, name: str, module_path: Path) -> Any:
        """
        Load a module dynamically
        """
        try:
            # Calculate checksum for change detection
            checksum = await self._calculate_module_checksum(module_path)
            self.module_checksums[name] = checksum

            # Load module spec
            spec = await self._load_module_spec(name, module_path)
            if not spec:
                raise ValueError(f"Could not load module spec for {name}")

            self.module_specs[name] = spec

            # Execute module
            module = await self._execute_module(spec)

            # Validate module interface
            await self._validate_module_interface(module)

            # Cache loaded module
            self.loaded_modules[name] = module

            return module

        except Exception as e:
            print(f"Failed to load module {name}: {e}")
            raise

    async def reload_module(self, name: str, module_path: Path) -> Any:
        """
        Hot-reload a module
        """
        try:
            # Check if module has changed
            new_checksum = await self._calculate_module_checksum(module_path)
            old_checksum = self.module_checksums.get(name)

            if new_checksum == old_checksum:
                # No changes, return existing module
                return self.loaded_modules.get(name)

            # Unload old module
            await self._unload_module(name)

            # Load new version
            return await self.load_module(name, module_path)

        except Exception as e:
            print(f"Failed to reload module {name}: {e}")
            raise

    async def unload_module(self, name: str) -> bool:
        """
        Unload a module
        """
        try:
            await self._unload_module(name)
            return True
        except Exception as e:
            print(f"Failed to unload module {name}: {e}")
            return False

    async def _load_module_spec(self, name: str, module_path: Path) -> Optional[Any]:
        """
        Load module spec from filesystem
        """
        # Read module metadata
        metadata_file = module_path / "module.json"
        if not metadata_file.exists():
            raise ValueError(f"Module metadata not found: {metadata_file}")

        with open(metadata_file, 'r') as f:
            metadata = json.load(f)

        # Get main entry point
        main_file = metadata.get("main", "__init__.py")
        main_path = module_path / main_file

        if not main_path.exists():
            raise ValueError(f"Main module file not found: {main_path}")

        # Create module spec
        spec = importlib.util.spec_from_file_location(name, main_path)
        return spec

    async def _execute_module(self, spec: Any) -> Any:
        """
        Execute a module spec
        """
        module = importlib.util.module_from_spec(spec)
        sys.modules[spec.name] = module
        spec.loader.exec_module(module)
        return module

    async def _validate_module_interface(self, module: Any):
        """
        Validate that module implements required interface
        """
        required_methods = ["initialize", "cleanup"]
        optional_methods = [
            "start_background_tasks", "stop_background_tasks",
            "health_check", "on_config_update", "get_capabilities",
            "prepare_handover"
        ]

        for method in required_methods:
            if not hasattr(module, method):
                raise ValueError(f"Module missing required method: {method}")

        # Check method signatures
        import inspect

        # initialize should be async and accept config and client
        if not inspect.iscoroutinefunction(module.initialize):
            raise ValueError("initialize method must be async")

        # cleanup should be async
        if not inspect.iscoroutinefunction(module.cleanup):
            raise ValueError("cleanup method must be async")

    async def _unload_module(self, name: str):
        """
        Internal unload method
        """
        # Remove from sys.modules
        if name in sys.modules:
            del sys.modules[name]

        # Clean up caches
        if name in self.loaded_modules:
            del self.loaded_modules[name]
        if name in self.module_specs:
            del self.module_specs[name]
        if name in self.module_checksums:
            del self.module_checksums[name]

    async def _calculate_module_checksum(self, module_path: Path) -> str:
        """
        Calculate checksum of module files for change detection
        """
        hasher = hashlib.sha256()

        # Walk through all Python files
        for py_file in module_path.rglob("*.py"):
            if py_file.is_file():
                with open(py_file, 'rb') as f:
                    hasher.update(f.read())

        # Include module.json
        json_file = module_path / "module.json"
        if json_file.exists():
            with open(json_file, 'rb') as f:
                hasher.update(f.read())

        return hasher.hexdigest()

    async def _create_basic_module_structure(self, name: str, version: str, target_path: Path):
        """
        Create a basic module structure for development/testing
        """
        # Create module.json
        metadata = {
            "name": name,
            "version": version,
            "description": f"Basic module structure for {name}",
            "main": "__init__.py",
            "author": "Proyecto Semilla",
            "dependencies": [],
            "capabilities": {
                "tools": [],
                "resources": [],
                "prompts": []
            }
        }

        with open(target_path / "module.json", 'w') as f:
            json.dump(metadata, f, indent=2)

        # Create __init__.py
        init_content = f'''"""
Basic module: {name}
Generated module structure for Proyecto Semilla
"""

import asyncio
from typing import Dict, List, Any, Optional


class {name.replace('_', ' ').title().replace(' ', '')}Module:
    """
    Basic module implementation
    """

    def __init__(self):
        self.name = "{name}"
        self.version = "{version}"
        self.config = {{}}
        self.client = None
        self.background_tasks = set()

    async def initialize(self, config: Dict[str, Any], client: Any):
        """
        Initialize the module
        """
        self.config = config
        self.client = client
        print(f"Module {{self.name}} initialized with config: {{config}}")

    async def cleanup(self):
        """
        Cleanup module resources
        """
        # Stop background tasks
        await self.stop_background_tasks()
        print(f"Module {{self.name}} cleaned up")

    async def start_background_tasks(self) -> set:
        """
        Start background tasks
        """
        # Example background task
        task = asyncio.create_task(self._background_worker())
        self.background_tasks.add(task)
        return self.background_tasks

    async def stop_background_tasks(self):
        """
        Stop background tasks
        """
        for task in self.background_tasks:
            task.cancel()
        if self.background_tasks:
            await asyncio.gather(*self.background_tasks, return_exceptions=True)
        self.background_tasks.clear()

    async def health_check(self) -> Dict[str, Any]:
        """
        Health check
        """
        return {{
            "healthy": True,
            "status": "running",
            "version": self.version
        }}

    async def on_config_update(self, config: Dict[str, Any]):
        """
        Handle configuration updates
        """
        self.config = config
        print(f"Module {{self.name}} config updated: {{config}}")

    async def get_capabilities(self) -> Dict[str, Any]:
        """
        Get module capabilities
        """
        return {{
            "tools": [],
            "resources": [],
            "prompts": []
        }}

    async def prepare_handover(self):
        """
        Prepare for handover during hot-reload
        """
        print(f"Module {{self.name}} preparing for handover")

    async def _background_worker(self):
        """
        Example background worker
        """
        while True:
            try:
                # Do some work
                await asyncio.sleep(60)  # Run every minute
            except asyncio.CancelledError:
                break


# Module instance
module_instance = {name.replace('_', ' ').title().replace(' ', '')}Module()
'''

        with open(target_path / "__init__.py", 'w') as f:
            f.write(init_content)

        # Create handlers directory
        handlers_dir = target_path / "handlers"
        handlers_dir.mkdir(exist_ok=True)

        with open(handlers_dir / "__init__.py", 'w') as f:
            f.write("")

        # Create schemas directory
        schemas_dir = target_path / "schemas"
        schemas_dir.mkdir(exist_ok=True)

        with open(schemas_dir / "__init__.py", 'w') as f:
            f.write("")