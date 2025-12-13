from __future__ import annotations

from django.contrib import messages
from django.http import HttpRequest, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse, reverse_lazy
from django.utils.text import slugify
from django.views import View
from django.views.generic import CreateView, DeleteView, ListView, UpdateView

from ..forms import RoleForm, RoleImportForm, RolePermissionsForm
from ..models import Permission, Role, RoleAuditLog
from .mixins import TenantPermissionMixin


class RoleListView(TenantPermissionMixin, ListView):
    model = Role
    template_name = "core/role_list.html"
    permission_codename = "core.manage_roles"

    def get_queryset(self):
        return Role.objects.filter(organization=self.organization).prefetch_related("permissions")


class RoleCreateView(TenantPermissionMixin, CreateView):
    model = Role
    form_class = RoleForm
    template_name = "core/role_form.html"
    permission_codename = "core.manage_roles"

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        if "perm_form" not in ctx:
            ctx["perm_form"] = RolePermissionsForm()
        return ctx

    def form_valid(self, form):
        role = form.save(commit=False)
        role.organization = self.organization
        role.save()
        perm_form = RolePermissionsForm(self.request.POST)
        if perm_form.is_valid():
            role.permissions.set(perm_form.cleaned_data["permissions"])

        RoleAuditLog.objects.create(
            organization=self.organization,
            actor=self.request.user,
            role=role,
            action=RoleAuditLog.Action.CREATED,
            after=_export_role(role),
        )
        messages.success(self.request, "Role created.")
        return redirect("core:role_list")


class RoleUpdateView(TenantPermissionMixin, UpdateView):
    model = Role
    form_class = RoleForm
    template_name = "core/role_form.html"
    permission_codename = "core.manage_roles"

    def get_queryset(self):
        return Role.objects.filter(organization=self.organization)

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        if "perm_form" not in ctx:
            ctx["perm_form"] = RolePermissionsForm(
                initial={"permissions": self.object.permissions.all()}
            )
        return ctx

    def form_valid(self, form):
        before = _export_role(self.object)
        role = form.save()
        perm_form = RolePermissionsForm(self.request.POST)
        if perm_form.is_valid():
            role.permissions.set(perm_form.cleaned_data["permissions"])

        RoleAuditLog.objects.create(
            organization=self.organization,
            actor=self.request.user,
            role=role,
            action=RoleAuditLog.Action.UPDATED,
            before=before,
            after=_export_role(role),
        )
        messages.success(self.request, "Role updated.")
        return redirect("core:role_list")


class RoleDeleteView(TenantPermissionMixin, DeleteView):
    template_name = "core/role_confirm_delete.html"
    success_url = reverse_lazy("core:role_list")
    permission_codename = "core.manage_roles"

    def get_queryset(self):
        return Role.objects.filter(organization=self.organization)

    def delete(self, request, *args, **kwargs):
        role = self.get_object()
        before = _export_role(role)
        resp = super().delete(request, *args, **kwargs)
        RoleAuditLog.objects.create(
            organization=self.organization,
            actor=request.user,
            role=None,
            action=RoleAuditLog.Action.DELETED,
            before=before,
        )
        messages.success(request, "Role deleted.")
        return resp


class RoleExportView(TenantPermissionMixin, View):
    permission_codename = "core.manage_roles"

    def get(self, request, pk: int):
        role = get_object_or_404(Role, pk=pk, organization=self.organization)
        data = _export_role(role)
        return JsonResponse(data)


class RoleImportView(TenantPermissionMixin, View):
    template_name = "core/role_import.html"
    permission_codename = "core.manage_roles"

    def get(self, request):
        return render(request, self.template_name, {"form": RoleImportForm()})

    def post(self, request):
        form = RoleImportForm(request.POST)
        if not form.is_valid():
            return render(request, self.template_name, {"form": form})

        payload = form.cleaned_data["json_data"]
        name = payload.get("name") or payload.get("slug") or "Imported role"
        slug = payload.get("slug") or slugify(name)
        role = Role.objects.create(
            organization=self.organization,
            name=name,
            slug=slug,
            description=payload.get("description", ""),
            position=payload.get("position", 0),
        )

        perms = Permission.objects.filter(codename__in=payload.get("permissions", []))
        role.permissions.set(perms)

        RoleAuditLog.objects.create(
            organization=self.organization,
            actor=request.user,
            role=role,
            action=RoleAuditLog.Action.IMPORTED,
            after=_export_role(role),
        )
        messages.success(request, "Role imported.")
        return redirect("core:role_list")


def _export_role(role: Role) -> dict:
    return {
        "name": role.name,
        "slug": role.slug,
        "description": role.description,
        "position": role.position,
        "permissions": list(role.permissions.values_list("codename", flat=True)),
    }
