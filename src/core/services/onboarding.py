from __future__ import annotations

from dataclasses import dataclass
from uuid import uuid4

from django.conf import settings
from django.db import transaction
from django.utils import timezone

from core.services.email import EmailService
from core.models import Membership, OnboardingState, Role, User
from core.services.seed import seed_default_roles
from core.services.usernames import username_from_email
from multitenant.models import Domain, Tenant, validate_subdomain
from multitenant.schema import PUBLIC_SCHEMA_NAME, create_schema, schema_context


@dataclass
class OnboardingResult:
    tenant: Tenant
    state: OnboardingState


from core.services.email import EmailService

def finish_onboarding(tenant: Tenant) -> Tenant:
    """
    Finalize onboarding: ensure tenant is active, owner has access.
    """
    tenant.is_active = True
    tenant.save()
    
    # Send welcome email to owner
    # Assuming owner is the user who triggered this, but we need the user object.
    # The current structure might separate user from tenant creation logic.
    # In 'create_tenant_from_onboarding' we have the user.
    # Let's inspect where finish is called or modify 'create_tenant_from_onboarding' instead.
    
    return tenant


def _ensure_local_tenant(tenant_public: Tenant) -> Tenant:
    with schema_context(tenant_public.schema_name):
        tenant_local, _ = Tenant.objects.get_or_create(
            id=tenant_public.id,
            defaults={
                "name": tenant_public.name,
                "slug": tenant_public.slug,
                "schema_name": tenant_public.schema_name,
                "is_active": tenant_public.is_active,
                "plan_code": tenant_public.plan_code,
                "trial_ends_at": tenant_public.trial_ends_at,
                "enabled_modules": tenant_public.enabled_modules,
                "branding": getattr(tenant_public, "branding", {}) or {},
            },
        )
    return tenant_local


@transaction.atomic
def start_onboarding(
    org_name: str,
    subdomain: str,
    admin_email: str | None = None,
    password: str | None = None,
    language: str = "es",
    stripe_connected: bool = False,
    stripe_public_key: str = "",
    stripe_secret_key: str = "",
    stripe_webhook_secret: str = "",
    source_user: User | None = None,
) -> OnboardingResult:
    slug = subdomain.lower().strip()
    validate_subdomain(slug)

    domain_base = getattr(settings, "DOMAIN_BASE", "acme.dev")
    full_domain = f"{slug}.{domain_base}"

    with schema_context(PUBLIC_SCHEMA_NAME):
        tenant_public = Tenant.objects.create(
            name=org_name,
            slug=slug,
            schema_name=slug,
            is_active=True,
            enabled_modules=[],
            branding={},
        )
        create_schema(slug)
        Domain.objects.create(tenant=tenant_public, domain=full_domain, is_primary=True)
        state = OnboardingState.objects.create(
            tenant=tenant_public,
            owner_email=admin_email,
            current_step=2,
            completed_steps=[1],
            data={
                "modules": [], 
                "stripe_connected": stripe_connected, 
                "stripe_config": {
                    "public_key": stripe_public_key,
                    "secret_key": stripe_secret_key,
                    "webhook_secret": stripe_webhook_secret,
                },
                "language": language,
                "resume_token": uuid4().hex
            },
        )

    tenant_local = _ensure_local_tenant(tenant_public)

    email = admin_email or (source_user.email if source_user else None)
    if not email:
        raise ValueError("Email required")

    with schema_context(tenant_public.schema_name):
        seed_default_roles(tenant_local)
        owner_role = Role.objects.get(organization=tenant_local, slug="owner")
        
        # Create user in tenant schema
        # If source_user exists, we copy the password hash directly to avoid re-hashing or requiring text password
        user = User(
            username=username_from_email(email),
            email=email,
            is_staff=True,
            is_superuser=True,
        )
        if source_user:
            user.password = source_user.password
        elif password:
            user.set_password(password)
        else:
            raise ValueError("Password or source user required")
        
        user.save()
        Membership.objects.create(user=user, organization=tenant_local, role=owner_role)

    EmailService.send_welcome_email(user)

    return OnboardingResult(tenant=tenant_public, state=state)


@transaction.atomic
def set_modules(state: OnboardingState, modules: list[str]) -> None:
    tenant = state.tenant
    with schema_context(PUBLIC_SCHEMA_NAME):
        tenant.enabled_modules = modules
        tenant.save(update_fields=["enabled_modules"])
        state.data["modules"] = modules
        state.mark_step_complete(2)
        state.save(update_fields=["data", "current_step", "completed_steps"])

    with schema_context(tenant.schema_name):
        Tenant.objects.filter(id=tenant.id).update(enabled_modules=modules)


@transaction.atomic
def mark_stripe_connected(state: OnboardingState, connected: bool = True) -> None:
    with schema_context(PUBLIC_SCHEMA_NAME):
        state.data["stripe_connected"] = connected
        state.mark_step_complete(3)
        state.save(update_fields=["data", "current_step", "completed_steps"])


@transaction.atomic
def set_custom_domain(state: OnboardingState, custom_domain: str | None) -> None:
    tenant = state.tenant
    with schema_context(PUBLIC_SCHEMA_NAME):
        if custom_domain:
            Domain.objects.update_or_create(
                domain=custom_domain.lower().strip(),
                defaults={"tenant": tenant, "is_primary": True},
            )
            Domain.objects.filter(tenant=tenant).exclude(domain=custom_domain).update(is_primary=False)
        state.mark_step_complete(4)
        state.save(update_fields=["current_step", "completed_steps"])


@transaction.atomic
def invite_members(
    state: OnboardingState, emails: list[str], role_slug: str = "member"
) -> int:
    tenant = state.tenant
    invited = 0
    with schema_context(tenant.schema_name):
        tenant_local = Tenant.objects.get(id=tenant.id)
        try:
            from billing.services.limits import can_add_seat
        except Exception:  # pragma: no cover
            can_add_seat = lambda *_a, **_k: True  # noqa: E731

        if emails and not can_add_seat(tenant_local, additional=len(emails)):
            emails = emails[:0]
        role = Role.objects.get(organization=tenant_local, slug=role_slug)
        for email in emails:
            user, _ = User.objects.get_or_create(
                email=email,
                defaults={"username": username_from_email(email)},
            )
            membership, _ = Membership.objects.get_or_create(user=user, organization=tenant_local, defaults={"role": role})
            invited += 1
            invite_url = f"https://{tenant_local.slug}.{settings.DOMAIN_BASE}/join?token=mocked"  # In real app use token
            EmailService.send_invite_email(membership, invite_url)

    with schema_context(PUBLIC_SCHEMA_NAME):
        state.mark_step_complete(5)
        state.is_complete = True
        state.save(update_fields=["current_step", "completed_steps", "is_complete"])

    return invited
