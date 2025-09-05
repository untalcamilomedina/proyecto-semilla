"""Add CMS tables only: Article, Category, Comment

Revision ID: add_cms_only
Revises: 9365aa3543ae
Create Date: 2025-09-04 19:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '20250904_190027'
down_revision: Union[str, None] = '9365aa3543ae'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Create categories table
    op.create_table('categories',
        sa.Column('id', sa.UUID(), autoincrement=False, nullable=False),
        sa.Column('tenant_id', sa.UUID(), autoincrement=False, nullable=False),
        sa.Column('name', sa.VARCHAR(length=100), autoincrement=False, nullable=False),
        sa.Column('slug', sa.VARCHAR(length=100), autoincrement=False, nullable=False),
        sa.Column('description', sa.TEXT(), autoincrement=False, nullable=True),
        sa.Column('color', sa.VARCHAR(length=7), autoincrement=False, nullable=True),
        sa.Column('parent_id', sa.UUID(), autoincrement=False, nullable=True),
        sa.Column('order_index', sa.INTEGER(), autoincrement=False, nullable=False),
        sa.Column('is_active', sa.BOOLEAN(), autoincrement=False, nullable=False),
        sa.Column('created_at', postgresql.TIMESTAMP(timezone=True), autoincrement=False, nullable=False),
        sa.Column('updated_at', postgresql.TIMESTAMP(timezone=True), autoincrement=False, nullable=False),
        sa.ForeignKeyConstraint(['tenant_id'], ['tenants.id'], name='categories_tenant_id_fkey'),
        sa.PrimaryKeyConstraint('id', name='categories_pkey')
    )
    op.create_index('ix_categories_tenant_id', 'categories', ['tenant_id'], unique=False)
    op.create_index('ix_categories_slug', 'categories', ['slug'], unique=False)
    op.create_index('ix_categories_name', 'categories', ['name'], unique=False)

    # Create articles table
    op.create_table('articles',
        sa.Column('id', sa.UUID(), autoincrement=False, nullable=False),
        sa.Column('tenant_id', sa.UUID(), autoincrement=False, nullable=False),
        sa.Column('title', sa.VARCHAR(length=200), autoincrement=False, nullable=False),
        sa.Column('slug', sa.VARCHAR(length=200), autoincrement=False, nullable=False),
        sa.Column('content', sa.TEXT(), autoincrement=False, nullable=False),
        sa.Column('excerpt', sa.TEXT(), autoincrement=False, nullable=True),
        sa.Column('author_id', sa.UUID(), autoincrement=False, nullable=False),
        sa.Column('category_id', sa.UUID(), autoincrement=False, nullable=True),
        sa.Column('seo_title', sa.VARCHAR(length=60), autoincrement=False, nullable=True),
        sa.Column('seo_description', sa.VARCHAR(length=160), autoincrement=False, nullable=True),
        sa.Column('featured_image', sa.VARCHAR(length=500), autoincrement=False, nullable=True),
        sa.Column('status', sa.VARCHAR(length=20), autoincrement=False, nullable=False),
        sa.Column('is_featured', sa.BOOLEAN(), autoincrement=False, nullable=False),
        sa.Column('view_count', sa.INTEGER(), autoincrement=False, nullable=False),
        sa.Column('comment_count', sa.INTEGER(), autoincrement=False, nullable=False),
        sa.Column('like_count', sa.INTEGER(), autoincrement=False, nullable=False),
        sa.Column('tags', sa.TEXT(), autoincrement=False, nullable=True),
        sa.Column('published_at', postgresql.TIMESTAMP(timezone=True), autoincrement=False, nullable=True),
        sa.Column('created_at', postgresql.TIMESTAMP(timezone=True), autoincrement=False, nullable=False),
        sa.Column('updated_at', postgresql.TIMESTAMP(timezone=True), autoincrement=False, nullable=False),
        sa.ForeignKeyConstraint(['author_id'], ['users.id'], name='articles_author_id_fkey'),
        sa.ForeignKeyConstraint(['tenant_id'], ['tenants.id'], name='articles_tenant_id_fkey'),
        sa.ForeignKeyConstraint(['category_id'], ['categories.id'], name='articles_category_id_fkey'),
        sa.PrimaryKeyConstraint('id', name='articles_pkey')
    )
    op.create_index('ix_articles_title', 'articles', ['title'], unique=False)
    op.create_index('ix_articles_tenant_id', 'articles', ['tenant_id'], unique=False)
    op.create_index('ix_articles_status', 'articles', ['status'], unique=False)
    op.create_index('ix_articles_slug', 'articles', ['slug'], unique=False)
    op.create_index('ix_articles_category_id', 'articles', ['category_id'], unique=False)
    op.create_index('ix_articles_author_id', 'articles', ['author_id'], unique=False)
    op.create_index('idx_articles_tenant_status', 'articles', ['tenant_id', 'status'], unique=False)
    op.create_index('idx_articles_tenant_published', 'articles', ['tenant_id', 'published_at'], unique=False)
    op.create_index('idx_articles_author', 'articles', ['author_id'], unique=False)

    # Create comments table
    op.create_table('comments',
        sa.Column('id', sa.UUID(), autoincrement=False, nullable=False),
        sa.Column('tenant_id', sa.UUID(), autoincrement=False, nullable=False),
        sa.Column('article_id', sa.UUID(), autoincrement=False, nullable=False),
        sa.Column('author_name', sa.VARCHAR(length=100), autoincrement=False, nullable=False),
        sa.Column('author_email', sa.VARCHAR(length=255), autoincrement=False, nullable=True),
        sa.Column('content', sa.TEXT(), autoincrement=False, nullable=False),
        sa.Column('user_id', sa.UUID(), autoincrement=False, nullable=True),
        sa.Column('is_approved', sa.BOOLEAN(), autoincrement=False, nullable=False),
        sa.Column('is_spam', sa.BOOLEAN(), autoincrement=False, nullable=False),
        sa.Column('parent_id', sa.UUID(), autoincrement=False, nullable=True),
        sa.Column('created_at', postgresql.TIMESTAMP(timezone=True), autoincrement=False, nullable=False),
        sa.Column('updated_at', postgresql.TIMESTAMP(timezone=True), autoincrement=False, nullable=False),
        sa.ForeignKeyConstraint(['article_id'], ['articles.id'], name='comments_article_id_fkey'),
        sa.ForeignKeyConstraint(['tenant_id'], ['tenants.id'], name='comments_tenant_id_fkey'),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], name='comments_user_id_fkey'),
        sa.PrimaryKeyConstraint('id', name='comments_pkey')
    )
    op.create_index('ix_comments_tenant_id', 'comments', ['tenant_id'], unique=False)
    op.create_index('ix_comments_article_id', 'comments', ['article_id'], unique=False)


def downgrade() -> None:
    # Drop comments table
    op.drop_index('ix_comments_article_id', table_name='comments')
    op.drop_index('ix_comments_tenant_id', table_name='comments')
    op.drop_table('comments')

    # Drop articles table
    op.drop_index('idx_articles_author', table_name='articles')
    op.drop_index('idx_articles_tenant_published', table_name='articles')
    op.drop_index('idx_articles_tenant_status', table_name='articles')
    op.drop_index('ix_articles_author_id', table_name='articles')
    op.drop_index('ix_articles_category_id', table_name='articles')
    op.drop_index('ix_articles_slug', table_name='articles')
    op.drop_index('ix_articles_status', table_name='articles')
    op.drop_index('ix_articles_tenant_id', table_name='articles')
    op.drop_index('ix_articles_title', table_name='articles')
    op.drop_table('articles')

    # Drop categories table
    op.drop_index('ix_categories_name', table_name='categories')
    op.drop_index('ix_categories_slug', table_name='categories')
    op.drop_index('ix_categories_tenant_id', table_name='categories')
    op.drop_table('categories')