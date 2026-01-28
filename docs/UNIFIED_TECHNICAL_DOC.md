# 📘 DOCUMENTO TÉCNICO UNIFICADO

## Plataforma de Diagramas → Miro → Notion (API-First)

### Autor: Arquitectura Técnica

### Stack base: Proyecto Semilla (Django, DRF, OpenAPI, Multitenancy, Celery, Next.js)

---

## 1. OBJETIVO DEL SISTEMA

Construir una plataforma **API-First** que permita:

1. Dibujar **diagramas de flujo y ERD** en una interfaz propia o en **Miro**
2. Convertir esos diagramas en:
   - Diagramas ERD estructurados
   - Bases de datos reales en **Notion**

3. Escanear **Notion** y reconstruir:
   - ERD
   - Diagramas visuales

4. Exportar e importar bidireccionalmente entre:
   - Editor propio
   - Miro
   - Notion

5. Usar **IA (Gemini 3)** como asistente de traducción y validación (no como fuente de verdad)

---

## 2. PRINCIPIOS ARQUITECTÓNICOS

- **API-First** (OpenAPI como contrato)
- **Modelo canónico interno** (no depender de Miro ni Notion)
- **Multitenancy por schema** (Proyecto Semilla)
- **Asincronía por Jobs** (Celery)
- **Integraciones desacopladas**
- **IA asistida, no determinística**
- **Idempotencia y auditoría**

---

## 3. MULTITENANCY (CRÍTICO)

### Estrategia adoptada

**Subdominio por tenant**

```
https://{tenant}.tudominio.com/api/v1/...
```

### Implicaciones

- Todos los datos viven en el schema del tenant
- OAuth callbacks reciben `state` con:

```json
{
  "tenant": "demo",
  "user_id": "uuid",
  "redirect": "/app/integrations"
}
```

---

## 4. MODELO CANÓNICO (LENGUAJE INTERNO)

### 4.1 FlowSpec (Diagrama de Flujo)

```json
{
  "nodes": [
    {
      "id": "n1",
      "type": "start|process|decision|end",
      "label": "Texto",
      "meta": {}
    }
  ],
  "edges": [
    {
      "id": "e1",
      "from": "n1",
      "to": "n2",
      "label": "",
      "meta": {}
    }
  ],
  "layout": {
    "engine": "elk|dagre|manual",
    "positions": {
      "n1": { "x": 0, "y": 0 }
    }
  }
}
```

---

### 4.2 ERDSpec (Entidad-Relación)

```json
{
  "entities": [
    {
      "id": "users",
      "name": "Users",
      "attributes": [
        { "name": "id", "type": "uuid", "pk": true },
        { "name": "email", "type": "text", "unique": true }
      ]
    }
  ],
  "relationships": [
    {
      "id": "users_orders",
      "from": "users",
      "to": "orders",
      "cardinality": "1:N",
      "fk": {
        "fromAttribute": "id",
        "toAttribute": "user_id"
      }
    }
  ],
  "notes": []
}
```

---

## 5. ESTRUCTURA DE MÓDULOS (BACKEND)

```
src/
├── api/                 # Gateway API + versionado
├── oauth/               # Auth base (ya existe)
├── integrations/
│   ├── miro/
│   │   ├── client.py
│   │   ├── models.py
│   │   ├── services.py
│   ├── notion/
│   │   ├── client.py
│   │   ├── models.py
│   │   ├── services.py
│   ├── schemas.py       # FlowSpec / ERDSpec
│   ├── tasks.py         # Celery jobs
│   ├── api.py           # DRF Views
│   └── models.py        # IntegrationConnection, Job
```

---

## 6. MAPA COMPLETO DE ENDPOINTS (API v1)

**Base URL**

```
/api/v1
```

---

### 6.1 Autenticación (existente)

```
POST   /auth/login
POST   /auth/refresh
POST   /auth/logout
```

---

## 6.2 Integraciones (OAuth)

### Miro

```
GET  /integrations/miro/connect
GET  /integrations/miro/callback
```

### Notion

```
GET  /integrations/notion/connect
GET  /integrations/notion/callback
POST /integrations/notion/token
```

---

## 6.3 Diagramas (Core)

```
POST   /diagrams
GET    /diagrams
GET    /diagrams/{diagramId}
PATCH  /diagrams/{diagramId}
POST   /diagrams/{diagramId}/versions
```

---

## 6.4 Traducciones / IA

```
POST /translate/flow-to-erd
POST /translate/notion-to-erd
POST /translate/erd-to-notion-plan
```

> Gemini 3 se usa aquí para:
>
> - inferencia de llaves
> - normalización de nombres
> - sugerencias de relaciones

---

## 6.5 Miro

### Exportar a Miro

```
POST /miro/boards/{boardId}/export
```

```json
{
  "diagramId": "uuid",
  "mode": "APPEND|REPLACE_LAYER",
  "layout": "elk",
  "idempotencyKey": "string"
}
```

### Importar desde Miro

```
POST /miro/boards/{boardId}/import
```

```json
{
  "selection": "ALL|FRAME_ID|ITEM_IDS",
  "frameId": "optional",
  "itemIds": []
}
```

---

## 6.6 Notion

### Crear bases de datos desde ERD

```
POST /notion/workspaces/{workspaceId}/apply-erd
```

```json
{
  "diagramId": "uuid",
  "parentPageId": "notion_page_id",
  "dryRun": true
}
```

---

### Escanear Notion → ERD

```
POST /notion/workspaces/{workspaceId}/scan
```

```json
{
  "mode": "DATABASE_IDS|SEARCH",
  "databaseIds": [],
  "searchQuery": "optional"
}
```

---

## 6.7 Jobs (Asíncronos)

```
GET /jobs/{jobId}
```

```json
{
  "id": "uuid",
  "status": "PENDING|RUNNING|SUCCEEDED|FAILED",
  "progress": 0.0,
  "result": {},
  "error": {}
}
```

---

## 7. OPENAPI (OBLIGATORIO)

- OpenAPI 3.x
- Schema expuesto en:

```
GET /api/schema/
GET /api/docs/
```

Todos los endpoints deben documentar:

- request / response
- errores
- ejemplos
- tags

---

## 8. FRONTEND (POST-API)

### Páginas mínimas

1. Login
2. Dashboard
3. Integrations (Miro / Notion)
4. Diagram Editor (Flow / ERD)
5. Import (Miro / Notion)
6. Jobs & Activity

---

## 9. MIRO APP (REQUERIDO PARA IMPORT)

- App embebida en board
- Permite:
  - seleccionar frame
  - leer shapes/connectors
  - enviar payload al backend

---

## 10. FASES DE DESARROLLO

### Fase 1 – Base

- OpenAPI
- Diagram CRUD
- Jobs

### Fase 2 – Notion

- Scan
- Apply ERD (dryRun + real)

### Fase 3 – Miro Export

- Shapes + connectors

### Fase 4 – Miro Import

- Backend + Miro App

### Fase 5 – IA (Gemini)

- Flow → ERD
- Normalización y validación

---

## 11. REGLAS CLAVE

- ❌ IA no escribe datos directamente
- ✅ Todo pasa por el modelo canónico
- ✅ Dry-run antes de escribir en Notion
- ✅ Todo es idempotente
- ✅ Todo es tenant-aware

---
