from __future__ import annotations

from django.contrib import admin

from .models import Invoice, Plan, Price, StripeEvent, Subscription


@admin.register(Plan)
class PlanAdmin(admin.ModelAdmin):
    list_display = ("organization", "code", "name", "seat_limit", "trial_days", "is_active")
    list_filter = ("organization", "is_active", "is_public")
    search_fields = ("code", "name")


@admin.register(Price)
class PriceAdmin(admin.ModelAdmin):
    list_display = ("plan", "amount", "currency", "interval", "is_active")
    list_filter = ("interval", "is_active")


@admin.register(Subscription)
class SubscriptionAdmin(admin.ModelAdmin):
    list_display = ("organization", "plan", "status", "quantity", "current_period_end")
    list_filter = ("status", "plan")
    search_fields = ("stripe_customer_id", "stripe_subscription_id")


@admin.register(Invoice)
class InvoiceAdmin(admin.ModelAdmin):
    list_display = ("organization", "stripe_invoice_id", "status", "amount_paid", "created_at")
    list_filter = ("status",)


@admin.register(StripeEvent)
class StripeEventAdmin(admin.ModelAdmin):
    list_display = ("event_id", "event_type", "processed_at")
    search_fields = ("event_id", "event_type")

