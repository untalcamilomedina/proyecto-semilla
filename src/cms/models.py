"""
CMS models for MDX-based content management.

Content is stored as MDX source (Markdown + JSX) in the database.
Rendering happens on the Next.js frontend via @next/mdx.
"""

from __future__ import annotations

from django.conf import settings
from django.db import models
from django.utils.text import slugify


class Category(models.Model):
    """Content category for organizing pages and articles."""

    organization = models.ForeignKey(
        "multitenant.Tenant", on_delete=models.CASCADE, related_name="cms_categories"
    )
    name = models.CharField(max_length=120)
    slug = models.SlugField(max_length=120)
    description = models.TextField(blank=True, default="")
    parent = models.ForeignKey(
        "self", on_delete=models.SET_NULL, null=True, blank=True, related_name="children"
    )
    position = models.PositiveIntegerField(default=0)

    class Meta:
        unique_together = [("organization", "slug")]
        ordering = ["position", "name"]
        verbose_name_plural = "categories"

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)[:120]
        super().save(*args, **kwargs)

    def __str__(self) -> str:
        return self.name


class ContentPage(models.Model):
    """MDX-based content page.

    Stores MDX source content that is rendered on the frontend.
    Supports SEO metadata, categories, and publishing workflow.
    """

    class Status(models.TextChoices):
        DRAFT = "draft", "Draft"
        PUBLISHED = "published", "Published"
        ARCHIVED = "archived", "Archived"

    organization = models.ForeignKey(
        "multitenant.Tenant", on_delete=models.CASCADE, related_name="cms_pages"
    )
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="cms_pages",
    )
    title = models.CharField(max_length=255)
    slug = models.SlugField(max_length=255)
    excerpt = models.TextField(blank=True, default="", help_text="Short description for listings")
    body_mdx = models.TextField(
        blank=True, default="", help_text="MDX content (Markdown + JSX components)"
    )
    category = models.ForeignKey(
        Category,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="pages",
    )
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.DRAFT)
    is_featured = models.BooleanField(default=False)

    # SEO fields
    seo_title = models.CharField(max_length=255, blank=True, default="")
    seo_description = models.TextField(blank=True, default="")
    og_image_url = models.URLField(blank=True, default="")

    # Frontmatter metadata (flexible JSON for custom fields)
    frontmatter = models.JSONField(default=dict, blank=True)
    tags = models.JSONField(default=list, blank=True)

    published_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = [("organization", "slug")]
        ordering = ["-published_at", "-created_at"]
        indexes = [
            models.Index(fields=["organization", "status", "-published_at"]),
        ]

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)[:255]
        super().save(*args, **kwargs)

    def __str__(self) -> str:
        return self.title


class MediaAsset(models.Model):
    """Media file associated with CMS content."""

    organization = models.ForeignKey(
        "multitenant.Tenant", on_delete=models.CASCADE, related_name="cms_media"
    )
    uploaded_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="cms_media",
    )
    file = models.FileField(upload_to="cms/media/%Y/%m/")
    filename = models.CharField(max_length=255)
    mime_type = models.CharField(max_length=127, blank=True, default="")
    size_bytes = models.PositiveBigIntegerField(default=0)
    alt_text = models.CharField(max_length=255, blank=True, default="")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self) -> str:
        return self.filename
