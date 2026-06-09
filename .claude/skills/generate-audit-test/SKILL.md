---
name: generate-audit-test
description: Crea tests unitarios de auditoría para validar la lógica "API First" (mocking de I/O externo).
author: AppNotion Dev Team
version: 1.0.0
---

# Skill: Generar Test de Auditoría

Esta skill guía la creación de tests unitarios que aíslan la lógica de negocio (`Service`) de las dependencias externas (`Client`). Es fundamental para el enfoque **API First**, permitiendo verificar la lógica sin necesidad de frontend ni conexiones reales a terceros.

## Prerrequisitos

- [ ] El `Service` y `Client` deben existir.
- [ ] `pytest` y `pytest-asyncio` instalados.

## Cuándo Usar

- Inmediatamente después de implementar `services.py`.
- Antes de escribir el código del Frontend.
- Para validar que la transformación de datos (Adapter) es correcta.

## Proceso

### Paso 1: Identificar el Flujo

Determinar qué método del servicio se va a probar (ej. `scan_resource`) y qué llamadas externas realiza (ej. `Client.get_resource`).

### Paso 2: Crear Archivo de Test

Crear el archivo en `tests/` con el prefijo `audit_`.

```bash
touch tests/audit_<integration>_flow.py
```

### Paso 3: Template de Audit Test

Copiar y adaptar este template. La clave es usar `unittest.mock.patch` para reemplazar el Cliente real.

```python
import pytest
from unittest.mock import AsyncMock, patch
from integrations.schemas import ERDSpec
# Importar módulos reales
from integrations.<integration>.services import <Integration>Service

@pytest.mark.asyncio
async def test_<integration>_flow():
    """
    Verifies the Logic Flow: Service -> Adapter -> Client.
    Mocks external API calls.
    """
    # 1. Mock Data (Respuesta simulada de la API externa)
    mock_external_response = {
        "id": "123",
        "name": "Test Resource",
        "properties": {}
    }

    # 2. Mock Internal Components
    # Patch apunta a donde se IMPORTA la clase Client en services.py
    with patch("integrations.<integration>.services.<Integration>Client") as MockClient:
        # Configurar la instancia del mock
        mock_instance = MockClient.return_value
        mock_instance.get_resource = AsyncMock(return_value=mock_external_response)

        # 3. Execute Service Logic
        result = await <Integration>Service.scan_resource("fake_token", "resource_123")

        # 4. Assertions (Audit)
        assert isinstance(result, ERDSpec)
        assert len(result.entities) == 1
        assert result.entities[0].name == "Test Resource"

        print("\n✅ API First Audit: <Integration> logic verified.")

if __name__ == "__main__":
    import asyncio
    asyncio.run(test_<integration>_flow())
```

### Paso 4: Ejecución

Ejecutar el test directamente o vía pytest (dentro de Docker si hay dependencias complejas).

```bash
python tests/audit_<integration>_flow.py
```

## Checklist de Verificación

- [ ] El test corre con `python file.py` (bloque main).
- [ ] Se usa `AsyncMock` para métodos asíncronos.
- [ ] Se valida el tipo de retorno (debe ser Modelo Canónico).
- [ ] No se hacen llamadas reales a internet.

## Errores Comunes

### Error: `ModuleNotFoundError`

**Causa:** Ejecutar el test fuera del contenedor Docker si faltan dependencias.
**Solución:** Ejecutar dentro de `docker compose exec web ...`.

### Error: `got Future <Future pending> attached to a different loop`

**Causa:** Mezclar loops de asyncio.
**Solución:** Usar `pytest-asyncio` o el bloque `if __name__ == "__main__"` correctamente.

## Referencias

- [Ejemplo Notion](../../tests/audit_notion_flow.py)
- [Ejemplo Miro](../../tests/audit_miro_flow.py)
