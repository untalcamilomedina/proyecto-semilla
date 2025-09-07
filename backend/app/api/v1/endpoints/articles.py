"""
Articles CRUD endpoints for CMS functionality
"""

from typing import Any, List
from uuid import UUID
import json

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text, desc

from app.core.database import get_db
from app.core.security import get_current_user
from app.models.user import User
from app.models.article import Article, Category
from app.schemas.article import (
    ArticleCreate,
    ArticleResponse,
    ArticleUpdate,
    ArticleWithContent,
    CategoryCreate,
    CategoryResponse,
    CategoryUpdate,
    ArticleStats
)

router = APIRouter()


@router.get("/", response_model=List[ArticleResponse])
async def read_articles(
    db: AsyncSession = Depends(get_db),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    status_filter: str = Query(None, regex="^(draft|published|review)$"),
    category_id: UUID = None,
    current_user: User = Depends(get_current_user)
) -> Any:
    """
    Retrieve articles with optional filtering
    """
    # Build query with named parameters
    query = """
    SELECT
        a.*,
        u.first_name || ' ' || u.last_name as author_name,
        c.name as category_name
    FROM articles a
    LEFT JOIN users u ON a.author_id = u.id
    LEFT JOIN categories c ON a.category_id = c.id
    WHERE a.tenant_id = :tenant_id
    """

    params = {"tenant_id": str(current_user.tenant_id)}

    if status_filter:
        query += " AND a.status = :status_filter"
        params["status_filter"] = status_filter

    if category_id:
        query += " AND a.category_id = :category_id"
        params["category_id"] = str(category_id)

    query += " ORDER BY a.created_at DESC LIMIT :limit OFFSET :offset"
    params["limit"] = limit
    params["offset"] = skip

    result = await db.execute(text(query), params)
    articles = result.fetchall()

    # Convert to response format
    article_list = []
    for row in articles:
        article_dict = {
            "id": str(row[0]),
            "tenant_id": str(row[1]),
            "title": row[2],
            "slug": row[3],
            "content": row[4],
            "excerpt": row[5],
            "author_id": str(row[6]),
            "category_id": str(row[7]) if row[7] else None,
            "seo_title": row[8],
            "seo_description": row[9],
            "featured_image": row[10],
            "status": row[11],
            "is_featured": row[12],
            "view_count": row[13],
            "comment_count": row[14],
            "like_count": row[15],
            "tags": json.loads(row[16]) if row[16] else [],
            "published_at": row[17],
            "created_at": row[18],
            "updated_at": row[19],
            "author_name": row[20],
            "category_name": row[21]
        }
        article_list.append(article_dict)

    return article_list


@router.post("/", response_model=ArticleResponse)
async def create_article(
    article_in: ArticleCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> Any:
    """
    Create new article
    """
    # Check if slug already exists
    existing = await db.execute(
        text("SELECT id FROM articles WHERE slug = $1 AND tenant_id = $2"),
        [article_in.slug, str(current_user.tenant_id)]
    )

    if existing.fetchone():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Article with this slug already exists"
        )

    # Verify category exists (if provided)
    if article_in.category_id:
        category = await db.execute(
            text("SELECT id FROM categories WHERE id = $1 AND tenant_id = $2"),
            [str(article_in.category_id), str(current_user.tenant_id)]
        )
        if not category.fetchone():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid category ID"
            )

    # Create article
    article_id = UUID()
    published_at = None
    if article_in.status == "published":
        published_at = "NOW()"

    await db.execute(
        text("""
        INSERT INTO articles (
            id, tenant_id, title, slug, content, excerpt, author_id, category_id,
            seo_title, seo_description, featured_image, status, is_featured,
            view_count, comment_count, like_count, tags, published_at
        ) VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $12, $13, $14, $15, $16, $17, """ + (published_at or "NULL") + ")"),
        [
            str(article_id), str(current_user.tenant_id), article_in.title, article_in.slug,
            article_in.content, article_in.excerpt, str(current_user.id), str(article_in.category_id) if article_in.category_id else None,
            article_in.seo_title, article_in.seo_description, article_in.featured_image,
            article_in.status, article_in.is_featured, 0, 0, 0, json.dumps(article_in.tags) if article_in.tags else None
        ]
    )

    await db.commit()

    # Return created article
    return await read_article(article_id, db, current_user)


@router.get("/{article_id}", response_model=ArticleWithContent)
async def read_article(
    article_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> Any:
    """
    Get article by ID with full content
    """
    query = """
    SELECT
        a.*,
        u.first_name || ' ' || u.last_name as author_name,
        c.name as category_name
    FROM articles a
    LEFT JOIN users u ON a.author_id = u.id
    LEFT JOIN categories c ON a.category_id = c.id
    WHERE a.id = $1 AND a.tenant_id = $2
    """

    result = await db.execute(text(query), [str(article_id), str(current_user.tenant_id)])
    row = result.fetchone()

    if not row:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Article not found"
        )

    return {
        "id": str(row[0]),
        "tenant_id": str(row[1]),
        "title": row[2],
        "slug": row[3],
        "content": row[4],
        "excerpt": row[5],
        "author_id": str(row[6]),
        "category_id": str(row[7]) if row[7] else None,
        "seo_title": row[8],
        "seo_description": row[9],
        "featured_image": row[10],
        "status": row[11],
        "is_featured": row[12],
        "view_count": row[13],
        "comment_count": row[14],
        "like_count": row[15],
        "tags": json.loads(row[16]) if row[16] else [],
        "published_at": row[17],
        "created_at": row[18],
        "updated_at": row[19],
        "author_name": row[20],
        "category_name": row[21]
    }


@router.put("/{article_id}", response_model=ArticleResponse)
async def update_article(
    article_id: UUID,
    article_in: ArticleUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> Any:
    """
    Update article
    """
    # Check if article exists and belongs to tenant
    existing = await db.execute(
        text("SELECT * FROM articles WHERE id = $1 AND tenant_id = $2"),
        [str(article_id), str(current_user.tenant_id)]
    )

    if not existing.fetchone():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Article not found"
        )

    # Build update query
    update_fields = []
    values = []
    param_count = 1

    if article_in.title is not None:
        update_fields.append(f"title = ${param_count}")
        values.append(article_in.title)
        param_count += 1

    if article_in.slug is not None:
        # Check if slug is already taken by another article
        slug_check = await db.execute(
            text("SELECT id FROM articles WHERE slug = $1 AND tenant_id = $2 AND id != $3"),
            [article_in.slug, str(current_user.tenant_id), str(article_id)]
        )
        if slug_check.fetchone():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Article with this slug already exists"
            )
        update_fields.append(f"slug = ${param_count}")
        values.append(article_in.slug)
        param_count += 1

    if article_in.content is not None:
        update_fields.append(f"content = ${param_count}")
        values.append(article_in.content)
        param_count += 1

    if article_in.excerpt is not None:
        update_fields.append(f"excerpt = ${param_count}")
        values.append(article_in.excerpt)
        param_count += 1

    if article_in.category_id is not None:
        update_fields.append(f"category_id = ${param_count}")
        values.append(str(article_in.category_id))
        param_count += 1

    if article_in.seo_title is not None:
        update_fields.append(f"seo_title = ${param_count}")
        values.append(article_in.seo_title)
        param_count += 1

    if article_in.seo_description is not None:
        update_fields.append(f"seo_description = ${param_count}")
        values.append(article_in.seo_description)
        param_count += 1

    if article_in.featured_image is not None:
        update_fields.append(f"featured_image = ${param_count}")
        values.append(article_in.featured_image)
        param_count += 1

    if article_in.status is not None:
        update_fields.append(f"status = ${param_count}")
        values.append(article_in.status)
        param_count += 1

        # Update published_at if status changed to published
        if article_in.status == "published":
            update_fields.append(f"published_at = NOW()")
        elif article_in.status in ["draft", "review"]:
            update_fields.append(f"published_at = NULL")

    if article_in.is_featured is not None:
        update_fields.append(f"is_featured = ${param_count}")
        values.append(article_in.is_featured)
        param_count += 1

    if article_in.tags is not None:
        update_fields.append(f"tags = ${param_count}")
        values.append(json.dumps(article_in.tags))
        param_count += 1

    if not update_fields:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No fields to update"
        )

    # Add article_id to values
    values.append(str(article_id))

    # Execute update
    update_query = f"""
    UPDATE articles
    SET {', '.join(update_fields)}, updated_at = NOW()
    WHERE id = ${param_count}
    """

    await db.execute(text(update_query), values)
    await db.commit()

    # Return updated article
    return await read_article(article_id, db, current_user)


@router.delete("/{article_id}")
async def delete_article(
    article_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> Any:
    """
    Delete article (soft delete - mark as inactive)
    """
    # Check if article exists and belongs to tenant
    existing = await db.execute(
        text("SELECT id FROM articles WHERE id = $1 AND tenant_id = $2"),
        [str(article_id), str(current_user.tenant_id)]
    )

    if not existing.fetchone():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Article not found"
        )

    # Soft delete - mark as inactive (you could add a deleted_at field)
    await db.execute(
        text("DELETE FROM articles WHERE id = $1"),
        [str(article_id)]
    )

    await db.commit()

    return {"message": "Article deleted successfully"}


@router.get("/stats/overview", response_model=ArticleStats)
async def get_article_stats(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> Any:
    """
    Get article statistics for the tenant
    """
    # Get total articles
    total_result = await db.execute(
        text("SELECT COUNT(*) FROM articles WHERE tenant_id = $1"),
        [str(current_user.tenant_id)]
    )
    total_articles = total_result.fetchone()[0]

    # Get published articles
    published_result = await db.execute(
        text("SELECT COUNT(*) FROM articles WHERE tenant_id = $1 AND status = 'published'"),
        [str(current_user.tenant_id)]
    )
    published_articles = published_result.fetchone()[0]

    # Get draft articles
    draft_result = await db.execute(
        text("SELECT COUNT(*) FROM articles WHERE tenant_id = $1 AND status = 'draft'"),
        [str(current_user.tenant_id)]
    )
    draft_articles = draft_result.fetchone()[0]

    # Get total views
    views_result = await db.execute(
        text("SELECT COALESCE(SUM(view_count), 0) FROM articles WHERE tenant_id = $1"),
        [str(current_user.tenant_id)]
    )
    total_views = views_result.fetchone()[0]

    # Get total comments
    comments_result = await db.execute(
        text("SELECT COALESCE(SUM(comment_count), 0) FROM articles WHERE tenant_id = $1"),
        [str(current_user.tenant_id)]
    )
    total_comments = comments_result.fetchone()[0]

    # Get total likes
    likes_result = await db.execute(
        text("SELECT COALESCE(SUM(like_count), 0) FROM articles WHERE tenant_id = $1"),
        [str(current_user.tenant_id)]
    )
    total_likes = likes_result.fetchone()[0]

    return {
        "total_articles": total_articles,
        "published_articles": published_articles,
        "draft_articles": draft_articles,
        "total_views": total_views,
        "total_comments": total_comments,
        "total_likes": total_likes
    }