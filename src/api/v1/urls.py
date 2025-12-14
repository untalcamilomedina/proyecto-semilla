from __future__ import annotations

from django.urls import include, path, re_path
from rest_framework.routers import DefaultRouter

from .views import csrf
from .viewsets import (
    ApiKeyViewSet,
    InvoiceViewSet,
    MembershipViewSet,
    PermissionViewSet,
    PlanViewSet,
    RoleViewSet,
    SubscriptionViewSet,
    TenantViewSet,
)

router = DefaultRouter()
router.trailing_slash = "/?"
router.register("tenant", TenantViewSet, basename="tenant")
router.register("permissions", PermissionViewSet, basename="permissions")
router.register("roles", RoleViewSet, basename="roles")
router.register("memberships", MembershipViewSet, basename="memberships")
router.register("plans", PlanViewSet, basename="plans")
router.register("subscriptions", SubscriptionViewSet, basename="subscriptions")
router.register("invoices", InvoiceViewSet, basename="invoices")
router.register("api-keys", ApiKeyViewSet, basename="api-keys")

urlpatterns = [
    re_path(r"^csrf/?$", csrf, name="csrf"),
    path("", include(router.urls)),
]
