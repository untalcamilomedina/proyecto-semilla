from __future__ import annotations

import rules

from common.policies import get_membership, has_permission


@rules.predicate
def is_org_member(user, organization):
    return get_membership(user, organization) is not None


@rules.predicate
def is_org_owner(user, organization):
    membership = get_membership(user, organization)
    return membership is not None and membership.role.slug == "owner"


def _perm(codename: str):
    @rules.predicate
    def predicate(user, organization):
        return has_permission(user, organization, codename)

    return predicate


# Core RBAC perms
rules.add_perm("core.manage_roles", _perm("core.manage_roles"))
rules.add_perm("core.invite_members", _perm("core.invite_members"))

