from __future__ import annotations

from django.contrib import admin

from .models import Forum, Post, Topic


@admin.register(Forum)
class ForumAdmin(admin.ModelAdmin):
    list_display = ("organization", "name", "is_active")
    list_filter = ("organization", "is_active")
    search_fields = ("name", "description")
    list_select_related = ("organization",)


@admin.register(Topic)
class TopicAdmin(admin.ModelAdmin):
    list_display = ("organization", "forum", "title", "author", "is_pinned", "is_locked")
    list_filter = ("organization", "forum", "is_pinned", "is_locked")
    search_fields = ("title", "forum__name", "author__email", "author__username")
    list_select_related = ("organization", "forum", "author")


@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = ("organization", "topic", "author", "created_at", "updated_at")
    list_filter = ("organization", "created_at")
    search_fields = ("topic__title", "author__email", "author__username", "content")
    list_select_related = ("organization", "topic", "author")

