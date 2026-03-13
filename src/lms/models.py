"""
LMS models for course management with sales support.

Enhanced models supporting:
- Course pricing and sales via Stripe
- MDX-based lesson content
- Modular course structure (sections → lessons)
- Certificates of completion
- Student reviews and ratings
"""

from __future__ import annotations

from decimal import Decimal

from django.conf import settings
from django.db import models
from django.utils import timezone
from django.utils.text import slugify


class Course(models.Model):
    """Enhanced course model with pricing and MDX content."""

    class Status(models.TextChoices):
        DRAFT = "draft", "Draft"
        PUBLISHED = "published", "Published"
        ARCHIVED = "archived", "Archived"

    class PricingType(models.TextChoices):
        FREE = "free", "Free"
        PAID = "paid", "Paid"
        SUBSCRIPTION = "subscription", "Subscription"

    organization = models.ForeignKey(
        "multitenant.Tenant", on_delete=models.CASCADE, related_name="courses"
    )
    instructor = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="taught_courses",
    )
    title = models.CharField(max_length=255)
    slug = models.SlugField(max_length=255)
    description = models.TextField(blank=True, default="")
    description_mdx = models.TextField(
        blank=True, default="",
        help_text="Rich course description in MDX format",
    )
    thumbnail_url = models.URLField(blank=True, default="")
    preview_video_url = models.URLField(blank=True, default="")

    # Status & visibility
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.DRAFT)
    is_featured = models.BooleanField(default=False)
    is_published = models.BooleanField(default=False)

    # Pricing
    pricing_type = models.CharField(
        max_length=20, choices=PricingType.choices, default=PricingType.FREE
    )
    price = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal("0.00"))
    currency = models.CharField(max_length=3, default="USD")
    stripe_price_id = models.CharField(max_length=128, blank=True, default="")
    stripe_product_id = models.CharField(max_length=128, blank=True, default="")

    # Metadata
    level = models.CharField(
        max_length=20,
        choices=[
            ("beginner", "Beginner"),
            ("intermediate", "Intermediate"),
            ("advanced", "Advanced"),
        ],
        default="beginner",
    )
    estimated_hours = models.PositiveSmallIntegerField(default=0)
    tags = models.JSONField(default=list, blank=True)
    requirements = models.JSONField(default=list, blank=True, help_text="List of prerequisites")
    what_you_learn = models.JSONField(default=list, blank=True, help_text="Learning outcomes")

    # Timestamps
    published_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]
        unique_together = [("organization", "slug")]
        indexes = [
            models.Index(fields=["organization", "status", "-published_at"]),
        ]

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)[:255]
        if self.status == self.Status.PUBLISHED and not self.published_at:
            self.published_at = timezone.now()
            self.is_published = True
        super().save(*args, **kwargs)

    @property
    def is_free(self) -> bool:
        return self.pricing_type == self.PricingType.FREE

    @property
    def total_lessons(self) -> int:
        return self.lessons.count()

    @property
    def total_enrolled(self) -> int:
        return self.enrollments.count()

    def __str__(self) -> str:
        return self.title


class Section(models.Model):
    """Course section/module for organizing lessons."""

    organization = models.ForeignKey(
        "multitenant.Tenant", on_delete=models.CASCADE, related_name="lms_sections"
    )
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name="sections")
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True, default="")
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ["course", "order"]
        unique_together = [("course", "order")]

    def __str__(self) -> str:
        return f"{self.course.title} — {self.title}"


class Lesson(models.Model):
    """Enhanced lesson with MDX content and video support."""

    class ContentType(models.TextChoices):
        VIDEO = "video", "Video"
        TEXT = "text", "Text/MDX"
        QUIZ = "quiz", "Quiz"
        ASSIGNMENT = "assignment", "Assignment"

    organization = models.ForeignKey(
        "multitenant.Tenant", on_delete=models.CASCADE, related_name="lessons"
    )
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name="lessons")
    section = models.ForeignKey(
        Section, on_delete=models.SET_NULL, null=True, blank=True, related_name="lessons"
    )
    title = models.CharField(max_length=255)
    slug = models.SlugField(max_length=255, blank=True, default="")
    order = models.PositiveIntegerField(default=0)
    content_type = models.CharField(
        max_length=20, choices=ContentType.choices, default=ContentType.TEXT
    )

    # Content (MDX source)
    content = models.TextField(blank=True, default="", help_text="MDX content for the lesson")

    # Video
    video_url = models.URLField(blank=True, default="")
    duration_minutes = models.PositiveSmallIntegerField(default=0)

    # Access control
    is_preview = models.BooleanField(default=False, help_text="Available without enrollment")
    is_published = models.BooleanField(default=True)

    class Meta:
        ordering = ["course", "section", "order"]
        unique_together = [("course", "order")]

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)[:255]
        super().save(*args, **kwargs)

    def __str__(self) -> str:
        return f"{self.course_id}:{self.title}"


class Enrollment(models.Model):
    """Student enrollment with payment tracking."""

    class Status(models.TextChoices):
        ACTIVE = "active", "Active"
        COMPLETED = "completed", "Completed"
        EXPIRED = "expired", "Expired"
        REFUNDED = "refunded", "Refunded"

    organization = models.ForeignKey(
        "multitenant.Tenant", on_delete=models.CASCADE, related_name="enrollments"
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="enrollments"
    )
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name="enrollments")
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.ACTIVE)
    progress = models.PositiveSmallIntegerField(default=0, help_text="0-100 percentage")

    # Payment
    amount_paid = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal("0.00"))
    currency = models.CharField(max_length=3, default="USD")
    stripe_payment_intent_id = models.CharField(max_length=128, blank=True, default="")

    enrolled_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ["-enrolled_at"]
        unique_together = [("user", "course")]

    def __str__(self) -> str:
        return f"{self.user_id}:{self.course_id}"


class LessonProgress(models.Model):
    """Tracks individual lesson completion per student."""

    organization = models.ForeignKey(
        "multitenant.Tenant", on_delete=models.CASCADE, related_name="lesson_progress"
    )
    enrollment = models.ForeignKey(
        Enrollment, on_delete=models.CASCADE, related_name="lesson_progress"
    )
    lesson = models.ForeignKey(
        Lesson, on_delete=models.CASCADE, related_name="lesson_progress"
    )
    completed_at = models.DateTimeField(blank=True, null=True)
    time_spent_seconds = models.PositiveIntegerField(default=0)

    class Meta:
        unique_together = [("enrollment", "lesson")]

    def __str__(self) -> str:
        return f"{self.enrollment_id}:{self.lesson_id}"


class Certificate(models.Model):
    """Certificate issued upon course completion."""

    organization = models.ForeignKey(
        "multitenant.Tenant", on_delete=models.CASCADE, related_name="certificates"
    )
    enrollment = models.OneToOneField(
        Enrollment, on_delete=models.CASCADE, related_name="certificate"
    )
    certificate_number = models.CharField(max_length=64, unique=True)
    issued_at = models.DateTimeField(auto_now_add=True)
    pdf_url = models.URLField(blank=True, default="")

    class Meta:
        ordering = ["-issued_at"]

    def __str__(self) -> str:
        return self.certificate_number


class Review(models.Model):
    """Student review/rating for a course."""

    organization = models.ForeignKey(
        "multitenant.Tenant", on_delete=models.CASCADE, related_name="course_reviews"
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="course_reviews"
    )
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name="reviews")
    rating = models.PositiveSmallIntegerField(
        help_text="1-5 stars",
    )
    comment = models.TextField(blank=True, default="")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = [("user", "course")]
        ordering = ["-created_at"]

    def __str__(self) -> str:
        return f"{self.user_id}:{self.course_id}:{self.rating}★"
