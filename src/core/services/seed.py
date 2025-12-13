from __future__ import annotations

from django.db import transaction

from core.models import Permission, Role


SYSTEM_PERMISSIONS = [
    {
        "module": "core",
        "codename": "core.manage_roles",
        "name": "Manage roles and permissions",
        "description": "Create/update/delete roles and assign permissions.",
    },
    {
        "module": "core",
        "codename": "core.invite_members",
        "name": "Invite members",
        "description": "Invite users to the organization.",
    },
    {
        "module": "billing",
        "codename": "billing.manage_billing",
        "name": "Manage billing",
        "description": "View and manage subscriptions and invoices.",
    },
]


DEFAULT_ROLES = [
    {"name": "Owner", "slug": "owner", "position": 100},
    {"name": "Admin", "slug": "admin", "position": 90},
    {"name": "Editor", "slug": "editor", "position": 80},
    {"name": "Member", "slug": "member", "position": 10},
    {"name": "Viewer", "slug": "viewer", "position": 0},
]


ROLE_PERMISSION_MAP = {
    "owner": ["core.manage_roles", "core.invite_members", "billing.manage_billing"],
    "admin": ["core.manage_roles", "core.invite_members", "billing.manage_billing"],
    "editor": ["core.invite_members"],
    "member": [],
    "viewer": [],
}


@transaction.atomic
def seed_system_permissions() -> list[Permission]:
    created: list[Permission] = []
    for perm in SYSTEM_PERMISSIONS:
        obj, _ = Permission.objects.get_or_create(
            codename=perm["codename"],
            defaults={
                "module": perm["module"],
                "name": perm["name"],
                "description": perm["description"],
                "is_system": True,
            },
        )
        created.append(obj)
    return created


@transaction.atomic
def seed_default_roles(organization) -> list[Role]:
    seed_system_permissions()
    perms_by_code = {p.codename: p for p in Permission.objects.all()}

    roles: list[Role] = []
    for role_def in DEFAULT_ROLES:
        role, _ = Role.objects.get_or_create(
            organization=organization,
            slug=role_def["slug"],
            defaults={
                "name": role_def["name"],
                "position": role_def["position"],
                "is_system": True,
            },
        )
        role.name = role_def["name"]
        role.position = role_def["position"]
        role.is_system = True
        role.save()

        perm_codes = ROLE_PERMISSION_MAP.get(role.slug, [])
        role.permissions.set([perms_by_code[c] for c in perm_codes if c in perms_by_code])
        roles.append(role)
    return roles

