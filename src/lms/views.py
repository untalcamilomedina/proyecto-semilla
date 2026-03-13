"""LMS viewsets for course management API."""

from __future__ import annotations

from django.utils import timezone
from rest_framework import mixins, viewsets
from rest_framework.decorators import action
from rest_framework.exceptions import NotFound
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from .models import Certificate, Course, Enrollment, Lesson, LessonProgress, Review, Section
from .serializers import (
    CertificateSerializer,
    CourseDetailSerializer,
    CourseListSerializer,
    EnrollmentSerializer,
    LessonListSerializer,
    LessonProgressSerializer,
    LessonSerializer,
    ReviewSerializer,
    SectionSerializer,
)


def request_tenant(request):
    return getattr(request, "tenant", None)


class TenantScopedViewSet(viewsets.GenericViewSet):
    permission_classes = [IsAuthenticated]

    def get_organization(self):
        organization = request_tenant(self.request)
        if organization is None:
            raise NotFound("Tenant required.")
        return organization


class CourseViewSet(
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    mixins.CreateModelMixin,
    mixins.UpdateModelMixin,
    mixins.DestroyModelMixin,
    TenantScopedViewSet,
):
    filterset_fields = ["status", "pricing_type", "level", "is_featured"]
    search_fields = ["title", "description"]

    def get_serializer_class(self):
        if self.action == "list":
            return CourseListSerializer
        return CourseDetailSerializer

    def get_queryset(self):
        return (
            Course.objects.filter(organization=self.get_organization())
            .select_related("instructor")
            .prefetch_related("sections")
        )

    def perform_create(self, serializer):
        serializer.save(
            organization=self.get_organization(),
            instructor=self.request.user,
        )

    def perform_update(self, serializer):
        serializer.save(organization=self.get_organization())


class SectionViewSet(
    mixins.ListModelMixin,
    mixins.CreateModelMixin,
    mixins.UpdateModelMixin,
    mixins.DestroyModelMixin,
    TenantScopedViewSet,
):
    serializer_class = SectionSerializer

    def get_queryset(self):
        return Section.objects.filter(organization=self.get_organization()).select_related("course")

    def perform_create(self, serializer):
        serializer.save(organization=self.get_organization())


class LessonViewSet(
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    mixins.CreateModelMixin,
    mixins.UpdateModelMixin,
    mixins.DestroyModelMixin,
    TenantScopedViewSet,
):
    def get_serializer_class(self):
        if self.action == "list":
            return LessonListSerializer
        return LessonSerializer

    def get_queryset(self):
        return (
            Lesson.objects.filter(organization=self.get_organization())
            .select_related("course", "section")
        )

    def perform_create(self, serializer):
        serializer.save(organization=self.get_organization())

    def perform_update(self, serializer):
        serializer.save(organization=self.get_organization())


class EnrollmentViewSet(
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    mixins.CreateModelMixin,
    TenantScopedViewSet,
):
    serializer_class = EnrollmentSerializer

    def get_queryset(self):
        return (
            Enrollment.objects.filter(organization=self.get_organization())
            .select_related("course", "user")
        )

    def perform_create(self, serializer):
        serializer.save(organization=self.get_organization())

    @action(detail=True, methods=["post"], url_path="complete")
    def mark_complete(self, request, pk=None):
        """Mark enrollment as completed and auto-generate certificate number."""
        enrollment = self.get_object()
        enrollment.status = Enrollment.Status.COMPLETED
        enrollment.progress = 100
        enrollment.completed_at = timezone.now()
        enrollment.save(update_fields=["status", "progress", "completed_at"])

        # Auto-generate certificate
        import secrets

        cert_number = f"CERT-{secrets.token_hex(6).upper()}"
        cert, created = Certificate.objects.get_or_create(
            organization=self.get_organization(),
            enrollment=enrollment,
            defaults={"certificate_number": cert_number},
        )

        return Response({
            "status": "completed",
            "certificate_number": cert.certificate_number,
        })


class LessonProgressViewSet(
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    mixins.CreateModelMixin,
    mixins.UpdateModelMixin,
    TenantScopedViewSet,
):
    serializer_class = LessonProgressSerializer

    def get_queryset(self):
        return (
            LessonProgress.objects.filter(organization=self.get_organization())
            .select_related("enrollment", "lesson")
        )

    def perform_create(self, serializer):
        serializer.save(organization=self.get_organization())

    def perform_update(self, serializer):
        serializer.save(organization=self.get_organization())


class CertificateViewSet(
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    TenantScopedViewSet,
):
    serializer_class = CertificateSerializer

    def get_queryset(self):
        return (
            Certificate.objects.filter(organization=self.get_organization())
            .select_related("enrollment__course", "enrollment__user")
        )


class ReviewViewSet(
    mixins.ListModelMixin,
    mixins.CreateModelMixin,
    mixins.UpdateModelMixin,
    mixins.DestroyModelMixin,
    TenantScopedViewSet,
):
    serializer_class = ReviewSerializer
    filterset_fields = ["course", "rating"]

    def get_queryset(self):
        return (
            Review.objects.filter(organization=self.get_organization())
            .select_related("user", "course")
        )

    def perform_create(self, serializer):
        serializer.save(
            organization=self.get_organization(),
            user=self.request.user,
        )
