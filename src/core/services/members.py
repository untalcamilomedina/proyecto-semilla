from __future__ import annotations

from django.db import transaction

from common.email import send_welcome_email
from core.models import Membership, Role, User
from core.services.usernames import username_from_email


@transaction.atomic
def invite_members_to_org(organization, emails: list[str], role_slug: str = "member") -> int:
    if not emails:
        return 0

    try:
        from billing.services.limits import can_add_seat
    except Exception:  # pragma: no cover
        can_add_seat = lambda *_a, **_k: True  # noqa: E731

    if not can_add_seat(organization, additional=len(emails)):
        return 0

    role = Role.objects.get(organization=organization, slug=role_slug)
    invited = 0
    for email in emails:
        user, _ = User.objects.get_or_create(
            email=email,
            defaults={"username": username_from_email(email)},
        )
        Membership.objects.get_or_create(
            user=user, organization=organization, defaults={"role": role}
        )
        from django.conf import settings

        send_welcome_email(
            email,
            subject=f"You've been invited to {organization.name}",
            body=f"Join your organization at https://{organization.slug}.{getattr(settings, 'DOMAIN_BASE', 'acme.dev')}",
        )
        invited += 1
    return invited
