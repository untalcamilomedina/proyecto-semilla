import uuid

import pytest
from django.urls import reverse

from core.models import OnboardingState
from core.onboarding.forms import StartOnboardingForm
from core.services.onboarding import OnboardingResult
from multitenant.models import Tenant
from multitenant.schema import PUBLIC_SCHEMA_NAME, schema_context


pytestmark = pytest.mark.django_db(transaction=True)


def _make_state(
    *,
    slug: str,
    current_step: int = 2,
    completed_steps: list[int] | None = None,
    data: dict | None = None,
    is_complete: bool = False,
) -> OnboardingState:
    with schema_context(PUBLIC_SCHEMA_NAME):
        tenant = Tenant.objects.create(name=f"Org {slug}", slug=slug, schema_name=slug)
        return OnboardingState.objects.create(
            tenant=tenant,
            owner_email=f"owner-{slug}@example.com",
            current_step=current_step,
            completed_steps=completed_steps or [],
            data=data or {},
            is_complete=is_complete,
        )


def test_onboarding_start_get_renders_form(client):
    res = client.get(reverse("core:onboarding_start"))
    assert res.status_code == 200
    assert isinstance(res.context["form"], StartOnboardingForm)


def test_onboarding_start_post_password_mismatch_renders_errors(client, monkeypatch):
    monkeypatch.setattr("core.onboarding.views.start_onboarding", lambda *_a, **_k: pytest.fail())
    slug = f"org{uuid.uuid4().hex[:8]}"
    res = client.post(
        reverse("core:onboarding_start"),
        {
            "org_name": "Org",
            "subdomain": slug,
            "admin_email": f"admin-{slug}@example.com",
            "password1": "pass1234",
            "password2": "pass5678",
        },
    )
    assert res.status_code == 200
    assert "password2" in res.context["form"].errors
    assert client.session.get("onboarding_state_id") is None


def test_onboarding_start_post_reserved_subdomain_renders_errors(client, monkeypatch):
    monkeypatch.setattr("core.onboarding.views.start_onboarding", lambda *_a, **_k: pytest.fail())
    res = client.post(
        reverse("core:onboarding_start"),
        {
            "org_name": "Org",
            "subdomain": "WWW",
            "admin_email": "admin@example.com",
            "password1": "pass1234",
            "password2": "pass1234",
        },
    )
    assert res.status_code == 200
    assert "subdomain" in res.context["form"].errors
    assert client.session.get("onboarding_state_id") is None


def test_onboarding_start_post_valid_sets_session_and_redirects(client, monkeypatch):
    slug = f"org{uuid.uuid4().hex[:8]}"
    seen: dict = {}

    def fake_start_onboarding(*, org_name: str, subdomain: str, admin_email: str, password: str):
        seen.update(
            {
                "org_name": org_name,
                "subdomain": subdomain,
                "admin_email": admin_email,
                "password": password,
            }
        )
        state = _make_state(
            slug=subdomain,
            completed_steps=[1],
            data={"modules": [], "stripe_connected": False, "resume_token": uuid.uuid4().hex},
        )
        return OnboardingResult(tenant=state.tenant, state=state)

    monkeypatch.setattr("core.onboarding.views.start_onboarding", fake_start_onboarding)

    res = client.post(
        reverse("core:onboarding_start"),
        {
            "org_name": "Org",
            "subdomain": slug.upper(),
            "admin_email": f"admin-{slug}@example.com",
            "password1": "pass1234",
            "password2": "pass1234",
        },
    )
    assert res.status_code == 302
    assert res["Location"] == reverse("core:onboarding_modules")
    assert seen["subdomain"] == slug
    assert client.session["onboarding_state_id"] is not None


def test_onboarding_step_views_redirect_to_start_without_state(client):
    res = client.get(reverse("core:onboarding_modules"))
    assert res.status_code == 302
    assert res["Location"] == reverse("core:onboarding_start")

    res = client.post(reverse("core:onboarding_modules"), {})
    assert res.status_code == 302
    assert res["Location"] == reverse("core:onboarding_start")

    res = client.get(reverse("core:onboarding_stripe"))
    assert res.status_code == 302
    assert res["Location"] == reverse("core:onboarding_start")

    res = client.post(reverse("core:onboarding_stripe"), {})
    assert res.status_code == 302
    assert res["Location"] == reverse("core:onboarding_start")

    res = client.get(reverse("core:onboarding_domain"))
    assert res.status_code == 302
    assert res["Location"] == reverse("core:onboarding_start")

    res = client.post(reverse("core:onboarding_domain"), {})
    assert res.status_code == 302
    assert res["Location"] == reverse("core:onboarding_start")

    res = client.get(reverse("core:onboarding_invite"))
    assert res.status_code == 302
    assert res["Location"] == reverse("core:onboarding_start")

    res = client.post(reverse("core:onboarding_invite"), {})
    assert res.status_code == 302
    assert res["Location"] == reverse("core:onboarding_start")


def test_onboarding_step_views_redirect_to_start_with_missing_state_id(client):
    session = client.session
    session["onboarding_state_id"] = 999999
    session.save()
    res = client.get(reverse("core:onboarding_modules"))
    assert res.status_code == 302
    assert res["Location"] == reverse("core:onboarding_start")


def test_onboarding_modules_get_prefills_from_state_data(client):
    state = _make_state(
        slug=f"org{uuid.uuid4().hex[:8]}",
        completed_steps=[1],
        data={"modules": ["cms", "community"]},
    )
    session = client.session
    session["onboarding_state_id"] = state.id
    session.save()

    res = client.get(reverse("core:onboarding_modules"))
    assert res.status_code == 200
    assert res.context["state"].id == state.id
    assert res.context["form"].initial["modules"] == ["cms", "community"]


def test_onboarding_modules_post_invalid_renders_errors(client, monkeypatch):
    state = _make_state(slug=f"org{uuid.uuid4().hex[:8]}", completed_steps=[1])
    session = client.session
    session["onboarding_state_id"] = state.id
    session.save()

    monkeypatch.setattr("core.onboarding.views.set_modules", lambda *_a, **_k: pytest.fail())
    res = client.post(reverse("core:onboarding_modules"), {"modules": ["not-a-module"]})
    assert res.status_code == 200
    assert "modules" in res.context["form"].errors


def test_onboarding_modules_post_valid_calls_service_and_redirects(client, monkeypatch):
    state = _make_state(slug=f"org{uuid.uuid4().hex[:8]}", completed_steps=[1])
    session = client.session
    session["onboarding_state_id"] = state.id
    session.save()

    seen: dict = {}

    def fake_set_modules(state_arg, modules):
        seen["state_id"] = state_arg.id
        seen["modules"] = modules

    monkeypatch.setattr("core.onboarding.views.set_modules", fake_set_modules)

    res = client.post(reverse("core:onboarding_modules"), {"modules": ["cms", "mcp"]})
    assert res.status_code == 302
    assert res["Location"] == reverse("core:onboarding_stripe")
    assert seen == {"state_id": state.id, "modules": ["cms", "mcp"]}


def test_onboarding_stripe_get_and_post_calls_service(client, monkeypatch):
    state = _make_state(
        slug=f"org{uuid.uuid4().hex[:8]}",
        completed_steps=[1, 2],
        data={"stripe_connected": True},
    )
    session = client.session
    session["onboarding_state_id"] = state.id
    session.save()

    res = client.get(reverse("core:onboarding_stripe"))
    assert res.status_code == 200
    assert res.context["form"].initial["stripe_connected"] is True

    seen: dict = {}

    def fake_mark_stripe_connected(state_arg, connected=False):
        seen["state_id"] = state_arg.id
        seen["connected"] = connected

    monkeypatch.setattr("core.onboarding.views.mark_stripe_connected", fake_mark_stripe_connected)
    res = client.post(reverse("core:onboarding_stripe"), {"stripe_connected": "on"})
    assert res.status_code == 302
    assert res["Location"] == reverse("core:onboarding_domain")
    assert seen == {"state_id": state.id, "connected": True}


def test_onboarding_domain_get_and_post_calls_service(client, monkeypatch, settings):
    state = _make_state(slug=f"org{uuid.uuid4().hex[:8]}", completed_steps=[1, 2, 3])
    session = client.session
    session["onboarding_state_id"] = state.id
    session.save()

    res = client.get(reverse("core:onboarding_domain"))
    assert res.status_code == 200
    assert res.context["DOMAIN_BASE"] == settings.DOMAIN_BASE

    seen: dict = {}

    def fake_set_custom_domain(state_arg, custom_domain):
        seen["state_id"] = state_arg.id
        seen["custom_domain"] = custom_domain

    monkeypatch.setattr("core.onboarding.views.set_custom_domain", fake_set_custom_domain)
    res = client.post(reverse("core:onboarding_domain"), {"custom_domain": ""})
    assert res.status_code == 302
    assert res["Location"] == reverse("core:onboarding_invite")
    assert seen == {"state_id": state.id, "custom_domain": None}


def test_onboarding_invite_post_invalid_email_renders_errors(client, monkeypatch):
    state = _make_state(slug=f"org{uuid.uuid4().hex[:8]}", completed_steps=[1, 2, 3, 4])
    session = client.session
    session["onboarding_state_id"] = state.id
    session.save()

    monkeypatch.setattr("core.onboarding.views.invite_members", lambda *_a, **_k: pytest.fail())
    res = client.post(reverse("core:onboarding_invite"), {"emails": "not-an-email"})
    assert res.status_code == 200
    assert "emails" in res.context["form"].errors


def test_onboarding_invite_post_valid_calls_service_clears_session_and_redirects(client, monkeypatch):
    state = _make_state(slug=f"org{uuid.uuid4().hex[:8]}", completed_steps=[1, 2, 3, 4])
    session = client.session
    session["onboarding_state_id"] = state.id
    session.save()

    seen: dict = {}

    def fake_invite_members(state_arg, emails):
        seen["state_id"] = state_arg.id
        seen["emails"] = emails
        return len(emails)

    monkeypatch.setattr("core.onboarding.views.invite_members", fake_invite_members)

    res = client.post(
        reverse("core:onboarding_invite"),
        {"emails": "U1@example.com\n\nu2@example.com\n"},
    )
    assert res.status_code == 302
    assert res["Location"] == reverse("core:onboarding_done")
    assert seen == {"state_id": state.id, "emails": ["u1@example.com", "u2@example.com"]}
    assert client.session.get("onboarding_state_id") is None


@pytest.mark.parametrize(
    ("current_step", "expected_url_name"),
    [
        (1, "core:onboarding_start"),
        (2, "core:onboarding_modules"),
        (3, "core:onboarding_stripe"),
        (4, "core:onboarding_domain"),
        (5, "core:onboarding_invite"),
        (99, "core:onboarding_start"),
    ],
)
def test_onboarding_resume_sets_session_and_redirects_to_step(client, current_step, expected_url_name):
    token = uuid.uuid4().hex
    state = _make_state(
        slug=f"org{uuid.uuid4().hex[:8]}",
        current_step=current_step,
        data={"resume_token": token},
    )
    res = client.get(reverse("core:onboarding_resume", args=[token]))
    assert res.status_code == 302
    assert res["Location"] == reverse(expected_url_name)
    assert client.session["onboarding_state_id"] == state.id


def test_onboarding_resume_invalid_token_redirects_to_start(client):
    res = client.get(reverse("core:onboarding_resume", args=[uuid.uuid4().hex]))
    assert res.status_code == 302
    assert res["Location"] == reverse("core:onboarding_start")


def test_onboarding_resume_complete_state_redirects_to_start(client):
    token = uuid.uuid4().hex
    _make_state(
        slug=f"org{uuid.uuid4().hex[:8]}",
        current_step=3,
        data={"resume_token": token},
        is_complete=True,
    )
    res = client.get(reverse("core:onboarding_resume", args=[token]))
    assert res.status_code == 302
    assert res["Location"] == reverse("core:onboarding_start")


def test_onboarding_done_view_renders(client):
    res = client.get(reverse("core:onboarding_done"))
    assert res.status_code == 200
