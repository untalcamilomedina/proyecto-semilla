"""Fachada de email del seed.

API estable para los servicios (onboarding, members): encola las tareas
Celery de core.tasks. En DEBUG/tests `CELERY_TASK_ALWAYS_EAGER=True` ejecuta
inline (sin worker); en producción el worker del compose las consume.
"""

from __future__ import annotations

from multitenant.schema import get_current_schema


class EmailService:
    @staticmethod
    def send_welcome_email(user) -> None:
        """Encola el email de bienvenida para un usuario nuevo."""
        from core.tasks import send_welcome_email_task

        send_welcome_email_task.delay(user_id=user.id, schema_name=get_current_schema())

    @staticmethod
    def send_invite_email(membership, invite_url: str, inviter=None) -> None:
        """Encola el email de invitación a una organización."""
        from core.tasks import send_invite_email_task

        send_invite_email_task.delay(
            membership_id=membership.id,
            invite_url=invite_url,
            schema_name=get_current_schema(),
            inviter_id=inviter.id if inviter else None,
        )
