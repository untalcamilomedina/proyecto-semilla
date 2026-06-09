---
name: generate-audit-test
description: Crea tests unitarios de auditoría para validar la lógica "API First" (mocking de I/O externo).
author: Proyecto Semilla Dev Team
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

Determinar qué método del servicio se va a probar (ej. `sync_items`) y qué llamadas externas realiza (ej. `Client.get_items`).

### Paso 2: Crear Archivo de Test

Crear el archivo en `tests/` con el sufijo `_audit` (el prefijo `test_` permite que pytest lo recolecte automáticamente).

```bash
touch tests/test_<integracion>_audit.py
```

### Paso 3: Template de Audit Test

Copiar y adaptar este template. La clave es usar `unittest.mock.patch` para reemplazar el Cliente real. El ejemplo usa una integración ficticia "Acme CRM" (`src/integrations_acme/`) — sustituye nombres y rutas por los de tu módulo.

```python
import pytest
from unittest.mock import AsyncMock, patch
from pydantic import BaseModel

class ItemSpec(BaseModel):
    """Modelo canónico de ejemplo — sustituye por el de tu dominio.
    En tu proyecto vivirá en tu app (ej. integrations_acme/schemas.py)
    y lo importarás desde allí."""
    name: str
    fields: list[str] = []

# Importar el servicio real de tu app
from integrations_acme.services import AcmeService

@pytest.mark.asyncio
async def test_acme_sync_audit():
    """
    Verifies the Logic Flow: Service -> Adapter -> Client.
    Mocks external API calls.
    """
    # 1. Mock Data (Respuesta simulada de la API externa)
    mock_external_response = {
        "id": "123",
        "name": "Test Resource",
        "properties": {"fields": ["email", "phone"]}
    }

    # 2. Mock Internal Components
    # Patch apunta a donde se IMPORTA la clase Client en services.py
    with patch("integrations_acme.services.AcmeClient") as MockClient:
        # Configurar la instancia del mock
        mock_instance = MockClient.return_value
        mock_instance.get_resource = AsyncMock(return_value=mock_external_response)

        # 3. Execute Service Logic
        result = await AcmeService.sync_items("fake_token", "resource_123")

        # 4. Assertions (Audit)
        assert isinstance(result, ItemSpec)
        assert result.name == "Test Resource"
        assert "email" in result.fields

        print("\n✅ API First Audit: Acme logic verified.")

if __name__ == "__main__":
    import asyncio
    asyncio.run(test_acme_sync_audit())
```

### Paso 4: Ejecución

Ejecutar el test directamente o vía pytest (dentro de Docker si hay dependencias complejas).

```bash
pytest tests/test_<integracion>_audit.py -v
# o de forma directa (bloque main):
python tests/test_<integracion>_audit.py
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

- [Ejemplo de tests con mocks de I/O externo](../../../tests/test_billing_webhooks.py)
- [Ejemplo de tests de API](../../../tests/test_api_v1.py)
