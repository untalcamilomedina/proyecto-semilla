from __future__ import annotations

from django.conf import settings
from django.db import models


class Forum(models.Model):
    organization = models.ForeignKey(
        "multitenant.Tenant", on_delete=models.CASCADE, related_name="forums"
    )
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True, default="")
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ["name"]
        unique_together = [("organization", "name")]

    def __str__(self) -> str:  # pragma: no cover
        return f"{self.organization.slug}:{self.name}"


class Topic(models.Model):
    organization = models.ForeignKey(
        "multitenant.Tenant", on_delete=models.CASCADE, related_name="topics"
    )
    forum = models.ForeignKey(Forum, on_delete=models.CASCADE, related_name="topics")
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="community_topics",
    )
    title = models.CharField(max_length=200)
    is_pinned = models.BooleanField(default=False)
    is_locked = models.BooleanField(default=False)

    class Meta:
        ordering = ["-is_pinned", "-id"]

    def __str__(self) -> str:  # pragma: no cover
        return self.title


class Post(models.Model):
    organization = models.ForeignKey(
        "multitenant.Tenant", on_delete=models.CASCADE, related_name="posts"
    )
    topic = models.ForeignKey(Topic, on_delete=models.CASCADE, related_name="posts")
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="community_posts",
    )
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["created_at"]

    def __str__(self) -> str:  # pragma: no cover
        return f"{self.topic_id}:{self.author_id}:{self.created_at:%Y-%m-%d %H:%M:%S}"

