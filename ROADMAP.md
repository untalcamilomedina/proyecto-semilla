# Roadmap - AppNotion Marketplace (Unified Architecture)

> **Documento Base**: [UNIFIED_TECHNICAL_DOC.md](./docs/UNIFIED_TECHNICAL_DOC.md)

## Fase 1: Base & Core (API-First)

- [x] **Arquitectura**
  - [x] Refactor de estructura folders (`integrations/`, `api/`, `canonical/`).
  - [x] Definición de Modelos Canónicos (`FlowSpec`, `ERDSpec`) en JSON Schema/Pydantic.
  - [x] Sistema de Jobs Asíncronos (Celery) para tareas largas.
- [x] **API Core (OpenAPI)**
  - [x] Endpoints Autenticación (Existentes).
  - [x] Endpoint `POST /diagrams` (CRUD de diagramas).
  - [x] Endpoint `GET /jobs/{jobId}` (Consistencia de estado).

## Fase 2: Integración Notion (Deep Dive)

- [ ] **Conexión**
  - [ ] OAuth Flow para Notion (`/integrations/notion/connect`).
  - [ ] Gestión de Tokens por Tenant.
- [x] **Funcionalidad Escaneo**
  - [x] `POST /notion/workspaces/scan`: Escaneo de DBs Notion -> ERD Canónico.
- [x] **Escritura en Notion**
  - [x] `POST /notion/workspaces/apply-erd`: ERD Canónico -> Crear DBs en Notion.
  - [ ] Modo `dryRun` para validación antes de escritura.

## Fase 3: Integración Miro - Export

- [ ] **Conexión Miro**
  - [ ] OAuth Flow para Miro.
- [ ] **Exportación**
  - [ ] Converter: Canonical ERD -> Miro Shapes (JSON Payload).
  - [ ] `POST /miro/boards/{boardId}/export`.

## Fase 4: Integración Miro - Import

- [ ] **Miro App (Plugin)**
  - [ ] UI embebida (Sidebar en Miro).
  - [ ] Leer selección de frames/shapes.
- [ ] **Backend Import**
  - [ ] `POST /miro/boards/import`: Miro JSON -> Canonical Flow/ERD.

## Fase 5: IA Assist (Gemini 3)

- [ ] **Traducción Semántica**
  - [ ] `POST /translate/flow-to-erd`: Inferencia de entidades desde diagramas de flujo.
  - [ ] `POST /translate/notion-to-erd`: Mejora de nombres y relaciones.
- [ ] **Validación**
  - [ ] Sugerencias de normalización de datos.

---

## Estado Actual

- [x] Configuración Inicial Docker/Django.
- [x] Autenticación Base (Allauth).
- [x] **Refactor hacia Estructura Unificada** (Completado).
- [x] **Fase 2: Integración Notion** (Lógica Core Completada).
