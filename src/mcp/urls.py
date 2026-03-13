from __future__ import annotations

from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import McpResourceViewSet, McpServerViewSet, McpToolViewSet, McpUsageLogViewSet, tool_catalog_view

router = DefaultRouter()
router.trailing_slash = "/?"
router.register("servers", McpServerViewSet, basename="servers")
router.register("tools", McpToolViewSet, basename="tools")
router.register("resources", McpResourceViewSet, basename="resources")
router.register("usage-logs", McpUsageLogViewSet, basename="usage-logs")

urlpatterns = [
    path("catalog/", tool_catalog_view, name="tool-catalog"),
    path("", include(router.urls)),
]
