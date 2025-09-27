"""
Marketplace service for MCP modules
Handles marketplace operations including publishing, searching, reviews, and ratings
"""

import asyncio
import json
import uuid
from typing import Dict, List, Optional, Any, Tuple
from uuid import UUID
from datetime import datetime

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, delete, func, and_, or_, text
from sqlalchemy.orm import selectinload

from app.models.marketplace import (
    ModuleCategory, ModuleMarketplaceEntry, ModuleReview, ModuleRating,
    ModuleDownload, ModuleUpdate, ModuleLicense
)
from app.models.module import ModuleRegistry
from app.models.user import User
from app.models.tenant import Tenant


class MarketplaceService:
    """
    Service for handling marketplace operations
    """

    @staticmethod
    async def get_categories(db: AsyncSession, include_inactive: bool = False) -> List[ModuleCategory]:
        """
        Get all marketplace categories
        """
        query = select(ModuleCategory)
        if not include_inactive:
            query = query.where(ModuleCategory.is_active == True)
        query = query.order_by(ModuleCategory.sort_order, ModuleCategory.name)

        result = await db.execute(query)
        return result.scalars().all()

    @staticmethod
    async def get_category_by_id(category_id: UUID, db: AsyncSession) -> Optional[ModuleCategory]:
        """
        Get category by ID
        """
        result = await db.execute(
            select(ModuleCategory).where(ModuleCategory.id == category_id)
        )
        return result.scalar_one_or_none()

    @staticmethod
    async def create_category(
        name: str,
        display_name: str,
        description: Optional[str] = None,
        icon: Optional[str] = None,
        color: Optional[str] = None,
        parent_id: Optional[UUID] = None,
        db: AsyncSession = None
    ) -> ModuleCategory:
        """
        Create a new category
        """
        # Validate parent exists if provided
        if parent_id:
            parent = await MarketplaceService.get_category_by_id(parent_id, db)
            if not parent:
                raise ValueError(f"Parent category {parent_id} not found")

        category = ModuleCategory(
            name=name,
            display_name=display_name,
            description=description,
            icon=icon,
            color=color,
            parent_id=parent_id
        )
        db.add(category)
        await db.commit()
        await db.refresh(category)
        return category

    @staticmethod
    async def search_marketplace(
        db: AsyncSession,
        query: Optional[str] = None,
        category_id: Optional[UUID] = None,
        tags: Optional[List[str]] = None,
        pricing_model: Optional[str] = None,
        min_rating: Optional[float] = None,
        is_featured: Optional[bool] = None,
        is_verified: Optional[bool] = None,
        sort_by: str = "downloads",
        sort_order: str = "desc",
        skip: int = 0,
        limit: int = 50
    ) -> Tuple[List[Dict[str, Any]], int]:
        """
        Search marketplace entries with filters
        """
        # Build base query
        base_query = select(ModuleMarketplaceEntry).where(
            ModuleMarketplaceEntry.moderation_status == "approved"
        ).options(
            selectinload(ModuleMarketplaceEntry.category),
            selectinload(ModuleMarketplaceEntry.module_registry)
        )

        # Apply filters
        filters = []

        if query:
            # Search in name, description, and tags
            search_filter = or_(
                ModuleMarketplaceEntry.publisher_name.ilike(f"%{query}%"),
                ModuleMarketplaceEntry.tags.contains([query]),
                ModuleMarketplaceEntry.module_registry.has(
                    or_(
                        ModuleRegistry.name.ilike(f"%{query}%"),
                        ModuleRegistry.display_name.ilike(f"%{query}%"),
                        ModuleRegistry.description.ilike(f"%{query}%")
                    )
                )
            )
            filters.append(search_filter)

        if category_id:
            filters.append(ModuleMarketplaceEntry.category_id == category_id)

        if tags:
            # Check if any of the provided tags are in the entry's tags
            tag_filters = []
            for tag in tags:
                tag_filters.append(ModuleMarketplaceEntry.tags.contains([tag]))
            if tag_filters:
                filters.append(or_(*tag_filters))

        if pricing_model:
            filters.append(ModuleMarketplaceEntry.pricing_model == pricing_model)

        if min_rating is not None:
            filters.append(ModuleMarketplaceEntry.average_rating >= min_rating)

        if is_featured is not None:
            filters.append(ModuleMarketplaceEntry.is_featured == is_featured)

        if is_verified is not None:
            filters.append(ModuleMarketplaceEntry.is_verified == is_verified)

        # Apply filters to query
        if filters:
            base_query = base_query.where(and_(*filters))

        # Get total count
        count_query = select(func.count()).select_from(base_query.subquery())
        total_count = await db.execute(count_query)
        total_count = total_count.scalar()

        # Apply sorting
        sort_column = {
            "downloads": ModuleMarketplaceEntry.total_downloads,
            "rating": ModuleMarketplaceEntry.average_rating,
            "name": ModuleMarketplaceEntry.module_registry.has(ModuleRegistry.display_name),
            "updated": ModuleMarketplaceEntry.last_updated,
            "published": ModuleMarketplaceEntry.published_at
        }.get(sort_by, ModuleMarketplaceEntry.total_downloads)

        if sort_order == "desc":
            base_query = base_query.order_by(sort_column.desc())
        else:
            base_query = base_query.order_by(sort_column.asc())

        # Apply pagination
        base_query = base_query.offset(skip).limit(limit)

        # Execute query
        result = await db.execute(base_query)
        entries = result.scalars().all()

        # Convert to dict format
        marketplace_items = []
        for entry in entries:
            item = await MarketplaceService._marketplace_entry_to_dict(entry, db)
            marketplace_items.append(item)

        return marketplace_items, total_count

    @staticmethod
    async def get_marketplace_entry(entry_id: UUID, db: AsyncSession) -> Optional[Dict[str, Any]]:
        """
        Get detailed marketplace entry information
        """
        result = await db.execute(
            select(ModuleMarketplaceEntry)
            .where(ModuleMarketplaceEntry.id == entry_id)
            .options(
                selectinload(ModuleMarketplaceEntry.category),
                selectinload(ModuleMarketplaceEntry.module_registry),
                selectinload(ModuleMarketplaceEntry.reviews),
                selectinload(ModuleMarketplaceEntry.ratings)
            )
        )
        entry = result.scalar_one_or_none()

        if not entry or entry.moderation_status != "approved":
            return None

        return await MarketplaceService._marketplace_entry_to_dict(entry, db, include_details=True)

    @staticmethod
    async def publish_module(
        module_registry_id: UUID,
        publisher_id: UUID,
        category_id: UUID,
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
        db: AsyncSession = None
    ) -> ModuleMarketplaceEntry:
        """
        Publish a module to the marketplace
        """
        # Get module registry info
        registry = await db.execute(
            select(ModuleRegistry).where(ModuleRegistry.id == module_registry_id)
        )
        registry = registry.scalar_one_or_none()
        if not registry:
            raise ValueError(f"Module registry {module_registry_id} not found")

        # Get publisher info
        publisher = await db.execute(
            select(User).where(User.id == publisher_id)
        )
        publisher = publisher.scalar_one_or_none()
        if not publisher:
            raise ValueError(f"Publisher {publisher_id} not found")

        # Check if already published
        existing = await db.execute(
            select(ModuleMarketplaceEntry)
            .where(ModuleMarketplaceEntry.module_registry_id == module_registry_id)
        )
        if existing.scalar_one_or_none():
            raise ValueError(f"Module {registry.name} is already published")

        # Validate category
        category = await MarketplaceService.get_category_by_id(category_id, db)
        if not category:
            raise ValueError(f"Category {category_id} not found")

        # Create marketplace entry
        entry = ModuleMarketplaceEntry(
            module_registry_id=module_registry_id,
            category_id=category_id,
            tags=tags or [],
            screenshots=screenshots or [],
            demo_url=demo_url,
            documentation_url=documentation_url,
            support_email=support_email,
            repository_url=repository_url,
            pricing_model=pricing_model,
            price=price,
            currency=currency,
            license_type=license_type,
            publisher_id=publisher_id,
            publisher_name=publisher.full_name or publisher.email,
            publisher_email=publisher.email,
            moderation_status="pending"  # Requires moderation
        )

        db.add(entry)
        await db.commit()
        await db.refresh(entry)
        return entry

    @staticmethod
    async def add_review(
        marketplace_entry_id: UUID,
        user_id: UUID,
        tenant_id: Optional[UUID],
        rating: int,
        title: str,
        content: str,
        pros: List[str] = None,
        cons: List[str] = None,
        db: AsyncSession = None
    ) -> ModuleReview:
        """
        Add a review for a marketplace entry
        """
        # Validate rating
        if not 1 <= rating <= 5:
            raise ValueError("Rating must be between 1 and 5")

        # Check if entry exists
        entry = await db.execute(
            select(ModuleMarketplaceEntry)
            .where(ModuleMarketplaceEntry.id == marketplace_entry_id)
        )
        entry = entry.scalar_one_or_none()
        if not entry:
            raise ValueError(f"Marketplace entry {marketplace_entry_id} not found")

        # Check if user already reviewed
        existing_review = await db.execute(
            select(ModuleReview)
            .where(
                and_(
                    ModuleReview.marketplace_entry_id == marketplace_entry_id,
                    ModuleReview.user_id == user_id
                )
            )
        )
        if existing_review.scalar_one_or_none():
            raise ValueError("User has already reviewed this module")

        # Create review
        review = ModuleReview(
            marketplace_entry_id=marketplace_entry_id,
            user_id=user_id,
            tenant_id=tenant_id,
            rating=rating,
            title=title,
            content=content,
            pros=pros or [],
            cons=cons or []
        )

        db.add(review)
        await db.commit()
        await db.refresh(review)

        # Update marketplace entry statistics
        await MarketplaceService._update_entry_statistics(marketplace_entry_id, db)

        return review

    @staticmethod
    async def add_rating(
        marketplace_entry_id: UUID,
        user_id: UUID,
        tenant_id: Optional[UUID],
        rating: int,
        db: AsyncSession = None
    ) -> ModuleRating:
        """
        Add or update a rating for a marketplace entry
        """
        # Validate rating
        if not 1 <= rating <= 5:
            raise ValueError("Rating must be between 1 and 5")

        # Check if entry exists
        entry = await db.execute(
            select(ModuleMarketplaceEntry)
            .where(ModuleMarketplaceEntry.id == marketplace_entry_id)
        )
        entry = entry.scalar_one_or_none()
        if not entry:
            raise ValueError(f"Marketplace entry {marketplace_entry_id} not found")

        # Check if rating already exists
        existing_rating = await db.execute(
            select(ModuleRating)
            .where(
                and_(
                    ModuleRating.marketplace_entry_id == marketplace_entry_id,
                    ModuleRating.user_id == user_id
                )
            )
        )
        existing_rating = existing_rating.scalar_one_or_none()

        if existing_rating:
            # Update existing rating
            existing_rating.rating = rating
            existing_rating.updated_at = datetime.utcnow()
            await db.commit()
            rating_obj = existing_rating
        else:
            # Create new rating
            rating_obj = ModuleRating(
                marketplace_entry_id=marketplace_entry_id,
                user_id=user_id,
                tenant_id=tenant_id,
                rating=rating
            )
            db.add(rating_obj)
            await db.commit()
            await db.refresh(rating_obj)

        # Update marketplace entry statistics
        await MarketplaceService._update_entry_statistics(marketplace_entry_id, db)

        return rating_obj

    @staticmethod
    async def get_reviews(
        marketplace_entry_id: UUID,
        skip: int = 0,
        limit: int = 20,
        sort_by: str = "created_at",
        sort_order: str = "desc",
        db: AsyncSession = None
    ) -> Tuple[List[Dict[str, Any]], int]:
        """
        Get reviews for a marketplace entry
        """
        # Get total count
        count_query = select(func.count()).select_from(
            select(ModuleReview)
            .where(
                and_(
                    ModuleReview.marketplace_entry_id == marketplace_entry_id,
                    ModuleReview.moderation_status == "approved"
                )
            ).subquery()
        )
        total_count = await db.execute(count_query)
        total_count = total_count.scalar()

        # Build reviews query
        query = select(ModuleReview).where(
            and_(
                ModuleReview.marketplace_entry_id == marketplace_entry_id,
                ModuleReview.moderation_status == "approved"
            )
        ).options(selectinload(ModuleReview.user))

        # Apply sorting
        sort_column = {
            "created_at": ModuleReview.created_at,
            "rating": ModuleReview.rating,
            "helpful_votes": ModuleReview.helpful_votes
        }.get(sort_by, ModuleReview.created_at)

        if sort_order == "desc":
            query = query.order_by(sort_column.desc())
        else:
            query = query.order_by(sort_column.asc())

        # Apply pagination
        query = query.offset(skip).limit(limit)

        result = await db.execute(query)
        reviews = result.scalars().all()

        # Convert to dict
        review_dicts = []
        for review in reviews:
            review_dict = {
                "id": str(review.id),
                "user": {
                    "id": str(review.user.id),
                    "name": review.user.full_name or review.user.email,
                    "avatar": getattr(review.user, 'avatar', None)
                },
                "rating": review.rating,
                "title": review.title,
                "content": review.content,
                "pros": review.pros,
                "cons": review.cons,
                "helpful_votes": review.helpful_votes,
                "total_votes": review.total_votes,
                "is_verified_purchase": review.is_verified_purchase,
                "created_at": review.created_at.isoformat()
            }
            review_dicts.append(review_dict)

        return review_dicts, total_count

    @staticmethod
    async def track_download(
        marketplace_entry_id: UUID,
        user_id: Optional[UUID],
        tenant_id: Optional[UUID],
        version: str,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None,
        download_source: str = "marketplace",
        db: AsyncSession = None
    ) -> ModuleDownload:
        """
        Track a module download
        """
        download = ModuleDownload(
            marketplace_entry_id=marketplace_entry_id,
            user_id=user_id,
            tenant_id=tenant_id,
            version=version,
            ip_address=ip_address,
            user_agent=user_agent,
            download_source=download_source
        )

        db.add(download)
        await db.commit()
        await db.refresh(download)

        # Update download count
        await db.execute(
            update(ModuleMarketplaceEntry)
            .where(ModuleMarketplaceEntry.id == marketplace_entry_id)
            .values(total_downloads=ModuleMarketplaceEntry.total_downloads + 1)
        )
        await db.commit()

        return download

    @staticmethod
    async def get_featured_modules(limit: int = 10, db: AsyncSession = None) -> List[Dict[str, Any]]:
        """
        Get featured marketplace modules
        """
        result = await db.execute(
            select(ModuleMarketplaceEntry)
            .where(
                and_(
                    ModuleMarketplaceEntry.is_featured == True,
                    ModuleMarketplaceEntry.moderation_status == "approved"
                )
            )
            .options(
                selectinload(ModuleMarketplaceEntry.category),
                selectinload(ModuleMarketplaceEntry.module_registry)
            )
            .order_by(ModuleMarketplaceEntry.total_downloads.desc())
            .limit(limit)
        )
        entries = result.scalars().all()

        featured_modules = []
        for entry in entries:
            item = await MarketplaceService._marketplace_entry_to_dict(entry, db)
            featured_modules.append(item)

        return featured_modules

    @staticmethod
    async def get_popular_modules(limit: int = 10, db: AsyncSession = None) -> List[Dict[str, Any]]:
        """
        Get most popular marketplace modules by downloads
        """
        result = await db.execute(
            select(ModuleMarketplaceEntry)
            .where(ModuleMarketplaceEntry.moderation_status == "approved")
            .options(
                selectinload(ModuleMarketplaceEntry.category),
                selectinload(ModuleMarketplaceEntry.module_registry)
            )
            .order_by(ModuleMarketplaceEntry.total_downloads.desc())
            .limit(limit)
        )
        entries = result.scalars().all()

        popular_modules = []
        for entry in entries:
            item = await MarketplaceService._marketplace_entry_to_dict(entry, db)
            popular_modules.append(item)

        return popular_modules

    @staticmethod
    async def _marketplace_entry_to_dict(
        entry: ModuleMarketplaceEntry,
        db: AsyncSession,
        include_details: bool = False
    ) -> Dict[str, Any]:
        """
        Convert marketplace entry to dictionary
        """
        item = {
            "id": str(entry.id),
            "module": {
                "name": entry.module_registry.name,
                "display_name": entry.module_registry.display_name,
                "description": entry.module_registry.description,
                "latest_version": entry.module_registry.latest_version,
                "author": entry.module_registry.author,
                "homepage": entry.module_registry.homepage,
                "repository": entry.module_registry.repository_url or entry.repository_url,
                "is_official": entry.module_registry.is_official
            },
            "category": {
                "id": str(entry.category.id),
                "name": entry.category.name,
                "display_name": entry.category.display_name,
                "icon": entry.category.icon
            },
            "tags": entry.tags,
            "screenshots": entry.screenshots,
            "demo_url": entry.demo_url,
            "documentation_url": entry.documentation_url,
            "support_email": entry.support_email,
            "pricing": {
                "model": entry.pricing_model,
                "price": entry.price,
                "currency": entry.currency,
                "license_type": entry.license_type
            },
            "publisher": {
                "name": entry.publisher_name,
                "email": entry.publisher_email
            },
            "stats": {
                "downloads": entry.total_downloads,
                "rating": entry.average_rating,
                "total_ratings": entry.total_ratings,
                "total_reviews": entry.total_reviews
            },
            "flags": {
                "is_featured": entry.is_featured,
                "is_verified": entry.is_verified,
                "is_deprecated": entry.is_deprecated
            },
            "published_at": entry.published_at.isoformat() if entry.published_at else None,
            "last_updated": entry.last_updated.isoformat()
        }

        if include_details:
            # Add reviews summary
            reviews, total_reviews = await MarketplaceService.get_reviews(
                entry.id, limit=5, db=db
            )
            item["recent_reviews"] = reviews
            item["reviews_count"] = total_reviews

        return item

    @staticmethod
    async def _update_entry_statistics(marketplace_entry_id: UUID, db: AsyncSession):
        """
        Update statistics for a marketplace entry based on ratings and reviews
        """
        # Get rating statistics
        rating_stats = await db.execute(
            select(
                func.count(ModuleRating.id).label('total_ratings'),
                func.avg(ModuleRating.rating).label('average_rating')
            )
            .select_from(ModuleRating)
            .where(ModuleRating.marketplace_entry_id == marketplace_entry_id)
        )
        rating_row = rating_stats.first()

        # Get review count
        review_count = await db.execute(
            select(func.count(ModuleReview.id))
            .select_from(ModuleReview)
            .where(
                and_(
                    ModuleReview.marketplace_entry_id == marketplace_entry_id,
                    ModuleReview.moderation_status == "approved"
                )
            )
        )
        review_count = review_count.scalar()

        # Update entry
        await db.execute(
            update(ModuleMarketplaceEntry)
            .where(ModuleMarketplaceEntry.id == marketplace_entry_id)
            .values(
                total_ratings=rating_row.total_ratings or 0,
                average_rating=float(rating_row.average_rating or 0.0),
                total_reviews=review_count or 0
            )
        )
        await db.commit()