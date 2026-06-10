"""Exportación de datos personales (GDPR art. 15 / portabilidad art. 20).

Recorre el schema público y todos los schemas de tenant buscando al usuario
por email, y emite un JSON con sus datos: perfil, membresías y registros de
actividad. Úsalo ante una solicitud de acceso del interesado.

    python manage.py export_user_data --email persona@dominio.com
    python manage.py export_user_data --email persona@dominio.com --output export.json
"""

from __future__ import annotations

import json

from django.core.management.base import BaseCommand, CommandError
from django.core.serializers.json import DjangoJSONEncoder

from multitenant.models import Tenant
from multitenant.schema import PUBLIC_SCHEMA_NAME, schema_context


def _collect_in_current_schema(email: str) -> dict | None:
    from core.models import ActivityLog, Membership, User

    user = User.objects.filter(email__iexact=email).first()
    if user is None:
        return None

    memberships = [
        {
            "organization": m.organization.slug,
            "role": m.role.slug if m.role else None,
            "is_active": m.is_active,
            "joined_at": m.joined_at,
        }
        for m in Membership.objects.filter(user=user).select_related("organization", "role")
    ]
    activity = [
        {
            "action": log.action,
            "object_repr": log.object_repr,
            "description": log.description,
            "created_at": log.created_at,
        }
        for log in ActivityLog.objects.filter(actor=user).order_by("-created_at")[:1000]
    ]
    return {
        "user": {
            "id": user.id,
            "username": user.username,
            "email": user.email,
            "first_name": user.first_name,
            "last_name": user.last_name,
            "date_joined": user.date_joined,
            "last_login": user.last_login,
            "is_active": user.is_active,
        },
        "memberships": memberships,
        "activity_logs": activity,
    }


class Command(BaseCommand):
    help = "Exporta todos los datos personales de un usuario (GDPR) en JSON."

    def add_arguments(self, parser):
        parser.add_argument("--email", required=True, help="Email del interesado")
        parser.add_argument("--output", help="Archivo destino (por defecto: stdout)")

    def handle(self, *args, **options):
        email = options["email"]
        export: dict[str, dict] = {}

        with schema_context(PUBLIC_SCHEMA_NAME):
            schemas = [
                PUBLIC_SCHEMA_NAME,
                *Tenant.objects.values_list("schema_name", flat=True),
            ]

        for schema in schemas:
            with schema_context(schema):
                data = _collect_in_current_schema(email)
            if data is not None:
                export[schema] = data

        if not export:
            raise CommandError(f"No se encontró ningún usuario con email {email}.")

        payload = json.dumps(
            {"email": email, "schemas": export}, cls=DjangoJSONEncoder, indent=2, ensure_ascii=False
        )
        if options.get("output"):
            with open(options["output"], "w", encoding="utf-8") as fh:
                fh.write(payload)
            self.stdout.write(self.style.SUCCESS(f"Export escrito en {options['output']}"))
        else:
            self.stdout.write(payload)
