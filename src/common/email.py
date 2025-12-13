from __future__ import annotations

from django.core.mail import send_mail


def send_welcome_email(to_email: str, subject: str, body: str) -> int:
    return send_mail(subject, body, None, [to_email])

