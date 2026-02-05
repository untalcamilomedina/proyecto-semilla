---
name: test-api-endpoint
description: Genera tests unitarios robustos para endpoints de API (DRF), validando Auth, Permisos y Status Codes.
author: AppNotion Architecture Team
version: 1.0.0
---

# Skill: Test API Endpoint

Esta skill estandariza la creación de tests para endpoints REST en Django Rest Framework.

## Objetivo

Asegurar que cada endpoint cumpla con:

1.  **Seguridad**: Rechazar usuarios anónimos o sin permisos (401/403).
2.  **Correctitud**: Retornar el Status Code esperado (200/201/204).
3.  **Estructura**: El JSON de respuesta tiene las keys esperadas.

## Template de Implementación

Usa `pytest` con `APIClient`.

```python
import pytest
from rest_framework.test import APIClient
from django.urls import reverse
from mixer.backend.django import mixer

@pytest.fixture
def api_client():
    return APIClient()

@pytest.mark.django_db
class TestEndpointName:

    def test_anonymous_access_denied(self, api_client):
        """
        GIVEN no authenticated user
        WHEN requesting the protected endpoint
        THEN return 401 Unauthorized
        """
        url = reverse("api:v1:endpoint-name-list")
        response = api_client.get(url)
        assert response.status_code == 401

    def test_authenticated_success(self, api_client):
        """
        GIVEN an authenticated user
        WHEN requesting the endpoint
        THEN return 200 OK and valid data
        """
        user = mixer.blend("core.User")
        api_client.force_authenticate(user=user)

        url = reverse("api:v1:endpoint-name-list")
        response = api_client.get(url)

        assert response.status_code == 200
        assert isinstance(response.data, (list, dict))

    def test_permission_logic(self, api_client):
        """
        GIVEN a user without specific permission
        WHEN performing restricted action
        THEN return 403 Forbidden
        """
        # Implementar lógica específica de permisos si aplica
        pass
```

## Checklist de Auditoría

- [ ] ¿El test cubre el caso 401 (Unauthenticated)?
- [ ] ¿El test cubre validaciones de input (400 Bad Request)?
- [ ] ¿Se usa `force_authenticate` para simular usuarios reales?
