from __future__ import annotations

from rest_framework import mixins, viewsets
from rest_framework.exceptions import NotFound
from rest_framework.permissions import IsAuthenticated

from .models import Course, Enrollment, Lesson, LessonProgress
from .serializers import (
    CourseSerializer,
    EnrollmentSerializer,
    LessonProgressSerializer,
    LessonSerializer,
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
    serializer_class = CourseSerializer

    def get_queryset(self):
        return Course.objects.filter(organization=self.get_organization())

    def perform_create(self, serializer):
        serializer.save(organization=self.get_organization())

    def perform_update(self, serializer):
        serializer.save(organization=self.get_organization())


class LessonViewSet(
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    mixins.CreateModelMixin,
    mixins.UpdateModelMixin,
    mixins.DestroyModelMixin,
    TenantScopedViewSet,
):
    serializer_class = LessonSerializer

    def get_queryset(self):
        return Lesson.objects.filter(organization=self.get_organization()).select_related("course")

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
        return Enrollment.objects.filter(organization=self.get_organization()).select_related(
            "course", "user"
        )

    def perform_create(self, serializer):
        serializer.save(organization=self.get_organization())


class LessonProgressViewSet(
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    mixins.CreateModelMixin,
    mixins.UpdateModelMixin,
    TenantScopedViewSet,
):
    serializer_class = LessonProgressSerializer

    def get_queryset(self):
        return LessonProgress.objects.filter(organization=self.get_organization()).select_related(
            "enrollment", "lesson"
        )

    def perform_create(self, serializer):
        serializer.save(organization=self.get_organization())

    def perform_update(self, serializer):
        serializer.save(organization=self.get_organization())
