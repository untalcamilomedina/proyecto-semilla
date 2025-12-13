from __future__ import annotations

from django.db import migrations, models


class Migration(migrations.Migration):
    initial = True

    dependencies: list[tuple[str, str]] = []

    operations = [
        migrations.CreateModel(
            name="Tenant",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("name", models.CharField(max_length=150)),
                (
                    "slug",
                    models.SlugField(
                        help_text="Used as default subdomain.", max_length=63, unique=True
                    ),
                ),
                ("schema_name", models.CharField(max_length=63, unique=True)),
                ("is_active", models.BooleanField(default=True)),
                ("plan_code", models.CharField(blank=True, default="", max_length=50)),
                ("trial_ends_at", models.DateTimeField(blank=True, null=True)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
            ],
        ),
        migrations.CreateModel(
            name="Domain",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("domain", models.CharField(max_length=255, unique=True)),
                ("is_primary", models.BooleanField(default=False)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                (
                    "tenant",
                    models.ForeignKey(
                        on_delete=models.deletion.CASCADE, related_name="domains", to="multitenant.tenant"
                    ),
                ),
            ],
            options={
                "verbose_name": "Domain",
                "verbose_name_plural": "Domains",
            },
        ),
    ]

