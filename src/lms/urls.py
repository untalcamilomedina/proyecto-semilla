from __future__ import annotations

from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import CourseViewSet, EnrollmentViewSet, LessonProgressViewSet, LessonViewSet

router = DefaultRouter()
router.trailing_slash = "/?"
router.register("courses", CourseViewSet, basename="courses")
router.register("lessons", LessonViewSet, basename="lessons")
router.register("enrollments", EnrollmentViewSet, basename="enrollments")
router.register("lesson-progress", LessonProgressViewSet, basename="lesson-progress")

urlpatterns = [
    path("", include(router.urls)),
]
