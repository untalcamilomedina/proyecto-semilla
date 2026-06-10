from __future__ import annotations

from rest_framework import mixins
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response

from common.api.permissions import IsTenantMember
from common.api.tenancy import TenantScopedViewSet

from .models import McpResource, McpServer, McpTool, McpUsageLog
from .serializers import (
    McpResourceSerializer,
    McpServerSerializer,
    McpToolSerializer,
    McpUsageLogSerializer,
)
from .tool_registry import get_tools_catalog


class McpServerViewSet(
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    mixins.CreateModelMixin,
    mixins.UpdateModelMixin,
    mixins.DestroyModelMixin,
    TenantScopedViewSet,
):
    """
    ViewSet for managing MCP Servers within a tenant.
    Allows CRUD operations on McpServer instances.
    """

    serializer_class = McpServerSerializer

    def get_queryset(self):
        return McpServer.objects.filter(organization=self.get_organization())

    def perform_create(self, serializer):
        serializer.save(organization=self.get_organization())

    def perform_update(self, serializer):
        serializer.save(organization=self.get_organization())


class McpToolViewSet(
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    mixins.CreateModelMixin,
    mixins.UpdateModelMixin,
    TenantScopedViewSet,
):
    """
    ViewSet for managing Tools associated with an MCP Server.
    """

    serializer_class = McpToolSerializer

    def get_queryset(self):
        return McpTool.objects.filter(organization=self.get_organization()).select_related("server")

    def perform_create(self, serializer):
        serializer.save(organization=self.get_organization())

    def perform_update(self, serializer):
        serializer.save(organization=self.get_organization())


class McpResourceViewSet(
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    mixins.CreateModelMixin,
    mixins.UpdateModelMixin,
    TenantScopedViewSet,
):
    """
    ViewSet for managing Resources exposed by an MCP Server.
    """

    serializer_class = McpResourceSerializer

    def get_queryset(self):
        return McpResource.objects.filter(organization=self.get_organization()).select_related(
            "server"
        )

    def perform_create(self, serializer):
        serializer.save(organization=self.get_organization())

    def perform_update(self, serializer):
        serializer.save(organization=self.get_organization())


class McpUsageLogViewSet(
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    mixins.CreateModelMixin,
    TenantScopedViewSet,
):
    """
    ViewSet for tracking usage logs of MCP Tools.
    ReadOnly for most users, but allows creation for logging purposes.
    """

    serializer_class = McpUsageLogSerializer

    def get_queryset(self):
        return McpUsageLog.objects.filter(organization=self.get_organization()).select_related(
            "server", "tool", "user"
        )

    def perform_create(self, serializer):
        serializer.save(organization=self.get_organization())


# ── MCP Protocol Endpoint ────────────────────────────────────


@api_view(["GET"])
@permission_classes([IsTenantMember])
def tool_catalog_view(request):
    """
    Return all auto-discovered API tools in MCP protocol format.

    This endpoint introspects the DRF router and returns tool definitions
    that AI agents can use to understand available API capabilities.

    Response format:
    {
        "tools": [
            {
                "name": "courses_list",
                "description": "List all courses",
                "inputSchema": { "type": "object", "properties": {...} }
            },
            ...
        ]
    }
    """
    tools = get_tools_catalog()
    return Response(
        {
            "tools": tools,
            "count": len(tools),
            "version": "1.0",
        }
    )
