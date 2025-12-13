from __future__ import annotations

from django.contrib import messages
from django.shortcuts import redirect, render
from django.views import View
from django.views.generic import ListView

from core.models import Membership
from core.onboarding.forms import InviteMembersForm
from core.services.members import invite_members_to_org

from .mixins import TenantPermissionMixin


class MemberListView(TenantPermissionMixin, ListView):
    model = Membership
    template_name = "core/member_list.html"
    permission_codename = "core.invite_members"

    def get_queryset(self):
        return (
            Membership.objects.filter(organization=self.organization)
            .select_related("user", "role")
            .order_by("-joined_at")
        )

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["invite_form"] = InviteMembersForm()
        return ctx


class MemberInviteView(TenantPermissionMixin, View):
    permission_codename = "core.invite_members"

    def post(self, request):
        form = InviteMembersForm(request.POST)
        if not form.is_valid():
            queryset = (
                Membership.objects.filter(organization=self.organization)
                .select_related("user", "role")
                .order_by("-joined_at")
            )
            return render(
                request,
                "core/member_list.html",
                {"invite_form": form, "object_list": queryset, "organization": self.organization},
            )

        emails = form.cleaned_data["emails"]
        count = invite_members_to_org(self.organization, emails)
        messages.success(request, f"Invited {count} members.")
        return redirect("core:member_list")
