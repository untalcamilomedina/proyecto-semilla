from __future__ import annotations

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("multitenant", "0002_enabled_modules"),
    ]

    operations = [
        migrations.AddField(
            model_name="tenant",
            name="branding",
            field=models.JSONField(blank=True, default=dict),
        ),
    ]

