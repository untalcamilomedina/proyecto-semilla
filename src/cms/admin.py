from __future__ import annotations

from django.contrib import admin

from .models import ArticleIndexPage, ArticlePage, HomePage


@admin.register(HomePage)
class HomePageAdmin(admin.ModelAdmin):
    list_display = ("title", "organization", "live", "first_published_at", "last_published_at")
    list_filter = ("organization", "live")
    search_fields = ("title", "slug")


@admin.register(ArticleIndexPage)
class ArticleIndexPageAdmin(admin.ModelAdmin):
    list_display = ("title", "organization", "live", "first_published_at", "last_published_at")
    list_filter = ("organization", "live")
    search_fields = ("title", "slug")


@admin.register(ArticlePage)
class ArticlePageAdmin(admin.ModelAdmin):
    list_display = ("title", "organization", "date", "live", "first_published_at", "last_published_at")
    list_filter = ("organization", "live", "date")
    search_fields = ("title", "slug", "intro")

