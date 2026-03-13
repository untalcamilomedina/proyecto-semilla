"""LMS Django admin registration."""

from __future__ import annotations

from django.contrib import admin

from lms.models import Certificate, Course, Enrollment, Lesson, LessonProgress, Review, Section


@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = [
        "title", "slug", "status", "pricing_type", "price",
        "level", "instructor", "is_featured", "published_at",
    ]
    list_filter = ["organization", "status", "pricing_type", "level", "is_featured"]
    search_fields = ["title", "description"]
    prepopulated_fields = {"slug": ("title",)}
    raw_id_fields = ["instructor", "organization"]
    date_hierarchy = "created_at"


@admin.register(Section)
class SectionAdmin(admin.ModelAdmin):
    list_display = ["title", "course", "order", "organization"]
    list_filter = ["organization"]
    raw_id_fields = ["course", "organization"]


@admin.register(Lesson)
class LessonAdmin(admin.ModelAdmin):
    list_display = [
        "title", "course", "section", "order", "content_type",
        "duration_minutes", "is_preview", "is_published",
    ]
    list_filter = ["organization", "content_type", "is_preview", "is_published"]
    search_fields = ["title"]
    raw_id_fields = ["course", "section", "organization"]


@admin.register(Enrollment)
class EnrollmentAdmin(admin.ModelAdmin):
    list_display = ["user", "course", "status", "progress", "amount_paid", "enrolled_at"]
    list_filter = ["organization", "status"]
    raw_id_fields = ["user", "course", "organization"]
    date_hierarchy = "enrolled_at"


@admin.register(LessonProgress)
class LessonProgressAdmin(admin.ModelAdmin):
    list_display = ["enrollment", "lesson", "completed_at", "time_spent_seconds"]
    list_filter = ["organization"]
    raw_id_fields = ["enrollment", "lesson", "organization"]


@admin.register(Certificate)
class CertificateAdmin(admin.ModelAdmin):
    list_display = ["certificate_number", "enrollment", "issued_at", "pdf_url"]
    list_filter = ["organization"]
    search_fields = ["certificate_number"]
    raw_id_fields = ["enrollment", "organization"]


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ["user", "course", "rating", "created_at"]
    list_filter = ["organization", "rating"]
    raw_id_fields = ["user", "course", "organization"]
