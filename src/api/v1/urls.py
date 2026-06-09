from __future__ import annotations

from django.urls import include, path, re_path
from rest_framework.routers import DefaultRouter

from config.settings.plugins import optional_api_urls
from core.api.dashboard import DashboardViewSet
from core.api.onboarding import OnboardingViewSet

from .views import csrf, login_view, logout_view, signup_view
from .viewsets import (
    ActivityLogViewSet,
    ApiKeyViewSet,
    InvoiceViewSet,
    MembershipViewSet,
    PermissionViewSet,
    PlanViewSet,
    ProfileViewSet,
    RoleViewSet,
    SubscriptionViewSet,
    TenantViewSet,
)

router = DefaultRouter()
router.trailing_slash = "/?"
router.register("onboarding", OnboardingViewSet, basename="onboarding")
router.register("dashboard", DashboardViewSet, basename="dashboard")
router.register("profile", ProfileViewSet, basename="profile")
router.register("tenant", TenantViewSet, basename="tenant")
router.register("activity-logs", ActivityLogViewSet, basename="activity-logs")
router.register("permissions", PermissionViewSet, basename="permissions")
router.register("roles", RoleViewSet, basename="roles")
router.register("memberships", MembershipViewSet, basename="memberships")
router.register("plans", PlanViewSet, basename="plans")
router.register("subscriptions", SubscriptionViewSet, basename="subscriptions")
router.register("invoices", InvoiceViewSet, basename="invoices")
router.register("api-keys", ApiKeyViewSet, basename="api-keys")

from rest_framework_simplejwt.views import (  # noqa: E402
    TokenObtainPairView,
    TokenRefreshView,
    TokenVerifyView,
)

urlpatterns = [
    # JWT Authentication (stateless)
    re_path(r"^auth/token/?$", TokenObtainPairView.as_view(), name="token_obtain_pair"),
    re_path(r"^auth/token/refresh/?$", TokenRefreshView.as_view(), name="token_refresh"),
    re_path(r"^auth/token/verify/?$", TokenVerifyView.as_view(), name="token_verify"),
    # Legacy session auth (kept for backward compatibility)
    re_path(r"^csrf/?$", csrf, name="csrf"),
    re_path(
        r"^me/?$", ProfileViewSet.as_view({"get": "retrieve", "patch": "partial_update"}), name="me"
    ),
    re_path(
        r"^tenant/?$",
        TenantViewSet.as_view({"get": "retrieve", "patch": "partial_update"}),
        name="tenant-current",
    ),
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
