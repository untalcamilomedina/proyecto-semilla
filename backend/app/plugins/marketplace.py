"""
Plugin Marketplace for Proyecto Semilla
Complete marketplace system with plugin discovery, reviews, and installation
"""

import json
import asyncio
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, AsyncGenerator, Tuple
from dataclasses import dataclass, asdict
import uuid
import re

from .models import (
    PluginModel, PluginReview, PluginMarketplaceEntry, PluginInstallation,
    PluginCategory, PluginStatus, EnvironmentType
)

class PluginRegistry:
    """Registry for managing published plugins"""

    def __init__(self):
        self.plugins: Dict[str, PluginModel] = {}
        self.categories: Dict[str, PluginCategory] = {}
        self.marketplace_entries: Dict[str, PluginMarketplaceEntry] = {}
        self._initialize_default_categories()

    def _initialize_default_categories(self):
        """Initialize default plugin categories"""
        default_categories = [
            PluginCategory(
                id="business",
                name="Business Logic",
                description="Core business functionality plugins",
                icon="🏢"
            ),
            PluginCategory(
                id="integration",
                name="Integrations",
                description="External service integrations",
                icon="🔗"
            ),
            PluginCategory(
                id="ui",
                name="User Interface",
                description="UI/UX enhancement plugins",
                icon="🎨"
            ),
            PluginCategory(
                id="analytics",
                name="Analytics",
                description="Analytics and reporting plugins",
                icon="📊"
            ),
            PluginCategory(
                id="security",
                name="Security",
                description="Security enhancement plugins",
                icon="🔒"
            ),
            PluginCategory(
                id="workflow",
                name="Workflow",
                description="Business process automation",
                icon="⚡"
            )
        ]

        for category in default_categories:
            self.categories[category.id] = category

    async def publish_plugin(self, plugin_data: Dict[str, Any]) -> str:
        """Publish a new plugin to the marketplace"""

        # Validate plugin data
        self._validate_plugin_data(plugin_data)

        # Create plugin model
        plugin = PluginModel(
            id=str(uuid.uuid4()),
            name=plugin_data["name"],
            version=plugin_data["version"],
            description=plugin_data["description"],
            author=plugin_data["author"],
            type=plugin_data["type"],
            status=PluginStatus.PUBLISHED.value,
            manifest=plugin_data.get("manifest", {}),
            downloads=0,
            rating=0.0,
            review_count=0
        )

        # Create marketplace entry
        marketplace_entry = PluginMarketplaceEntry(
            id=str(uuid.uuid4()),
            plugin_id=plugin.id,
            category_id=plugin_data["category_id"],
            tags=plugin_data.get("tags", []),
            screenshots=plugin_data.get("screenshots", []),
            demo_url=plugin_data.get("demo_url"),
            documentation_url=plugin_data.get("documentation_url"),
            support_email=plugin_data.get("support_email"),
            pricing=plugin_data.get("pricing", {"type": "free"}),
            featured=plugin_data.get("featured", False)
        )

        # Store plugin and marketplace entry
        self.plugins[plugin.id] = plugin
        self.marketplace_entries[plugin.id] = marketplace_entry

        return plugin.id

    async def search_plugins(self, query: str, filters: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        """Search plugins in the marketplace"""
        filters = filters or {}

        # Filter plugins
        matching_plugins = []
        for plugin in self.plugins.values():
            if plugin.status != PluginStatus.PUBLISHED.value:
                continue

            # Text search
            searchable_text = f"{plugin.name} {plugin.description} {plugin.author}".lower()
            if query.lower() not in searchable_text:
                continue

            # Category filter
            if filters.get("category") and plugin.id in self.marketplace_entries:
                entry = self.marketplace_entries[plugin.id]
                if entry.category_id != filters["category"]:
                    continue

            # Type filter
            if filters.get("type") and plugin.type != filters["type"]:
                continue

            # Rating filter
            if filters.get("min_rating") and plugin.rating < filters["min_rating"]:
                continue

            matching_plugins.append(self._plugin_to_dict(plugin))

        # Sort by relevance (simplified)
        return sorted(matching_plugins, key=lambda x: x["rating"], reverse=True)

    async def get_plugin_details(self, plugin_id: str) -> Optional[Dict[str, Any]]:
        """Get detailed plugin information"""
        if plugin_id not in self.plugins:
            return None

        plugin = self.plugins[plugin_id]
        entry = self.marketplace_entries.get(plugin_id)

        if not entry:
            return None

        return {
            "plugin": self._plugin_to_dict(plugin),
            "marketplace": asdict(entry),
            "category": asdict(self.categories.get(entry.category_id)) if entry.category_id in self.categories else None
        }

    async def get_featured_plugins(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Get featured plugins"""
        featured = []
        for plugin_id, entry in self.marketplace_entries.items():
            if entry.featured and plugin_id in self.plugins:
                plugin = self.plugins[plugin_id]
                if plugin.status == PluginStatus.PUBLISHED.value:
                    featured.append(self._plugin_to_dict(plugin))

        return featured[:limit]

    async def get_plugins_by_category(self, category_id: str) -> List[Dict[str, Any]]:
        """Get plugins by category"""
        category_plugins = []
        for plugin_id, entry in self.marketplace_entries.items():
            if entry.category_id == category_id and plugin_id in self.plugins:
                plugin = self.plugins[plugin_id]
                if plugin.status == PluginStatus.PUBLISHED.value:
                    category_plugins.append(self._plugin_to_dict(plugin))

        return category_plugins

    def _validate_plugin_data(self, data: Dict[str, Any]):
        """Validate plugin publication data"""
        required_fields = ["name", "version", "description", "author", "type", "category_id"]
        for field in required_fields:
            if field not in data:
                raise ValueError(f"Missing required field: {field}")

        # Validate version format
        if not re.match(r'^\d+\.\d+\.\d+$', data["version"]):
            raise ValueError("Version must be in format x.y.z")

        # Validate category exists
        if data["category_id"] not in self.categories:
            raise ValueError(f"Invalid category: {data['category_id']}")

    def _plugin_to_dict(self, plugin: PluginModel) -> Dict[str, Any]:
        """Convert plugin model to dictionary"""
        return {
            "id": plugin.id,
            "name": plugin.name,
            "version": plugin.version,
            "description": plugin.description,
            "author": plugin.author,
            "type": plugin.type,
            "status": plugin.status,
            "downloads": plugin.downloads,
            "rating": plugin.rating,
            "review_count": plugin.review_count,
            "created_at": plugin.created_at.isoformat() if plugin.created_at else None,
            "updated_at": plugin.updated_at.isoformat() if plugin.updated_at else None
        }

class ReviewSystem:
    """Plugin review and rating system"""

    def __init__(self):
        self.reviews: Dict[str, List[PluginReview]] = {}
        self.user_reviews: Dict[str, Dict[str, PluginReview]] = {}  # user_id -> {plugin_id: review}

    async def add_review(self, plugin_id: str, user_id: str, tenant_id: Optional[str],
                        rating: int, title: str, comment: str,
                        pros: Optional[List[str]] = None, cons: Optional[List[str]] = None) -> str:
        """Add a new review for a plugin"""

        # Validate rating
        if not 1 <= rating <= 5:
            raise ValueError("Rating must be between 1 and 5")

        # Check if user already reviewed this plugin
        if user_id in self.user_reviews and plugin_id in self.user_reviews[user_id]:
            raise ValueError("User has already reviewed this plugin")

        # Create review
        review = PluginReview(
            id=str(uuid.uuid4()),
            plugin_id=plugin_id,
            user_id=user_id,
            tenant_id=tenant_id,
            rating=rating,
            title=title,
            comment=comment,
            pros=pros or [],
            cons=cons or []
        )

        # Store review
        if plugin_id not in self.reviews:
            self.reviews[plugin_id] = []
        self.reviews[plugin_id].append(review)

        if user_id not in self.user_reviews:
            self.user_reviews[user_id] = {}
        self.user_reviews[user_id][plugin_id] = review

        # Update plugin rating
        await self._update_plugin_rating(plugin_id)

        return review.id

    async def get_plugin_reviews(self, plugin_id: str, limit: int = 50,
                               offset: int = 0) -> List[Dict[str, Any]]:
        """Get reviews for a plugin"""
        if plugin_id not in self.reviews:
            return []

        plugin_reviews = self.reviews[plugin_id]
        reviews_data = [asdict(review) for review in plugin_reviews[offset:offset + limit]]

        return reviews_data

    async def get_review_summary(self, plugin_id: str) -> Dict[str, Any]:
        """Get review summary for a plugin"""
        if plugin_id not in self.reviews:
            return {
                "total_reviews": 0,
                "average_rating": 0,
                "rating_distribution": {1: 0, 2: 0, 3: 0, 4: 0, 5: 0}
            }

        reviews = self.reviews[plugin_id]
        if not reviews:
            return {
                "total_reviews": 0,
                "average_rating": 0,
                "rating_distribution": {1: 0, 2: 0, 3: 0, 4: 0, 5: 0}
            }

        total_reviews = len(reviews)
        average_rating = sum(review.rating for review in reviews) / total_reviews

        rating_distribution = {1: 0, 2: 0, 3: 0, 4: 0, 5: 0}
        for review in reviews:
            rating_distribution[review.rating] += 1

        return {
            "total_reviews": total_reviews,
            "average_rating": round(average_rating, 1),
            "rating_distribution": rating_distribution
        }

    async def update_review(self, review_id: str, user_id: str, updates: Dict[str, Any]) -> bool:
        """Update an existing review"""

        # Find review
        review = None
        plugin_id = None

        for pid, reviews in self.reviews.items():
            for r in reviews:
                if r.id == review_id and r.user_id == user_id:
                    review = r
                    plugin_id = pid
                    break
            if review:
                break

        if not review:
            return False

        # Update review
        for key, value in updates.items():
            if hasattr(review, key):
                setattr(review, key, value)

        review.created_at = datetime.utcnow()  # Update timestamp

        # Update plugin rating
        if plugin_id:
            await self._update_plugin_rating(plugin_id)

        return True

    async def delete_review(self, review_id: str, user_id: str) -> bool:
        """Delete a review"""

        # Find and remove review
        for plugin_id, reviews in self.reviews.items():
            for i, review in enumerate(reviews):
                if review.id == review_id and review.user_id == user_id:
                    reviews.pop(i)

                    # Remove from user reviews
                    if user_id in self.user_reviews and plugin_id in self.user_reviews[user_id]:
                        del self.user_reviews[user_id][plugin_id]

                    # Update plugin rating
                    await self._update_plugin_rating(plugin_id)

                    return True

        return False

    async def _update_plugin_rating(self, plugin_id: str):
        """Update plugin rating based on reviews"""
        # This would update the plugin rating in the registry
        # Implementation depends on how plugins are stored
        pass

class PluginInstaller:
    """Plugin installation and management system"""

    def __init__(self, registry: PluginRegistry):
        self.registry = registry
        self.installations: Dict[str, List[PluginInstallation]] = {}

    async def install_plugin(self, plugin_id: str, tenant_id: str, environment: EnvironmentType,
                           installed_by: str, config: Optional[Dict[str, Any]] = None) -> str:
        """Install a plugin for a tenant"""

        # Validate plugin exists and is published
        if plugin_id not in self.registry.plugins:
            raise ValueError(f"Plugin {plugin_id} not found")

        plugin = self.registry.plugins[plugin_id]
        if plugin.status != PluginStatus.PUBLISHED.value:
            raise ValueError(f"Plugin {plugin_id} is not available for installation")

        # Create installation record
        installation = PluginInstallation(
            id=str(uuid.uuid4()),
            plugin_id=plugin_id,
            tenant_id=tenant_id,
            environment=environment,
            installed_by=installed_by,
            status="completed",
            version=plugin.version,
            config_backup=config or {}
        )

        # Store installation
        if tenant_id not in self.installations:
            self.installations[tenant_id] = []
        self.installations[tenant_id].append(installation)

        # Update plugin download count
        plugin.downloads += 1

        return installation.id

    async def uninstall_plugin(self, plugin_id: str, tenant_id: str) -> bool:
        """Uninstall a plugin from a tenant"""

        if tenant_id not in self.installations:
            return False

        # Find and remove installation
        for i, installation in enumerate(self.installations[tenant_id]):
            if installation.plugin_id == plugin_id:
                self.installations[tenant_id].pop(i)
                return True

        return False

    async def get_tenant_plugins(self, tenant_id: str) -> List[Dict[str, Any]]:
        """Get all plugins installed for a tenant"""

        if tenant_id not in self.installations:
            return []

        installed_plugins = []
        for installation in self.installations[tenant_id]:
            if installation.plugin_id in self.registry.plugins:
                plugin = self.registry.plugins[installation.plugin_id]
                installed_plugins.append({
                    "installation": asdict(installation),
                    "plugin": self.registry._plugin_to_dict(plugin)
                })

        return installed_plugins

    async def update_plugin(self, plugin_id: str, tenant_id: str, new_version: str) -> bool:
        """Update a plugin to a new version"""

        if tenant_id not in self.installations:
            return False

        # Find installation
        for installation in self.installations[tenant_id]:
            if installation.plugin_id == plugin_id:
                installation.version = new_version
                installation.installed_at = datetime.utcnow()
                return True

        return False

class MarketplaceAnalytics:
    """Analytics for marketplace performance"""

    def __init__(self):
        self.download_stats: Dict[str, int] = {}
        self.search_stats: Dict[str, int] = {}
        self.category_stats: Dict[str, int] = {}

    async def track_download(self, plugin_id: str, tenant_id: str):
        """Track plugin download"""
        if plugin_id not in self.download_stats:
            self.download_stats[plugin_id] = 0
        self.download_stats[plugin_id] += 1

    async def track_search(self, query: str, results_count: int):
        """Track search query"""
        # Simplified search tracking
        pass

    async def get_popular_plugins(self, limit: int = 10) -> List[Tuple[str, int]]:
        """Get most popular plugins by downloads"""
        sorted_plugins = sorted(
            self.download_stats.items(),
            key=lambda x: x[1],
            reverse=True
        )
        return sorted_plugins[:limit]

    async def get_marketplace_stats(self) -> Dict[str, Any]:
        """Get overall marketplace statistics"""
        return {
            "total_plugins": len(self.download_stats),
            "total_downloads": sum(self.download_stats.values()),
            "most_popular": await self.get_popular_plugins(5)
        }

# Global instances
plugin_registry = PluginRegistry()
review_system = ReviewSystem()
plugin_installer = PluginInstaller(plugin_registry)
marketplace_analytics = MarketplaceAnalytics()

async def get_plugin_registry() -> PluginRegistry:
    """Dependency injection for plugin registry"""
    return plugin_registry

async def get_review_system() -> ReviewSystem:
    """Dependency injection for review system"""
    return review_system

async def get_plugin_installer() -> PluginInstaller:
    """Dependency injection for plugin installer"""
    return plugin_installer

# Marketplace configuration
MARKETPLACE_CONFIG = {
    "featured_plugins_limit": 10,
    "search_results_limit": 50,
    "reviews_per_page": 20,
    "enable_reviews": True,
    "enable_ratings": True,
    "auto_publish_plugins": False,
    "moderation_required": True
}