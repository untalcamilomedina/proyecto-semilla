"""Borrado/anonimización de datos personales (GDPR art. 17 — derecho al olvido).

Anonimiza al usuario en el schema público y en todos los schemas de tenant:
email/username/nombres se reemplazan por valores no identificables, la cuenta
se desactiva y la contraseña queda inutilizable. Se conserva la fila (con los
FKs de auditoría/billing intactos) — el rastro deja de ser personal.

    python manage.py delete_user_data --email persona@dominio.com --yes
"""

from __future__ import annotations

from django.core.management.base import BaseCommand, CommandError

from multitenant.models import Tenant
from multitenant.schema import PUBLIC_SCHEMA_NAME, schema_context


def _anonymize_in_current_schema(email: str, schema: str) -> bool:
    from core.models import User

    user = User.objects.filter(email__iexact=email).first()
    if user is None:
        return False

    user.email = f"deleted-{user.pk}@anonimo.invalid"
    user.username = f"deleted-{user.pk}-{schema}"[:150]
    user.first_name = ""
    user.last_name = ""
    user.is_active = False
    user.set_unusable_password()
    user.save(
        update_fields=["email", "username", "first_name", "last_name", "is_active", "password"]
    )
    # Desactivar membresías para que no aparezca en listados del tenant.
    from core.models import Membership

    Membership.objects.filter(user=user).update(is_active=False)
    return True


class Command(BaseCommand):
    help = "Anonimiza los datos personales de un usuario en todos los schemas (GDPR)."

    def add_arguments(self, parser):
        parser.add_argument("--email", required=True, help="Email del interesado")
        parser.add_argument("--yes", action="store_true", help="No pedir confirmación interactiva")

    def handle(self, *args, **options):
        email = options["email"]
        if not options["yes"]:
            answer = input(f"¿Anonimizar TODOS los datos de {email}? Es irreversible [s/N]: ")
            if answer.strip().lower() not in {"s", "si", "sí", "y", "yes"}:
                self.stdout.write("Cancelado.")
                return

        with schema_context(PUBLIC_SCHEMA_NAME):
            schemas = [
                PUBLIC_SCHEMA_NAME,
                *Tenant.objects.values_list("schema_name", flat=True),
            ]

        touched: list[str] = []
        for schema in schemas:
            with schema_context(schema):
                if _anonymize_in_current_schema(email, schema):
                    touched.append(schema)

        if not touched:
            raise CommandError(f"No se encontró ningún usuario con email {email}.")

        self.stdout.write(
            self.style.SUCCESS(
                f"Usuario anonimizado en {len(touched)} schema(s): {', '.join(touched)}"
            )
        )
