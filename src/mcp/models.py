from __future__ import annotations

from django.conf import settings
from django.db import models


class McpServer(models.Model):
    """
    Represents an external or internal MCP Server configuration.
    Stores connection details and metadata.
    """
    organization = models.ForeignKey(
        "multitenant.Tenant", on_delete=models.CASCADE, related_name="mcp_servers"
    )
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True, default="")
    endpoint_url = models.URLField()
    api_key_hash = models.CharField(max_length=128, blank=True, default="")
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ["name"]
        unique_together = [("organization", "name")]

    def __str__(self) -> str:  # pragma: no cover
        return f"{self.organization.slug}:{self.name}"


class McpTool(models.Model):
    """
    Represents a specific tool exposed by an MCP Server.
    Includes input schema definition.
    """
    organization = models.ForeignKey(
        "multitenant.Tenant", on_delete=models.CASCADE, related_name="mcp_tools"
    )
    server = models.ForeignKey(McpServer, on_delete=models.CASCADE, related_name="tools")
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True, default="")
    input_schema = models.JSONField(default=dict, blank=True)

    class Meta:
        ordering = ["name"]
        unique_together = [("server", "name")]

    def __str__(self) -> str:  # pragma: no cover
        return f"{self.server_id}:{self.name}"


class McpResource(models.Model):
    """
    Represents a data resource exposed by an MCP Server (e.g. file, database table).
    """
    organization = models.ForeignKey(
        "multitenant.Tenant", on_delete=models.CASCADE, related_name="mcp_resources"
    )
    server = models.ForeignKey(McpServer, on_delete=models.CASCADE, related_name="resources")
    uri = models.CharField(max_length=500)
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True, default="")
    mime_type = models.CharField(max_length=127, blank=True, default="")

    class Meta:
        ordering = ["name"]
        unique_together = [("server", "uri")]

    def __str__(self) -> str:  # pragma: no cover
        return self.uri


class McpUsageLog(models.Model):
    """
    Audit log for MCP Tool execution. 
    Tracks inputs and outputs for debugging and compliance.
    """
    organization = models.ForeignKey(
        "multitenant.Tenant", on_delete=models.CASCADE, related_name="mcp_usage_logs"
    )
    server = models.ForeignKey(McpServer, on_delete=models.CASCADE, related_name="usage_logs")
    tool = models.ForeignKey(McpTool, on_delete=models.CASCADE, related_name="usage_logs")
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="mcp_usage_logs",
    )
    request_data = models.JSONField(default=dict, blank=True)
    response_data = models.JSONField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self) -> str:  # pragma: no cover
        return f"{self.server_id}:{self.tool_id}:{self.user_id}:{self.created_at:%Y-%m-%d %H:%M:%S}"

