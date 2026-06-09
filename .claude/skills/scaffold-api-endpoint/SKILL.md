---
name: scaffold-api-endpoint
description: Guía para exponer servicios en la API (ViewSet + URLs) de forma segura y estándar.
author: AppNotion Dev Team
version: 1.0.0
---

# Skill: Scaffold API Endpoint

Esta skill sistematiza el proceso de exponer lógica de negocio en la API REST, asegurando que se registren correctamente en el router y se maneje la sincronicidad.

## Prerrequisitos

- [ ] `Service` implementado.
- [ ] `integrations/api.py` existente.
- [ ] `api/v1/urls.py` existente.

## Proceso

### Paso 1: Definir ViewSet

Editar `src/integrations/api.py`. Crear un `ViewSet` que envuelva el servicio.
**Nota Importante**: Django REST Framework (DRF) es síncrono por defecto. Si el servicio es asíncrono, usar `asgiref.sync.async_to_sync`.

```python
from asgiref.sync import async_to_sync
from rest_framework import viewsets, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from .<integration>.services import <Integration>Service

class <Integration>ViewSet(viewsets.ViewSet):
    permission_classes = [permissions.IsAuthenticated]

    @action(detail=False, methods=["post"])
    def <action_name>(self, request):
        # 1. Input Validation
        token = request.data.get("token")
        if not token:
             return Response({"error": "Missing token"}, status=400)

        try:
            # 2. Call Service (Sync Wrapper)
            result = async_to_sync(<Integration>Service.<method_name>)(token)
            return Response(result)
        except Exception as e:
            return Response({"error": str(e)}, status=500)
```

### Paso 2: Registrar URL

Editar `src/api/v1/urls.py`.

1.  **Importar el ViewSet**:
    ```python
    from integrations.api import <Integration>ViewSet
    ```
2.  **Registrar en Router**:
    ```python
    router.register("integrations/<name>", <Integration>ViewSet, basename="<name>-integration")
    ```

## Checklist de Verificación

- [ ] ViewSet hereda de `viewsets.ViewSet` (o ModelViewSet si hay DB).
- [ ] Se usa `async_to_sync` si el servicio es `async def`.
- [ ] Permisos configurados (`IsAuthenticated`).
- [ ] endpoint registrado en `router`.
- [ ] Verificar en `http://localhost:8010/api/docs/` que el endpoint aparece.

## Errores Comunes

### Error: `ImproperlyConfigured`

**Causa:** Registrar el ViewSet sin `basename` cuando no tiene `queryset`.
**Solución:** Siempre añadir `basename="..."` en `router.register` para ViewSets personalizados.

### Error: `RuntimeError: There is no current event loop`

**Causa:** Llamar código async sin `async_to_sync` adentro de una vista síncrona.
