---
name: test-api-contract
description: Valida que las respuestas de la API cumplan estrictamente con el esquema OpenAPI y los Modelos Canónicos.
author: Proyecto Semilla Architecture Team
version: 2.0.0
---

# Skill: Test API Contract

Esta skill se enfoca en la "Integridad" de los datos y el contrato entre Backend y Frontend, usando fixtures del proyecto.

## Objetivo

Garantizar que si el backend dice retornar un modelo canónico (ej. `ItemSpec`), la estructura JSON sea **idéntica** a la definida en Pydantic, sin campos faltantes ni tipos incorrectos.

## Prerrequisitos

- Modelos Pydantic canónicos definidos en tu app (ej. `src/<tu_app>/schemas.py`)
- Fixtures de `tests/conftest.py`
- `drf-spectacular` instalado para validación OpenAPI

## Template de Implementación

### Template 1: Validación de Contrato con Pydantic

```python
import pytest
from pydantic import BaseModel, ValidationError

class ItemSpec(BaseModel):
    """Modelo canónico de ejemplo — sustituye por el de tu dominio."""
    name: str
    fields: list[str] = []

@pytest.mark.django_db
class TestAPIContract:
    """
    Valida que las respuestas API coincidan con los schemas Pydantic.
    Usa fixtures de conftest.py para autenticación.
    """

    def test_item_response_matches_schema(self, tenant_client, db):
        """
        GIVEN a stored resource in the database
        WHEN fetched via API
        THEN the payload must validate against the Canonical Pydantic Model
        """
        # Setup: crea el recurso con TU modelo y ajusta la ruta a TU endpoint
        # from <tu_app>.models import Item
        # item = Item.objects.create(name="Test Item", fields=["id", "title"])

        response = tenant_client.get("/api/v1/items/1/")  # ajusta a tu recurso
        assert response.status_code == 200

        data = response.json()

        # Validar Contrato Estricto
        try:
            ItemSpec(**data)
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
        response = authenticated_client.get("/api/v1/roles/")
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
        response = api_client.get("/api/v1/roles/")
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
        "/api/v1/roles/",
        "/api/v1/plans/",
        "/api/v1/subscriptions/",
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
      - 'src/**/schemas.py'

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

- `tests/test_api_v1.py` - Ejemplo real de tests contra la API v1
- `tests/conftest.py` - Fixtures de autenticación
- `drf-spectacular` docs - https://drf-spectacular.readthedocs.io/
