"""
Categories CRUD endpoints for CMS functionality
"""

from typing import Any, List
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text

from app.core.database import get_db
from app.core.security import get_current_user
from app.models.user import User
from app.schemas.article import (
    CategoryCreate,
    CategoryResponse,
    CategoryUpdate,
    CategoryStats
)

router = APIRouter()


@router.get("/", response_model=List[CategoryResponse])
async def read_categories(
    db: AsyncSession = Depends(get_db),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    include_inactive: bool = Query(False),
    current_user: User = Depends(get_current_user)
) -> Any:
    """
    Retrieve categories with optional filtering
    """
    query = """
    SELECT * FROM categories
    WHERE tenant_id = :tenant_id
    """

    params = {"tenant_id": str(current_user.tenant_id)}

    if not include_inactive:
        query += " AND is_active = true"

    query += " ORDER BY order_index ASC, created_at DESC"
    query += " LIMIT :limit OFFSET :offset"
    params["limit"] = limit
    params["offset"] = skip

    result = await db.execute(text(query), params)
    categories = result.fetchall()

    # Convert to response format
    category_list = []
    for row in categories:
        category_dict = {
            "id": str(row[0]),
            "tenant_id": str(row[1]),
            "name": row[2],
            "slug": row[3],
            "description": row[4],
            "color": row[5],
            "parent_id": str(row[6]) if row[6] else None,
            "order_index": row[7],
            "is_active": row[8],
            "created_at": row[9],
            "updated_at": row[10]
        }
        category_list.append(category_dict)

    return category_list


@router.post("/", response_model=CategoryResponse)
async def create_category(
    category_in: CategoryCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> Any:
    """
    Create new category
    """
    # Check if slug already exists
    existing = await db.execute(
        text("SELECT id FROM categories WHERE slug = $1 AND tenant_id = $2"),
        [category_in.slug, str(current_user.tenant_id)]
    )

    if existing.fetchone():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Category with this slug already exists"
        )

    # Verify parent category exists (if provided)
    if category_in.parent_id:
        parent = await db.execute(
            text("SELECT id FROM categories WHERE id = $1 AND tenant_id = $2"),
            [str(category_in.parent_id), str(current_user.tenant_id)]
        )
        if not parent.fetchone():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid parent category ID"
            )

    # Create category
    category_id = UUID()
    await db.execute(
        text("""
        INSERT INTO categories (
            id, tenant_id, name, slug, description, color, parent_id, order_index, is_active
        ) VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9)
        """),
        [
            str(category_id), str(current_user.tenant_id), category_in.name, category_in.slug,
            category_in.description, category_in.color, str(category_in.parent_id) if category_in.parent_id else None,
            category_in.order_index, category_in.is_active
        ]
    )

    await db.commit()

    # Return created category
    return await read_category(category_id, db, current_user)


@router.get("/{category_id}", response_model=CategoryResponse)
async def read_category(
    category_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> Any:
    """
    Get category by ID
    """
    result = await db.execute(
        text("SELECT * FROM categories WHERE id = $1 AND tenant_id = $2"),
        [str(category_id), str(current_user.tenant_id)]
    )
    row = result.fetchone()

    if not row:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Category not found"
        )

    return {
        "id": str(row[0]),
        "tenant_id": str(row[1]),
        "name": row[2],
        "slug": row[3],
        "description": row[4],
        "color": row[5],
        "parent_id": str(row[6]) if row[6] else None,
        "order_index": row[7],
        "is_active": row[8],
        "created_at": row[9],
        "updated_at": row[10]
    }


@router.put("/{category_id}", response_model=CategoryResponse)
async def update_category(
    category_id: UUID,
    category_in: CategoryUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> Any:
    """
    Update category
    """
    # Check if category exists and belongs to tenant
    existing = await db.execute(
        text("SELECT * FROM categories WHERE id = $1 AND tenant_id = $2"),
        [str(category_id), str(current_user.tenant_id)]
    )

    if not existing.fetchone():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Category not found"
        )

    # Build update query
    update_fields = []
    values = []
    param_count = 1

    if category_in.name is not None:
        update_fields.append(f"name = ${param_count}")
        values.append(category_in.name)
        param_count += 1

    if category_in.slug is not None:
        # Check if slug is already taken by another category
        slug_check = await db.execute(
            text("SELECT id FROM categories WHERE slug = $1 AND tenant_id = $2 AND id != $3"),
            [category_in.slug, str(current_user.tenant_id), str(category_id)]
        )
        if slug_check.fetchone():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Category with this slug already exists"
            )
        update_fields.append(f"slug = ${param_count}")
        values.append(category_in.slug)
        param_count += 1

    if category_in.description is not None:
        update_fields.append(f"description = ${param_count}")
        values.append(category_in.description)
        param_count += 1

    if category_in.color is not None:
        update_fields.append(f"color = ${param_count}")
        values.append(category_in.color)
        param_count += 1

    if category_in.parent_id is not None:
        update_fields.append(f"parent_id = ${param_count}")
        values.append(str(category_in.parent_id))
        param_count += 1

    if category_in.order_index is not None:
        update_fields.append(f"order_index = ${param_count}")
        values.append(category_in.order_index)
        param_count += 1

    if category_in.is_active is not None:
        update_fields.append(f"is_active = ${param_count}")
        values.append(category_in.is_active)
        param_count += 1

    if not update_fields:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No fields to update"
        )

    # Add category_id to values
    values.append(str(category_id))

    # Execute update
    update_query = f"""
    UPDATE categories
    SET {', '.join(update_fields)}, updated_at = NOW()
    WHERE id = ${param_count}
    """

    await db.execute(text(update_query), values)
    await db.commit()

    # Return updated category
    return await read_category(category_id, db, current_user)


@router.delete("/{category_id}")
async def delete_category(
    category_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> Any:
    """
    Delete category (soft delete - mark as inactive)
    """
    # Check if category exists and belongs to tenant
    existing = await db.execute(
        text("SELECT * FROM categories WHERE id = $1 AND tenant_id = $2"),
        [str(category_id), str(current_user.tenant_id)]
    )

    if not existing.fetchone():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Category not found"
        )

    # Check if category has articles
    articles_count = await db.execute(
        text("SELECT COUNT(*) FROM articles WHERE category_id = $1"),
        [str(category_id)]
    )

    if articles_count.fetchone()[0] > 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot delete category with existing articles. Move articles to another category first."
        )

    # Soft delete - mark as inactive
    await db.execute(
        text("UPDATE categories SET is_active = false, updated_at = NOW() WHERE id = $1"),
        [str(category_id)]
    )

    await db.commit()

    return {"message": "Category deleted successfully"}


@router.get("/stats/overview", response_model=CategoryStats)
async def get_category_stats(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> Any:
    """
    Get category statistics for the tenant
    """
    # Get total categories
    total_result = await db.execute(
        text("SELECT COUNT(*) FROM categories WHERE tenant_id = $1"),
        [str(current_user.tenant_id)]
    )
    total_categories = total_result.fetchone()[0]

    # Get active categories
    active_result = await db.execute(
        text("SELECT COUNT(*) FROM categories WHERE tenant_id = $1 AND is_active = true"),
        [str(current_user.tenant_id)]
    )
    active_categories = active_result.fetchone()[0]

    # Get articles per category
    articles_result = await db.execute(
        text("""
        SELECT c.name, COUNT(a.id) as article_count
        FROM categories c
        LEFT JOIN articles a ON c.id = a.category_id
        WHERE c.tenant_id = $1 AND c.is_active = true
        GROUP BY c.id, c.name
        ORDER BY article_count DESC
        """),
        [str(current_user.tenant_id)]
    )

    articles_per_category = [
        {"category": row[0], "count": row[1]}
        for row in articles_result.fetchall()
    ]

    return {
        "total_categories": total_categories,
        "active_categories": active_categories,
        "articles_per_category": articles_per_category
    }