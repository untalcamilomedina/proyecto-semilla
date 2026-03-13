"""Community Django admin registration."""

from __future__ import annotations

from django.contrib import admin

from community.models import MemberProfile, Post, Reaction, Space, Topic


@admin.register(Space)
class SpaceAdmin(admin.ModelAdmin):
    list_display = ["name", "slug", "icon_emoji", "is_active", "is_public", "position", "organization"]
    list_filter = ["organization", "is_active", "is_public"]
    search_fields = ["name"]
    prepopulated_fields = {"slug": ("name",)}


@admin.register(Topic)
class TopicAdmin(admin.ModelAdmin):
    list_display = ["title", "space", "topic_type", "author", "reply_count", "like_count", "is_pinned", "created_at"]
    list_filter = ["organization", "space", "topic_type", "is_pinned", "is_answered"]
    search_fields = ["title"]
    raw_id_fields = ["author", "organization"]
    date_hierarchy = "created_at"


@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = ["topic", "author", "like_count", "is_answer", "created_at"]
    list_filter = ["organization", "is_answer"]
    raw_id_fields = ["author", "topic", "parent", "organization"]


@admin.register(Reaction)
class ReactionAdmin(admin.ModelAdmin):
    list_display = ["user", "reaction_type", "topic", "post", "created_at"]
    list_filter = ["organization", "reaction_type"]
    raw_id_fields = ["user", "topic", "post", "organization"]


@admin.register(MemberProfile)
class MemberProfileAdmin(admin.ModelAdmin):
    list_display = ["user", "level", "points", "topics_created", "posts_created", "likes_received"]
    list_filter = ["organization", "level"]
    search_fields = ["user__email", "user__first_name"]
    raw_id_fields = ["user", "organization"]
