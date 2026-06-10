"""Tareas Celery del núcleo.

Patrón multitenant: las tareas reciben `schema_name` y restauran el contexto
con `schema_context` — el worker corre fuera del ciclo request/response y no
pasa por TenantMiddleware. Sigue este patrón en cualquier task nueva.
"""

from __future__ import annotations

from celery import shared_task
from django.conf import settings
from django.core.mail import send_mail
from django.template.loader import render_to_string

from multitenant.schema import schema_context


@shared_task(
    bind=True,
    autoretry_for=(Exception,),
    retry_backoff=30,
    retry_kwargs={"max_retries": 3},
)
def send_welcome_email_task(self, user_id: int, schema_name: str) -> None:
    from core.models import User

    with schema_context(schema_name):
        user = User.objects.get(id=user_id)
        context = {
            "user": user,
            "site_name": settings.PROJECT_NAME,
            "frontend_url": settings.FRONTEND_URL,
        }
        send_mail(
            subject=f"Welcome to {settings.PROJECT_NAME}!",
            message=render_to_string("emails/welcome.txt", context),
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[user.email],
            html_message=render_to_string("emails/welcome.html", context),
        )


@shared_task(
    bind=True,
    autoretry_for=(Exception,),
    retry_backoff=30,
    retry_kwargs={"max_retries": 3},
)
def send_invite_email_task(
    self,
    membership_id: int,
    invite_url: str,
    schema_name: str,
    inviter_id: int | None = None,
) -> None:
    from core.models import Membership, User

    with schema_context(schema_name):
        membership = Membership.objects.select_related("organization", "user").get(id=membership_id)
        inviter = User.objects.filter(id=inviter_id).first() if inviter_id else None
        context = {
            "inviter": inviter,
            "organization": membership.organization,
            "invite_url": invite_url,
            "site_name": settings.PROJECT_NAME,
        }
        send_mail(
            subject=(
                f"Invitation to join {membership.organization.name} on {settings.PROJECT_NAME}"
            ),
            message=render_to_string("emails/invite.txt", context),
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[membership.user.email],
            html_message=render_to_string("emails/invite.html", context),
        )
