---
name: test-api-endpoint
description: Guía para crear tests de integración HTTP que validan endpoints de la API REST.
author: AppNotion Dev Team
version: 1.0.0
---

# Skill: Test de Endpoint API

Esta skill estandariza la creación de tests de integración que prueban endpoints reales de la API usando Django REST Framework's `APIClient`. Valida responses HTTP, permisos RBAC, y comportamiento multi-tenant.

## Prerrequisitos

- [ ] `pytest` y `pytest-django` instalados.
- [ ] Endpoint implementado en `api/v1/urls.py`.
- [ ] Fixtures de `conftest.py` disponibles.

## Cuándo Usar

- Después de implementar un ViewSet.
- Para validar permisos (RBAC) antes del frontend.
- Para asegurar que la API responde correctamente.
- Antes de marcar un endpoint como "listo para frontend".

## Arquitectura de Tests

```
tests/
├── conftest.py              # Fixtures compartidos
├── test_api_v1.py           # Tests generales de API
├── test_<feature>_api.py    # Tests por feature
├── audit_<integration>.py   # Tests de lógica (mocks)
└── factories/               # Factories de datos (opcional)
    └── user_factory.py
```

---

## Proceso

### Paso 1: Identificar el Endpoint

Documentar:
- **URL**: `/api/v1/resource/`
- **Métodos**: GET, POST, PUT, DELETE
- **Permisos requeridos**: `view_resource`, `manage_resource`
- **Tenant-aware**: Sí/No

### Paso 2: Crear Archivo de Test

**Ubicación:** `tests/test_<feature>_api.py`

### Paso 3: Usar Template según Caso

---

## Templates

### Template A: Test CRUD Básico

```python
import pytest
from rest_framework import status
from rest_framework.test import APIClient

from core.models import User, Role, Membership
from multitenant.models import Tenant


@pytest.fixture
def setup_tenant_context(db):
    """Setup completo de tenant con usuario autenticado."""
    # Crear tenant
    tenant = Tenant.objects.create(
        name="Test Org",
        slug="test-org",
        schema_name="test_org",
    )

    # Crear usuario
    user = User.objects.create_user(
        username="testuser",
        email="test@example.com",
        password="testpass123",
    )

    # Crear rol y membership
    role = Role.objects.create(
        organization=tenant,
        name="Owner",
        slug="owner",
        is_system=True,
    )

    Membership.objects.create(
        user=user,
        organization=tenant,
        role=role,
        is_active=True,
    )

    # Retornar contexto
    return {
        "tenant": tenant,
        "user": user,
        "role": role,
    }


@pytest.fixture
def authenticated_client(setup_tenant_context):
    """Cliente autenticado con contexto de tenant."""
    client = APIClient()
    client.force_authenticate(user=setup_tenant_context["user"])
    client.defaults["HTTP_X_TENANT"] = setup_tenant_context["tenant"].slug
    return client


class TestResourceEndpoint:
    """Tests para /api/v1/resources/"""

    endpoint = "/api/v1/resources/"

    # ==================== LIST ====================
    @pytest.mark.django_db
    def test_list_returns_200(self, authenticated_client):
        """GET /resources/ devuelve 200 con lista."""
        response = authenticated_client.get(self.endpoint)

        assert response.status_code == status.HTTP_200_OK
        assert isinstance(response.data, list)

    @pytest.mark.django_db
    def test_list_requires_authentication(self, api_client):
        """GET /resources/ sin auth devuelve 401."""
        response = api_client.get(self.endpoint)

        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    # ==================== CREATE ====================
    @pytest.mark.django_db
    def test_create_returns_201(self, authenticated_client):
        """POST /resources/ crea recurso correctamente."""
        payload = {
            "name": "Test Resource",
            "description": "Test description",
        }

        response = authenticated_client.post(
            self.endpoint,
            payload,
            format="json",
        )

        assert response.status_code == status.HTTP_201_CREATED
        assert response.data["name"] == "Test Resource"
        assert "id" in response.data

    @pytest.mark.django_db
    def test_create_validates_required_fields(self, authenticated_client):
        """POST /resources/ valida campos requeridos."""
        payload = {}  # Falta 'name'

        response = authenticated_client.post(
            self.endpoint,
            payload,
            format="json",
        )

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "name" in response.data

    # ==================== RETRIEVE ====================
    @pytest.mark.django_db
    def test_retrieve_returns_200(self, authenticated_client, setup_tenant_context):
        """GET /resources/{id}/ devuelve recurso."""
        # Crear recurso primero
        from myapp.models import Resource
        resource = Resource.objects.create(
            name="Test",
            organization=setup_tenant_context["tenant"],
        )

        response = authenticated_client.get(f"{self.endpoint}{resource.id}/")

        assert response.status_code == status.HTTP_200_OK
        assert response.data["id"] == resource.id

    @pytest.mark.django_db
    def test_retrieve_returns_404_for_nonexistent(self, authenticated_client):
        """GET /resources/{id}/ devuelve 404 si no existe."""
        response = authenticated_client.get(f"{self.endpoint}99999/")

        assert response.status_code == status.HTTP_404_NOT_FOUND

    # ==================== UPDATE ====================
    @pytest.mark.django_db
    def test_update_returns_200(self, authenticated_client, setup_tenant_context):
        """PUT /resources/{id}/ actualiza recurso."""
        from myapp.models import Resource
        resource = Resource.objects.create(
            name="Original",
            organization=setup_tenant_context["tenant"],
        )

        payload = {"name": "Updated"}
        response = authenticated_client.put(
            f"{self.endpoint}{resource.id}/",
            payload,
            format="json",
        )

        assert response.status_code == status.HTTP_200_OK
        assert response.data["name"] == "Updated"

    # ==================== DELETE ====================
    @pytest.mark.django_db
    def test_delete_returns_204(self, authenticated_client, setup_tenant_context):
        """DELETE /resources/{id}/ elimina recurso."""
        from myapp.models import Resource
        resource = Resource.objects.create(
            name="To Delete",
            organization=setup_tenant_context["tenant"],
        )

        response = authenticated_client.delete(f"{self.endpoint}{resource.id}/")

        assert response.status_code == status.HTTP_204_NO_CONTENT
        assert not Resource.objects.filter(id=resource.id).exists()
```

### Template B: Test de Permisos (RBAC)

```python
import pytest
from rest_framework import status


class TestResourcePermissions:
    """Tests de permisos para /api/v1/resources/"""

    endpoint = "/api/v1/resources/"

    @pytest.mark.django_db
    def test_viewer_cannot_create(self, api_client, setup_tenant_context):
        """Usuario con rol viewer NO puede crear recursos."""
        # Crear usuario viewer
        viewer = User.objects.create_user(
            username="viewer",
            email="viewer@example.com",
            password="pass123",
        )
        viewer_role = Role.objects.create(
            organization=setup_tenant_context["tenant"],
            name="Viewer",
            slug="viewer",
        )
        Membership.objects.create(
            user=viewer,
            organization=setup_tenant_context["tenant"],
            role=viewer_role,
        )

        api_client.force_authenticate(user=viewer)
        api_client.defaults["HTTP_X_TENANT"] = setup_tenant_context["tenant"].slug

        response = api_client.post(
            self.endpoint,
            {"name": "Test"},
            format="json",
        )

        assert response.status_code == status.HTTP_403_FORBIDDEN

    @pytest.mark.django_db
    def test_owner_can_create(self, authenticated_client):
        """Usuario con rol owner SÍ puede crear recursos."""
        response = authenticated_client.post(
            self.endpoint,
            {"name": "Test"},
            format="json",
        )

        assert response.status_code == status.HTTP_201_CREATED

    @pytest.mark.django_db
    def test_user_only_sees_own_tenant_resources(
        self,
        authenticated_client,
        setup_tenant_context
    ):
        """Usuario solo ve recursos de su tenant."""
        from myapp.models import Resource

        # Crear recurso en otro tenant
        other_tenant = Tenant.objects.create(
            name="Other Org",
            slug="other-org",
            schema_name="other_org",
        )
        Resource.objects.create(
            name="Other Tenant Resource",
            organization=other_tenant,
        )

        # Crear recurso en tenant actual
        Resource.objects.create(
            name="My Resource",
            organization=setup_tenant_context["tenant"],
        )

        response = authenticated_client.get(self.endpoint)

        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) == 1
        assert response.data[0]["name"] == "My Resource"
```

### Template C: Test con API Key

```python
import pytest
from rest_framework import status

from api.models import ApiKey


class TestApiKeyAuthentication:
    """Tests de autenticación con API Key."""

    endpoint = "/api/v1/resources/"

    @pytest.mark.django_db
    def test_api_key_authentication_works(self, api_client, setup_tenant_context):
        """API Key válida permite acceso."""
        # Generar API Key
        _key_obj, plain_key = ApiKey.generate(
            organization=setup_tenant_context["tenant"],
            user=setup_tenant_context["user"],
            name="test-key",
        )

        response = api_client.get(
            self.endpoint,
            HTTP_AUTHORIZATION=f"Bearer {plain_key}",
            HTTP_HOST=f"{setup_tenant_context['tenant'].slug}.acme.dev",
        )

        assert response.status_code == status.HTTP_200_OK

    @pytest.mark.django_db
    def test_invalid_api_key_returns_401(self, api_client, setup_tenant_context):
        """API Key inválida devuelve 401."""
        response = api_client.get(
            self.endpoint,
            HTTP_AUTHORIZATION="Bearer invalid-key-12345",
            HTTP_HOST=f"{setup_tenant_context['tenant'].slug}.acme.dev",
        )

        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    @pytest.mark.django_db
    def test_revoked_api_key_returns_401(self, api_client, setup_tenant_context):
        """API Key revocada devuelve 401."""
        key_obj, plain_key = ApiKey.generate(
            organization=setup_tenant_context["tenant"],
            user=setup_tenant_context["user"],
            name="revoked-key",
        )
        key_obj.is_revoked = True
        key_obj.save()

        response = api_client.get(
            self.endpoint,
            HTTP_AUTHORIZATION=f"Bearer {plain_key}",
            HTTP_HOST=f"{setup_tenant_context['tenant'].slug}.acme.dev",
        )

        assert response.status_code == status.HTTP_401_UNAUTHORIZED
```

### Template D: Test de Validación de Payload

```python
import pytest
from rest_framework import status


class TestResourceValidation:
    """Tests de validación de datos."""

    endpoint = "/api/v1/resources/"

    @pytest.mark.django_db
    @pytest.mark.parametrize("invalid_payload,expected_error_field", [
        ({}, "name"),  # Campo requerido faltante
        ({"name": ""}, "name"),  # String vacío
        ({"name": "x" * 256}, "name"),  # Muy largo
        ({"name": "Valid", "email": "invalid"}, "email"),  # Email inválido
    ])
    def test_validation_errors(
        self,
        authenticated_client,
        invalid_payload,
        expected_error_field
    ):
        """POST con datos inválidos devuelve 400 con campo específico."""
        response = authenticated_client.post(
            self.endpoint,
            invalid_payload,
            format="json",
        )

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert expected_error_field in response.data

    @pytest.mark.django_db
    def test_duplicate_slug_returns_400(self, authenticated_client, setup_tenant_context):
        """POST con slug duplicado devuelve 400."""
        from myapp.models import Resource
        Resource.objects.create(
            name="Existing",
            slug="existing-slug",
            organization=setup_tenant_context["tenant"],
        )

        response = authenticated_client.post(
            self.endpoint,
            {"name": "New", "slug": "existing-slug"},
            format="json",
        )

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "slug" in response.data
```

---

## Ejecución de Tests

```bash
# Todos los tests
pytest tests/

# Tests de un archivo específico
pytest tests/test_resources_api.py

# Tests de una clase
pytest tests/test_resources_api.py::TestResourceEndpoint

# Test específico
pytest tests/test_resources_api.py::TestResourceEndpoint::test_create_returns_201

# Con coverage
pytest tests/ --cov=src --cov-report=html

# En Docker
docker compose exec web pytest tests/test_resources_api.py -v
```

---

## Checklist de Verificación

### Cobertura Mínima
- [ ] Test de autenticación (401 sin auth)
- [ ] Test de LIST (GET /)
- [ ] Test de CREATE (POST /)
- [ ] Test de RETRIEVE (GET /{id}/)
- [ ] Test de UPDATE (PUT /{id}/)
- [ ] Test de DELETE (DELETE /{id}/)
- [ ] Test de 404 para recursos inexistentes

### Permisos (RBAC)
- [ ] Test de permisos insuficientes (403)
- [ ] Test de permisos correctos (200/201)
- [ ] Test de aislamiento por tenant

### Validación
- [ ] Test de campos requeridos
- [ ] Test de formatos inválidos
- [ ] Test de unicidad (si aplica)

---

## Errores Comunes

### Error: `TransactionTestCase` vs `TestCase`

**Causa:** Tests con multitenancy requieren transacciones reales.

**Solución:** Usar `@pytest.mark.django_db(transaction=True)`.

### Error: "No schema selected"

**Causa:** Falta contexto de tenant en tests multi-tenant.

**Solución:** Usar `schema_context()` o headers HTTP correctos.

### Error: Fixtures no se limpian

**Causa:** Datos persisten entre tests.

**Solución:** Usar fixtures con scope `function` (default).

---

## Referencias

- [pytest-django Docs](https://pytest-django.readthedocs.io/)
- [DRF Testing](https://www.django-rest-framework.org/api-guide/testing/)
- [Tests existentes](../../tests/test_api_v1.py)
- [Fixtures](../../tests/conftest.py)

---

*Última actualización: 2025-02-04*
