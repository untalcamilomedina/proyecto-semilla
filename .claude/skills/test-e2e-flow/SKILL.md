---
name: test-e2e-flow
description: Genera tests de integración que simulan flujos completos de usuario (Chain of Requests).
author: Proyecto Semilla Architecture Team
version: 2.0.0
---

# Skill: Test E2E Flow

Esta skill se enfoca en verificar que los componentes del sistema (Integraciones, DB, Tasks, API) funcionen en orquesta, usando fixtures del proyecto.

## Objetivo

Validar flujos de negocio complejos donde el output de un endpoint es el input del siguiente.

## Prerrequisitos

- Fixtures de `tests/conftest.py`
- Servicios de negocio en `src/` (ej. `src/billing/`, `src/core/`)
- Si pruebas una integración externa, su módulo `Client -> Adapter -> Service` (ver skill `new-integration-module`)

## Template de Implementación

### Template 1: Flujo de Importación desde una API Externa

El ejemplo usa la integración ficticia "Acme CRM" (`src/integrations_acme/`) y el endpoint que tú expongas para ella. Sustituye nombres, rutas y campos por los de tu integración.

```python
import pytest
from unittest.mock import patch, MagicMock

@pytest.mark.django_db
class TestAcmeImportFlow:
    """
    E2E: Usuario importa recursos desde Acme CRM y los consulta en la API.
    Flow:
    1. Authenticate (via fixture)
    2. Mock Acme CRM API response
    3. POST /integrations/acme/import
    4. GET /items/{id}
    5. Verify canonical spec content
    """

    def test_full_acme_import_flow(self, tenant_client, tenant):
        """
        GIVEN authenticated user with tenant context
        WHEN importing resources from Acme CRM
        THEN the item is created and retrievable with correct spec
        """
        # 1. Mock Acme CRM API (solo lo externo)
        mock_external_response = {
            "id": "res-1",
            "name": "Customers",
            "properties": {"fields": ["email", "phone", "company"]}
        }

        # Patch apunta a donde se IMPORTA la clase Client en services.py
        with patch("integrations_acme.services.AcmeClient") as MockAcmeClient:
            mock_instance = MagicMock()
            mock_instance.get_resource.return_value = mock_external_response
            MockAcmeClient.return_value = mock_instance

            # 2. Trigger Import (endpoint creado por ti para tu integración)
            response = tenant_client.post(
                "/api/v1/integrations/acme/import",
                {
                    "resource_id": "res-1",
                    "api_key": "fake-acme-token"
                },
                format="json"
            )

            assert response.status_code in [200, 201], \
                f"Import failed: {response.data}"
            item_id = response.data["id"]

        # 3. Fetch Created Item (fuera del mock - usa DB real)
        resp_item = tenant_client.get(f"/api/v1/items/{item_id}/")
        assert resp_item.status_code == 200

        # 4. Verify Spec Integrity (modelo canónico de tu integración)
        assert resp_item.data["name"] == "Customers"
        assert "email" in resp_item.data["fields"]

        # 5. Verify Database State (ajusta a tu modelo)
        # from integrations_acme.models import Item
        # item = Item.objects.get(id=item_id)
        # assert item.name == "Customers"


    def test_acme_import_invalid_resource_returns_error(self, tenant_client):
        """
        GIVEN invalid resource ID
        WHEN importing
        THEN return 400 with descriptive error
        """
        with patch("integrations_acme.services.AcmeClient") as MockAcmeClient:
            mock_instance = MagicMock()
            mock_instance.get_resource.side_effect = Exception("Resource not found")
            MockAcmeClient.return_value = mock_instance

            response = tenant_client.post(
                "/api/v1/integrations/acme/import",
                {"resource_id": "invalid-resource", "api_key": "fake-token"},
                format="json"
            )

            assert response.status_code == 400
            assert "error" in response.data or "detail" in response.data
```

### Template 2: Flujo de Webhook Externo (Billing)

Este flujo existe de verdad en el boilerplate (`src/billing/`): un evento externo de Stripe dispara el handler y actualiza el estado de la suscripción. Ver el ejemplo completo en `tests/test_billing_webhooks.py`.

```python
import pytest
from unittest.mock import MagicMock
from djstripe.models import Event
from billing.webhooks import handle_stripe_event
from billing.models import Subscription
from multitenant.schema import schema_context

@pytest.mark.django_db(transaction=True)
class TestBillingWebhookFlow:
    """
    E2E: Un evento del proveedor de pagos activa la suscripción del tenant.
    """

    def test_subscription_updated_flow(self, tenant, plan):
        """
        GIVEN an existing incomplete subscription
        WHEN the external provider sends 'customer.subscription.updated'
        THEN the subscription becomes active in the tenant schema
        """
        subscription_id = "sub_e2e_demo"

        with schema_context(tenant.schema_name):
            sub = Subscription.objects.create(
                organization=tenant,
                plan=plan,
                stripe_subscription_id=subscription_id,
                status="incomplete"
            )

        # Mock del evento externo (solo lo externo se simula)
        event_mock = MagicMock(spec=Event)
        event_mock.type = "customer.subscription.updated"
        event_mock.data = {
            "object": {
                "id": subscription_id,
                "status": "active",
                "metadata": {
                    "tenant_schema": tenant.schema_name,
                    "tenant_id": str(tenant.id)
                },
                "items": {"data": []}
            }
        }

        handle_stripe_event(sender=None, event=event_mock)

        # Verify Database State
        with schema_context(tenant.schema_name):
            sub.refresh_from_db()
            assert sub.status == "active"
```

### Template 3: Flujo de Autenticación + Operaciones

```python
import pytest

@pytest.mark.django_db
class TestAuthenticationFlow:
    """
    E2E: Flujo completo de registro -> login -> operación protegida.
    """

    def test_register_login_access_flow(self, api_client, db):
        """
        GIVEN a new user
        WHEN registering, logging in, and accessing protected resource
        THEN all operations succeed in sequence
        """
        # 1. Register
        register_response = api_client.post(
            "/api/v1/auth/register/",
            {
                "email": "newuser@example.com",
                "password": "SecurePass123!",
                "password_confirm": "SecurePass123!",
                "first_name": "New",
                "last_name": "User"
            },
            format="json"
        )
        assert register_response.status_code == 201

        # 2. Login
        login_response = api_client.post(
            "/api/v1/auth/login/",
            {
                "email": "newuser@example.com",
                "password": "SecurePass123!"
            },
            format="json"
        )
        assert login_response.status_code == 200
        token = login_response.data.get("access") or login_response.data.get("token")
        assert token is not None

        # 3. Access Protected Resource
        api_client.credentials(HTTP_AUTHORIZATION=f"Bearer {token}")
        protected_response = api_client.get("/api/v1/users/me/")
        assert protected_response.status_code == 200
        assert protected_response.data["email"] == "newuser@example.com"
```

### Template 4: Flujo CRUD Completo

Usa un recurso real del boilerplate (`/api/v1/roles/`) — adapta payload y ruta a tu recurso.

```python
import pytest

@pytest.mark.django_db
class TestCRUDFlow:
    """
    E2E: Create -> Read -> Update -> Delete de un recurso.
    """

    def test_full_crud_lifecycle(self, tenant_client, tenant):
        """
        GIVEN authenticated user with tenant
        WHEN performing full CRUD cycle
        THEN all operations succeed and data is consistent
        """
        base_url = "/api/v1/roles/"

        # CREATE
        create_resp = tenant_client.post(
            base_url,
            {"name": "Test Role", "description": "", "position": 1, "permissions": []},
            format="json"
        )
        assert create_resp.status_code == 201
        role_id = create_resp.data["id"]

        # READ
        read_resp = tenant_client.get(f"{base_url}{role_id}/")
        assert read_resp.status_code == 200
        assert read_resp.data["name"] == "Test Role"

        # UPDATE
        update_resp = tenant_client.patch(
            f"{base_url}{role_id}/",
            {"name": "Updated Role"},
            format="json"
        )
        assert update_resp.status_code == 200
        assert update_resp.data["name"] == "Updated Role"

        # Verify update persisted
        verify_resp = tenant_client.get(f"{base_url}{role_id}/")
        assert verify_resp.data["name"] == "Updated Role"

        # DELETE
        delete_resp = tenant_client.delete(f"{base_url}{role_id}/")
        assert delete_resp.status_code == 204

        # Verify deletion
        gone_resp = tenant_client.get(f"{base_url}{role_id}/")
        assert gone_resp.status_code == 404
```

### Template 5: Flujo con Dependencias entre Recursos

Ejemplo genérico padre -> hijo. Sustituye `projects`/`items` por tus recursos reales.

```python
import pytest

@pytest.mark.django_db
class TestResourceDependencyFlow:
    """
    E2E: Crear recurso padre -> Crear hijo -> Verificar relación.
    """

    def test_project_with_items_flow(self, tenant_client, tenant):
        """
        GIVEN authenticated user
        WHEN creating a parent resource and adding children
        THEN resources are correctly linked
        """
        # 1. Create Parent
        project_resp = tenant_client.post(
            "/api/v1/projects/",
            {"name": "My Project", "description": "Test project"},
            format="json"
        )
        assert project_resp.status_code == 201
        project_id = project_resp.data["id"]

        # 2. Create Child linked to Parent
        item_resp = tenant_client.post(
            "/api/v1/items/",
            {
                "name": "Project Item",
                "fields": ["title", "status"],
                "project": project_id
            },
            format="json"
        )
        assert item_resp.status_code == 201
        item_id = item_resp.data["id"]

        # 3. Verify linkage via Parent endpoint
        project_detail = tenant_client.get(f"/api/v1/projects/{project_id}/")
        assert project_detail.status_code == 200

        # Parent should list its children
        items = project_detail.data.get("items", [])
        item_ids = [i["id"] if isinstance(i, dict) else i for i in items]
        assert item_id in item_ids or str(item_id) in [str(x) for x in item_ids]
```

## Fixtures Utilizados

| Fixture | Uso en E2E |
|---------|------------|
| `api_client` | Flujos de autenticación (sin auth previa) |
| `tenant_client` | Flujos que requieren user + tenant |
| `tenant` | Acceso al objeto tenant para verificaciones DB |
| `user` | Verificaciones de usuario |

## Checklist de E2E

- [ ] ¿El test cubre el "Happy Path" completo?
- [ ] ¿El test mockea _solo_ lo externo (APIs de terceros, proveedor de pagos, IA) y usa componentes reales internos (DB/Service)?
- [ ] ¿Se verifica el estado final de la base de datos?
- [ ] ¿Se usan fixtures de conftest.py en lugar de crear usuarios manualmente?
- [ ] ¿Los imports están completos? (`from unittest.mock import patch, MagicMock`)
- [ ] ¿Se verifica la cadena completa de requests?

## Errores Comunes

| Error | Causa | Solución |
|-------|-------|----------|
| `NameError: patch not defined` | Falta import | `from unittest.mock import patch, MagicMock` |
| `NameError: setup_user not defined` | Función inexistente | Usar fixture `user` o `tenant_client` |
| Test pasa pero DB vacía | Mock muy amplio | Mockear solo el client externo, no el service |
| `IntegrityError` | Falta tenant en modelo | Usar `tenant_client` que incluye tenant context |

## Referencias

- `tests/conftest.py` - Fixtures disponibles
- `tests/test_billing_webhooks.py` - Ejemplo real de flujo con evento externo
- `tests/test_api_v1.py` - Ejemplo real de requests autenticados a la API v1
