import pytest

from common.policies import has_permission
from core.models import Membership, Permission, Role, User
from core.services.seed import seed_default_roles, seed_system_permissions
from multitenant.models import Tenant
from multitenant.schema import create_schema


@pytest.mark.django_db
def test_seed_system_permissions_idempotent():
    seed_system_permissions()
    seed_system_permissions()
    assert Permission.objects.filter(codename="core.manage_roles").count() == 1


@pytest.mark.django_db
def test_seed_default_roles_creates_roles_per_tenant():
    tenant = Tenant.objects.create(name="Org", slug="org", schema_name="org")
    create_schema("org")
    seed_default_roles(tenant)
    assert Role.objects.filter(organization=tenant, slug="owner").exists()
    assert Role.objects.filter(organization=tenant, slug="viewer").exists()


@pytest.mark.django_db
def test_has_permission_via_membership_role():
    tenant = Tenant.objects.create(name="Org2", slug="org2", schema_name="org2")
    create_schema("org2")
    seed_default_roles(tenant)
    owner_role = Role.objects.get(organization=tenant, slug="owner")

    user = User.objects.create_user(username="u1", email="u1@example.com", password="pass1234")
    Membership.objects.create(user=user, organization=tenant, role=owner_role)

    assert has_permission(user, tenant, "core.manage_roles") is True
    assert has_permission(user, tenant, "core.invite_members") is True


@pytest.mark.django_db
def test_membership_unique_per_user_org():
    tenant = Tenant.objects.create(name="Org3", slug="org3", schema_name="org3")
    create_schema("org3")
    seed_default_roles(tenant)
    role = Role.objects.get(organization=tenant, slug="member")

    user = User.objects.create_user(username="u2", email="u2@example.com", password="pass1234")
    Membership.objects.create(user=user, organization=tenant, role=role)
    with pytest.raises(Exception):
        Membership.objects.create(user=user, organization=tenant, role=role)

