from __future__ import annotations

from core.models import Membership

from billing.models import Subscription


def get_active_subscription(organization):
    return (
        Subscription.objects.filter(organization=organization, status__in=["trialing", "active"])
        .order_by("-created_at")
        .first()
    )


def seat_limit_for_org(organization) -> int | None:
    sub = get_active_subscription(organization)
    if not sub:
        return None
    return sub.plan.seat_limit


def seats_used(organization) -> int:
    return Membership.objects.filter(organization=organization, is_active=True).count()


def can_add_seat(organization, additional: int = 1) -> bool:
    limit = seat_limit_for_org(organization)
    if limit is None:
        return True
    return seats_used(organization) + additional <= limit

