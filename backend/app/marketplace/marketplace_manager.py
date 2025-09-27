"""
Marketplace Manager for Proyecto Semilla
Central manager for marketplace operations including publishing, moderation, and analytics
"""

import asyncio
import json
import uuid
from typing import Dict, List, Optional, Any, Tuple
from uuid import UUID
from datetime import datetime, timedelta

from sqlalchemy.ext.asyncio import AsyncSession

from app.services.marketplace_service import MarketplaceService
from app.models.marketplace import (
    ModuleCategory, ModuleMarketplaceEntry, ModuleReview, ModuleRating
)
from app.models.module import ModuleRegistry


class MarketplaceManager:
    """
    Central manager for marketplace operations
    """

    def __init__(self):
        self._default_categories_created = False

    async def initialize_marketplace(self, db: AsyncSession):
        """
        Initialize marketplace with default categories and settings
        """
        if not self._default_categories_created:
            await self._create_default_categories(db)
            self._default_categories_created = True

    async def _create_default_categories(self, db: AsyncSession):
        """
        Create default marketplace categories
        """
        default_categories = [
            {
                "name": "business-logic",
                "display_name": "Business Logic",
                "description": "Core business functionality and workflows",
                "icon": "🏢",
                "color": "#3B82F6"
            },
            {
                "name": "integrations",
                "display_name": "Integrations",
                "description": "External service integrations and APIs",
                "icon": "🔗",
                "color": "#10B981"
            },
            {
                "name": "user-interface",
                "display_name": "User Interface",
                "description": "UI/UX enhancements and components",
                "icon": "🎨",
                "color": "#F59E0B"
            },
            {
                "name": "analytics",
                "display_name": "Analytics",
                "description": "Analytics, reporting, and data visualization",
                "icon": "📊",
                "color": "#8B5CF6"
            },
            {
                "name": "security",
                "display_name": "Security",
                "description": "Security enhancements and compliance",
                "icon": "🔒",
                "color": "#EF4444"
            },
            {
                "name": "automation",
                "display_name": "Automation",
                "description": "Workflow automation and process optimization",
                "icon": "⚡",
                "color": "#06B6D4"
            },
            {
                "name": "communication",
                "display_name": "Communication",
                "description": "Communication and collaboration tools",
                "icon": "💬",
                "color": "#EC4899"
            },
            {
                "name": "utilities",
                "display_name": "Utilities",
                "description": "General utilities and helper modules",
                "icon": "🛠️",
                "color": "#6B7280"
            }
        ]

        for i, cat_data in enumerate(default_categories):
            # Check if category already exists
            existing = await db.execute(
                MarketplaceService.get_categories(db).where(ModuleCategory.name == cat_data["name"])
            )
            if not existing.scalar_one_or_none():
                await MarketplaceService.create_category(
                    name=cat_data["name"],
                    display_name=cat_data["display_name"],
                    description=cat_data["description"],
                    icon=cat_data["icon"],
                    color=cat_data["color"],
                    db=db
                )

        await db.commit()

    async def publish_module_to_marketplace(
        self,
        module_registry_id: UUID,
        publisher_id: UUID,
        category_name: str,
        tags: List[str] = None,
        screenshots: List[str] = None,
        demo_url: Optional[str] = None,
        documentation_url: Optional[str] = None,
        support_email: Optional[str] = None,
        repository_url: Optional[str] = None,
        pricing_model: str = "free",
        price: Optional[float] = None,
        currency: str = "USD",
        license_type: Optional[str] = None,
        auto_approve: bool = False,
        db: AsyncSession = None
    ) -> ModuleMarketplaceEntry:
        """
        Publish a module to the marketplace with validation and moderation
        """
        # Get category by name
        category_result = await db.execute(
            MarketplaceService.get_categories(db).where(ModuleCategory.name == category_name)
        )
        category = category_result.scalar_one_or_none()
        if not category:
            raise ValueError(f"Category '{category_name}' not found")

        # Publish the module
        entry = await MarketplaceService.publish_module(
            module_registry_id=module_registry_id,
            publisher_id=publisher_id,
            category_id=category.id,
            tags=tags,
            screenshots=screenshots,
            demo_url=demo_url,
            documentation_url=documentation_url,
            support_email=support_email,
            repository_url=repository_url,
            pricing_model=pricing_model,
            price=price,
            currency=currency,
            license_type=license_type,
            db=db
        )

        # Auto-approve if requested (for trusted publishers)
        if auto_approve:
            entry.moderation_status = "approved"
            entry.published_at = datetime.utcnow()
            await db.commit()

        return entry

    async def moderate_entry(
        self,
        entry_id: UUID,
        action: str,  # "approve", "reject", "feature", "unfeature"
        moderator_id: UUID,
        reason: Optional[str] = None,
        db: AsyncSession = None
    ) -> bool:
        """
        Moderate a marketplace entry
        """
        entry = await db.execute(
            select(ModuleMarketplaceEntry).where(ModuleMarketplaceEntry.id == entry_id)
        )
        entry = entry.scalar_one_or_none()
        if not entry:
            raise ValueError(f"Marketplace entry {entry_id} not found")

        if action == "approve":
            entry.moderation_status = "approved"
            entry.published_at = datetime.utcnow()
        elif action == "reject":
            entry.moderation_status = "rejected"
        elif action == "feature":
            entry.is_featured = True
        elif action == "unfeature":
            entry.is_featured = False
        else:
            raise ValueError(f"Invalid moderation action: {action}")

        entry.updated_at = datetime.utcnow()
        await db.commit()

        return True

    async def get_marketplace_stats(self, db: AsyncSession) -> Dict[str, Any]:
        """
        Get comprehensive marketplace statistics
        """
        # Total modules
        total_modules_result = await db.execute(
            select(func.count(ModuleMarketplaceEntry.id))
            .where(ModuleMarketplaceEntry.moderation_status == "approved")
        )
        total_modules = total_modules_result.scalar()

        # Total downloads
        total_downloads_result = await db.execute(
            select(func.sum(ModuleMarketplaceEntry.total_downloads))
        )
        total_downloads = total_downloads_result.scalar() or 0

        # Total reviews
        total_reviews_result = await db.execute(
            select(func.count(ModuleReview.id))
            .where(ModuleReview.moderation_status == "approved")
        )
        total_reviews = total_reviews_result.scalar()

        # Categories breakdown
        categories_result = await db.execute(
            select(
                ModuleCategory.name,
                ModuleCategory.display_name,
                func.count(ModuleMarketplaceEntry.id).label('module_count')
            )
            .select_from(ModuleCategory)
            .outerjoin(
                ModuleMarketplaceEntry,
                and_(
                    ModuleCategory.id == ModuleMarketplaceEntry.category_id,
                    ModuleMarketplaceEntry.moderation_status == "approved"
                )
            )
            .group_by(ModuleCategory.id, ModuleCategory.name, ModuleCategory.display_name)
            .order_by(func.count(ModuleMarketplaceEntry.id).desc())
        )
        categories_stats = [
            {
                "name": row.name,
                "display_name": row.display_name,
                "module_count": row.module_count
            }
            for row in categories_result
        ]

        # Top publishers
        publishers_result = await db.execute(
            select(
                ModuleMarketplaceEntry.publisher_name,
                func.count(ModuleMarketplaceEntry.id).label('module_count'),
                func.sum(ModuleMarketplaceEntry.total_downloads).label('total_downloads')
            )
            .where(ModuleMarketplaceEntry.moderation_status == "approved")
            .group_by(ModuleMarketplaceEntry.publisher_name)
            .order_by(func.sum(ModuleMarketplaceEntry.total_downloads).desc())
            .limit(10)
        )
        top_publishers = [
            {
                "name": row.publisher_name,
                "module_count": row.module_count,
                "total_downloads": row.total_downloads or 0
            }
            for row in publishers_result
        ]

        return {
            "total_modules": total_modules,
            "total_downloads": total_downloads,
            "total_reviews": total_reviews,
            "categories_breakdown": categories_stats,
            "top_publishers": top_publishers,
            "generated_at": datetime.utcnow().isoformat()
        }

    async def search_modules_advanced(
        self,
        db: AsyncSession,
        query: Optional[str] = None,
        category: Optional[str] = None,
        tags: Optional[List[str]] = None,
        pricing_model: Optional[str] = None,
        min_rating: Optional[float] = None,
        publisher: Optional[str] = None,
        is_featured: Optional[bool] = None,
        is_verified: Optional[bool] = None,
        sort_by: str = "relevance",
        sort_order: str = "desc",
        page: int = 1,
        per_page: int = 20
    ) -> Dict[str, Any]:
        """
        Advanced search with multiple filters and pagination
        """
        skip = (page - 1) * per_page

        # Convert category name to ID if provided
        category_id = None
        if category:
            category_result = await db.execute(
                select(ModuleCategory.id).where(ModuleCategory.name == category)
            )
            category_id = category_result.scalar_one_or_none()

        # Perform search
        modules, total_count = await MarketplaceService.search_marketplace(
            db=db,
            query=query,
            category_id=category_id,
            tags=tags,
            pricing_model=pricing_model,
            min_rating=min_rating,
            is_featured=is_featured,
            is_verified=is_verified,
            sort_by=sort_by if sort_by != "relevance" else "downloads",
            sort_order=sort_order,
            skip=skip,
            limit=per_page
        )

        # Filter by publisher if specified
        if publisher:
            modules = [m for m in modules if m["publisher"]["name"].lower() == publisher.lower()]

        total_pages = (total_count + per_page - 1) // per_page

        return {
            "modules": modules,
            "pagination": {
                "page": page,
                "per_page": per_page,
                "total_count": total_count,
                "total_pages": total_pages,
                "has_next": page < total_pages,
                "has_prev": page > 1
            },
            "filters_applied": {
                "query": query,
                "category": category,
                "tags": tags,
                "pricing_model": pricing_model,
                "min_rating": min_rating,
                "publisher": publisher,
                "is_featured": is_featured,
                "is_verified": is_verified
            }
        }

    async def get_module_details_with_reviews(
        self,
        entry_id: UUID,
        include_reviews: bool = True,
        reviews_page: int = 1,
        reviews_per_page: int = 10,
        db: AsyncSession = None
    ) -> Optional[Dict[str, Any]]:
        """
        Get detailed module information including reviews and ratings
        """
        module = await MarketplaceService.get_marketplace_entry(entry_id, db)
        if not module:
            return None

        if include_reviews:
            reviews, total_reviews = await MarketplaceService.get_reviews(
                entry_id,
                skip=(reviews_page - 1) * reviews_per_page,
                limit=reviews_per_page,
                db=db
            )
            module["reviews"] = {
                "items": reviews,
                "pagination": {
                    "page": reviews_page,
                    "per_page": reviews_per_page,
                    "total_count": total_reviews,
                    "total_pages": (total_reviews + reviews_per_page - 1) // reviews_per_page
                }
            }

        return module

    async def bulk_update_module_status(
        self,
        entry_ids: List[UUID],
        status: str,  # "approved", "rejected", "featured", "unfeatured"
        moderator_id: UUID,
        db: AsyncSession = None
    ) -> Dict[str, int]:
        """
        Bulk update status for multiple marketplace entries
        """
        updated_count = 0
        for entry_id in entry_ids:
            try:
                if status in ["approved", "rejected"]:
                    await self.moderate_entry(entry_id, status, moderator_id, db=db)
                elif status in ["featured", "unfeatured"]:
                    action = "feature" if status == "featured" else "unfeature"
                    await self.moderate_entry(entry_id, action, moderator_id, db=db)
                updated_count += 1
            except Exception:
                # Continue with other entries if one fails
                continue

        return {
            "updated_count": updated_count,
            "total_requested": len(entry_ids)
        }

    async def cleanup_old_pending_entries(self, days_old: int = 30, db: AsyncSession = None) -> int:
        """
        Clean up old pending marketplace entries that haven't been moderated
        """
        cutoff_date = datetime.utcnow() - timedelta(days=days_old)

        result = await db.execute(
            select(func.count(ModuleMarketplaceEntry.id))
            .where(
                and_(
                    ModuleMarketplaceEntry.moderation_status == "pending",
                    ModuleMarketplaceEntry.created_at < cutoff_date
                )
            )
        )
        count = result.scalar()

        # Mark as rejected (could also delete, but keeping for audit)
        await db.execute(
            update(ModuleMarketplaceEntry)
            .where(
                and_(
                    ModuleMarketplaceEntry.moderation_status == "pending",
                    ModuleMarketplaceEntry.created_at < cutoff_date
                )
            )
            .values(moderation_status="rejected")
        )
        await db.commit()

        return count

    async def get_publisher_dashboard(
        self,
        publisher_id: UUID,
        db: AsyncSession
    ) -> Dict[str, Any]:
        """
        Get dashboard data for a publisher
        """
        # Get publisher's modules
        modules_result = await db.execute(
            select(ModuleMarketplaceEntry)
            .where(ModuleMarketplaceEntry.publisher_id == publisher_id)
            .options(
                selectinload(ModuleMarketplaceEntry.category),
                selectinload(ModuleMarketplaceEntry.module_registry)
            )
        )
        modules = modules_result.scalars().all()

        # Calculate stats
        total_modules = len(modules)
        published_modules = len([m for m in modules if m.moderation_status == "approved"])
        pending_modules = len([m for m in modules if m.moderation_status == "pending"])
        featured_modules = len([m for m in modules if m.is_featured])

        total_downloads = sum(m.total_downloads for m in modules)
        total_ratings = sum(m.total_ratings for m in modules)
        avg_rating = sum(m.average_rating for m in modules) / total_ratings if total_ratings > 0 else 0

        # Recent modules
        recent_modules = sorted(modules, key=lambda x: x.created_at, reverse=True)[:5]
        recent_modules_data = []
        for module in recent_modules:
            recent_modules_data.append({
                "id": str(module.id),
                "name": module.module_registry.display_name,
                "status": module.moderation_status,
                "downloads": module.total_downloads,
                "rating": module.average_rating,
                "created_at": module.created_at.isoformat()
            })

        return {
            "stats": {
                "total_modules": total_modules,
                "published_modules": published_modules,
                "pending_modules": pending_modules,
                "featured_modules": featured_modules,
                "total_downloads": total_downloads,
                "total_ratings": total_ratings,
                "average_rating": round(avg_rating, 1)
            },
            "recent_modules": recent_modules_data
        }


# Global marketplace manager instance
marketplace_manager = MarketplaceManager()