from __future__ import annotations

from django.urls import include, path, re_path
from rest_framework.routers import DefaultRouter

from config.settings.plugins import optional_api_urls

from .views import csrf, me, login_view, logout_view, signup_view
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
    re_path(r"^me/?$", me, name="me"),
    re_path(r"^login/?$", login_view, name="login"),
    re_path(r"^logout/?$", logout_view, name="logout"),
    re_path(r"^signup/?$", signup_view, name="signup"),
    path("", include(router.urls)),
]

for prefix, module in optional_api_urls():
    try:
        urlpatterns.append(path(prefix, include(module)))
    except ImportError as exc:
        if getattr(exc, "name", None) in {module.split(".")[0], module}:
            continue
        raise
