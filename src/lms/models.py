from __future__ import annotations

from django.conf import settings
from django.db import models


class Course(models.Model):
    organization = models.ForeignKey(
        "multitenant.Tenant", on_delete=models.CASCADE, related_name="courses"
    )
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True, default="")
    is_published = models.BooleanField(default=False)

    class Meta:
        ordering = ["title"]

    def __str__(self) -> str:  # pragma: no cover
        return self.title


class Lesson(models.Model):
    organization = models.ForeignKey(
        "multitenant.Tenant", on_delete=models.CASCADE, related_name="lessons"
    )
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name="lessons")
    title = models.CharField(max_length=200)
    order = models.PositiveIntegerField(default=0)
    content = models.TextField(blank=True, default="")

    class Meta:
        ordering = ["course", "order"]
        unique_together = [("course", "order")]

    def __str__(self) -> str:  # pragma: no cover
        return f"{self.course_id}:{self.title}"


class Enrollment(models.Model):
    organization = models.ForeignKey(
        "multitenant.Tenant", on_delete=models.CASCADE, related_name="enrollments"
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="enrollments"
    )
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name="enrollments")
    enrolled_at = models.DateTimeField(auto_now_add=True)
    progress = models.PositiveSmallIntegerField(default=0)

    class Meta:
        ordering = ["-enrolled_at"]
        unique_together = [("user", "course")]

    def __str__(self) -> str:  # pragma: no cover
        return f"{self.user_id}:{self.course_id}"


class LessonProgress(models.Model):
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

    class Meta:
        unique_together = [("enrollment", "lesson")]

    def __str__(self) -> str:  # pragma: no cover
        return f"{self.enrollment_id}:{self.lesson_id}"

