from __future__ import annotations

from django.contrib import admin

from .models import Activity, Company, Contact, Deal


@admin.register(Company)
class CompanyAdmin(admin.ModelAdmin):
    list_display = ("name", "organization", "industry", "owner", "created_at")
    list_filter = ("industry",)
    search_fields = ("name", "domain")


@admin.register(Contact)
class ContactAdmin(admin.ModelAdmin):
    list_display = ("first_name", "last_name", "email", "status", "company", "organization")
    list_filter = ("status",)
    search_fields = ("first_name", "last_name", "email")


@admin.register(Deal)
class DealAdmin(admin.ModelAdmin):
    list_display = ("name", "stage", "amount", "currency", "organization", "owner")
    list_filter = ("stage", "currency")
    search_fields = ("name",)


@admin.register(Activity)
class ActivityAdmin(admin.ModelAdmin):
    list_display = ("kind", "subject", "contact", "deal", "organization", "created_at")
    list_filter = ("kind",)
    search_fields = ("subject",)
