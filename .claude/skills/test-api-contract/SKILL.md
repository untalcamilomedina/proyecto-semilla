---
name: test-api-contract
description: Valida que las respuestas de la API cumplan estrictamente con el esquema OpenAPI y los Modelos Canónicos.
author: AppNotion Architecture Team
version: 2.0.0
---

# Skill: Test API Contract

Esta skill se enfoca en la "Integridad" de los datos y el contrato entre Backend y Frontend, usando fixtures del proyecto.

## Objetivo

Garantizar que si el backend dice retornar un `FlowSpec`, la estructura JSON sea **idéntica** a la definida en Pydantic, sin campos faltantes ni tipos incorrectos.

## Prerrequisitos

- Modelos Pydantic definidos en `src/integrations/schemas.py`
- Fixtures de `tests/conftest.py`
- `drf-spectacular` instalado para validación OpenAPI

## Template de Implementación

### Template 1: Validación de Contrato con Pydantic

```python
import pytest
from pydantic import ValidationError

@pytest.mark.django_db
class TestAPIContract:
    """
    Valida que las respuestas API coincidan con los schemas Pydantic.
    Usa fixtures de conftest.py para autenticación.
    """

    def test_diagram_response_matches_schema(self, tenant_client, db):
        """
        GIVEN a stored Diagram in the database
        WHEN fetched via API
        THEN the 'spec' field must validate against the Canonical Pydantic Model
        """
        from integrations.schemas import FlowSpec, ERDSpec
        from integrations.models import Diagram  # Ajustar según tu modelo

        # Setup: Crear un diagrama de prueba
        diagram = Diagram.objects.create(
            name="Test Diagram",
            type="flow",
            spec={"nodes": [], "edges": []},
            # tenant=tenant (si aplica multi-tenant)
        )

        response = tenant_client.get(f"/api/v1/diagrams/{diagram.id}/")
        assert response.status_code == 200

        data = response.json()
        spec_data = data.get("spec")

        # Validar Contrato Estricto
        try:
            if data["type"] == "flow":
                FlowSpec(**spec_data)
            elif data["type"] == "erd":
                ERDSpec(**spec_data)
        except ValidationError as e:
            pytest.fail(
                f"API Contract Breach: Response does not match Canonical Schema.\n"
                f"Errors: {e.errors()}"
            )

    def test_list_response_structure(self, authenticated_client):
        """
        GIVEN a list endpoint
        WHEN fetched
        THEN response has expected pagination structure
        """
        response = authenticated_client.get("/api/v1/diagrams/")
        assert response.status_code == 200

        data = response.json()

        # Validar estructura de paginación (si usa PageNumberPagination)
        if isinstance(data, dict):
            assert "results" in data or "count" in data, \
                "Paginated response must have 'results' or 'count'"

    def test_error_response_format(self, api_client):
        """
        GIVEN an unauthenticated request
        WHEN accessing protected endpoint
        THEN error response follows standard format
        """
        response = api_client.get("/api/v1/diagrams/")
        assert response.status_code == 401

        data = response.json()
        # DRF estándar: {"detail": "..."}
        assert "detail" in data, "Error response must have 'detail' field"
```

### Template 2: Validación OpenAPI Schema

```python
import pytest

def test_openapi_schema_is_valid():
    """
    Verifica que el schema OpenAPI se genera sin errores.
    Este test NO requiere base de datos.
    """
    from drf_spectacular.validation import validate_schema
    from drf_spectacular.generators import SchemaGenerator

    generator = SchemaGenerator()
    schema = generator.get_schema()

    # Esto lanza excepción si el schema es inválido
    validate_schema(schema)


def test_openapi_schema_has_required_endpoints():
    """
    Verifica que endpoints críticos estén documentados en OpenAPI.
    """
    from drf_spectacular.generators import SchemaGenerator

    generator = SchemaGenerator()
    schema = generator.get_schema()

    paths = schema.get("paths", {})

    # Endpoints críticos que DEBEN existir
    required_endpoints = [
        "/api/v1/integrations/notion/import",
        "/api/v1/integrations/miro/import",
        "/api/v1/diagrams/",
    ]

    for endpoint in required_endpoints:
        assert endpoint in paths, \
            f"Critical endpoint '{endpoint}' missing from OpenAPI schema"


def test_openapi_schema_has_auth_security():
    """
    Verifica que el schema OpenAPI declare seguridad.
    """
    from drf_spectacular.generators import SchemaGenerator

    generator = SchemaGenerator()
    schema = generator.get_schema()

    # Debe tener securitySchemes definidos
    components = schema.get("components", {})
    security_schemes = components.get("securitySchemes", {})

    assert len(security_schemes) > 0, \
        "OpenAPI schema must declare security schemes"
```

### Template 3: Validación de Tipos Específicos

```python
import pytest
from uuid import UUID
from datetime import datetime

@pytest.mark.django_db
class TestFieldTypeContract:
    """
    Valida que los tipos de campos sean correctos en las respuestas.
    """

    def test_uuid_fields_are_strings(self, tenant_client, db):
        """
        GIVEN a resource with UUID primary key
        WHEN fetched via API
        THEN 'id' is a valid UUID string
        """
        response = tenant_client.get("/api/v1/resources/")
        assert response.status_code == 200

        data = response.json()
        results = data.get("results", data) if isinstance(data, dict) else data

        if results:
            first_item = results[0]
            # Validar que el ID es un UUID válido
            try:
                UUID(first_item["id"])
            except (ValueError, KeyError):
                pytest.fail("'id' field must be a valid UUID string")

    def test_datetime_fields_are_iso_format(self, tenant_client, db):
        """
        GIVEN a resource with datetime fields
        WHEN fetched via API
        THEN datetime fields are ISO 8601 format
        """
        response = tenant_client.get("/api/v1/resources/")
        assert response.status_code == 200

        data = response.json()
        results = data.get("results", data) if isinstance(data, dict) else data

        if results:
            first_item = results[0]
            if "created_at" in first_item:
                try:
                    datetime.fromisoformat(
                        first_item["created_at"].replace("Z", "+00:00")
                    )
                except ValueError:
                    pytest.fail("'created_at' must be ISO 8601 format")
```

## Integración con CI/CD

```yaml
# .github/workflows/api-contract.yml
name: API Contract Validation

on:
  pull_request:
    paths:
      - 'src/api/**'
      - 'src/integrations/schemas.py'

jobs:
  contract-test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Run Contract Tests
        run: |
          pytest tests/ -k "contract" -v --tb=short

      - name: Validate OpenAPI Schema
        run: |
          python manage.py spectacular --validate --fail-on-warn
```

## Checklist de Integridad

- [ ] ¿Se usan fixtures de conftest.py para autenticación?
- [ ] ¿El endpoint usa `Serializer` que hereda de la estructura canónica?
- [ ] ¿Los campos `required` en Pydantic están presentes en la respuesta?
- [ ] ¿Los tipos de datos (UUID vs String) son consistentes?
- [ ] ¿El schema OpenAPI se genera sin warnings?
- [ ] ¿Los endpoints críticos están documentados en OpenAPI?

## Errores Comunes

| Error | Causa | Solución |
|-------|-------|----------|
| `ValidationError` en Pydantic | Respuesta no coincide con schema | Revisar Serializer vs Schema Pydantic |
| Campo faltante | Serializer no incluye campo | Agregar campo a `fields` del Serializer |
| Tipo incorrecto | UUID como objeto en lugar de string | Usar `UUIDField` con `format='hex_verbose'` |
| Schema OpenAPI inválido | Serializer mal configurado | Revisar `@extend_schema` decorators |

## Referencias

- `src/integrations/schemas.py` - Modelos Pydantic canónicos
- `tests/conftest.py` - Fixtures de autenticación
- `drf-spectacular` docs - https://drf-spectacular.readthedocs.io/
