from __future__ import annotations

from django.apps import AppConfig


class McpConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    # El paquete se llama mcp_registry para no eclipsar al SDK oficial `mcp`
    # (Model Context Protocol). El label se mantiene en "mcp": las migraciones,
    # FKs ("mcp.McpServer") y tablas existentes siguen siendo válidas.
    name = "mcp_registry"
    label = "mcp"
    verbose_name = "MCP Registry"
