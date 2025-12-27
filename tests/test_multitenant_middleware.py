import pytest
from django.test import RequestFactory, override_settings
from django.http import HttpResponse
from django.conf import settings
from multitenant.middleware import TenantMiddleware
from multitenant.models import Tenant, Domain
from multitenant.schema import PUBLIC_SCHEMA_NAME, schema_context, set_schema, get_current_schema
import uuid

@pytest.mark.django_db(transaction=True)
class TestTenantMiddleware:
    
    @pytest.fixture
    def factory(self):
        return RequestFactory()
        
    @pytest.fixture
    def middleware(self):
        return TenantMiddleware(lambda r: HttpResponse("OK"))

    @pytest.fixture
    def tenant(self):
        slug = f"testmw-{uuid.uuid4().hex[:8]}"
        with schema_context(PUBLIC_SCHEMA_NAME):
            tenant = Tenant.objects.create(name="Middleware Test", slug=slug, schema_name=slug)
            Domain.objects.create(tenant=tenant, domain=f"{slug}.test.com", is_primary=True)
        
        # Ensure schema exists (locally simulated as it's cleaner)
        with schema_context(slug):
             pass # Schema created by signal usually
             
        # Need local tenant copy for middleware's get(schema_name=...)
        with schema_context(slug):
             Tenant.objects.get_or_create(id=tenant.id, defaults={
                 "name": tenant.name, "slug": tenant.slug, "schema_name": tenant.schema_name
             })
        return tenant

    @override_settings(MULTITENANT_MODE="schema", ALLOWED_HOSTS=["*"])
    def test_process_request_public_domain(self, factory, middleware):
        """Test request to public domain (no tenant)."""
        request = factory.get("/", HTTP_HOST="public.com")
        middleware.process_request(request)
        assert request.tenant is None
        
    @override_settings(MULTITENANT_MODE="schema", ALLOWED_HOSTS=["*"])
    def test_process_request_valid_tenant_domain(self, factory, middleware, tenant):
        """Test request to valid tenant domain."""
        domain = f"{tenant.slug}.test.com"
        request = factory.get("/", HTTP_HOST=domain)
        middleware.process_request(request)
        
        assert request.tenant is not None
        assert request.tenant.id == tenant.id
        assert request.tenant.schema_name == tenant.schema_name

    @override_settings(MULTITENANT_MODE="schema", ALLOWED_HOSTS=["*"])
    def test_process_request_invalid_tenant_domain(self, factory, middleware):
        """Test request to unknown domain."""
        request = factory.get("/", HTTP_HOST="unknown.test.com")
        middleware.process_request(request)
        assert request.tenant is None
    
    @override_settings(MULTITENANT_MODE="off")
    def test_process_request_multitenant_off(self, factory, middleware, tenant):
        """Test middleware disabled."""
        domain = f"{tenant.slug}.test.com"
        request = factory.get("/", HTTP_HOST=domain)
        middleware.process_request(request)
        assert request.tenant is None

    @override_settings(MULTITENANT_MODE="schema", ALLOWED_HOSTS=["*"])
    def test_process_response_resets_schema(self, factory, middleware):
        """Test that schema is reset to public after response."""
        from django.db import connection
        
        request = factory.get("/")
        response = HttpResponse("OK")
        
        
        # Simulate being in a tenant schema
        set_schema("some_schema")
        
        middleware.process_response(request, response)
        
        assert get_current_schema() == PUBLIC_SCHEMA_NAME
