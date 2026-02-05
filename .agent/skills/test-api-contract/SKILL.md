---
name: test-api-contract
description: Valida que la API cumple con el schema OpenAPI (Contract Testing).
author: AppNotion Dev Team
version: 1.0.0
---

# Skill: Test de Contrato API (OpenAPI)

Esta skill implementa Contract Testing para garantizar que la API real cumple con la especificación OpenAPI documentada. Detecta discrepancias entre lo documentado y lo implementado antes de que el frontend las descubra.

## ¿Por qué Contract Testing?

| Sin Contract Testing | Con Contract Testing |
|---------------------|----------------------|
| Frontend descubre errores | CI/CD detecta errores |
| "La API cambió sin aviso" | Cambios son intencionales |
| Documentación desactualizada | Documentación = Código |
| Debug manual de responses | Validación automática |

## Prerrequisitos

- [ ] `drf-spectacular` configurado (ya presente).
- [ ] Instalar dependencias:
  ```bash
  pip install schemathesis pytest-schemathesis
  ```
- [ ] OpenAPI schema accesible en `/api/schema/`.

## Cuándo Usar

- En CI/CD antes de merge a main.
- Después de modificar ViewSets o Serializers.
- Antes de marcar una versión de API como "stable".

---

## Opciones de Implementación

### Opción A: Schemathesis (Recomendado)

Schemathesis genera tests automáticamente desde el schema OpenAPI.

### Opción B: Validación Manual con jsonschema

Para casos específicos donde necesitas control total.

---

## Implementación con Schemathesis

### 1. Configuración Básica

**Archivo:** `tests/test_api_contract.py`

```python
"""
Contract Tests - Valida que la API cumple con OpenAPI schema.

Ejecutar con:
    pytest tests/test_api_contract.py -v

O con schemathesis CLI:
    schemathesis run http://localhost:8010/api/schema/ --base-url http://localhost:8010
"""

import pytest
import schemathesis
from django.test import override_settings
from hypothesis import settings as hypothesis_settings, Phase

# Cargar schema desde la app Django
schema = schemathesis.from_pytest_fixture("openapi_schema")


@pytest.fixture
def openapi_schema(live_server):
    """Obtiene el schema OpenAPI del servidor de test."""
    return schemathesis.from_uri(f"{live_server.url}/api/schema/")


# Configurar Hypothesis para tests más rápidos en CI
hypothesis_settings.register_profile(
    "ci",
    max_examples=10,
    phases=[Phase.explicit, Phase.generate],
)
hypothesis_settings.load_profile("ci")


@schema.parametrize()
@pytest.mark.django_db(transaction=True)
def test_api_contract(case):
    """
    Test generado automáticamente para cada endpoint del schema.

    Schemathesis genera payloads válidos según el schema y verifica:
    - Status codes documentados
    - Response schema matches
    - No errores 500
    """
    # Configurar autenticación si es necesaria
    case.headers = {"Authorization": "Bearer test-token"}

    response = case.call_and_validate()

    # Validaciones adicionales
    assert response.status_code != 500, f"Server error en {case.operation.path}"
```

### 2. Configuración Avanzada con Autenticación

```python
import pytest
import schemathesis
from rest_framework.test import APIClient
from api.models import ApiKey


@pytest.fixture
def auth_headers(db, setup_tenant_context):
    """Genera headers de autenticación válidos."""
    _key, plain = ApiKey.generate(
        organization=setup_tenant_context["tenant"],
        user=setup_tenant_context["user"],
        name="contract-test",
    )
    return {
        "Authorization": f"Bearer {plain}",
        "Host": f"{setup_tenant_context['tenant'].slug}.acme.dev",
    }


@pytest.fixture
def openapi_schema(live_server, auth_headers):
    """Schema con autenticación configurada."""
    schema = schemathesis.from_uri(
        f"{live_server.url}/api/schema/",
        headers=auth_headers,
    )

    # Configurar headers para todas las requests
    schema.hooks.register("before_call")(
        lambda context, case: case.headers.update(auth_headers)
    )

    return schema


@schema.parametrize()
@pytest.mark.django_db(transaction=True)
def test_authenticated_endpoints(case, auth_headers):
    """Test de endpoints que requieren autenticación."""
    case.headers.update(auth_headers)
    response = case.call_and_validate()

    # No debería dar 401/403 con auth válida
    assert response.status_code not in [401, 403], \
        f"Auth failed en {case.operation.path}"
```

### 3. Excluir Endpoints Específicos

```python
import schemathesis


@pytest.fixture
def openapi_schema(live_server):
    """Schema con endpoints excluidos."""
    schema = schemathesis.from_uri(f"{live_server.url}/api/schema/")

    # Excluir endpoints problemáticos o en desarrollo
    return schema.filter(
        lambda op: op.path not in [
            "/api/v1/internal/",  # Endpoints internos
            "/api/v1/webhooks/",  # Webhooks no testeables así
        ]
    )
```

### 4. Validar Endpoints Específicos

```python
import schemathesis


@pytest.fixture
def openapi_schema(live_server):
    """Solo endpoints de producción."""
    schema = schemathesis.from_uri(f"{live_server.url}/api/schema/")

    # Solo endpoints que empiezan con /api/v1/
    return schema.filter(lambda op: op.path.startswith("/api/v1/"))


# Test específico para un endpoint
@schema.parametrize(endpoint="/api/v1/roles/")
@pytest.mark.django_db(transaction=True)
def test_roles_endpoint_contract(case):
    """Contract test específico para roles."""
    response = case.call_and_validate()
    assert response.status_code in [200, 201, 400, 401, 403]
```

---

## Implementación Manual (jsonschema)

Para casos donde necesitas validación más específica.

### 1. Extraer Schema y Validar

```python
import pytest
import json
import jsonschema
from django.test import Client


@pytest.fixture
def api_schema(client):
    """Obtiene el schema OpenAPI."""
    response = client.get("/api/schema/", HTTP_ACCEPT="application/json")
    return response.json()


@pytest.fixture
def response_schema(api_schema):
    """Extrae schema de response para un endpoint específico."""
    def _get_schema(path: str, method: str, status_code: int):
        endpoint = api_schema["paths"].get(path, {})
        operation = endpoint.get(method.lower(), {})
        response = operation.get("responses", {}).get(str(status_code), {})

        # Resolver $ref si existe
        content = response.get("content", {}).get("application/json", {})
        schema = content.get("schema", {})

        if "$ref" in schema:
            ref_path = schema["$ref"].replace("#/components/schemas/", "")
            return api_schema["components"]["schemas"][ref_path]

        return schema

    return _get_schema


class TestRolesContract:
    """Contract tests manuales para /api/v1/roles/"""

    @pytest.mark.django_db
    def test_list_response_matches_schema(
        self,
        authenticated_client,
        response_schema
    ):
        """GET /roles/ devuelve response que cumple schema."""
        response = authenticated_client.get("/api/v1/roles/")
        schema = response_schema("/api/v1/roles/", "GET", 200)

        # Validar contra schema
        jsonschema.validate(instance=response.json(), schema=schema)

    @pytest.mark.django_db
    def test_create_request_matches_schema(
        self,
        authenticated_client,
        api_schema
    ):
        """POST /roles/ acepta payload que cumple schema."""
        # Obtener schema de request
        request_schema = (
            api_schema["paths"]["/api/v1/roles/"]
            ["post"]["requestBody"]["content"]
            ["application/json"]["schema"]
        )

        # Payload válido según schema
        valid_payload = {
            "name": "Test Role",
            "description": "Test",
            "permissions": [],
        }

        # Validar payload contra schema
        jsonschema.validate(instance=valid_payload, schema=request_schema)

        # Enviar y verificar éxito
        response = authenticated_client.post(
            "/api/v1/roles/",
            valid_payload,
            format="json",
        )
        assert response.status_code == 201
```

---

## CLI de Schemathesis

Para tests rápidos sin escribir código:

```bash
# Test básico contra server corriendo
schemathesis run http://localhost:8010/api/schema/ \
    --base-url http://localhost:8010

# Con autenticación
schemathesis run http://localhost:8010/api/schema/ \
    --base-url http://localhost:8010 \
    --header "Authorization: Bearer <token>"

# Solo endpoints específicos
schemathesis run http://localhost:8010/api/schema/ \
    --base-url http://localhost:8010 \
    --endpoint "/api/v1/roles/"

# Generar reporte
schemathesis run http://localhost:8010/api/schema/ \
    --base-url http://localhost:8010 \
    --report report.json

# Modo stateful (detecta dependencias entre endpoints)
schemathesis run http://localhost:8010/api/schema/ \
    --base-url http://localhost:8010 \
    --stateful=links
```

---

## Integración con CI/CD

### GitHub Actions

```yaml
# .github/workflows/api-contract.yml
name: API Contract Tests

on:
  pull_request:
    paths:
      - 'src/**'
      - 'tests/**'

jobs:
  contract-tests:
    runs-on: ubuntu-latest
    services:
      postgres:
        image: postgres:15
        env:
          POSTGRES_PASSWORD: postgres
        options: >-
          --health-cmd pg_isready
          --health-interval 10s
          --health-timeout 5s
          --health-retries 5

    steps:
      - uses: actions/checkout@v4

      - name: Setup Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'

      - name: Install dependencies
        run: |
          pip install -r requirements/test.txt
          pip install schemathesis

      - name: Run API server
        run: |
          python manage.py migrate
          python manage.py runserver 8010 &
          sleep 5

      - name: Run contract tests
        run: |
          schemathesis run http://localhost:8010/api/schema/ \
            --base-url http://localhost:8010 \
            --checks all \
            --hypothesis-max-examples=20
```

---

## Checklist de Verificación

### Configuración
- [ ] `drf-spectacular` genera schema válido en `/api/schema/`
- [ ] `schemathesis` instalado
- [ ] Tests corren en CI/CD

### Cobertura
- [ ] Todos los endpoints públicos testeados
- [ ] Responses validan contra schema
- [ ] No hay errores 500 inesperados
- [ ] Códigos de error documentados

### Exclusiones Documentadas
- [ ] Endpoints internos excluidos
- [ ] Webhooks excluidos (si aplica)
- [ ] Razón de exclusión documentada

---

## Errores Comunes

### Error: Schema no encontrado

**Causa:** `drf-spectacular` no está configurado.

**Solución:** Verificar `SPECTACULAR_SETTINGS` en settings.py.

### Error: 401 en todos los tests

**Causa:** Autenticación no configurada en tests.

**Solución:** Usar fixture con `auth_headers` como se muestra arriba.

### Error: "Response does not match schema"

**Causa:** La implementación difiere del schema documentado.

**Solución:** Actualizar el ViewSet/Serializer o el schema (decidir cuál es correcto).

---

## Referencias

- [Schemathesis Documentation](https://schemathesis.readthedocs.io/)
- [drf-spectacular](https://drf-spectacular.readthedocs.io/)
- [OpenAPI Schema](../../api/schema/)
- [Skill enrich-openapi-schema](../enrich-openapi-schema/SKILL.md)

---

*Última actualización: 2025-02-04*
