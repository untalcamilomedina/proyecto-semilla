from __future__ import annotations

from django.conf import settings
from django.core.management.base import BaseCommand, CommandError
from django.core.management import call_command
from django.db import transaction, connection

from multitenant.models import Domain, Tenant
from multitenant.schema import PUBLIC_SCHEMA_NAME, create_schema, drop_schema, schema_context


class Command(BaseCommand):
    help = "Create a tenant (schema) and its primary domain."

    def add_arguments(self, parser):
        parser.add_argument("name")
        parser.add_argument("slug", help="Default subdomain for the tenant.")
        parser.add_argument("--schema", dest="schema_name", help="Schema name override.")
        parser.add_argument("--domain", dest="domain", help="Primary full domain override.")
        parser.add_argument("--plan", dest="plan_code", default="")
        parser.add_argument("--inactive", action="store_true")

    def handle(self, *args, **options):
        if getattr(settings, "MULTITENANT_MODE", "off") != "schema":
            raise CommandError("MULTITENANT_MODE must be 'schema' to create tenants.")

        slug = options["slug"].lower()
        schema_name = (options.get("schema_name") or slug).lower()
        domain = options.get("domain") or f"{slug}.{getattr(settings, 'DOMAIN_BASE', 'acme.dev')}"

        tenant = Tenant(
            name=options["name"],
            slug=slug,
            schema_name=schema_name,
            plan_code=options["plan_code"],
            is_active=not options["inactive"],
        )
        tenant.full_clean()

        # Phase 1: Create tenant, schema, and domain in public (atomic DML)
        with transaction.atomic():
            with schema_context(PUBLIC_SCHEMA_NAME):
                tenant.save()
                create_schema(schema_name)
                Domain.objects.create(tenant=tenant, domain=domain, is_primary=True)

        # Phase 2: Run migrations in new schema (DDL - must be outside transaction)
        # PostgreSQL cannot run ALTER TABLE with pending trigger events in same transaction
        try:
            with schema_context(schema_name):
                # Force search path to strictly tenant schema
                with connection.cursor() as cursor:
                    cursor.execute(f'SET search_path TO "{schema_name}"')
                call_command("migrate", interactive=False, verbosity=0)
        except Exception as e:
            # Rollback phase 1 if migrations fail
            self.stderr.write(self.style.ERROR(f"Migration failed: {e}"))
            with schema_context(PUBLIC_SCHEMA_NAME):
                Domain.objects.filter(tenant=tenant).delete()
                tenant.delete()
            drop_schema(schema_name)
            raise CommandError(f"Migration failed, tenant rolled back: {e}") from e

        # Phase 3: Create tenant copy in new schema (atomic DML)
        with transaction.atomic():
            with schema_context(schema_name):
                # Restore search path to include public
                with connection.cursor() as cursor:
                    cursor.execute(f'SET search_path TO "{schema_name}", {PUBLIC_SCHEMA_NAME}')
                Tenant.objects.create(
                    id=tenant.id,
                    name=tenant.name,
                    slug=tenant.slug,
                    schema_name=tenant.schema_name,
                    is_active=tenant.is_active,
                    plan_code=tenant.plan_code,
                    trial_ends_at=tenant.trial_ends_at,
                    enabled_modules=tenant.enabled_modules,
                    branding=getattr(tenant, "branding", {}) or {},
                )

        self.stdout.write(
            self.style.SUCCESS(
                f"Created tenant '{tenant.slug}' with schema '{tenant.schema_name}' and domain '{domain}'."
            )
        )
