---
name: test-e2e-flow
description: Genera tests de integración que simulan flujos completos de usuario (Chain of Requests).
author: AppNotion Architecture Team
version: 1.0.0
---

# Skill: Test E2E Flow

Esta skill se enfoca en verificar que los componentes del sistema (Integraciones, DB, Tasks, API) funcionen en orquesta.

## Objetivo

Validar flujos de negocio complejos donde el output de un endpoint es el input del siguiente.

## Template de Implementación

```python
import pytest
from rest_framework.test import APIClient

@pytest.mark.django_db
def test_full_miro_import_flow():
    """
    Scenario: User imports a board from Miro and visualizes it.
    Flow:
    1. Authenticate
    2. Mock Miro API response
    3. POST /miro/import
    4. GET /diagrams/{id}
    5. Verify ERDSpec content
    """
    client = APIClient()
    user = setup_user() # fixture
    client.force_authenticate(user=user)

    # 1. Trigger Import
    with patch("integrations.miro.services.MiroClient") as MockClient:
        # Configurar Mock para devolver items de tablero
        MockClient.return_value.get_board_items.return_value = [...]

        response = client.post("/api/v1/integrations/miro/import", {
            "token": "fake-token",
            "board_id": "123"
        })
        assert response.status_code == 200
        diagram_id = response.data["id"]

    # 2. Fetch Diagram
    resp_diag = client.get(f"/api/v1/diagrams/{diagram_id}")
    assert resp_diag.status_code == 200
    assert resp_diag.data["type"] == "erd"

    # 3. Verify Integrity
    spec = resp_diag.data["spec"]
    assert len(spec["entities"]) > 0
```

## Checklist de E2E

- [ ] ¿El test cubre el "Happy Path" completo?
- [ ] ¿El test mockea _solo_ lo externo (Miro/Notion/AI) y usa componentes reales internos (DB/Service)?
- [ ] ¿Se verifica el estado final de la base de datos?
