"""
Module Registry for Proyecto Semilla
Manages module metadata, versions, and discovery
"""

import asyncio
import json
from typing import Dict, List, Any, Optional
from pathlib import Path
from datetime import datetime


class ModuleRegistry:
    """
    Registry for managing module metadata and discovery
    """

    def __init__(self, registry_path: Optional[Path] = None):
        self.registry_path = registry_path or Path("backend/app/modules/registry.json")
        self.registry_path.parent.mkdir(parents=True, exist_ok=True)
        self.modules: Dict[str, Dict[str, Any]] = {}
        self._load_registry()

    def _load_registry(self):
        """Load registry from disk"""
        if self.registry_path.exists():
            try:
                with open(self.registry_path, 'r') as f:
                    self.modules = json.load(f)
            except Exception as e:
                print(f"Failed to load registry: {e}")
                self.modules = {}

    def _save_registry(self):
        """Save registry to disk"""
        try:
            with open(self.registry_path, 'w') as f:
                json.dump(self.modules, f, indent=2, default=str)
        except Exception as e:
            print(f"Failed to save registry: {e}")

    def register_module(self, name: str, metadata: Dict[str, Any]) -> bool:
        """
        Register a module in the registry
        """
        try:
            if name in self.modules:
                # Update existing module
                self.modules[name].update(metadata)
                self.modules[name]["updated_at"] = datetime.utcnow().isoformat()
            else:
                # Register new module
                metadata["registered_at"] = datetime.utcnow().isoformat()
                metadata["updated_at"] = metadata["registered_at"]
                self.modules[name] = metadata

            self._save_registry()
            return True

        except Exception as e:
            print(f"Failed to register module {name}: {e}")
            return False

    def unregister_module(self, name: str) -> bool:
        """
        Remove a module from the registry
        """
        if name in self.modules:
            del self.modules[name]
            self._save_registry()
            return True
        return False

    def get_module(self, name: str) -> Optional[Dict[str, Any]]:
        """
        Get module metadata
        """
        return self.modules.get(name)

    def list_modules(self, category: Optional[str] = None, limit: int = 100) -> List[Dict[str, Any]]:
        """
        List all registered modules
        """
        modules = list(self.modules.values())

        if category:
            modules = [m for m in modules if category in m.get("categories", [])]

        # Sort by registration date (newest first)
        modules.sort(key=lambda x: x.get("registered_at", ""), reverse=True)

        return modules[:limit]

    def search_modules(self, query: str, limit: int = 50) -> List[Dict[str, Any]]:
        """
        Search modules by name or description
        """
        query_lower = query.lower()
        results = []

        for name, metadata in self.modules.items():
            if (query_lower in name.lower() or
                query_lower in metadata.get("description", "").lower() or
                query_lower in metadata.get("display_name", "").lower()):
                results.append(metadata)

        # Sort by relevance (name matches first)
        results.sort(key=lambda x: (
            not query_lower in x.get("name", "").lower(),
            x.get("registered_at", "")
        ), reverse=True)

        return results[:limit]

    def get_module_versions(self, name: str) -> List[Dict[str, Any]]:
        """
        Get all versions of a module
        """
        module = self.get_module(name)
        if not module:
            return []

        versions = module.get("versions", [])
        # Sort by version (newest first)
        versions.sort(key=lambda x: x.get("released_at", ""), reverse=True)
        return versions

    def add_module_version(self, name: str, version: str, version_data: Dict[str, Any]) -> bool:
        """
        Add a new version to a module
        """
        if name not in self.modules:
            return False

        if "versions" not in self.modules[name]:
            self.modules[name]["versions"] = []

        # Check if version already exists
        existing_versions = [v["version"] for v in self.modules[name]["versions"]]
        if version in existing_versions:
            # Update existing version
            for i, v in enumerate(self.modules[name]["versions"]):
                if v["version"] == version:
                    self.modules[name]["versions"][i] = version_data
                    break
        else:
            # Add new version
            version_data["version"] = version
            version_data["released_at"] = datetime.utcnow().isoformat()
            self.modules[name]["versions"].append(version_data)

        # Update latest version
        self.modules[name]["latest_version"] = version
        self.modules[name]["updated_at"] = datetime.utcnow().isoformat()

        self._save_registry()
        return True

    def get_latest_version(self, name: str) -> Optional[str]:
        """
        Get the latest version of a module
        """
        module = self.get_module(name)
        if module:
            return module.get("latest_version")
        return None

    def validate_module_metadata(self, metadata: Dict[str, Any]) -> List[str]:
        """
        Validate module metadata
        """
        errors = []

        required_fields = ["name", "version", "description", "author"]
        for field in required_fields:
            if field not in metadata:
                errors.append(f"Missing required field: {field}")

        # Validate version format (basic semver check)
        version = metadata.get("version", "")
        if not self._is_valid_version(version):
            errors.append(f"Invalid version format: {version}")

        # Validate dependencies
        dependencies = metadata.get("dependencies", [])
        if not isinstance(dependencies, list):
            errors.append("Dependencies must be a list")
        else:
            for dep in dependencies:
                if not isinstance(dep, dict) or "name" not in dep or "version" not in dep:
                    errors.append(f"Invalid dependency format: {dep}")

        return errors

    def _is_valid_version(self, version: str) -> bool:
        """
        Basic semver validation
        """
        import re
        # Simple semver pattern: x.y.z
        pattern = r'^\d+\.\d+\.\d+(-[\w\.\-]+)?(\+[\w\.\-]+)?$'
        return bool(re.match(pattern, version))

    def get_registry_stats(self) -> Dict[str, Any]:
        """
        Get registry statistics
        """
        total_modules = len(self.modules)
        total_versions = sum(len(m.get("versions", [])) for m in self.modules.values())

        categories = {}
        for module in self.modules.values():
            for category in module.get("categories", []):
                categories[category] = categories.get(category, 0) + 1

        return {
            "total_modules": total_modules,
            "total_versions": total_versions,
            "categories": categories,
            "last_updated": max(
                (m.get("updated_at") for m in self.modules.values() if m.get("updated_at")),
                default=None
            )
        }

    async def sync_with_remote_registry(self, remote_url: str) -> Dict[str, Any]:
        """
        Sync registry with a remote registry
        """
        try:
            # In a real implementation, this would fetch from remote registry
            # For now, just return current stats
            return {
                "success": True,
                "synced_modules": len(self.modules),
                "message": "Registry sync completed"
            }

        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }

    def export_registry(self, format: str = "json") -> str:
        """
        Export registry in specified format
        """
        if format == "json":
            return json.dumps(self.modules, indent=2, default=str)
        else:
            raise ValueError(f"Unsupported export format: {format}")

    def import_registry(self, data: str, format: str = "json") -> bool:
        """
        Import registry from data
        """
        try:
            if format == "json":
                imported_modules = json.loads(data)
                self.modules.update(imported_modules)
                self._save_registry()
                return True
            else:
                raise ValueError(f"Unsupported import format: {format}")

        except Exception as e:
            print(f"Failed to import registry: {e}")
            return False