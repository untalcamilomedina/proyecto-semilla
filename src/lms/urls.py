"""LMS URL configuration."""

from __future__ import annotations

from django.urls import include, path
from rest_framework.routers import DefaultRouter

from lms.views import (
    CertificateViewSet,
    CourseViewSet,
    EnrollmentViewSet,
    LessonProgressViewSet,
    LessonViewSet,
    ReviewViewSet,
    SectionViewSet,
)

router = DefaultRouter()
router.register("courses", CourseViewSet, basename="lms-course")
router.register("sections", SectionViewSet, basename="lms-section")
router.register("lessons", LessonViewSet, basename="lms-lesson")
router.register("enrollments", EnrollmentViewSet, basename="lms-enrollment")
router.register("progress", LessonProgressViewSet, basename="lms-progress")
router.register("certificates", CertificateViewSet, basename="lms-certificate")
router.register("reviews", ReviewViewSet, basename="lms-review")

urlpatterns = [
    path("", include(router.urls)),
]
