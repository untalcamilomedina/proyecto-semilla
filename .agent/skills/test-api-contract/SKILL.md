---
name: test-api-contract
description: Valida que las respuestas de la API cumplan estrictamente con el esquema OpenAPI y los Modelos Canónicos.
author: AppNotion Architecture Team
version: 1.0.0
---

# Skill: Test API Contract

Esta skill se enfoca en la "Integridad" de los datos y el contrato entre Backend y Frontend.

## Objetivo

Garantizar que si el backend dice retornar un `FlowSpec`, la estructura JSON sea **idéntica** a la definida en Pydantic, sin campos faltantes ni tipos incorrectos.

## Template de Implementación

Usa `drf-spectacular` para introspección o validación directa con Pydantic.

```python
import pytest
from rest_framework.test import APIClient
from integrations.schemas import FlowSpec, ERDSpec

@pytest.mark.django_db
def test_diagram_contract_validity():
    """
    GIVEN a stored Diagram
    WHEN fetched via API
    THEN the 'spec' field must validate against the Canonical Pydantic Model
    """
    client = APIClient()
    # auth setup...

    response = client.get("/api/v1/diagrams/uuid/")
    assert response.status_code == 200

    data = response.json()
    spec_data = data.get("spec")

    # Validar Contrato Estricto
    # Si esto falla, rompimos el contrato con el Frontend
    try:
        if data["type"] == "flow":
            FlowSpec(**spec_data)
        else:
            ERDSpec(**spec_data)
    except Exception as e:
        pytest.fail(f"API Contract Breach: Response does not match Canonical Schema. Error: {e}")

def test_openapi_schema_generation():
    """
    Verifica que el schema.yml se genera sin errores.
    """
    from drf_spectacular.validation import validate_schema
    from drf_spectacular.generators import SchemaGenerator

    generator = SchemaGenerator()
    schema = generator.get_schema()
    validate_schema(schema)
```

## Checklist de Integridad

- [ ] ¿El endpoint usa `Serializer` que hereda de la estructura canónica?
- [ ] ¿Los campos `required` en Pydantic están presentes en la respuesta?
- [ ] ¿Los tipos de datos (UUID vs String) son consistentes?
