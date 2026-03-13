"""CMS serializers for MDX content management."""

from __future__ import annotations

from rest_framework import serializers

from cms.models import Category, ContentPage, MediaAsset


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = [
            "id", "name", "slug", "description", "parent", "position",
        ]
        read_only_fields = ["id", "slug"]


class ContentPageListSerializer(serializers.ModelSerializer):
    """Lightweight serializer for listing pages (excludes body_mdx)."""
    author_email = serializers.EmailField(source="author.email", read_only=True)
    category_name = serializers.CharField(source="category.name", read_only=True, default="")

    class Meta:
        model = ContentPage
        fields = [
            "id", "title", "slug", "excerpt", "status", "is_featured",
            "author_email", "category", "category_name",
            "seo_title", "tags", "published_at", "created_at", "updated_at",
        ]
        read_only_fields = ["id", "slug", "author_email", "category_name", "created_at", "updated_at"]


class ContentPageDetailSerializer(serializers.ModelSerializer):
    """Full serializer including body_mdx for detail view/editing."""
    author_email = serializers.EmailField(source="author.email", read_only=True)

    class Meta:
        model = ContentPage
        fields = [
            "id", "title", "slug", "excerpt", "body_mdx", "status",
            "is_featured", "author", "author_email", "category",
            "seo_title", "seo_description", "og_image_url",
            "frontmatter", "tags", "published_at", "created_at", "updated_at",
        ]
        read_only_fields = ["id", "slug", "author_email", "created_at", "updated_at"]


class MediaAssetSerializer(serializers.ModelSerializer):
    class Meta:
        model = MediaAsset
        fields = [
            "id", "filename", "file", "mime_type", "size_bytes",
            "alt_text", "uploaded_by", "created_at",
        ]
        read_only_fields = ["id", "filename", "mime_type", "size_bytes", "uploaded_by", "created_at"]
