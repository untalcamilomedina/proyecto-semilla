from __future__ import annotations


def tenant_branding(request):
    tenant = getattr(request, "tenant", None)
    branding = {}
    if tenant is not None:
        branding = getattr(tenant, "branding", {}) or {}
    from django.conf import settings

    return {
        "tenant": tenant,
        "branding": branding,
        "DOMAIN_BASE": getattr(settings, "DOMAIN_BASE", "acme.dev"),
    }
