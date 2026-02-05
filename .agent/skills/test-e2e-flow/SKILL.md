---
name: test-e2e-flow
description: Guía para crear tests End-to-End que validan flujos completos de usuario en la API.
author: AppNotion Dev Team
version: 1.0.0
---

# Skill: Test End-to-End de Flujos API

Esta skill estandariza la creación de tests E2E que validan flujos completos de usuario a nivel de API. Simula el comportamiento real de un frontend consumiendo la API.

## ¿Qué es un Test E2E de API?

| Test Unitario | Test Integración | Test E2E |
|---------------|------------------|----------|
| Una función | Un endpoint | Múltiples endpoints |
| Mocks | DB real | Sistema completo |
| Aislado | Parcial | Flujo real |
| Rápido | Medio | Lento |

## Prerrequisitos

- [ ] API funcionando.
- [ ] DB de test configurada.
- [ ] Fixtures de datos base.

## Cuándo Usar

- Para validar flujos críticos de negocio.
- Antes de release a producción.
- Para detectar regresiones en integraciones.
- Como "smoke tests" en CI/CD.

---

## Flujos Críticos a Testear

| Flujo | Endpoints Involucrados | Prioridad |
|-------|------------------------|-----------|
| **Onboarding** | signup → create-org → invite | CRÍTICO |
| **Login** | login → get-token → refresh | CRÍTICO |
| **CRUD Completo** | create → read → update → delete | ALTA |
| **Billing** | subscribe → webhook → activate | ALTA |
| **RBAC** | create-role → assign → verify | MEDIA |

---

## Templates

### Template A: Flujo de Onboarding Completo

```python
"""
E2E Test: Flujo de Onboarding
Tests the complete flow: Signup → Create Org → Configure → Invite Team
"""

import pytest
from rest_framework import status
from rest_framework.test import APIClient


class TestOnboardingE2EFlow:
    """
    End-to-End test del flujo de onboarding.

    Simula un usuario nuevo que:
    1. Se registra
    2. Crea una organización
    3. Configura módulos
    4. Invita miembros
    """

    @pytest.mark.django_db(transaction=True)
    def test_complete_onboarding_flow(self):
        """Flujo completo de onboarding exitoso."""
        client = APIClient()

        # ========== STEP 1: Signup ==========
        signup_response = client.post(
            "/api/v1/auth/register/",
            {
                "email": "newuser@example.com",
                "password": "SecurePass123!",
                "password_confirm": "SecurePass123!",
            },
            format="json",
        )
        assert signup_response.status_code == status.HTTP_201_CREATED
        assert "access" in signup_response.data
        access_token = signup_response.data["access"]

        # Autenticar para siguientes requests
        client.credentials(HTTP_AUTHORIZATION=f"Bearer {access_token}")

        # ========== STEP 2: Create Organization ==========
        create_org_response = client.post(
            "/api/v1/onboarding/organization/",
            {
                "name": "Acme Corp",
                "slug": "acme-corp",
            },
            format="json",
        )
        assert create_org_response.status_code == status.HTTP_201_CREATED
        org_slug = create_org_response.data["slug"]

        # ========== STEP 3: Configure Modules ==========
        modules_response = client.post(
            "/api/v1/onboarding/modules/",
            {
                "modules": ["cms", "lms"],
            },
            format="json",
            HTTP_X_TENANT=org_slug,
        )
        assert modules_response.status_code == status.HTTP_200_OK

        # ========== STEP 4: Invite Members ==========
        invite_response = client.post(
            "/api/v1/onboarding/invite/",
            {
                "emails": ["member1@example.com", "member2@example.com"],
            },
            format="json",
            HTTP_X_TENANT=org_slug,
        )
        assert invite_response.status_code == status.HTTP_200_OK
        assert invite_response.data["invited_count"] == 2

        # ========== STEP 5: Complete Onboarding ==========
        complete_response = client.post(
            "/api/v1/onboarding/complete/",
            format="json",
            HTTP_X_TENANT=org_slug,
        )
        assert complete_response.status_code == status.HTTP_200_OK

        # ========== VERIFY: Dashboard Accessible ==========
        dashboard_response = client.get(
            "/api/v1/tenant/",
            HTTP_X_TENANT=org_slug,
        )
        assert dashboard_response.status_code == status.HTTP_200_OK
        assert dashboard_response.data["slug"] == org_slug
        assert dashboard_response.data["onboarding_completed"] is True

        print("\n✅ E2E: Onboarding flow completed successfully")
```

### Template B: Flujo de Autenticación

```python
"""
E2E Test: Flujo de Autenticación
Tests: Login → Access Protected → Refresh → Logout
"""

import pytest
from rest_framework import status
from rest_framework.test import APIClient
from django.contrib.auth import get_user_model

User = get_user_model()


class TestAuthenticationE2EFlow:
    """E2E test del flujo de autenticación."""

    @pytest.fixture
    def existing_user(self, db):
        """Usuario existente para login."""
        return User.objects.create_user(
            username="existinguser",
            email="existing@example.com",
            password="TestPass123!",
        )

    @pytest.mark.django_db(transaction=True)
    def test_complete_auth_flow(self, existing_user):
        """Flujo completo de autenticación."""
        client = APIClient()

        # ========== STEP 1: Login ==========
        login_response = client.post(
            "/api/v1/auth/token/",
            {
                "email": "existing@example.com",
                "password": "TestPass123!",
            },
            format="json",
        )
        assert login_response.status_code == status.HTTP_200_OK
        assert "access" in login_response.data
        assert "refresh" in login_response.data

        access_token = login_response.data["access"]
        refresh_token = login_response.data["refresh"]

        # ========== STEP 2: Access Protected Resource ==========
        client.credentials(HTTP_AUTHORIZATION=f"Bearer {access_token}")
        protected_response = client.get("/api/v1/users/me/")
        assert protected_response.status_code == status.HTTP_200_OK
        assert protected_response.data["email"] == "existing@example.com"

        # ========== STEP 3: Refresh Token ==========
        refresh_response = client.post(
            "/api/v1/auth/token/refresh/",
            {"refresh": refresh_token},
            format="json",
        )
        assert refresh_response.status_code == status.HTTP_200_OK
        new_access_token = refresh_response.data["access"]

        # ========== STEP 4: Access with New Token ==========
        client.credentials(HTTP_AUTHORIZATION=f"Bearer {new_access_token}")
        verify_response = client.get("/api/v1/users/me/")
        assert verify_response.status_code == status.HTTP_200_OK

        # ========== STEP 5: Logout (Blacklist Token) ==========
        logout_response = client.post(
            "/api/v1/auth/logout/",
            {"refresh": refresh_token},
            format="json",
        )
        assert logout_response.status_code == status.HTTP_200_OK

        # ========== VERIFY: Old Refresh Token Invalid ==========
        invalid_refresh_response = client.post(
            "/api/v1/auth/token/refresh/",
            {"refresh": refresh_token},
            format="json",
        )
        assert invalid_refresh_response.status_code == status.HTTP_401_UNAUTHORIZED

        print("\n✅ E2E: Authentication flow completed successfully")
```

### Template C: Flujo CRUD Completo

```python
"""
E2E Test: Flujo CRUD de Resource
Tests: Create → Read → Update → Delete
"""

import pytest
from rest_framework import status
from rest_framework.test import APIClient


class TestResourceCRUDE2EFlow:
    """E2E test de operaciones CRUD completas."""

    @pytest.mark.django_db(transaction=True)
    def test_complete_crud_flow(self, authenticated_client, setup_tenant_context):
        """Flujo CRUD completo para un recurso."""
        client = authenticated_client
        tenant_slug = setup_tenant_context["tenant"].slug

        # ========== CREATE ==========
        create_response = client.post(
            "/api/v1/roles/",
            {
                "name": "Custom Role",
                "description": "A custom role for testing",
                "permissions": [],
            },
            format="json",
            HTTP_X_TENANT=tenant_slug,
        )
        assert create_response.status_code == status.HTTP_201_CREATED
        role_id = create_response.data["id"]

        # Verificar que aparece en lista
        list_response = client.get(
            "/api/v1/roles/",
            HTTP_X_TENANT=tenant_slug,
        )
        assert any(r["id"] == role_id for r in list_response.data)

        # ========== READ ==========
        read_response = client.get(
            f"/api/v1/roles/{role_id}/",
            HTTP_X_TENANT=tenant_slug,
        )
        assert read_response.status_code == status.HTTP_200_OK
        assert read_response.data["name"] == "Custom Role"

        # ========== UPDATE ==========
        update_response = client.put(
            f"/api/v1/roles/{role_id}/",
            {
                "name": "Updated Role",
                "description": "Updated description",
                "permissions": [],
            },
            format="json",
            HTTP_X_TENANT=tenant_slug,
        )
        assert update_response.status_code == status.HTTP_200_OK
        assert update_response.data["name"] == "Updated Role"

        # Verificar update persistió
        verify_response = client.get(
            f"/api/v1/roles/{role_id}/",
            HTTP_X_TENANT=tenant_slug,
        )
        assert verify_response.data["name"] == "Updated Role"

        # ========== DELETE ==========
        delete_response = client.delete(
            f"/api/v1/roles/{role_id}/",
            HTTP_X_TENANT=tenant_slug,
        )
        assert delete_response.status_code == status.HTTP_204_NO_CONTENT

        # Verificar que ya no existe
        not_found_response = client.get(
            f"/api/v1/roles/{role_id}/",
            HTTP_X_TENANT=tenant_slug,
        )
        assert not_found_response.status_code == status.HTTP_404_NOT_FOUND

        # Verificar que no aparece en lista
        final_list_response = client.get(
            "/api/v1/roles/",
            HTTP_X_TENANT=tenant_slug,
        )
        assert not any(r["id"] == role_id for r in final_list_response.data)

        print("\n✅ E2E: CRUD flow completed successfully")
```

### Template D: Flujo con Dependencias entre Recursos

```python
"""
E2E Test: Flujo con Dependencias
Tests: Create Parent → Create Child → Cascade Delete
"""

import pytest
from rest_framework import status


class TestDependencyE2EFlow:
    """E2E test de recursos con dependencias."""

    @pytest.mark.django_db(transaction=True)
    def test_parent_child_relationship_flow(
        self,
        authenticated_client,
        setup_tenant_context
    ):
        """Flujo con relaciones padre-hijo."""
        client = authenticated_client
        tenant_slug = setup_tenant_context["tenant"].slug

        # ========== CREATE PARENT (Role) ==========
        role_response = client.post(
            "/api/v1/roles/",
            {
                "name": "Manager",
                "permissions": ["view_members", "invite_members"],
            },
            format="json",
            HTTP_X_TENANT=tenant_slug,
        )
        assert role_response.status_code == status.HTTP_201_CREATED
        role_id = role_response.data["id"]

        # ========== CREATE CHILD (Membership with Role) ==========
        # Primero invitar usuario
        invite_response = client.post(
            "/api/v1/members/invite/",
            {
                "email": "newmember@example.com",
                "role_id": role_id,
            },
            format="json",
            HTTP_X_TENANT=tenant_slug,
        )
        assert invite_response.status_code == status.HTTP_200_OK

        # ========== VERIFY RELATIONSHIP ==========
        members_response = client.get(
            "/api/v1/members/",
            HTTP_X_TENANT=tenant_slug,
        )
        # Buscar el miembro invitado
        invited_member = next(
            (m for m in members_response.data if m["email"] == "newmember@example.com"),
            None
        )
        assert invited_member is not None
        assert invited_member["role"]["id"] == role_id

        # ========== UPDATE PARENT ==========
        update_role_response = client.put(
            f"/api/v1/roles/{role_id}/",
            {
                "name": "Senior Manager",
                "permissions": ["view_members", "invite_members", "manage_roles"],
            },
            format="json",
            HTTP_X_TENANT=tenant_slug,
        )
        assert update_role_response.status_code == status.HTTP_200_OK

        # Verificar que child refleja el cambio
        members_response = client.get(
            "/api/v1/members/",
            HTTP_X_TENANT=tenant_slug,
        )
        invited_member = next(
            (m for m in members_response.data if m["email"] == "newmember@example.com"),
            None
        )
        assert invited_member["role"]["name"] == "Senior Manager"

        print("\n✅ E2E: Dependency flow completed successfully")
```

### Template E: Flujo de Error Handling

```python
"""
E2E Test: Manejo de Errores
Tests: Invalid inputs → Error responses → Recovery
"""

import pytest
from rest_framework import status


class TestErrorHandlingE2EFlow:
    """E2E test de manejo de errores."""

    @pytest.mark.django_db(transaction=True)
    def test_error_recovery_flow(self, authenticated_client, setup_tenant_context):
        """Flujo de errores y recuperación."""
        client = authenticated_client
        tenant_slug = setup_tenant_context["tenant"].slug

        # ========== STEP 1: Request Inválido ==========
        invalid_response = client.post(
            "/api/v1/roles/",
            {},  # Falta name requerido
            format="json",
            HTTP_X_TENANT=tenant_slug,
        )
        assert invalid_response.status_code == status.HTTP_400_BAD_REQUEST
        assert "name" in invalid_response.data

        # ========== STEP 2: Corregir y Reintentar ==========
        valid_response = client.post(
            "/api/v1/roles/",
            {"name": "Valid Role"},
            format="json",
            HTTP_X_TENANT=tenant_slug,
        )
        assert valid_response.status_code == status.HTTP_201_CREATED

        # ========== STEP 3: Recurso No Encontrado ==========
        not_found_response = client.get(
            "/api/v1/roles/99999/",
            HTTP_X_TENANT=tenant_slug,
        )
        assert not_found_response.status_code == status.HTTP_404_NOT_FOUND

        # ========== STEP 4: Conflicto (Duplicado) ==========
        duplicate_response = client.post(
            "/api/v1/roles/",
            {"name": "Valid Role", "slug": valid_response.data["slug"]},
            format="json",
            HTTP_X_TENANT=tenant_slug,
        )
        assert duplicate_response.status_code == status.HTTP_400_BAD_REQUEST

        print("\n✅ E2E: Error handling flow completed successfully")
```

---

## Estructura de Archivo E2E

```python
"""
tests/e2e/test_<feature>_e2e.py

Estructura recomendada para archivos E2E.
"""

import pytest
from rest_framework import status
from rest_framework.test import APIClient


# ==================== FIXTURES ====================

@pytest.fixture
def clean_state(db):
    """Asegura estado limpio antes de cada test."""
    # Cleanup si es necesario
    yield
    # Cleanup después del test


@pytest.fixture
def api_client():
    """Cliente API fresco."""
    return APIClient()


# ==================== HELPERS ====================

def assert_success(response, expected_status=status.HTTP_200_OK):
    """Helper para verificar respuestas exitosas."""
    assert response.status_code == expected_status, \
        f"Expected {expected_status}, got {response.status_code}: {response.data}"


def assert_error(response, expected_status, expected_field=None):
    """Helper para verificar respuestas de error."""
    assert response.status_code == expected_status
    if expected_field:
        assert expected_field in response.data


# ==================== E2E TESTS ====================

class TestFeatureE2EFlow:
    """E2E tests para Feature X."""

    @pytest.mark.django_db(transaction=True)
    def test_happy_path(self, api_client, clean_state):
        """Flujo exitoso completo."""
        pass

    @pytest.mark.django_db(transaction=True)
    def test_error_path(self, api_client, clean_state):
        """Flujo con errores y recuperación."""
        pass

    @pytest.mark.django_db(transaction=True)
    def test_edge_cases(self, api_client, clean_state):
        """Casos límite."""
        pass
```

---

## Ejecución

```bash
# Todos los tests E2E
pytest tests/e2e/ -v

# Un flujo específico
pytest tests/e2e/test_onboarding_e2e.py -v

# Con output detallado
pytest tests/e2e/ -v -s

# Solo tests marcados como E2E
pytest -m e2e -v
```

---

## Checklist de Verificación

### Flujo Completo
- [ ] Todos los pasos del flujo testeados
- [ ] Verificaciones intermedias
- [ ] Estado final correcto

### Datos
- [ ] No depende de datos externos
- [ ] Cleanup después del test
- [ ] Aislamiento entre tests

### Errores
- [ ] Errores 4xx manejados
- [ ] Errores 5xx detectados
- [ ] Recovery path testeado

---

## Referencias

- [Skill test-api-endpoint](../test-api-endpoint/SKILL.md)
- [Tests existentes](../../tests/)
- [pytest-django](https://pytest-django.readthedocs.io/)

---

*Última actualización: 2025-02-04*
