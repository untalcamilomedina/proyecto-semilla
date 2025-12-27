from __future__ import annotations


from django.core.exceptions import PermissionDenied


class PolicyError(Exception):
    pass


def allow_all(*_args, **_kwargs) -> bool:
    return True


def get_membership(user, organization):
    if user is None or organization is None or not user.is_authenticated:
        return None
    from core.models import Membership

    try:
        return Membership.objects.select_related("role").get(
            user=user, organization=organization, is_active=True
        )
    except Membership.DoesNotExist:
        return None



def has_permission(user, organization, codename: str) -> bool:
    if user is not None and getattr(user, "is_superuser", False):
        return True
    membership = get_membership(user, organization)
    if membership is None:
        return False
    return membership.role.permissions.filter(codename=codename).exists()


def require_permission(user, organization, codename: str) -> None:
    if not has_permission(user, organization, codename):
        raise PermissionDenied
