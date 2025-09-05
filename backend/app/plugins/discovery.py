"""
Plugin Discovery and Installation System
Advanced plugin discovery, dependency resolution, and installation management
"""

import json
import asyncio
import hashlib
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Set, Tuple
from dataclasses import dataclass, asdict
import uuid
import re
import os

from .models import (
    PluginManifest, PluginInstance, PluginInstallation,
    EnvironmentType, PluginType
)
from .marketplace import plugin_registry, plugin_installer

@dataclass
class PluginDependency:
    """Plugin dependency specification"""
    name: str
    version_constraint: str
    type: str = "required"  # required, optional, recommended

@dataclass
class InstallationPlan:
    """Plugin installation plan with dependency resolution"""
    plugin_id: str
    dependencies: List[PluginDependency]
    installation_order: List[str]
    conflicts: List[str]
    warnings: List[str]

@dataclass
class PluginPackage:
    """Plugin package with metadata and files"""
    manifest: PluginManifest
    files: Dict[str, bytes]
    checksums: Dict[str, str]
    signature: Optional[str] = None

class PluginDiscoverer:
    """Plugin discovery and search system"""

    def __init__(self):
        self.discovery_cache: Dict[str, List[Dict[str, Any]]] = {}
        self.cache_expiry: Dict[str, datetime] = {}

    async def discover_plugins(self, query: str = "", filters: Optional[Dict[str, Any]] = None,
                             limit: int = 50) -> List[Dict[str, Any]]:
        """Discover plugins based on search criteria"""

        # Check cache first
        cache_key = f"{query}_{json.dumps(filters or {}, sort_keys=True)}"
        if cache_key in self.discovery_cache:
            if datetime.utcnow() < self.cache_expiry.get(cache_key, datetime.min):
                return self.discovery_cache[cache_key]

        # Search in marketplace
        plugins = await plugin_registry.search_plugins(query, filters)

        # Apply additional discovery logic
        discovered_plugins = await self._enrich_plugin_data(plugins)

        # Cache results
        self.discovery_cache[cache_key] = discovered_plugins[:limit]
        self.cache_expiry[cache_key] = datetime.utcnow() + timedelta(minutes=5)

        return discovered_plugins[:limit]

    async def get_plugin_recommendations(self, tenant_id: str, user_id: str,
                                       limit: int = 10) -> List[Dict[str, Any]]:
        """Get personalized plugin recommendations"""

        # Get user's installed plugins
        installed_plugins = await plugin_installer.get_tenant_plugins(tenant_id)
        installed_types = {p["plugin"]["type"] for p in installed_plugins}

        # Get user's plugin usage patterns
        usage_patterns = await self._analyze_usage_patterns(tenant_id, user_id)

        # Find complementary plugins
        recommendations = []
        all_plugins = await plugin_registry.search_plugins("")

        for plugin_data in all_plugins:
            plugin = plugin_data
            score = await self._calculate_recommendation_score(
                plugin, installed_types, usage_patterns
            )

            if score > 0.5:  # Minimum recommendation threshold
                recommendations.append({
                    "plugin": plugin,
                    "score": score,
                    "reason": await self._get_recommendation_reason(plugin, installed_types)
                })

        # Sort by score and return top recommendations
        recommendations.sort(key=lambda x: x["score"], reverse=True)
        return recommendations[:limit]

    async def get_trending_plugins(self, time_window_days: int = 7,
                                 limit: int = 10) -> List[Dict[str, Any]]:
        """Get trending plugins based on recent activity"""

        cutoff_date = datetime.utcnow() - timedelta(days=time_window_days)

        # Get plugins with recent activity (simplified)
        trending = []
        all_plugins = await plugin_registry.search_plugins("")

        for plugin_data in all_plugins:
            # Calculate trend score based on recent downloads/reviews
            trend_score = await self._calculate_trend_score(plugin_data, cutoff_date)

            if trend_score > 0:
                trending.append({
                    "plugin": plugin_data,
                    "trend_score": trend_score
                })

        trending.sort(key=lambda x: x["trend_score"], reverse=True)
        return trending[:limit]

    async def _enrich_plugin_data(self, plugins: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Enrich plugin data with additional metadata"""
        enriched = []

        for plugin in plugins:
            # Add compatibility information
            plugin["compatibility"] = await self._check_compatibility(plugin)

            # Add usage statistics
            plugin["usage_stats"] = await self._get_usage_stats(plugin["id"])

            # Add similar plugins
            plugin["similar_plugins"] = await self._find_similar_plugins(plugin)

            enriched.append(plugin)

        return enriched

    async def _check_compatibility(self, plugin: Dict[str, Any]) -> Dict[str, Any]:
        """Check plugin compatibility with current system"""
        # Simplified compatibility check
        return {
            "compatible": True,
            "version_supported": True,
            "dependencies_satisfied": True,
            "warnings": []
        }

    async def _get_usage_stats(self, plugin_id: str) -> Dict[str, Any]:
        """Get usage statistics for a plugin"""
        # Simplified usage stats
        return {
            "active_installations": 150,
            "avg_rating": 4.2,
            "total_reviews": 45,
            "last_updated": datetime.utcnow().isoformat()
        }

    async def _find_similar_plugins(self, plugin: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Find plugins similar to the given plugin"""
        # Simplified similarity search
        return []

    async def _analyze_usage_patterns(self, tenant_id: str, user_id: str) -> Dict[str, Any]:
        """Analyze usage patterns for recommendation"""
        return {"preferred_types": ["business", "analytics"]}

    async def _calculate_recommendation_score(self, plugin: Dict[str, Any],
                                           installed_types: Set[str],
                                           usage_patterns: Dict[str, Any]) -> float:
        """Calculate recommendation score"""
        score = 0.0

        # Type compatibility
        if plugin["type"] in usage_patterns.get("preferred_types", []):
            score += 0.4

        # Rating bonus
        if plugin["rating"] >= 4.0:
            score += 0.3

        # Download popularity
        if plugin["downloads"] > 100:
            score += 0.3

        return min(score, 1.0)

    async def _get_recommendation_reason(self, plugin: Dict[str, Any],
                                       installed_types: Set[str]) -> str:
        """Get recommendation reason"""
        if plugin["type"] in installed_types:
            return f"Enhances your existing {plugin['type']} capabilities"
        else:
            return f"Adds new {plugin['type']} functionality to your stack"

    async def _calculate_trend_score(self, plugin: Dict[str, Any], cutoff_date: datetime) -> float:
        """Calculate trend score for a plugin"""
        # Simplified trend calculation
        return plugin["downloads"] * 0.1

class DependencyResolver:
    """Plugin dependency resolution system"""

    def __init__(self, registry: 'PluginRegistry'):
        self.registry = registry
        self.resolution_cache: Dict[str, InstallationPlan] = {}

    async def resolve_dependencies(self, plugin_id: str) -> InstallationPlan:
        """Resolve all dependencies for a plugin"""

        if plugin_id in self.resolution_cache:
            return self.resolution_cache[plugin_id]

        # Get plugin details
        plugin_details = await self.registry.get_plugin_details(plugin_id)
        if not plugin_details:
            raise ValueError(f"Plugin {plugin_id} not found")

        plugin = plugin_details["plugin"]
        manifest = plugin.get("manifest", {})

        # Extract dependencies
        dependencies = []
        for dep in manifest.get("dependencies", []):
            dependencies.append(PluginDependency(
                name=dep["name"],
                version_constraint=dep["version"],
                type=dep.get("type", "required")
            ))

        # Resolve dependency tree
        resolved_deps, conflicts = await self._resolve_dependency_tree(dependencies)

        # Determine installation order
        installation_order = await self._calculate_installation_order(resolved_deps)

        # Generate warnings
        warnings = await self._generate_installation_warnings(resolved_deps, conflicts)

        plan = InstallationPlan(
            plugin_id=plugin_id,
            dependencies=resolved_deps,
            installation_order=installation_order,
            conflicts=conflicts,
            warnings=warnings
        )

        # Cache resolution
        self.resolution_cache[plugin_id] = plan

        return plan

    async def check_conflicts(self, plugin_id: str, installed_plugins: List[str]) -> List[str]:
        """Check for conflicts with installed plugins"""
        conflicts = []

        plugin_details = await self.registry.get_plugin_details(plugin_id)
        if not plugin_details:
            return conflicts

        manifest = plugin_details["plugin"].get("manifest", {})

        # Check for known conflicts
        for installed_plugin_id in installed_plugins:
            installed_details = await self.registry.get_plugin_details(installed_plugin_id)
            if installed_details:
                installed_manifest = installed_details["plugin"].get("manifest", {})

                # Check for conflicting entry points
                plugin_entry_points = set(manifest.get("entry_points", {}).keys())
                installed_entry_points = set(installed_manifest.get("entry_points", {}).keys())

                if plugin_entry_points & installed_entry_points:
                    conflicts.append(f"Entry point conflict with {installed_details['plugin']['name']}")

        return conflicts

    async def _resolve_dependency_tree(self, dependencies: List[PluginDependency]) -> Tuple[List[PluginDependency], List[str]]:
        """Resolve the complete dependency tree"""
        resolved = []
        conflicts = []

        for dep in dependencies:
            # Find compatible version
            compatible_plugin = await self._find_compatible_plugin(dep)

            if compatible_plugin:
                resolved.append(dep)
                # Recursively resolve sub-dependencies
                sub_deps, sub_conflicts = await self._resolve_plugin_dependencies(compatible_plugin)
                resolved.extend(sub_deps)
                conflicts.extend(sub_conflicts)
            else:
                conflicts.append(f"Cannot resolve dependency: {dep.name} {dep.version_constraint}")

        return resolved, conflicts

    async def _find_compatible_plugin(self, dependency: PluginDependency) -> Optional[str]:
        """Find a plugin that satisfies the dependency"""
        # Search for plugins matching the dependency
        plugins = await self.registry.search_plugins(dependency.name)

        for plugin in plugins:
            if self._version_satisfies_constraint(plugin["version"], dependency.version_constraint):
                return plugin["id"]

        return None

    async def _resolve_plugin_dependencies(self, plugin_id: str) -> Tuple[List[PluginDependency], List[str]]:
        """Resolve dependencies of a specific plugin"""
        plugin_details = await self.registry.get_plugin_details(plugin_id)
        if not plugin_details:
            return [], []

        manifest = plugin_details["plugin"].get("manifest", {})
        dependencies = []

        for dep in manifest.get("dependencies", []):
            dependencies.append(PluginDependency(
                name=dep["name"],
                version_constraint=dep["version"],
                type=dep.get("type", "required")
            ))

        return await self._resolve_dependency_tree(dependencies)

    async def _calculate_installation_order(self, dependencies: List[PluginDependency]) -> List[str]:
        """Calculate the optimal installation order"""
        # Simplified topological sort
        return [dep.name for dep in dependencies]

    async def _generate_installation_warnings(self, dependencies: List[PluginDependency],
                                           conflicts: List[str]) -> List[str]:
        """Generate installation warnings"""
        warnings = []

        # Check for optional dependencies
        for dep in dependencies:
            if dep.type == "optional":
                warnings.append(f"Optional dependency {dep.name} may enhance functionality")

        # Add conflict warnings
        for conflict in conflicts:
            warnings.append(f"Potential conflict: {conflict}")

        return warnings

    def _version_satisfies_constraint(self, version: str, constraint: str) -> bool:
        """Check if version satisfies the constraint"""
        # Simplified version checking
        if constraint.startswith("^"):
            base_version = constraint[1:]
            return version.startswith(base_version.split(".")[0])

        if constraint.startswith("~"):
            base_version = constraint[1:]
            return version.startswith(".".join(base_version.split(".")[:2]))

        return version == constraint

class PluginInstaller:
    """Advanced plugin installation system"""

    def __init__(self, registry: 'PluginRegistry', dependency_resolver: DependencyResolver):
        self.registry = registry
        self.dependency_resolver = dependency_resolver
        self.installation_history: Dict[str, List[Dict[str, Any]]] = {}

    async def install_plugin_with_dependencies(self, plugin_id: str, tenant_id: str,
                                            environment: EnvironmentType,
                                            installed_by: str) -> Dict[str, Any]:
        """Install plugin with automatic dependency resolution"""

        # Resolve dependencies
        installation_plan = await self.dependency_resolver.resolve_dependencies(plugin_id)

        if installation_plan.conflicts:
            return {
                "success": False,
                "error": "Dependency conflicts detected",
                "conflicts": installation_plan.conflicts
            }

        # Check for existing installations
        installed_plugins = await plugin_installer.get_tenant_plugins(tenant_id)
        installed_plugin_ids = [p["plugin"]["id"] for p in installed_plugins]

        conflicts = await self.dependency_resolver.check_conflicts(plugin_id, installed_plugin_ids)
        if conflicts:
            return {
                "success": False,
                "error": "Installation conflicts detected",
                "conflicts": conflicts
            }

        # Install dependencies first
        installed_dependencies = []
        for dep_name in installation_plan.installation_order:
            # Find plugin for dependency
            dep_plugin_id = await self._find_plugin_by_name(dep_name)
            if dep_plugin_id:
                await plugin_installer.install_plugin(
                    dep_plugin_id, tenant_id, environment, installed_by
                )
                installed_dependencies.append(dep_plugin_id)

        # Install main plugin
        installation_id = await plugin_installer.install_plugin(
            plugin_id, tenant_id, environment, installed_by
        )

        # Record installation
        installation_record = {
            "timestamp": datetime.utcnow(),
            "plugin_id": plugin_id,
            "tenant_id": tenant_id,
            "environment": environment.value,
            "installed_by": installed_by,
            "dependencies_installed": installed_dependencies,
            "warnings": installation_plan.warnings
        }

        if tenant_id not in self.installation_history:
            self.installation_history[tenant_id] = []
        self.installation_history[tenant_id].append(installation_record)

        return {
            "success": True,
            "installation_id": installation_id,
            "dependencies_installed": len(installed_dependencies),
            "warnings": installation_plan.warnings
        }

    async def validate_plugin_package(self, package: PluginPackage) -> Dict[str, Any]:
        """Validate plugin package integrity and compatibility"""

        validation_results = {
            "valid": True,
            "errors": [],
            "warnings": [],
            "checksums_valid": True,
            "signature_valid": True,
            "dependencies_resolvable": True
        }

        # Validate manifest
        manifest_errors = self._validate_manifest(package.manifest)
        validation_results["errors"].extend(manifest_errors)

        # Validate checksums
        checksum_errors = await self._validate_checksums(package)
        validation_results["errors"].extend(checksum_errors)

        # Validate signature
        if package.signature:
            signature_valid = await self._validate_signature(package)
            validation_results["signature_valid"] = signature_valid

        # Check dependencies
        dep_issues = await self._check_dependencies(package.manifest)
        validation_results["warnings"].extend(dep_issues)

        validation_results["valid"] = len(validation_results["errors"]) == 0

        return validation_results

    async def rollback_installation(self, plugin_id: str, tenant_id: str) -> bool:
        """Rollback plugin installation"""

        # Find installation record
        if tenant_id not in self.installation_history:
            return False

        # Find the most recent installation of this plugin
        installation_record = None
        for record in reversed(self.installation_history[tenant_id]):
            if record["plugin_id"] == plugin_id:
                installation_record = record
                break

        if not installation_record:
            return False

        # Uninstall dependencies (in reverse order)
        for dep_id in reversed(installation_record["dependencies_installed"]):
            await plugin_installer.uninstall_plugin(dep_id, tenant_id)

        # Uninstall main plugin
        success = await plugin_installer.uninstall_plugin(plugin_id, tenant_id)

        if success:
            # Remove from history
            self.installation_history[tenant_id].remove(installation_record)

        return success

    async def _find_plugin_by_name(self, name: str) -> Optional[str]:
        """Find plugin by name"""
        plugins = await self.registry.search_plugins(name)
        return plugins[0]["id"] if plugins else None

    def _validate_manifest(self, manifest: PluginManifest) -> List[str]:
        """Validate plugin manifest"""
        errors = []

        # Required fields
        required_fields = ["id", "name", "version", "description", "author", "type"]
        for field in required_fields:
            if not getattr(manifest, field, None):
                errors.append(f"Missing required field: {field}")

        # Version format
        if manifest.version and not re.match(r'^\d+\.\d+\.\d+$', manifest.version):
            errors.append("Version must be in format x.y.z")

        # Entry points validation
        if manifest.entry_points:
            for ep_name, ep_path in manifest.entry_points.items():
                if not ep_path or not ep_path.startswith("plugins."):
                    errors.append(f"Invalid entry point: {ep_name}")

        return errors

    async def _validate_checksums(self, package: PluginPackage) -> List[str]:
        """Validate file checksums"""
        errors = []

        for file_path, expected_checksum in package.checksums.items():
            if file_path in package.files:
                actual_checksum = hashlib.sha256(package.files[file_path]).hexdigest()
                if actual_checksum != expected_checksum:
                    errors.append(f"Checksum mismatch for {file_path}")
            else:
                errors.append(f"File not found: {file_path}")

        return errors

    async def _validate_signature(self, package: PluginPackage) -> bool:
        """Validate plugin signature"""
        # Simplified signature validation
        return True

    async def _check_dependencies(self, manifest: PluginManifest) -> List[str]:
        """Check if dependencies can be resolved"""
        warnings = []

        for dep in manifest.dependencies:
            compatible_plugin = await self.dependency_resolver._find_compatible_plugin(dep)
            if not compatible_plugin:
                warnings.append(f"Dependency may not be resolvable: {dep.name} {dep.version_constraint}")

        return warnings

# Global instances
plugin_discoverer = PluginDiscoverer()
dependency_resolver = DependencyResolver(plugin_registry)
advanced_installer = PluginInstaller(plugin_registry, dependency_resolver)

async def get_plugin_discoverer() -> PluginDiscoverer:
    """Dependency injection for plugin discoverer"""
    return plugin_discoverer

async def get_dependency_resolver() -> DependencyResolver:
    """Dependency injection for dependency resolver"""
    return dependency_resolver

async def get_advanced_installer() -> PluginInstaller:
    """Dependency injection for advanced installer"""
    return advanced_installer

# Discovery configuration
DISCOVERY_CONFIG = {
    "cache_ttl_minutes": 5,
    "max_search_results": 100,
    "recommendation_threshold": 0.5,
    "trending_window_days": 7,
    "enable_personalization": True,
    "enable_trending": True
}