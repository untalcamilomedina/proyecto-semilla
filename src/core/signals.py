from __future__ import annotations

from django.db.models.signals import m2m_changed
from django.dispatch import receiver

from .models import Role, RoleAuditLog


def _export_role(role: Role) -> dict:
    return {
        "name": role.name,
        "slug": role.slug,
        "description": role.description,
        "position": role.position,
        "permissions": list(role.permissions.values_list("codename", flat=True)),
    }


@receiver(m2m_changed, sender=Role.permissions.through)
def role_permissions_changed(sender, instance: Role, action: str, **kwargs):
    if action not in {"post_add", "post_remove", "post_clear"}:
        return
    RoleAuditLog.objects.create(
        organization=instance.organization,
        actor=None,
        role=instance,
        action=RoleAuditLog.Action.PERMS_CHANGED,
        after=_export_role(instance),
    )

