from __future__ import annotations

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    dependencies = [
        ("core", "0001_initial"),
        ("multitenant", "0001_initial"),
    ]

    operations = [
        migrations.CreateModel(
            name="Permission",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("module", models.CharField(max_length=50)),
                ("codename", models.SlugField(max_length=120, unique=True)),
                ("name", models.CharField(max_length=150)),
                ("description", models.TextField(blank=True, default="")),
                ("is_system", models.BooleanField(default=False)),
            ],
            options={"ordering": ["module", "codename"]},
        ),
        migrations.CreateModel(
            name="Role",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("name", models.CharField(max_length=80)),
                ("slug", models.SlugField(max_length=80)),
                ("description", models.TextField(blank=True, default="")),
                ("position", models.PositiveIntegerField(default=0)),
                ("is_system", models.BooleanField(default=False)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                (
                    "organization",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="roles",
                        to="multitenant.tenant",
                    ),
                ),
            ],
            options={
                "ordering": ["-position", "name"],
                "unique_together": {("organization", "slug")},
            },
        ),
        migrations.CreateModel(
            name="RolePermission",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                (
                    "permission",
                    models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to="core.permission"),
                ),
                (
                    "role",
                    models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to="core.role"),
                ),
            ],
            options={"unique_together": {("role", "permission")}},
        ),
        migrations.AddField(
            model_name="role",
            name="permissions",
            field=models.ManyToManyField(related_name="roles", through="core.RolePermission", to="core.permission"),
        ),
        migrations.CreateModel(
            name="Membership",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("is_active", models.BooleanField(default=True)),
                ("joined_at", models.DateTimeField(auto_now_add=True)),
                (
                    "organization",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="memberships",
                        to="multitenant.tenant",
                    ),
                ),
                (
                    "role",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.PROTECT,
                        related_name="memberships",
                        to="core.role",
                    ),
                ),
                (
                    "user",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="memberships",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
            options={"unique_together": {("user", "organization")}},
        ),
        migrations.CreateModel(
            name="RoleAuditLog",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("action", models.CharField(choices=[("created", "created"), ("updated", "updated"), ("deleted", "deleted"), ("perms_changed", "perms_changed"), ("imported", "imported")], max_length=20)),
                ("before", models.JSONField(blank=True, null=True)),
                ("after", models.JSONField(blank=True, null=True)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                (
                    "actor",
                    models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL),
                ),
                (
                    "organization",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="role_audits",
                        to="multitenant.tenant",
                    ),
                ),
                (
                    "role",
                    models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to="core.role"),
                ),
            ],
        ),
    ]

