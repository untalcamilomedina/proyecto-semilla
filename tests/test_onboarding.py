import pytest

from core.services import onboarding as onboarding_service
from multitenant.models import Tenant
from multitenant.schema import PUBLIC_SCHEMA_NAME, schema_context


@pytest.mark.django_db(transaction=True)
def test_start_onboarding_creates_public_state_and_local_seed(monkeypatch):
    monkeypatch.setattr(onboarding_service, "send_welcome_email", lambda *a, **k: 1)
    result = onboarding_service.start_onboarding(
        org_name="Org A",
        subdomain="orga",
        admin_email="admin@orga.dev",
        password="pass1234",
    )

    with schema_context(PUBLIC_SCHEMA_NAME):
        tenant_public = Tenant.objects.get(slug="orga")
        state = tenant_public.onboarding_state
        assert state.current_step == 2
        assert 1 in state.completed_steps

    with schema_context("orga"):
        tenant_local = Tenant.objects.get(id=tenant_public.id)
        from core.models import Membership, Role, User

        assert Role.objects.filter(organization=tenant_local, slug="owner").exists()
        assert User.objects.filter(email="admin@orga.dev").exists()
        assert Membership.objects.filter(organization=tenant_local, user__email="admin@orga.dev").exists()


@pytest.mark.django_db(transaction=True)
def test_modules_syncs_to_public_and_local(monkeypatch):
    monkeypatch.setattr(onboarding_service, "send_welcome_email", lambda *a, **k: 1)
    result = onboarding_service.start_onboarding(
        org_name="Org B",
        subdomain="orgb",
        admin_email="admin@orgb.dev",
        password="pass1234",
    )

    onboarding_service.set_modules(result.state, ["cms", "community"])

    with schema_context(PUBLIC_SCHEMA_NAME):
        tenant_public = Tenant.objects.get(slug="orgb")
        assert tenant_public.enabled_modules == ["cms", "community"]

    with schema_context("orgb"):
        tenant_local = Tenant.objects.get(id=tenant_public.id)
        assert tenant_local.enabled_modules == ["cms", "community"]


@pytest.mark.django_db(transaction=True)
def test_invite_members_marks_complete(monkeypatch):
    monkeypatch.setattr(onboarding_service, "send_welcome_email", lambda *a, **k: 1)
    result = onboarding_service.start_onboarding(
        org_name="Org C",
        subdomain="orgc",
        admin_email="admin@orgc.dev",
        password="pass1234",
    )

    count = onboarding_service.invite_members(result.state, ["u1@orgc.dev", "u2@orgc.dev"])
    assert count == 2

    with schema_context(PUBLIC_SCHEMA_NAME):
        state = result.state.__class__.objects.get(id=result.state.id)
        assert state.is_complete is True
        assert 5 in state.completed_steps

