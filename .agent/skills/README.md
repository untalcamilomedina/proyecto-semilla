# Catálogo de Skills - AppNotion

Este directorio contiene las "Skills" (capacidades automatizadas) desarrolladas para estandarizar y acelerar el desarrollo del proyecto **AppNotion**, siguiendo la arquitectura **Clean Architecture API-First**.

## Índice de Skills

### 🧩 Arquitectura & Backend

| Skill                                                       | Descripción                                                                      | Uso Típico                                     |
| ----------------------------------------------------------- | -------------------------------------------------------------------------------- | ---------------------------------------------- |
| [new-integration-module](./new-integration-module/SKILL.md) | Genera el esqueleto estándar (Client-Adapter-Service) para nuevas integraciones. | Al añadir una herramienta nueva (ej. Jira).    |
| [scaffold-api-endpoint](./scaffold-api-endpoint/SKILL.md)   | Expone servicios de negocio en la API (ViewSet + Router) correctamente.          | Al crear endpoints REST para lógica existente. |

### 🧪 Calidad & Testing

| Skill                                                     | Descripción                                                 | Uso Típico                                           |
| --------------------------------------------------------- | ----------------------------------------------------------- | ---------------------------------------------------- |
| [generate-audit-test](./generate-audit-test/SKILL.md)     | Crea tests de auditoría para validar "API First" con mocks. | Después de crear lógica de negocio, antes del front. |
| [canonical-model-check](./canonical-model-check/SKILL.md) | Validación manual de Adaptadores contra Esquemas Pydantic.  | Al escribir lógica de adaptación de datos.           |
| [test-api-endpoint](./test-api-endpoint/SKILL.md)         | Tests de integración HTTP para endpoints REST.              | Para validar endpoints antes del frontend.           |
| [test-api-contract](./test-api-contract/SKILL.md)         | Valida que la API cumple con el schema OpenAPI.             | En CI/CD para detectar breaking changes.             |
| [test-e2e-flow](./test-e2e-flow/SKILL.md)                 | Tests E2E de flujos completos de usuario en la API.         | Para validar flujos críticos de negocio.             |

### 📜 Documentación & API First

| Skill                                                     | Descripción                                                | Uso Típico                          |
| --------------------------------------------------------- | ---------------------------------------------------------- | ----------------------------------- |
| [enrich-openapi-schema](./enrich-openapi-schema/SKILL.md) | Enriquece Swagger con ejemplos y descripciones detalladas. | Para documentar endpoints públicos. |

### 🎨 Frontend & UI

| Skill                                                             | Descripción                                                        | Uso Típico                                     |
| ----------------------------------------------------------------- | ------------------------------------------------------------------ | ---------------------------------------------- |
| [create-design-component](./create-design-component/SKILL.md)     | Crea componentes UI "Glass Minimalist" con a11y e i18n.            | Al desarrollar nuevos elementos visuales.      |
| [scaffold-page](./scaffold-page/SKILL.md)                         | Genera páginas Next.js App Router con i18n y layout consistente.   | Al crear nuevas secciones del dashboard.       |
| [create-form-component](./create-form-component/SKILL.md)         | Formularios validados con react-hook-form, Zod e i18n.             | Al crear formularios de entrada de datos.      |
| [scaffold-offline-repository](./scaffold-offline-repository/SKILL.md) | Repositorio Offline-First con IndexedDB encriptado + Sync.     | Al implementar funcionalidad PWA.              |

### ✨ UX & Micro-Interacciones (Estilo Notion/Google)

| Skill                                                             | Descripción                                                        | Uso Típico                                     |
| ----------------------------------------------------------------- | ------------------------------------------------------------------ | ---------------------------------------------- |
| [create-micro-interaction](./create-micro-interaction/SKILL.md)   | Animaciones, skeleton loaders, transiciones estilo Notion/Google.  | Al pulir la experiencia visual.                |
| [scaffold-command-palette](./scaffold-command-palette/SKILL.md)   | Command Palette (⌘K) para navegación rápida estilo Notion.         | Al implementar búsqueda global y acciones.     |

### 🌍 Internacionalización (i18n)

| Skill                                           | Descripción                                                     | Uso Típico                                 |
| ----------------------------------------------- | --------------------------------------------------------------- | ------------------------------------------ |
| [add-i18n-keys](./add-i18n-keys/SKILL.md)       | Agregar traducciones i18n consistentemente (es-LA, en-US).      | Al crear componentes con texto al usuario. |

### 🛠️ Meta-Skills

| Skill                                             | Descripción                                        | Uso Típico                                 |
| ------------------------------------------------- | -------------------------------------------------- | ------------------------------------------ |
| [skill-generator](./skill-generator/SKILL.md)     | Meta-skill para crear nuevas skills correctamente. | Al identificar un nuevo patrón repetitivo. |

---

## Cobertura por Área

| Área | Skills | Estado |
|------|--------|--------|
| Backend/Integraciones | 2 | ✅ Cubierto |
| Testing/Calidad | 5 | ✅ Pirámide Completa |
| Documentación API | 1 | ✅ Bueno |
| Frontend/UI | 4 | ✅ Completo |
| UX/Micro-Interacciones | 2 | ✅ Estilo Notion/Google |
| i18n | 1 | ✅ Cubierto |
| Meta-Skills | 1 | ✅ Cubierto |

**Total: 16 Skills**

---

## Cómo Usar una Skill

1. **Leer**: Abrir el archivo `SKILL.md` de la skill deseada.
2. **Copiar**: Usar los templates proporcionados.
3. **Adaptar**: Reemplazar placeholders (`<IntegrationName>`, etc.).
4. **Verificar**: Seguir el checklist de la skill antes de darla por terminada.

## Flujo Recomendado para Nuevas Features

```
┌─────────────────────────────────────────────────────────────────┐
│                     DESARROLLO DE FEATURE                       │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  1. BACKEND                                                     │
│     └─► new-integration-module (si es integración externa)      │
│     └─► scaffold-api-endpoint (exponer en API)                  │
│     └─► enrich-openapi-schema (documentar)                      │
│                                                                 │
│  2. TESTING API (antes del frontend)                            │
│     └─► generate-audit-test (tests unitarios con mocks)         │
│     └─► test-api-endpoint (tests de integración HTTP)           │
│     └─► test-api-contract (validar OpenAPI schema)              │
│     └─► test-e2e-flow (flujos completos críticos)               │
│                                                                 │
│  3. FRONTEND                                                    │
│     └─► add-i18n-keys (crear traducciones)                      │
│     └─► scaffold-page (crear página)                            │
│     └─► create-design-component (componentes UI)                │
│     └─► create-form-component (si tiene formularios)            │
│                                                                 │
│  4. UX POLISH (estilo Notion/Google)                            │
│     └─► create-micro-interaction (animaciones, skeletons)       │
│     └─► scaffold-command-palette (⌘K navigation)                │
│                                                                 │
│  5. PWA (opcional)                                              │
│     └─► scaffold-offline-repository (datos offline)             │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

---

## Convenciones

### Estructura de cada Skill

```
.agent/skills/
└── nombre-skill/
    └── SKILL.md          # Documentación principal
```

### Formato de SKILL.md

1. **Frontmatter YAML** con name, description, author, version
2. **Introducción** de 1-2 párrafos
3. **Prerrequisitos** (checklist)
4. **Cuándo Usar / NO usar**
5. **Proceso** paso a paso
6. **Templates** copiables
7. **Checklist** de verificación
8. **Errores Comunes** con soluciones
9. **Referencias** a archivos del proyecto

---

_Mantenido por el Equipo de Desarrollo AppNotion._
_Última actualización: 2025-02-04_
