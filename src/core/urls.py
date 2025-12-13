from __future__ import annotations

from django.urls import include, path

from .views.dashboard import DashboardView
from .views.members import MemberInviteView, MemberListView
from .views.roles import (
    RoleCreateView,
    RoleDeleteView,
    RoleExportView,
    RoleImportView,
    RoleListView,
    RoleUpdateView,
)

app_name = "core"

urlpatterns = [
    path("onboarding/", include("core.onboarding.urls")),
    path("", DashboardView.as_view(), name="dashboard"),
    path("members/", MemberListView.as_view(), name="member_list"),
    path("members/invite/", MemberInviteView.as_view(), name="member_invite"),
    path("roles/", RoleListView.as_view(), name="role_list"),
    path("roles/new/", RoleCreateView.as_view(), name="role_create"),
    path("roles/import/", RoleImportView.as_view(), name="role_import"),
    path("roles/<int:pk>/edit/", RoleUpdateView.as_view(), name="role_update"),
    path("roles/<int:pk>/delete/", RoleDeleteView.as_view(), name="role_delete"),
    path("roles/<int:pk>/export/", RoleExportView.as_view(), name="role_export"),
]
