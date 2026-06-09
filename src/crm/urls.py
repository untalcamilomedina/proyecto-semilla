"""CRM URL configuration."""

from __future__ import annotations

from django.urls import include, path
from rest_framework.routers import DefaultRouter

from crm.views import ActivityViewSet, CompanyViewSet, ContactViewSet, DealViewSet

router = DefaultRouter()
router.register("companies", CompanyViewSet, basename="crm-company")
router.register("contacts", ContactViewSet, basename="crm-contact")
router.register("deals", DealViewSet, basename="crm-deal")
router.register("activities", ActivityViewSet, basename="crm-activity")

urlpatterns = [
    path("", include(router.urls)),
]
