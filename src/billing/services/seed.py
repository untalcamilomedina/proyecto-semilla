from __future__ import annotations

from decimal import Decimal

from django.conf import settings
from django.db import transaction

from billing.models import Plan, Price


DEMO_PLANS = [
    {
        "code": "free",
        "name": "Free",
        "amount": Decimal("0.00"),
        "seat_limit": 3,
        "trial_days": 0,
        "roles_on_activation": [],
    },
    {
        "code": "pro",
        "name": "Pro",
        "amount": Decimal("19.00"),
        "seat_limit": 20,
        "trial_days": 14,
        "roles_on_activation": ["editor"],
    },
    {
        "code": "business",
        "name": "Business",
        "amount": Decimal("59.00"),
        "seat_limit": None,
        "trial_days": 14,
        "roles_on_activation": ["admin"],
    },
]


@transaction.atomic
def seed_demo_plans(organization) -> list[Plan]:
    plans: list[Plan] = []
    for plan_def in DEMO_PLANS:
        plan, _ = Plan.objects.update_or_create(
            organization=organization,
            code=plan_def["code"],
            defaults={
                "name": plan_def["name"],
                "seat_limit": plan_def["seat_limit"],
                "trial_days": plan_def["trial_days"],
                "roles_on_activation": plan_def["roles_on_activation"],
                "is_active": True,
                "is_public": True,
            },
        )

        env_key = f"STRIPE_PRICE_ID_{plan.code.upper()}"
        stripe_price_id = getattr(settings, env_key, "")

        Price.objects.update_or_create(
            plan=plan,
            interval="month",
            defaults={
                "amount": plan_def["amount"],
                "currency": settings.STRIPE_DEFAULT_CURRENCY,
                "stripe_price_id": stripe_price_id,
                "is_active": True,
            },
        )
        plans.append(plan)
    return plans

