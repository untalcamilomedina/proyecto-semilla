from __future__ import annotations

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    dependencies = [
        ("core", "0002_rbac_models"),
        ("multitenant", "0002_enabled_modules"),
    ]

    operations = [
        migrations.CreateModel(
            name="OnboardingState",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("owner_email", models.EmailField(max_length=254)),
                ("current_step", models.PositiveSmallIntegerField(default=1)),
                ("completed_steps", models.JSONField(blank=True, default=list)),
                ("data", models.JSONField(blank=True, default=dict)),
                ("is_complete", models.BooleanField(default=False)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                (
                    "tenant",
                    models.OneToOneField(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="onboarding_state",
                        to="multitenant.tenant",
                    ),
                ),
            ],
        ),
    ]

