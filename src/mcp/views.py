from __future__ import annotations

from rest_framework import mixins, viewsets
from rest_framework.exceptions import NotFound
from rest_framework.permissions import IsAuthenticated

from .models import McpResource, McpServer, McpTool, McpUsageLog
from .serializers import (
    McpResourceSerializer,
    McpServerSerializer,
    McpToolSerializer,
    McpUsageLogSerializer,
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
        return McpResource.objects.filter(organization=self.get_organization()).select_related("server")

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
