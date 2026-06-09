# Renombra el metering específico del producto retirado a contadores genéricos.

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("billing", "0003_plan_max_diagrams_plan_max_requests_and_more"),
    ]

    operations = [
        migrations.RenameField(
            model_name="plan",
            old_name="max_diagrams",
            new_name="max_items",
        ),
        migrations.RenameField(
            model_name="subscription",
            old_name="diagrams_used",
            new_name="items_used",
        ),
        migrations.AlterField(
            model_name="plan",
            name="max_items",
            field=models.PositiveIntegerField(
                default=5,
                help_text="Cuota genérica de items almacenados (renombrar según el producto)",
            ),
        ),
        migrations.AlterField(
            model_name="plan",
            name="max_requests",
            field=models.PositiveIntegerField(default=10, help_text="Max API requests per month"),
        ),
    ]
