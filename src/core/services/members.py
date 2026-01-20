from __future__ import annotations

from django.db import transaction

from core.services.email import EmailService
from core.models import Membership, Role, User
from core.services.usernames import username_from_email


@transaction.atomic
def invite_members_to_org(organization, emails: list[str], role_slug: str = "member", inviter=None) -> int:
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
        membership, _ = Membership.objects.get_or_create(
            user=user, organization=organization, defaults={"role": role}
        )
        from django.conf import settings
        invite_url = f"https://{organization.slug}.{getattr(settings, 'DOMAIN_BASE', 'acme.dev')}/join"
        EmailService.send_invite_email(membership, invite_url, inviter=inviter)
        invited += 1
    return invited
