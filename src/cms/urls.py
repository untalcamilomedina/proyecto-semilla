"""CMS URL configuration."""

from __future__ import annotations

from django.urls import include, path
from rest_framework.routers import DefaultRouter

from cms.views import CategoryViewSet, ContentPageViewSet, MediaAssetViewSet

router = DefaultRouter()
router.register("categories", CategoryViewSet, basename="cms-category")
router.register("pages", ContentPageViewSet, basename="cms-page")
router.register("media", MediaAssetViewSet, basename="cms-media")

urlpatterns = [
    path("", include(router.urls)),
]
