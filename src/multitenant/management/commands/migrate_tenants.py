from __future__ import annotations

from django.conf import settings
from django.core.management import call_command
from django.core.management.base import BaseCommand

from multitenant.models import Tenant
from multitenant.schema import PUBLIC_SCHEMA_NAME, schema_context


class Command(BaseCommand):
    help = "Run migrations on all tenant schemas."

    def add_arguments(self, parser):
        parser.add_argument("--schema", dest="schema_name", help="Only migrate a given schema.")
        parser.add_argument("--skip-public", action="store_true", help="Skip migrating public schema.")
        parser.add_argument("--noinput", action="store_true")

    def handle(self, *args, **options):
        interactive = not options["noinput"]

        if getattr(settings, "MULTITENANT_MODE", "off") != "schema":
            call_command("migrate", interactive=interactive)
            return

        if not options["skip_public"]:
            call_command("migrate", interactive=interactive)

        with schema_context(PUBLIC_SCHEMA_NAME):
            tenants = Tenant.objects.filter(is_active=True)
            if options.get("schema_name"):
                tenants = tenants.filter(schema_name=options["schema_name"])
            tenants = list(tenants)

        for tenant in tenants:
            self.stdout.write(f"Migrating schema '{tenant.schema_name}'")
            with schema_context(tenant.schema_name):
                call_command("migrate", interactive=interactive)
