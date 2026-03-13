"""CMS viewsets for MDX content management API."""

from __future__ import annotations

from rest_framework import viewsets, permissions, parsers, status
from rest_framework.response import Response
from django.utils import timezone

from cms.models import Category, ContentPage, MediaAsset
from cms.serializers import (
    CategorySerializer,
    ContentPageDetailSerializer,
    ContentPageListSerializer,
    MediaAssetSerializer,
)


class TenantScopedMixin:
    """Mixin to scope querysets to the current tenant."""

    def get_queryset(self):
        qs = super().get_queryset()
        tenant = getattr(self.request, "tenant", None)
        if tenant:
            return qs.filter(organization=tenant)
        return qs.none()

    def perform_create(self, serializer):
        tenant = getattr(self.request, "tenant", None)
        extra = {"organization": tenant}
        if hasattr(serializer.Meta.model, "author"):
            extra["author"] = self.request.user
        if hasattr(serializer.Meta.model, "uploaded_by"):
            extra["uploaded_by"] = self.request.user
        serializer.save(**extra)


class CategoryViewSet(TenantScopedMixin, viewsets.ModelViewSet):
    """CRUD for content categories."""
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [permissions.IsAuthenticated]
    search_fields = ["name"]
    filterset_fields = ["parent"]


class ContentPageViewSet(TenantScopedMixin, viewsets.ModelViewSet):
    """CRUD for MDX content pages.

    Uses lightweight serializer for list, full serializer for detail/create/update.
    """
    queryset = ContentPage.objects.select_related("author", "category").all()
    permission_classes = [permissions.IsAuthenticated]
    search_fields = ["title", "excerpt"]
    filterset_fields = ["status", "category", "is_featured"]

    def get_serializer_class(self):
        if self.action == "list":
            return ContentPageListSerializer
        return ContentPageDetailSerializer

    def perform_create(self, serializer):
        tenant = getattr(self.request, "tenant", None)
        extra = {"organization": tenant, "author": self.request.user}
        if serializer.validated_data.get("status") == ContentPage.Status.PUBLISHED:
            extra["published_at"] = timezone.now()
        serializer.save(**extra)

    def perform_update(self, serializer):
        instance = self.get_object()
        new_status = serializer.validated_data.get("status")
        extra = {}
        if new_status == ContentPage.Status.PUBLISHED and not instance.published_at:
            extra["published_at"] = timezone.now()
        serializer.save(**extra)


class MediaAssetViewSet(TenantScopedMixin, viewsets.ModelViewSet):
    """CRUD for media assets with file upload support."""
    queryset = MediaAsset.objects.all()
    serializer_class = MediaAssetSerializer
    permission_classes = [permissions.IsAuthenticated]
    parser_classes = [parsers.MultiPartParser, parsers.FormParser]

    def perform_create(self, serializer):
        tenant = getattr(self.request, "tenant", None)
        uploaded_file = self.request.FILES.get("file")
        extra = {
            "organization": tenant,
            "uploaded_by": self.request.user,
        }
        if uploaded_file:
            extra["filename"] = uploaded_file.name
            extra["mime_type"] = uploaded_file.content_type or ""
            extra["size_bytes"] = uploaded_file.size
        serializer.save(**extra)
