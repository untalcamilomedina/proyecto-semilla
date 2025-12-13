from __future__ import annotations

from decimal import Decimal

from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):
    initial = True

    dependencies = [
        ("multitenant", "0002_enabled_modules"),
    ]

    operations = [
        migrations.CreateModel(
            name="Plan",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("code", models.SlugField(max_length=50)),
                ("name", models.CharField(max_length=120)),
                ("description", models.TextField(blank=True, default="")),
                ("stripe_product_id", models.CharField(blank=True, default="", max_length=120)),
                ("is_active", models.BooleanField(default=True)),
                ("is_public", models.BooleanField(default=True)),
                ("seat_limit", models.PositiveIntegerField(blank=True, null=True)),
                ("trial_days", models.PositiveIntegerField(default=0)),
                ("roles_on_activation", models.JSONField(blank=True, default=list)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                (
                    "organization",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="plans",
                        to="multitenant.tenant",
                    ),
                ),
            ],
            options={
                "ordering": ["created_at"],
                "unique_together": {("organization", "code")},
            },
        ),
        migrations.CreateModel(
            name="Price",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("stripe_price_id", models.CharField(blank=True, default="", max_length=120)),
                ("currency", models.CharField(default="usd", max_length=10)),
                (
                    "amount",
                    models.DecimalField(decimal_places=2, default=Decimal("0.00"), max_digits=10),
                ),
                (
                    "interval",
                    models.CharField(
                        choices=[("month", "month"), ("year", "year"), ("one_time", "one_time")],
                        default="month",
                        max_length=10,
                    ),
                ),
                ("interval_count", models.PositiveIntegerField(default=1)),
                ("is_active", models.BooleanField(default=True)),
                (
                    "plan",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="prices",
                        to="billing.plan",
                    ),
                ),
            ],
            options={"ordering": ["amount"]},
        ),
        migrations.CreateModel(
            name="Subscription",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("stripe_customer_id", models.CharField(blank=True, default="", max_length=120)),
                ("stripe_subscription_id", models.CharField(blank=True, default="", max_length=120)),
                (
                    "status",
                    models.CharField(
                        choices=[
                            ("incomplete", "incomplete"),
                            ("trialing", "trialing"),
                            ("active", "active"),
                            ("past_due", "past_due"),
                            ("canceled", "canceled"),
                            ("unpaid", "unpaid"),
                            ("paused", "paused"),
                        ],
                        default="incomplete",
                        max_length=20,
                    ),
                ),
                ("quantity", models.PositiveIntegerField(default=1)),
                ("cancel_at_period_end", models.BooleanField(default=False)),
                ("current_period_end", models.DateTimeField(blank=True, null=True)),
                ("trial_end", models.DateTimeField(blank=True, null=True)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                (
                    "organization",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="subscriptions",
                        to="multitenant.tenant",
                    ),
                ),
                (
                    "plan",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.PROTECT,
                        related_name="subscriptions",
                        to="billing.plan",
                    ),
                ),
            ],
            options={"unique_together": {("organization", "stripe_subscription_id")}},
        ),
        migrations.CreateModel(
            name="Invoice",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("stripe_invoice_id", models.CharField(max_length=120, unique=True)),
                ("status", models.CharField(blank=True, default="", max_length=30)),
                (
                    "amount_paid",
                    models.DecimalField(decimal_places=2, default=Decimal("0.00"), max_digits=10),
                ),
                ("currency", models.CharField(default="usd", max_length=10)),
                ("hosted_invoice_url", models.URLField(blank=True, default="")),
                ("invoice_pdf", models.URLField(blank=True, default="")),
                ("created_at", models.DateTimeField(default=django.utils.timezone.now)),
                (
                    "organization",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="invoices",
                        to="multitenant.tenant",
                    ),
                ),
            ],
            options={"ordering": ["-created_at"]},
        ),
        migrations.CreateModel(
            name="StripeEvent",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("event_id", models.CharField(max_length=255, unique=True)),
                ("event_type", models.CharField(max_length=255)),
                ("payload", models.JSONField()),
                ("processed_at", models.DateTimeField(auto_now_add=True)),
            ],
            options={"ordering": ["-processed_at"]},
        ),
    ]

