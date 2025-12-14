from __future__ import annotations

from django.contrib import admin

from .models import Course, Enrollment, Lesson, LessonProgress


@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = ("organization", "title", "is_published")
    list_filter = ("organization", "is_published")
    search_fields = ("title",)


@admin.register(Lesson)
class LessonAdmin(admin.ModelAdmin):
    list_display = ("organization", "course", "order", "title")
    list_filter = ("organization", "course")
    search_fields = ("title", "course__title")
    list_select_related = ("organization", "course")


@admin.register(Enrollment)
class EnrollmentAdmin(admin.ModelAdmin):
    list_display = ("organization", "user", "course", "progress", "enrolled_at")
    list_filter = ("organization", "course")
    search_fields = ("user__email", "course__title")
    list_select_related = ("organization", "user", "course")


@admin.register(LessonProgress)
class LessonProgressAdmin(admin.ModelAdmin):
    list_display = ("organization", "enrollment", "lesson", "completed_at")
    list_filter = ("organization",)
    search_fields = ("enrollment__user__email", "lesson__title")
    list_select_related = ("organization", "enrollment", "lesson")

