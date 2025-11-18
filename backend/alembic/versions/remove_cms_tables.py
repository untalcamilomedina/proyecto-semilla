"""Remove CMS tables (articles, categories, comments)

Revision ID: remove_cms
Revises: 4859d159e0c9
Create Date: 2025-09-19 06:57:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = 'remove_cms'
down_revision: Union[str, None] = '4859d159e0c9'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Remove CMS-related tables and indexes"""
    # Drop tables in correct order (considering foreign key constraints)
    # Comments table first (references articles)
    op.drop_table('comments', schema=None, if_exists=True)

    # Articles table (referenced by comments)
    op.drop_table('articles', schema=None, if_exists=True)

    # Categories table (referenced by articles)
    op.drop_table('categories', schema=None, if_exists=True)

    # Drop indexes if they exist
    op.drop_index('idx_articles_tenant_status', table_name='articles', schema=None, if_exists=True)
    op.drop_index('idx_articles_tenant_published', table_name='articles', schema=None, if_exists=True)
    op.drop_index('idx_articles_author', table_name='articles', schema=None, if_exists=True)
    op.drop_index('idx_cms_articles_tenant_status', table_name='articles', schema=None, if_exists=True)
    op.drop_index('idx_cms_articles_tenant_published', table_name='articles', schema=None, if_exists=True)
    op.drop_index('idx_cms_categories_tenant_order', table_name='categories', schema=None, if_exists=True)
    op.drop_index('idx_cms_comments_article_status', table_name='comments', schema=None, if_exists=True)


def downgrade() -> None:
    """Recreate CMS tables (for rollback purposes)"""
    # Note: This is a simplified rollback. In production, you might want to restore data from backups.

    # Recreate categories table
    op.create_table('categories',
        sa.Column('id', sa.UUID(), nullable=False),
        sa.Column('tenant_id', sa.UUID(), nullable=False),
        sa.Column('name', sa.String(length=100), nullable=False),
        sa.Column('slug', sa.String(length=100), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('color', sa.String(length=7), nullable=True),
        sa.Column('parent_id', sa.UUID(), nullable=True),
        sa.Column('order_index', sa.Integer(), nullable=False),
        sa.Column('is_active', sa.Boolean(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(['tenant_id'], ['tenants.id'], name='categories_tenant_id_fkey'),
        sa.PrimaryKeyConstraint('id')
    )

    # Recreate articles table
    op.create_table('articles',
        sa.Column('id', sa.UUID(), nullable=False),
        sa.Column('tenant_id', sa.UUID(), nullable=False),
        sa.Column('title', sa.String(length=200), nullable=False),
        sa.Column('slug', sa.String(length=200), nullable=False),
        sa.Column('content', sa.Text(), nullable=False),
        sa.Column('excerpt', sa.Text(), nullable=True),
        sa.Column('author_id', sa.UUID(), nullable=False),
        sa.Column('category_id', sa.UUID(), nullable=True),
        sa.Column('seo_title', sa.String(length=60), nullable=True),
        sa.Column('seo_description', sa.String(length=160), nullable=True),
        sa.Column('featured_image', sa.String(length=500), nullable=True),
        sa.Column('status', sa.String(length=20), nullable=False),
        sa.Column('is_featured', sa.Boolean(), nullable=False),
        sa.Column('view_count', sa.Integer(), nullable=False),
        sa.Column('comment_count', sa.Integer(), nullable=False),
        sa.Column('like_count', sa.Integer(), nullable=False),
        sa.Column('tags', sa.Text(), nullable=True),
        sa.Column('published_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(['author_id'], ['users.id'], name='articles_author_id_fkey'),
        sa.ForeignKeyConstraint(['category_id'], ['categories.id'], name='articles_category_id_fkey'),
        sa.ForeignKeyConstraint(['tenant_id'], ['tenants.id'], name='articles_tenant_id_fkey'),
        sa.PrimaryKeyConstraint('id')
    )

    # Recreate comments table
    op.create_table('comments',
        sa.Column('id', sa.UUID(), nullable=False),
        sa.Column('tenant_id', sa.UUID(), nullable=False),
        sa.Column('article_id', sa.UUID(), nullable=False),
        sa.Column('author_name', sa.String(length=100), nullable=False),
        sa.Column('author_email', sa.String(length=255), nullable=True),
        sa.Column('content', sa.Text(), nullable=False),
        sa.Column('user_id', sa.UUID(), nullable=True),
        sa.Column('is_approved', sa.Boolean(), nullable=False),
        sa.Column('is_spam', sa.Boolean(), nullable=False),
        sa.Column('parent_id', sa.UUID(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(['article_id'], ['articles.id'], name='comments_article_id_fkey'),
        sa.ForeignKeyConstraint(['tenant_id'], ['tenants.id'], name='comments_tenant_id_fkey'),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], name='comments_user_id_fkey'),
        sa.PrimaryKeyConstraint('id')
    )

    # Recreate indexes
    op.create_index('idx_articles_tenant_status', 'articles', ['tenant_id', 'status'], unique=False)
    op.create_index('idx_articles_tenant_published', 'articles', ['tenant_id', 'published_at'], unique=False)
    op.create_index('idx_articles_author', 'articles', ['author_id'], unique=False)
    op.create_index('idx_cms_articles_tenant_status', 'articles', ['tenant_id', 'status'], unique=False)
    op.create_index('idx_cms_articles_tenant_published', 'articles', ['tenant_id', 'published_at'], unique=False)
    op.create_index('idx_cms_categories_tenant_order', 'categories', ['tenant_id', 'order_index'], unique=False)
    op.create_index('idx_cms_comments_article_status', 'comments', ['article_id', 'is_approved'], unique=False)