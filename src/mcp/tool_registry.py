"""MCP Tool Registry — auto-discovers DRF endpoints as MCP tools.

Introspects the DRF router to generate tool definitions that follow
the Model Context Protocol specification. Each ViewSet action becomes
an MCP tool with auto-generated input schemas from serializer fields.

Usage:
    from mcp.tool_registry import discover_tools, execute_tool
    tools = discover_tools()
    result = execute_tool("courses_list", {}, request)
"""

from __future__ import annotations

import logging
from typing import Any

from django.urls import URLPattern, URLResolver
from rest_framework.routers import DefaultRouter
from rest_framework.serializers import Serializer
from rest_framework.viewsets import ViewSetMixin

logger = logging.getLogger(__name__)


# ── Tool Definition ──────────────────────────────────────────

class ToolDefinition:
    """MCP-compatible tool definition."""

    def __init__(
        self,
        name: str,
        description: str,
        input_schema: dict[str, Any],
        endpoint: str,
        method: str,
        viewset_class: type | None = None,
        action: str = "",
    ):
        self.name = name
        self.description = description
        self.input_schema = input_schema
        self.endpoint = endpoint
        self.method = method
        self.viewset_class = viewset_class
        self.action = action

    def to_mcp_format(self) -> dict[str, Any]:
        """Convert to MCP protocol tool format."""
        return {
            "name": self.name,
            "description": self.description,
            "inputSchema": {
                "type": "object",
                "properties": self.input_schema.get("properties", {}),
                "required": self.input_schema.get("required", []),
            },
        }


# ── Schema Extraction ────────────────────────────────────────

FIELD_TYPE_MAP = {
    "IntegerField": "integer",
    "FloatField": "number",
    "DecimalField": "number",
    "BooleanField": "boolean",
    "CharField": "string",
    "TextField": "string",
    "EmailField": "string",
    "URLField": "string",
    "SlugField": "string",
    "UUIDField": "string",
    "DateField": "string",
    "DateTimeField": "string",
    "ChoiceField": "string",
    "JSONField": "object",
    "ListField": "array",
    "PrimaryKeyRelatedField": "integer",
    "ManyRelatedField": "array",
}


def serializer_to_json_schema(serializer_class: type[Serializer]) -> dict[str, Any]:
    """Convert a DRF Serializer to JSON Schema for MCP input_schema."""
    try:
        serializer = serializer_class()
    except Exception:
        return {"type": "object", "properties": {}}

    properties = {}
    required = []

    for field_name, field in serializer.fields.items():
        if field.read_only:
            continue

        field_type_name = type(field).__name__
        json_type = FIELD_TYPE_MAP.get(field_type_name, "string")

        prop: dict[str, Any] = {"type": json_type}

        if hasattr(field, "help_text") and field.help_text:
            prop["description"] = str(field.help_text)

        if hasattr(field, "max_length") and field.max_length:
            prop["maxLength"] = field.max_length

        if hasattr(field, "choices") and field.choices:
            prop["enum"] = [str(k) for k in field.choices.keys()]

        properties[field_name] = prop

        if field.required:
            required.append(field_name)

    return {
        "type": "object",
        "properties": properties,
        "required": required,
    }


# ── Tool Discovery ───────────────────────────────────────────

ACTION_METHOD_MAP = {
    "list": "GET",
    "retrieve": "GET",
    "create": "POST",
    "update": "PUT",
    "partial_update": "PATCH",
    "destroy": "DELETE",
}


def discover_tools(router: DefaultRouter | None = None) -> list[ToolDefinition]:
    """
    Discover all DRF ViewSet actions and convert them to MCP tools.

    If no router is provided, uses the main API v1 router.
    """
    if router is None:
        try:
            from api.v1.urls import router as api_router
            router = api_router
        except ImportError:
            logger.warning("Could not import API v1 router")
            return []

    tools = []

    for prefix, viewset_class, basename in router.registry:
        # Get the serializer class for schema extraction
        serializer_class = getattr(viewset_class, "serializer_class", None)
        input_schema = (
            serializer_to_json_schema(serializer_class) if serializer_class else {"type": "object", "properties": {}}
        )

        # Standard CRUD actions
        for action, method in ACTION_METHOD_MAP.items():
            if not _viewset_has_action(viewset_class, action):
                continue

            tool_name = f"{basename}_{action}"
            description = _generate_description(basename, action, viewset_class)

            # For retrieve/update/destroy, add 'id' parameter
            action_schema = dict(input_schema)
            if action in ("retrieve", "update", "partial_update", "destroy"):
                action_schema = {
                    "type": "object",
                    "properties": {
                        "id": {"type": "integer", "description": f"ID of the {basename} to {action}"},
                        **(input_schema.get("properties", {}) if action != "destroy" else {}),
                    },
                    "required": ["id"],
                }
            elif action == "list":
                action_schema = {
                    "type": "object",
                    "properties": {
                        "page": {"type": "integer", "description": "Page number", "default": 1},
                        "page_size": {"type": "integer", "description": "Results per page", "default": 50},
                    },
                }

            tools.append(
                ToolDefinition(
                    name=tool_name,
                    description=description,
                    input_schema=action_schema,
                    endpoint=f"/api/v1/{prefix}/",
                    method=method,
                    viewset_class=viewset_class,
                    action=action,
                )
            )

        # Custom @action methods
        for attr_name in dir(viewset_class):
            attr = getattr(viewset_class, attr_name, None)
            if callable(attr) and hasattr(attr, "mapping"):
                tool_name = f"{basename}_{attr_name}"
                tools.append(
                    ToolDefinition(
                        name=tool_name,
                        description=f"Custom action '{attr_name}' on {basename}",
                        input_schema={"type": "object", "properties": {}},
                        endpoint=f"/api/v1/{prefix}/{attr_name}/",
                        method=list(attr.mapping.keys())[0].upper() if attr.mapping else "POST",
                        viewset_class=viewset_class,
                        action=attr_name,
                    )
                )

    return tools


def _viewset_has_action(viewset_class: type, action: str) -> bool:
    """Check if a ViewSet supports a given action."""
    mixin_actions = {
        "list": "list",
        "retrieve": "retrieve",
        "create": "create",
        "update": "update",
        "partial_update": "partial_update",
        "destroy": "destroy",
    }
    return hasattr(viewset_class, mixin_actions.get(action, action))


def _generate_description(basename: str, action: str, viewset_class: type) -> str:
    """Generate a human-readable description for a tool."""
    action_descriptions = {
        "list": f"List all {basename}",
        "retrieve": f"Get details of a specific {basename}",
        "create": f"Create a new {basename}",
        "update": f"Fully update a {basename}",
        "partial_update": f"Partially update a {basename}",
        "destroy": f"Delete a {basename}",
    }
    base = action_descriptions.get(action, f"{action} on {basename}")

    # Add docstring context if available
    doc = getattr(viewset_class, "__doc__", None)
    if doc:
        first_line = doc.strip().split("\n")[0].strip()
        if first_line:
            base += f". {first_line}"

    return base


# ── Tool Listing Endpoint Helper ─────────────────────────────

def get_tools_catalog() -> list[dict[str, Any]]:
    """Return all discovered tools in MCP protocol format."""
    return [tool.to_mcp_format() for tool in discover_tools()]
