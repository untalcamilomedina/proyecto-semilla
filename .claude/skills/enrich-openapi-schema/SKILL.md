---
name: enrich-openapi-schema
description: Guía para enriquecer la documentación OpenAPI (Swagger) con ejemplos, descripciones y tipos explícitos usando drf-spectacular.
author: Proyecto Semilla Dev Team
version: 1.0.0
---

# Skill: Enriquecer Schema OpenAPI

Esta skill transforma una API funcional pero mal documentada en una API "Producto", donde cada endpoint tiene contratos claros, ejemplos y códigos de error explicados. Fundamental para el enfoque **API First**.

## Prerrequisitos

- [ ] ViewSet implementado en el `api.py` (o `views.py`) de tu app (ej. `src/api/`).
- [ ] `drf-spectacular` instalado.

## Proceso

### Paso 1: Importar Decoradores

En el módulo de tu ViewSet, importar las herramientas de `drf-spectacular`. Para el ejemplo definimos un modelo canónico mínimo; en tu proyecto usa el Serializer o modelo Pydantic real de tu dominio.

```python
from drf_spectacular.utils import extend_schema, OpenApiParameter, OpenApiExample, OpenApiTypes
from drf_spectacular.types import OpenApiTypes
from pydantic import BaseModel

class ItemSpec(BaseModel):
    """Modelo canónico de ejemplo — sustituye por el de tu dominio."""
    name: str
    fields: list[str] = []
```

### Paso 2: Decorar la Acción

Aplicar `@extend_schema` sobre el método del ViewSet.

**Reglas de Oro:**

1.  **Summary**: Qué hace (Título corto).
2.  **Description**: Detalles técnicos y de negocio.
3.  **Responses**: Mapear TODOS los códigos de estado posibles (200, 400, 403, 500).
4.  **Examples**: Proveer un JSON real de lo que devuelve.

```python
@extend_schema(
    summary="Sincronizar Items desde el servicio externo",
    description="""
    Inicia la sincronización de recursos desde la API externa configurada.
    Retorna una especificación canónica (`ItemSpec`) con los items encontrados.
    """,
    request=OpenApiTypes.OBJECT, # O un Serializer específico si existe
    responses={
        200: ItemSpec, # Enlace directo al Pydantic/Serializer
        400: OpenApiTypes.OBJECT,
        401: OpenApiTypes.OBJECT
    },
    examples=[
        OpenApiExample(
            "Respuesta Exitosa",
            value={
                "name": "Projects",
                "fields": ["id", "title", "status"]
            },
            status_codes=["200"]
        ),
        OpenApiExample(
            "Error Token",
            value={"error": "Token is required"},
            status_codes=["400"]
        )
    ]
)
def sync(self, request):
    # implementación...
```

### Paso 3: Validar en Swagger UI

1.  Abrir `http://localhost:8010/api/docs/`.
2.  Buscar el endpoint.
3.  Verificar que el botón "Try it out" muestre los ejemplos y esquemas correctos.

## Checklist de Calidad

- [ ] `summary` es conciso (Verbo + Objeto).
- [ ] `description` explica efectos secundarios (ej. "Crea un Job asíncrono").
- [ ] `responses` cubre casos de éxito y error.
- [ ] `examples` son realistas (no usar "foo", "bar").

## Errores Comunes

### Error: `drf_spectacular.errors.Error: unable to resolve type`

**Causa:** Usar una clase python plano sin Serializer/Pydantic válido.
**Solución:** Asegurar que el objeto en `responses` sea un `Serializer` de DRF o usar `inline_serializer`.

## Referencias

- [Documentación drf-spectacular](https://drf-spectacular.readthedocs.io/)
