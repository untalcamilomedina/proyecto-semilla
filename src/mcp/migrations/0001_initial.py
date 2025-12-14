from __future__ import annotations

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    initial = True

    dependencies = [
        ("multitenant", "0003_branding"),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name="McpServer",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("name", models.CharField(max_length=200)),
                ("description", models.TextField(blank=True, default="")),
                ("endpoint_url", models.URLField()),
                ("api_key_hash", models.CharField(blank=True, default="", max_length=128)),
                ("is_active", models.BooleanField(default=True)),
                (
                    "organization",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="mcp_servers",
                        to="multitenant.tenant",
                    ),
                ),
            ],
            options={
                "ordering": ["name"],
                "unique_together": {("organization", "name")},
            },
        ),
        migrations.CreateModel(
            name="McpTool",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("name", models.CharField(max_length=200)),
                ("description", models.TextField(blank=True, default="")),
                ("input_schema", models.JSONField(blank=True, default=dict)),
                (
                    "organization",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="mcp_tools",
                        to="multitenant.tenant",
                    ),
                ),
                (
                    "server",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE, related_name="tools", to="mcp.mcpserver"
                    ),
                ),
            ],
            options={
                "ordering": ["name"],
                "unique_together": {("server", "name")},
            },
        ),
        migrations.CreateModel(
            name="McpResource",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("uri", models.CharField(max_length=500)),
                ("name", models.CharField(max_length=200)),
                ("description", models.TextField(blank=True, default="")),
                ("mime_type", models.CharField(blank=True, default="", max_length=127)),
                (
                    "organization",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="mcp_resources",
                        to="multitenant.tenant",
                    ),
                ),
                (
                    "server",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="resources",
                        to="mcp.mcpserver",
                    ),
                ),
            ],
            options={
                "ordering": ["name"],
                "unique_together": {("server", "uri")},
            },
        ),
        migrations.CreateModel(
            name="McpUsageLog",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("request_data", models.JSONField(blank=True, default=dict)),
                ("response_data", models.JSONField(blank=True, null=True)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                (
                    "organization",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="mcp_usage_logs",
                        to="multitenant.tenant",
                    ),
                ),
                (
                    "server",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="usage_logs",
                        to="mcp.mcpserver",
                    ),
                ),
                (
                    "tool",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="usage_logs",
                        to="mcp.mcptool",
                    ),
                ),
                (
                    "user",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="mcp_usage_logs",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
            options={
                "ordering": ["-created_at"],
            },
        ),
    ]

