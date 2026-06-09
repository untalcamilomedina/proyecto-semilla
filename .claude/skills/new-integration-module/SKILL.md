---
name: new-integration-module
description: Genera el esqueleto estándar (Clean Architecture) para integrar cualquier API de terceros en Proyecto Semilla.
author: Proyecto Semilla Dev Team
version: 1.1.0
---

# Skill: Crear Nuevo Módulo de Integración

Esta skill estandariza la integración de cualquier API de terceros (e.g., Jira, Stripe, HubSpot, Google Drive) asegurando que todas sigan la arquitectura de capas: `Client` -> `Adapter` -> `Service`. Cada integración vive en su propia app Django que tú creas (ej. `src/integrations_acme/`); el boilerplate no incluye ninguna app de integraciones preexistente.

A lo largo de la skill usamos una API ficticia, **"Acme CRM"**, como dominio de ejemplo — sustituye `acme`/`Acme` por el nombre real de tu proveedor.

## Prerrequisitos

- [ ] Conocer el nombre en minúsculas de la integración (ej. `acme`).
- [ ] Tener acceso a `src/` para crear la nueva app.

## Cuándo Usar

- Al iniciar el desarrollo de una nueva integración externa.
- Para evitar copiar y pegar archivos de otras integraciones y arrastrar errores.

## Proceso

### Paso 1: Crear la App de la Integración

Crear el paquete Python de la nueva integración como app independiente dentro de `src/`.

```bash
mkdir -p src/integrations_acme
touch src/integrations_acme/__init__.py
```

> Si la integración necesita persistir datos (modelos/migraciones), créala con `python manage.py startapp integrations_acme src/integrations_acme` y regístrala en `INSTALLED_APPS`. Si solo orquesta llamadas externas, basta con el paquete plano.

### Paso 2: Crear `schemas.py` (Modelo Canónico)

Define aquí el modelo Pydantic al que TODA respuesta externa debe traducirse. El resto del proyecto solo conoce este modelo, nunca el formato del proveedor.

**Archivo:** `src/integrations_acme/schemas.py`

```python
from pydantic import BaseModel

class ItemSpec(BaseModel):
    """Modelo canónico de ejemplo — sustituye por el de tu dominio."""
    name: str
    fields: list[str] = []
```

### Paso 3: Crear `client.py` (SDK Wrapper)

Este archivo maneja la comunicación HTTP pura y la autenticación. Nunca debe contener lógica de negocio.

**Archivo:** `src/integrations_acme/client.py`

```python
import logging
from typing import Any, Dict

logger = logging.getLogger(__name__)

class AcmeClient:
    """
    Wrapper for the Acme CRM API.
    Handles Auth and HTTP transport.
    """
    def __init__(self, token: str):
        self.token = token
        # Initialize SDK or HTTP Client here (httpx.AsyncClient, etc.)

    async def get_resource(self, resource_id: str) -> Dict[str, Any]:
        """
        Example method to fetch raw data from Acme CRM.
        """
        # Implement API call (GET https://api.acme.example/v1/resources/{id})
        ...
```

### Paso 4: Crear `adapters.py` (Translator)

Este archivo convierte los datos "sucios" de la API externa al Modelo Canónico (`ItemSpec`). Debe ser una función pura: dict de entrada, modelo de salida, sin I/O.

**Archivo:** `src/integrations_acme/adapters.py`

```python
from typing import Any, Dict
from .schemas import ItemSpec

class AcmeAdapter:
    """
    Transforms Acme CRM domain objects to Canonical Models.
    """

    @staticmethod
    def external_to_canonical(data: Dict[str, Any]) -> ItemSpec:
        """
        Maps external dict to ItemSpec.
        """
        return ItemSpec(
            name=data.get("name", "Untitled"),
            fields=list(data.get("properties", {}).get("fields", [])),
        )
```

### Paso 5: Crear `services.py` (Business Logic)

Orquesta el flujo: Cliente -> Adaptador -> Resultado.

**Archivo:** `src/integrations_acme/services.py`

```python
from .schemas import ItemSpec
from .client import AcmeClient
from .adapters import AcmeAdapter

class AcmeService:
    """
    Business logic for the Acme CRM integration.
    """

    @staticmethod
    async def sync_items(token: str, resource_id: str) -> ItemSpec:
        """
        Orchestrates fetching and adapting data.
        """
        client = AcmeClient(token)
        # 1. Fetch
        raw_data = await client.get_resource(resource_id)
        # 2. Adapt
        return AcmeAdapter.external_to_canonical(raw_data)
```

## Checklist de Verificación

- [ ] App creada en `src/integrations_<proveedor>/` (registrada en `INSTALLED_APPS` solo si tiene modelos).
- [ ] `schemas.py` define el modelo canónico (Pydantic) de la integración.
- [ ] `client.py` maneja la autenticación y el transporte HTTP, sin lógica de negocio.
- [ ] `adapters.py` solo importa `schemas` y es una transformación pura (sin I/O).
- [ ] `services.py` es estático o singleton (stateless).
- [ ] Los nombres de clases siguen PascalCase (ej. `AcmeClient`, `AcmeService`).

## Errores Comunes

### Error: "Ciclo de Importación"

**Causa:** Importar `services` dentro de `models` o viceversa.
**Solución:** Los servicios deben ser "hojas" o solo importar adaptadores/clientes.

## Referencias

- [Arquitectura del proyecto](../../../docs/architecture.md)
- [Skill: generate-audit-test](../generate-audit-test/SKILL.md) — para testear el servicio con mocks.
