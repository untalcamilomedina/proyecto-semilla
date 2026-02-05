---
name: canonical-model-check
description: Skill de validación para asegurar que los adaptadores cumplan estrictamente con los esquemas Pydantic.
author: AppNotion Dev Team
version: 1.0.0
---

# Skill: Verificación de Modelos Canónicos

Esta skill actúa como un linter lógico/manual para garantizar que los "Adaptadores" no estén devolviendo diccionarios sucios, sino instancias válidas de los Modelos Canónicos (`ERDSpec`, `FlowSpec`).

## Prerrequisitos

- [ ] `adapters.py` implementado.
- [ ] `integrations/schemas.py` accesible.

## Proceso

### Paso 1: Revisión Estática

Abrir `src/integrations/<integration>/adapters.py` y verificar:

1.  **Tipo de Retorno**: ¿El método devuelve `-> ERDEntity` (hinting) o `Dict`? Debe ser el Modelo.
2.  **Validación**: ¿Se está instanciando la clase? ej. `return ERDEntity(...)`.
    - ❌ Incorrecto: `return { "id": ... }`
    - ✅ Correcto: `return ERDEntity(id=...)`

### Paso 2: Script de Validación (Dynamic Check)

Crear un pequeño script temporal para forzar la validación de Pydantic sobre un payload de ejemplo de la API externa.

```python
# check_adapter.py (Temporal)
from integrations.<integration>.adapters import <Integration>Adapter
from integrations.schemas import ERDSpec

# 1. Payload real o simulado de la API externa
mock_api_data = {
    "id": "123", # Asegurar que esto coincide con lo que espera el adapter
    "title": "Project X"
}

try:
    # 2. Invocar el adaptador
    canonical_obj = <Integration>Adapter.external_to_canonical(mock_api_data)

    # 3. Validar serialización (dump)
    print("✅ Transformación Exitosa:")
    print(canonical_obj.model_dump_json(indent=2))

except Exception as e:
    print(f"❌ Error de Validación: {e}")
```

## Checklist de Verificación de Campos Críticos

Para `ERDEntity`:

- [ ] `id`: ¿Es string único?
- [ ] `attributes`: ¿Es una lista de `ERDAttribute`?
- [ ] `pk`: ¿Al menos un atributo tiene `pk=True`?

Para `ERDAttribute`:

- [ ] `type`: ¿Está normalizado (ej. "string", "int", "uuid") o es el tipo crudo de la herramienta externa? (Debería normalizarse).

## Errores Comunes

### Error: `ValidationError: Field required`

**Causa:** El adaptador no está pasando un campo obligatorio al constructor del modelo.
**Solución:** Revisar qué campos son `Optional` en `schemas.py` y proveer valores por defecto en el adaptador.

## Referencias

- [schemas.py](../../src/integrations/schemas.py)
