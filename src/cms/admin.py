"""CMS Django admin registration."""

from __future__ import annotations

from django.contrib import admin

from cms.models import Category, ContentPage, MediaAsset


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ["name", "slug", "organization", "parent", "position"]
    list_filter = ["organization"]
    search_fields = ["name"]
    prepopulated_fields = {"slug": ("name",)}


@admin.register(ContentPage)
class ContentPageAdmin(admin.ModelAdmin):
    list_display = ["title", "slug", "status", "author", "category", "is_featured", "published_at"]
    list_filter = ["status", "is_featured", "organization", "category"]
    search_fields = ["title", "excerpt"]
    prepopulated_fields = {"slug": ("title",)}
    raw_id_fields = ["author", "organization"]
    date_hierarchy = "created_at"


@admin.register(MediaAsset)
class MediaAssetAdmin(admin.ModelAdmin):
    list_display = ["filename", "mime_type", "size_bytes", "uploaded_by", "created_at"]
    list_filter = ["organization", "mime_type"]
    search_fields = ["filename", "alt_text"]
    raw_id_fields = ["uploaded_by", "organization"]
