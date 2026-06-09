---
name: test-e2e-flow
description: Genera tests de integración que simulan flujos completos de usuario (Chain of Requests).
author: AppNotion Architecture Team
version: 2.0.0
---

# Skill: Test E2E Flow

Esta skill se enfoca en verificar que los componentes del sistema (Integraciones, DB, Tasks, API) funcionen en orquesta, usando fixtures del proyecto.

## Objetivo

Validar flujos de negocio complejos donde el output de un endpoint es el input del siguiente.

## Prerrequisitos

- Fixtures de `tests/conftest.py`
- Servicios de integración en `src/integrations/`
- Modelos canónicos en `src/integrations/schemas.py`

## Template de Implementación

### Template 1: Flujo de Importación Miro

```python
import pytest
from unittest.mock import patch, MagicMock

@pytest.mark.django_db
class TestMiroImportFlow:
    """
    E2E: Usuario importa un tablero de Miro y visualiza el diagrama.
    Flow:
    1. Authenticate (via fixture)
    2. Mock Miro API response
    3. POST /miro/import
    4. GET /diagrams/{id}
    5. Verify ERDSpec content
    """

    def test_full_miro_import_flow(self, tenant_client, tenant):
        """
        GIVEN authenticated user with tenant context
        WHEN importing a Miro board
        THEN diagram is created and retrievable with correct spec
        """
        # 1. Mock Miro API (solo lo externo)
        mock_board_items = [
            {
                "id": "item-1",
                "type": "shape",
                "data": {"content": "Users Table"},
                "position": {"x": 100, "y": 100}
            },
            {
                "id": "item-2",
                "type": "shape",
                "data": {"content": "Orders Table"},
                "position": {"x": 300, "y": 100}
            },
            {
                "id": "conn-1",
                "type": "connector",
                "startItem": {"id": "item-1"},
                "endItem": {"id": "item-2"}
            }
        ]

        with patch("integrations.miro.client.MiroClient") as MockMiroClient:
            mock_instance = MagicMock()
            mock_instance.get_board_items.return_value = mock_board_items
            MockMiroClient.return_value = mock_instance

            # 2. Trigger Import
            response = tenant_client.post(
                "/api/v1/integrations/miro/import",
                {
                    "board_id": "test-board-123",
                    "api_key": "fake-miro-token"
                },
                format="json"
            )

            assert response.status_code in [200, 201], \
                f"Import failed: {response.data}"
            diagram_id = response.data["id"]

        # 3. Fetch Created Diagram (fuera del mock - usa DB real)
        resp_diagram = tenant_client.get(f"/api/v1/diagrams/{diagram_id}/")
        assert resp_diagram.status_code == 200
        assert resp_diagram.data["type"] == "erd"

        # 4. Verify Spec Integrity
        spec = resp_diagram.data["spec"]
        assert "entities" in spec
        assert len(spec["entities"]) >= 2  # Users + Orders

        # 5. Verify Database State
        from integrations.models import Diagram
        diagram = Diagram.objects.get(id=diagram_id)
        assert diagram.name is not None


    def test_miro_import_invalid_board_returns_error(self, tenant_client):
        """
        GIVEN invalid board ID
        WHEN importing
        THEN return 400 with descriptive error
        """
        with patch("integrations.miro.client.MiroClient") as MockMiroClient:
            mock_instance = MagicMock()
            mock_instance.get_board_items.side_effect = Exception("Board not found")
            MockMiroClient.return_value = mock_instance

            response = tenant_client.post(
                "/api/v1/integrations/miro/import",
                {"board_id": "invalid-board", "api_key": "fake-token"},
                format="json"
            )

            assert response.status_code == 400
            assert "error" in response.data or "detail" in response.data
```

### Template 2: Flujo de Importación Notion

```python
import pytest
from unittest.mock import patch, MagicMock

@pytest.mark.django_db
class TestNotionImportFlow:
    """
    E2E: Usuario importa una página de Notion como flujo de proceso.
    """

    def test_full_notion_import_flow(self, tenant_client, tenant):
        """
        GIVEN authenticated user
        WHEN importing a Notion page
        THEN flow diagram is created with correct nodes/edges
        """
        mock_page_blocks = [
            {"type": "heading_1", "heading_1": {"text": [{"plain_text": "Process Start"}]}},
            {"type": "bulleted_list_item", "bulleted_list_item": {"text": [{"plain_text": "Step 1"}]}},
            {"type": "bulleted_list_item", "bulleted_list_item": {"text": [{"plain_text": "Step 2"}]}},
            {"type": "bulleted_list_item", "bulleted_list_item": {"text": [{"plain_text": "Step 3"}]}},
        ]

        with patch("integrations.notion.client.NotionClient") as MockNotionClient:
            mock_instance = MagicMock()
            mock_instance.get_page_blocks.return_value = mock_page_blocks
            MockNotionClient.return_value = mock_instance

            # Import
            response = tenant_client.post(
                "/api/v1/integrations/notion/import",
                {
                    "page_id": "notion-page-uuid",
                    "api_key": "fake-notion-token"
                },
                format="json"
            )

            assert response.status_code in [200, 201]
            diagram_id = response.data["id"]

        # Verify
        resp_diagram = tenant_client.get(f"/api/v1/diagrams/{diagram_id}/")
        assert resp_diagram.status_code == 200
        assert resp_diagram.data["type"] == "flow"

        spec = resp_diagram.data["spec"]
        assert "nodes" in spec
        assert len(spec["nodes"]) >= 3  # At least 3 steps
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
        base_url = "/api/v1/diagrams/"

        # CREATE
        create_resp = tenant_client.post(
            base_url,
            {"name": "Test Diagram", "type": "flow", "spec": {"nodes": [], "edges": []}},
            format="json"
        )
        assert create_resp.status_code == 201
        diagram_id = create_resp.data["id"]

        # READ
        read_resp = tenant_client.get(f"{base_url}{diagram_id}/")
        assert read_resp.status_code == 200
        assert read_resp.data["name"] == "Test Diagram"

        # UPDATE
        update_resp = tenant_client.patch(
            f"{base_url}{diagram_id}/",
            {"name": "Updated Diagram"},
            format="json"
        )
        assert update_resp.status_code == 200
        assert update_resp.data["name"] == "Updated Diagram"

        # Verify update persisted
        verify_resp = tenant_client.get(f"{base_url}{diagram_id}/")
        assert verify_resp.data["name"] == "Updated Diagram"

        # DELETE
        delete_resp = tenant_client.delete(f"{base_url}{diagram_id}/")
        assert delete_resp.status_code == 204

        # Verify deletion
        gone_resp = tenant_client.get(f"{base_url}{diagram_id}/")
        assert gone_resp.status_code == 404
```

### Template 5: Flujo con Dependencias entre Recursos

```python
import pytest

@pytest.mark.django_db
class TestResourceDependencyFlow:
    """
    E2E: Crear recurso padre -> Crear hijo -> Verificar relación.
    """

    def test_project_with_diagrams_flow(self, tenant_client, tenant):
        """
        GIVEN authenticated user
        WHEN creating project and adding diagrams
        THEN resources are correctly linked
        """
        # 1. Create Project
        project_resp = tenant_client.post(
            "/api/v1/projects/",
            {"name": "My Project", "description": "Test project"},
            format="json"
        )
        assert project_resp.status_code == 201
        project_id = project_resp.data["id"]

        # 2. Create Diagram linked to Project
        diagram_resp = tenant_client.post(
            "/api/v1/diagrams/",
            {
                "name": "Project Diagram",
                "type": "erd",
                "spec": {"entities": []},
                "project": project_id
            },
            format="json"
        )
        assert diagram_resp.status_code == 201
        diagram_id = diagram_resp.data["id"]

        # 3. Verify linkage via Project endpoint
        project_detail = tenant_client.get(f"/api/v1/projects/{project_id}/")
        assert project_detail.status_code == 200

        # Project should list its diagrams
        diagrams = project_detail.data.get("diagrams", [])
        diagram_ids = [d["id"] if isinstance(d, dict) else d for d in diagrams]
        assert diagram_id in diagram_ids or str(diagram_id) in [str(x) for x in diagram_ids]
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
- [ ] ¿El test mockea _solo_ lo externo (Miro/Notion/AI) y usa componentes reales internos (DB/Service)?
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
- `src/integrations/miro/` - Cliente y servicios Miro
- `src/integrations/notion/` - Cliente y servicios Notion
- `src/integrations/schemas.py` - Modelos Pydantic (FlowSpec, ERDSpec)
