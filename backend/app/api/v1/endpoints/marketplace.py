"""
Marketplace API endpoints for Proyecto Semilla
Public API for module marketplace operations
"""

import uuid
from typing import List, Optional, Dict, Any
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, BackgroundTasks
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.services.marketplace_service import MarketplaceService
from app.marketplace.marketplace_manager import marketplace_manager
from app.core.security import get_current_user
from app.models.user import User

router = APIRouter(prefix="/marketplace", tags=["marketplace"])


@router.on_event("startup")
async def startup_event():
    """Initialize marketplace on startup"""
    # This would be called during app startup
    pass


@router.get("/categories", response_model=List[Dict[str, Any]])
async def get_categories(db: AsyncSession = Depends(get_db)):
    """
    Get all marketplace categories
    """
    categories = await MarketplaceService.get_categories(db)
    return [
        {
            "id": str(cat.id),
            "name": cat.name,
            "display_name": cat.display_name,
            "description": cat.description,
            "icon": cat.icon,
            "color": cat.color,
            "sort_order": cat.sort_order
        }
        for cat in categories
    ]


@router.get("/search")
async def search_modules(
    q: Optional[str] = Query(None, description="Search query"),
    category: Optional[str] = Query(None, description="Category name"),
    tags: Optional[List[str]] = Query(None, description="Tags to filter by"),
    pricing_model: Optional[str] = Query(None, description="Pricing model (free, paid, etc.)"),
    min_rating: Optional[float] = Query(None, description="Minimum rating (1-5)"),
    publisher: Optional[str] = Query(None, description="Publisher name"),
    featured: Optional[bool] = Query(None, description="Show only featured modules"),
    verified: Optional[bool] = Query(None, description="Show only verified modules"),
    sort_by: str = Query("downloads", description="Sort by: downloads, rating, name, updated"),
    sort_order: str = Query("desc", description="Sort order: asc or desc"),
    page: int = Query(1, ge=1, description="Page number"),
    per_page: int = Query(20, ge=1, le=100, description="Items per page"),
    db: AsyncSession = Depends(get_db)
):
    """
    Advanced search for marketplace modules
    """
    try:
        result = await marketplace_manager.search_modules_advanced(
            db=db,
            query=q,
            category=category,
            tags=tags,
            pricing_model=pricing_model,
            min_rating=min_rating,
            publisher=publisher,
            is_featured=featured,
            is_verified=verified,
            sort_by=sort_by,
            sort_order=sort_order,
            page=page,
            per_page=per_page
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/modules/{entry_id}")
async def get_module_details(
    entry_id: UUID,
    include_reviews: bool = Query(True, description="Include reviews in response"),
    reviews_page: int = Query(1, ge=1, description="Reviews page number"),
    reviews_per_page: int = Query(10, ge=1, le=50, description="Reviews per page"),
    db: AsyncSession = Depends(get_db)
):
    """
    Get detailed information about a specific module
    """
    module = await marketplace_manager.get_module_details_with_reviews(
        entry_id=entry_id,
        include_reviews=include_reviews,
        reviews_page=reviews_page,
        reviews_per_page=reviews_per_page,
        db=db
    )

    if not module:
        raise HTTPException(status_code=404, detail="Module not found")

    return module


@router.get("/featured")
async def get_featured_modules(
    limit: int = Query(10, ge=1, le=50, description="Maximum number of modules to return"),
    db: AsyncSession = Depends(get_db)
):
    """
    Get featured marketplace modules
    """
    try:
        modules = await MarketplaceService.get_featured_modules(limit=limit, db=db)
        return {"modules": modules}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/popular")
async def get_popular_modules(
    limit: int = Query(10, ge=1, le=50, description="Maximum number of modules to return"),
    db: AsyncSession = Depends(get_db)
):
    """
    Get most popular marketplace modules by downloads
    """
    try:
        modules = await MarketplaceService.get_popular_modules(limit=limit, db=db)
        return {"modules": modules}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/modules/{entry_id}/reviews")
async def add_review(
    entry_id: UUID,
    review_data: Dict[str, Any],
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Add a review for a marketplace module
    """
    try:
        rating = review_data.get("rating")
        title = review_data.get("title")
        content = review_data.get("content")
        pros = review_data.get("pros", [])
        cons = review_data.get("cons", [])

        if not rating or not isinstance(rating, int) or not 1 <= rating <= 5:
            raise HTTPException(status_code=400, detail="Rating must be an integer between 1 and 5")

        if not title or not content:
            raise HTTPException(status_code=400, detail="Title and content are required")

        review = await MarketplaceService.add_review(
            marketplace_entry_id=entry_id,
            user_id=current_user.id,
            tenant_id=getattr(current_user, 'tenant_id', None),
            rating=rating,
            title=title,
            content=content,
            pros=pros,
            cons=cons,
            db=db
        )

        return {
            "id": str(review.id),
            "message": "Review added successfully"
        }

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/modules/{entry_id}/ratings")
async def add_rating(
    entry_id: UUID,
    rating_data: Dict[str, Any],
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Add or update a rating for a marketplace module
    """
    try:
        rating = rating_data.get("rating")

        if not rating or not isinstance(rating, int) or not 1 <= rating <= 5:
            raise HTTPException(status_code=400, detail="Rating must be an integer between 1 and 5")

        rating_obj = await MarketplaceService.add_rating(
            marketplace_entry_id=entry_id,
            user_id=current_user.id,
            tenant_id=getattr(current_user, 'tenant_id', None),
            rating=rating,
            db=db
        )

        return {
            "message": "Rating added successfully",
            "rating": rating_obj.rating
        }

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/modules/{entry_id}/reviews")
async def get_module_reviews(
    entry_id: UUID,
    page: int = Query(1, ge=1, description="Page number"),
    per_page: int = Query(20, ge=1, le=50, description="Reviews per page"),
    sort_by: str = Query("created_at", description="Sort by: created_at, rating, helpful_votes"),
    sort_order: str = Query("desc", description="Sort order: asc or desc"),
    db: AsyncSession = Depends(get_db)
):
    """
    Get reviews for a specific module
    """
    try:
        reviews, total_count = await MarketplaceService.get_reviews(
            marketplace_entry_id=entry_id,
            skip=(page - 1) * per_page,
            limit=per_page,
            sort_by=sort_by,
            sort_order=sort_order,
            db=db
        )

        total_pages = (total_count + per_page - 1) // per_page

        return {
            "reviews": reviews,
            "pagination": {
                "page": page,
                "per_page": per_page,
                "total_count": total_count,
                "total_pages": total_pages,
                "has_next": page < total_pages,
                "has_prev": page > 1
            }
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/modules/{entry_id}/download")
async def track_download(
    entry_id: UUID,
    download_data: Dict[str, Any] = None,
    current_user: Optional[User] = Depends(get_current_user),
    background_tasks: BackgroundTasks = None,
    db: AsyncSession = Depends(get_db)
):
    """
    Track a module download
    """
    try:
        download_data = download_data or {}
        version = download_data.get("version", "latest")
        ip_address = download_data.get("ip_address")
        user_agent = download_data.get("user_agent")

        # Track download asynchronously
        background_tasks.add_task(
            MarketplaceService.track_download,
            marketplace_entry_id=entry_id,
            user_id=current_user.id if current_user else None,
            tenant_id=getattr(current_user, 'tenant_id', None) if current_user else None,
            version=version,
            ip_address=ip_address,
            user_agent=user_agent,
            db=db
        )

        return {"message": "Download tracked successfully"}

    except Exception as e:
        # Don't fail the download if tracking fails
        return {"message": "Download initiated"}


@router.get("/stats")
async def get_marketplace_stats(db: AsyncSession = Depends(get_db)):
    """
    Get marketplace statistics
    """
    try:
        stats = await marketplace_manager.get_marketplace_stats(db)
        return stats
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/publisher/dashboard")
async def get_publisher_dashboard(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Get dashboard data for the current publisher
    """
    try:
        dashboard = await marketplace_manager.get_publisher_dashboard(
            publisher_id=current_user.id,
            db=db
        )
        return dashboard
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# Publisher endpoints (require authentication)

@router.post("/publish")
async def publish_module(
    publish_data: Dict[str, Any],
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Publish a module to the marketplace
    """
    try:
        # Required fields
        module_registry_id = publish_data.get("module_registry_id")
        category_name = publish_data.get("category")

        if not module_registry_id or not category_name:
            raise HTTPException(status_code=400, detail="module_registry_id and category are required")

        # Optional fields
        tags = publish_data.get("tags", [])
        screenshots = publish_data.get("screenshots", [])
        demo_url = publish_data.get("demo_url")
        documentation_url = publish_data.get("documentation_url")
        support_email = publish_data.get("support_email")
        repository_url = publish_data.get("repository_url")
        pricing_model = publish_data.get("pricing_model", "free")
        price = publish_data.get("price")
        currency = publish_data.get("currency", "USD")
        license_type = publish_data.get("license_type")

        entry = await marketplace_manager.publish_module_to_marketplace(
            module_registry_id=UUID(module_registry_id),
            publisher_id=current_user.id,
            category_name=category_name,
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

        return {
            "id": str(entry.id),
            "message": "Module published successfully",
            "status": entry.moderation_status
        }

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# Update management endpoints

@router.get("/updates/check")
async def check_for_updates(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Check for available updates for the current tenant's modules
    """
    try:
        from app.services.module_service import ModuleService

        updates = await ModuleService.check_for_updates(current_user.tenant_id, db)
        return {"updates": updates, "count": len(updates)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/modules/{module_id}/update")
async def apply_module_update(
    module_id: UUID,
    update_data: Dict[str, Any],
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Apply an update to a specific module
    """
    try:
        from app.services.module_service import ModuleService

        target_version = update_data.get("target_version")
        if not target_version:
            raise HTTPException(status_code=400, detail="target_version is required")

        result = await ModuleService.apply_update(
            module_id=module_id,
            tenant_id=current_user.tenant_id,
            target_version=target_version,
            db=db
        )

        return result

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/modules/{module_id}/updates")
async def get_module_update_history(
    module_id: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Get update history for a specific module
    """
    try:
        from app.services.module_service import ModuleService

        # Verify module belongs to tenant
        module = await ModuleService.get_module_by_id(module_id, current_user.tenant_id, db)
        if not module:
            raise HTTPException(status_code=404, detail="Module not found")

        history = await ModuleService.get_update_history(module_id, current_user.tenant_id, db)
        return {"updates": history}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# License management endpoints

@router.post("/modules/{entry_id}/purchase")
async def purchase_module_license(
    entry_id: UUID,
    purchase_data: Dict[str, Any],
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Purchase a license for a marketplace module
    """
    try:
        from app.models.marketplace import ModuleLicense

        # This is a placeholder for license purchase logic
        # In a real implementation, this would integrate with a payment processor

        license_type = purchase_data.get("license_type", "perpetual")

        # Create license record
        license_obj = ModuleLicense(
            marketplace_entry_id=entry_id,
            tenant_id=current_user.tenant_id,
            user_id=current_user.id,
            license_type=license_type,
            purchase_price=0.0,  # Would be set by payment processor
            currency="USD"
        )

        db.add(license_obj)
        await db.commit()
        await db.refresh(license_obj)

        return {
            "license_id": str(license_obj.id),
            "license_key": license_obj.license_key,
            "message": "License purchased successfully"
        }

    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/licenses")
async def get_tenant_licenses(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Get all licenses for the current tenant
    """
    try:
        from app.models.marketplace import ModuleLicense

        result = await db.execute(
            select(ModuleLicense)
            .where(ModuleLicense.tenant_id == current_user.tenant_id)
            .options(selectinload(ModuleLicense.marketplace_entry))
        )
        licenses = result.scalars().all()

        return {
            "licenses": [{
                "id": str(license.id),
                "marketplace_entry_id": str(license.marketplace_entry_id),
                "module_name": license.marketplace_entry.module_registry.display_name if license.marketplace_entry else "Unknown",
                "license_key": license.license_key,
                "license_type": license.license_type,
                "is_active": license.is_active,
                "expires_at": license.expires_at.isoformat() if license.expires_at else None,
                "purchased_at": license.purchased_at.isoformat()
            } for license in licenses]
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# Admin endpoints (would require admin permissions)

@router.post("/admin/moderate/{entry_id}")
async def moderate_entry(
    entry_id: UUID,
    moderation_data: Dict[str, Any],
    current_user: User = Depends(get_current_user),  # Would check for admin role
    db: AsyncSession = Depends(get_db)
):
    """
    Moderate a marketplace entry (admin only)
    """
    try:
        action = moderation_data.get("action")  # approve, reject, feature, unfeature
        reason = moderation_data.get("reason")

        if action not in ["approve", "reject", "feature", "unfeature"]:
            raise HTTPException(status_code=400, detail="Invalid moderation action")

        success = await marketplace_manager.moderate_entry(
            entry_id=entry_id,
            action=action,
            moderator_id=current_user.id,
            reason=reason,
            db=db
        )

        if success:
            return {"message": f"Entry {action}d successfully"}
        else:
            raise HTTPException(status_code=404, detail="Entry not found")

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/admin/bulk-moderate")
async def bulk_moderate_entries(
    bulk_data: Dict[str, Any],
    current_user: User = Depends(get_current_user),  # Would check for admin role
    db: AsyncSession = Depends(get_db)
):
    """
    Bulk moderate marketplace entries (admin only)
    """
    try:
        entry_ids = bulk_data.get("entry_ids", [])
        action = bulk_data.get("action")

        if not entry_ids or action not in ["approve", "reject", "feature", "unfeature"]:
            raise HTTPException(status_code=400, detail="Invalid request data")

        result = await marketplace_manager.bulk_update_module_status(
            entry_ids=[UUID(eid) for eid in entry_ids],
            status=action,
            moderator_id=current_user.id,
            db=db
        )

        return result

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))