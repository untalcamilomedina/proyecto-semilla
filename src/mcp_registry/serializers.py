from __future__ import annotations

from rest_framework import serializers

from .models import McpResource, McpServer, McpTool, McpUsageLog


class McpServerSerializer(serializers.ModelSerializer):
    class Meta:
        model = McpServer
        fields = ["id", "name", "description", "endpoint_url", "api_key_hash", "is_active"]


class McpToolSerializer(serializers.ModelSerializer):
    class Meta:
        model = McpTool
        fields = ["id", "server", "name", "description", "input_schema"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        request = self.context.get("request")
        tenant = getattr(request, "tenant", None) if request else None
        if tenant is None:
            self.fields["server"].queryset = McpServer.objects.none()
        else:
            self.fields["server"].queryset = McpServer.objects.filter(organization=tenant)


class McpResourceSerializer(serializers.ModelSerializer):
    class Meta:
        model = McpResource
        fields = ["id", "server", "uri", "name", "description", "mime_type"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        request = self.context.get("request")
        tenant = getattr(request, "tenant", None) if request else None
        if tenant is None:
            self.fields["server"].queryset = McpServer.objects.none()
        else:
            self.fields["server"].queryset = McpServer.objects.filter(organization=tenant)


class McpUsageLogSerializer(serializers.ModelSerializer):
    class Meta:
        model = McpUsageLog
        fields = [
            "id",
            "server",
            "tool",
            "user",
            "request_data",
            "response_data",
            "created_at",
        ]
        read_only_fields = ["created_at"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        request = self.context.get("request")
        tenant = getattr(request, "tenant", None) if request else None
        if tenant is None:
            self.fields["server"].queryset = McpServer.objects.none()
            self.fields["tool"].queryset = McpTool.objects.none()
        else:
            self.fields["server"].queryset = McpServer.objects.filter(organization=tenant)
            self.fields["tool"].queryset = McpTool.objects.filter(organization=tenant)

    def validate(self, attrs):
        server = attrs.get("server") or getattr(self.instance, "server", None)
        tool = attrs.get("tool") or getattr(self.instance, "tool", None)
        if server and tool and tool.server_id != server.id:
            raise serializers.ValidationError({"tool": "Tool must belong to the selected server."})
        return attrs
