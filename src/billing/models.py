from __future__ import annotations

from decimal import Decimal

from django.db import models
from django.utils import timezone


class Plan(models.Model):
    organization = models.ForeignKey(
        "multitenant.Tenant", on_delete=models.CASCADE, related_name="plans"
    )
    code = models.SlugField(max_length=50)
    name = models.CharField(max_length=120)
    description = models.TextField(blank=True, default="")
    stripe_product_id = models.CharField(max_length=120, blank=True, default="")
    is_active = models.BooleanField(default=True)
    is_public = models.BooleanField(default=True)
    seat_limit = models.PositiveIntegerField(blank=True, null=True)
    max_diagrams = models.PositiveIntegerField(default=5, help_text="Max stored diagrams")
    max_requests = models.PositiveIntegerField(default=10, help_text="Max integration requests per month")
    trial_days = models.PositiveIntegerField(default=0)
    roles_on_activation = models.JSONField(default=list, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = [("organization", "code")]
        ordering = ["created_at"]

    def __str__(self) -> str:  # pragma: no cover
        return f"{self.organization.slug}:{self.code}"


class Price(models.Model):
    INTERVAL_CHOICES = [
        ("month", "month"),
        ("year", "year"),
        ("one_time", "one_time"),
    ]

    plan = models.ForeignKey(Plan, on_delete=models.CASCADE, related_name="prices")
    stripe_price_id = models.CharField(max_length=120, blank=True, default="")
    currency = models.CharField(max_length=10, default="usd")
    amount = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal("0.00"))
    interval = models.CharField(max_length=10, choices=INTERVAL_CHOICES, default="month")
    interval_count = models.PositiveIntegerField(default=1)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ["amount"]

    def __str__(self) -> str:  # pragma: no cover
        return f"{self.plan.code}:{self.amount}{self.currency}/{self.interval}"


class Subscription(models.Model):
    STATUS_CHOICES = [
        ("incomplete", "incomplete"),
        ("trialing", "trialing"),
        ("active", "active"),
        ("past_due", "past_due"),
        ("canceled", "canceled"),
        ("unpaid", "unpaid"),
        ("paused", "paused"),
    ]

    organization = models.ForeignKey(
        "multitenant.Tenant", on_delete=models.CASCADE, related_name="subscriptions"
    )
    plan = models.ForeignKey(Plan, on_delete=models.PROTECT, related_name="subscriptions")
    stripe_customer_id = models.CharField(max_length=120, blank=True, default="")
    stripe_subscription_id = models.CharField(max_length=120, blank=True, default="")
    djstripe_subscription = models.ForeignKey(
        "djstripe.Subscription",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="tenant_subscriptions",
    )
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="incomplete")
    quantity = models.PositiveIntegerField(default=1)
    
    # Usage Metering
    diagrams_used = models.PositiveIntegerField(default=0)
    requests_used = models.PositiveIntegerField(default=0)
    usage_reset_at = models.DateTimeField(blank=True, null=True)

    cancel_at_period_end = models.BooleanField(default=False)
    current_period_end = models.DateTimeField(blank=True, null=True)
    trial_end = models.DateTimeField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = [("organization", "stripe_subscription_id")]

    @property
    def is_active(self) -> bool:
        return self.status in {"trialing", "active"}

    def is_over_seat_limit(self) -> bool:
        if self.plan.seat_limit is None:
            return False
        return self.quantity > self.plan.seat_limit

    def __str__(self) -> str:  # pragma: no cover
        return f"{self.organization.slug}:{self.status}"


class Invoice(models.Model):
    organization = models.ForeignKey(
        "multitenant.Tenant", on_delete=models.CASCADE, related_name="invoices"
    )
    stripe_invoice_id = models.CharField(max_length=120, unique=True)
    status = models.CharField(max_length=30, blank=True, default="")
    amount_paid = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal("0.00"))
    currency = models.CharField(max_length=10, default="usd")
    hosted_invoice_url = models.URLField(blank=True, default="")
    invoice_pdf = models.URLField(blank=True, default="")
    created_at = models.DateTimeField(default=timezone.now)

    class Meta:
        ordering = ["-created_at"]


class StripeEvent(models.Model):
    event_id = models.CharField(max_length=255, unique=True)
    event_type = models.CharField(max_length=255)
    payload = models.JSONField()
    processed_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-processed_at"]

