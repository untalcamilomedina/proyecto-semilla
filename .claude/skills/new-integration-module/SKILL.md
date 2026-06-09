---
name: new-integration-module
description: Genera el esqueleto estándar (Clean Architecture) para una nueva integración en AppNotion.
author: AppNotion Dev Team
version: 1.0.0
---

# Skill: Crear Nuevo Módulo de Integración

Esta skill estandariza la creación de nuevas integraciones (e.g., Jira, Trello, Google Drive) asegurando que todas sigan la arquitectura de capas definida en el proyecto: `Client` -> `Adapter` -> `Service`.

## Prerrequisitos

- [ ] Conocer el nombre en minúsculas de la integración (ej. `jira`).
- [ ] Tener acceso a `src/integrations/`.

## Cuándo Usar

- Al iniciar el desarrollo de una nueva integración externa.
- Para evitar copiar y pegar archivos de otras integraciones y arrastrar errores.

## Proceso

### Paso 1: Crear Directorio

Crear el paquete de python para la nueva integración.

```bash
mkdir -p src/integrations/<integration_name>
touch src/integrations/<integration_name>/__init__.py
```

### Paso 2: Crear `client.py` (SDK Wrapper)

Este archivo maneja la comunicación HTTP pura y la autenticación. Nunca debe contener lógica de negocio.

**Archivo:** `src/integrations/<integration_name>/client.py`

```python
import logging
from typing import Any, Dict, Optional

logger = logging.getLogger(__name__)

class <IntegrationName>Client:
    """
    Wrapper for <IntegrationName> API.
    Handles Auth and HTTP transport.
    """
    def __init__(self, token: str):
        self.token = token
        # Initialize SDK or HTTP Client here

    async def get_resource(self, resource_id: str) -> Dict[str, Any]:
        """
        Example method to fetch data.
        """
        # Implement API call
        pass
```

### Paso 3: Crear `adapters.py` (Translator)

Este archivo convierte los datos "sucios" de la API externa a los Modelos Canónicos (`ERDSpec`, `FlowSpec`).

**Archivo:** `src/integrations/<integration_name>/adapters.py`

```python
from typing import Dict, Any
from integrations.schemas import ERDEntity, ERDAttribute

class <IntegrationName>Adapter:
    """
    Transforms <IntegrationName> domain objects to Canonical Models.
    """

    @staticmethod
    def external_to_canonical(data: Dict[str, Any]) -> ERDEntity:
        """
        Maps external dict to ERDEntity.
        """
        # Implement mapping logic
        return ERDEntity(
            id=str(data.get("id")),
            name=data.get("name", "Untitled"),
            attributes=[]
        )
```

### Paso 4: Crear `services.py` (Business Logic)

Orquesta el flujo: Cliente -> Adaptador -> Resultado.

**Archivo:** `src/integrations/<integration_name>/services.py`

```python
from integrations.schemas import ERDSpec
from .client import <IntegrationName>Client
from .adapters import <IntegrationName>Adapter

class <IntegrationName>Service:
    """
    Business logic for <IntegrationName> integration.
    """

    @staticmethod
    async def scan_resource(token: str, resource_id: str) -> ERDSpec:
        """
        Orchestrates fetching and adapting data.
        """
        client = <IntegrationName>Client(token)
        # 1. Fetch
        raw_data = await client.get_resource(resource_id)
        # 2. Adapt
        entity = <IntegrationName>Adapter.external_to_canonical(raw_data)

        return ERDSpec(entities=[entity], relationships=[])
```

## Checklist de Verificación

- [ ] Directorio creado en `src/integrations/`.
- [ ] `client.py` maneja la autenticación.
- [ ] `adapters.py` importa `integrations.schemas`.
- [ ] `services.py` es estático o singleton (stateless).
- [ ] Los nombres de clases siguen PascalCase (ej. `JiraClient`).

## Errores Comunes

### Error: "Ciclo de Importación"

**Causa:** Importar `services` dentro de `models` o viceversa.
**Solución:** Los servicios deben ser "hojas" o solo importar adaptadores/clientes.

## Referencias

- [Arquitectura Unificada](../../docs/UNIFIED_TECHNICAL_DOC.md)
