---
name: test-api-endpoint
description: Genera tests unitarios robustos para endpoints de API (DRF), validando Auth, Permisos y Status Codes.
author: AppNotion Architecture Team
version: 2.0.0
---

# Skill: Test API Endpoint

Esta skill estandariza la creación de tests para endpoints REST en Django Rest Framework, alineada con la arquitectura multi-tenant del proyecto.

## Objetivo

Asegurar que cada endpoint cumpla con:

1. **Seguridad**: Rechazar usuarios anónimos o sin permisos (401/403).
2. **Correctitud**: Retornar el Status Code esperado (200/201/204).
3. **Estructura**: El JSON de respuesta tiene las keys esperadas.
4. **Multi-tenancy**: Respetar el contexto del tenant.

## Prerrequisitos

- Fixtures definidos en `tests/conftest.py`
- No redefinir fixtures existentes (`api_client`, `user`, `tenant_client`)

## Template de Implementación

### Template 1: Endpoint Básico (Sin Multi-tenant)

```python
import pytest
from django.urls import reverse

@pytest.mark.django_db
class TestEndpointName:
    """
    Tests para el endpoint <EndpointName>.
    Usa fixtures de conftest.py: api_client, user, authenticated_client
    """

    def test_anonymous_access_denied(self, api_client):
        """
        GIVEN no authenticated user
        WHEN requesting the protected endpoint
        THEN return 401 Unauthorized
        """
        url = reverse("api:v1:endpoint-name-list")
        response = api_client.get(url)
        assert response.status_code == 401

    def test_authenticated_success(self, authenticated_client):
        """
        GIVEN an authenticated user (fixture from conftest.py)
        WHEN requesting the endpoint
        THEN return 200 OK and valid data
        """
        url = reverse("api:v1:endpoint-name-list")
        response = authenticated_client.get(url)

        assert response.status_code == 200
        assert isinstance(response.data, (list, dict))

    def test_create_resource(self, authenticated_client):
        """
        GIVEN valid payload
        WHEN POST to create endpoint
        THEN return 201 Created
        """
        url = reverse("api:v1:endpoint-name-list")
        payload = {
            "name": "Test Resource",
            "description": "Test description"
        }
        response = authenticated_client.post(url, payload, format="json")

        assert response.status_code == 201
        assert response.data["name"] == payload["name"]
```

### Template 2: Endpoint Multi-Tenant

```python
import pytest
from django.urls import reverse

@pytest.mark.django_db
class TestTenantScopedEndpoint:
    """
    Tests para endpoints que requieren contexto de tenant.
    Usa fixtures: tenant_client (incluye user + tenant + membership)
    """

    def test_requires_tenant_header(self, authenticated_client):
        """
        GIVEN authenticated user WITHOUT tenant header
        WHEN requesting tenant-scoped endpoint
        THEN return 400 or 403
        """
        url = reverse("api:v1:tenant-resource-list")
        response = authenticated_client.get(url)
        # Sin header X-Tenant, debe fallar
        assert response.status_code in [400, 403]

    def test_access_with_tenant_context(self, tenant_client):
        """
        GIVEN user with tenant membership (tenant_client fixture)
        WHEN requesting tenant-scoped endpoint
        THEN return 200 OK with tenant data
        """
        url = reverse("api:v1:tenant-resource-list")
        response = tenant_client.get(url)

        assert response.status_code == 200

    def test_cannot_access_other_tenant_data(self, tenant_client, db):
        """
        GIVEN user in Tenant A
        WHEN trying to access Tenant B resources
        THEN return 404 or 403
        """
        from multitenant.models import Tenant

        # Crear otro tenant
        other_tenant = Tenant.objects.create(
            name="Other Org",
            slug="other-org",
            schema_name="other_org"
        )

        # Intentar acceder a recursos del otro tenant
        url = reverse("api:v1:tenant-resource-detail", args=[other_tenant.id])
        response = tenant_client.get(url)

        assert response.status_code in [403, 404]
```

### Template 3: Endpoint con Permisos RBAC

```python
import pytest
from django.urls import reverse

@pytest.mark.django_db
class TestRBACEndpoint:
    """
    Tests para endpoints con control de permisos por rol.
    """

    def test_owner_can_manage(self, tenant_client, owner_membership):
        """
        GIVEN user with owner role
        WHEN performing admin action
        THEN return 200 OK
        """
        url = reverse("api:v1:admin-action")
        response = tenant_client.post(url, {}, format="json")
        assert response.status_code in [200, 201]

    def test_member_cannot_manage(self, api_client, member_membership):
        """
        GIVEN user with member role (not owner)
        WHEN performing admin action
        THEN return 403 Forbidden
        """
        api_client.force_authenticate(user=member_membership.user)
        api_client.defaults["HTTP_X_TENANT"] = member_membership.organization.slug

        url = reverse("api:v1:admin-action")
        response = api_client.post(url, {}, format="json")

        assert response.status_code == 403
```

## Fixtures Disponibles (de conftest.py)

| Fixture | Descripción | Uso |
|---------|-------------|-----|
| `api_client` | APIClient sin autenticar | Tests 401 |
| `user` | Usuario básico | Crear usuarios |
| `authenticated_client` | APIClient con user autenticado | Tests simples |
| `tenant` | Tenant de prueba | Multi-tenant |
| `owner_role` / `member_role` | Roles del sistema | Tests RBAC |
| `owner_membership` | User como owner de tenant | Tests de owner |
| `member_membership` | User como member de tenant | Tests de member |
| `tenant_client` | APIClient con user + tenant + header | Tests multi-tenant |

## Checklist de Auditoría

- [ ] ¿Usa fixtures de conftest.py en lugar de crear propios?
- [ ] ¿El test cubre el caso 401 (Unauthenticated)?
- [ ] ¿El test cubre validaciones de input (400 Bad Request)?
- [ ] ¿Se usa `force_authenticate` solo cuando no hay fixture disponible?
- [ ] ¿Se prueba el aislamiento multi-tenant si aplica?
- [ ] ¿Se prueban los permisos RBAC si el endpoint los usa?

## Errores Comunes

| Error | Causa | Solución |
|-------|-------|----------|
| `fixture 'api_client' not found` | Test fuera de `tests/` | Mover a directorio `tests/` |
| `401` inesperado | Falta autenticación | Usar `authenticated_client` o `tenant_client` |
| `403` en tenant endpoint | Falta header X-Tenant | Usar `tenant_client` fixture |
| Datos de otro tenant visibles | No hay filtro por tenant | Verificar queryset del ViewSet |

## Referencias

- `tests/conftest.py` - Fixtures disponibles
- `src/api/v1/urls.py` - Rutas de API
- `src/core/models.py` - Modelos User, Membership, Role
