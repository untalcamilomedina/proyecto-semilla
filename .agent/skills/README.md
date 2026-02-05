# Catálogo de Skills - AppNotion

Este directorio contiene las "Skills" (capacidades automatizadas) desarrolladas para estandarizar y acelerar el desarrollo del proyecto **AppNotion**, siguiendo la arquitectura **Clean Architecture API-First**.

## Indice de Skills

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

### 📜 Documentación & API First

| Skill                                                     | Descripción                                                | Uso Típico                          |
| --------------------------------------------------------- | ---------------------------------------------------------- | ----------------------------------- |
| [enrich-openapi-schema](./enrich-openapi-schema/SKILL.md) | Enriquece Swagger con ejemplos y descripciones detalladas. | Para documentar endpoints públicos. |

### 🎨 Frontend & Diseño

| Skill                                                         | Descripción                                                   | Uso Típico                                 |
| ------------------------------------------------------------- | ------------------------------------------------------------- | ------------------------------------------ |
| [create-design-component](./create-design-component/SKILL.md) | Crea componentes UI "Google Glass Minimalist" (Mobile First). | Al desarrollar nuevos elementos visuales.  |
| [skill-generator](./skill-generator/SKILL.md)                 | Meta-skill para crear nuevas skills correctamente.            | Al identificar un nuevo patrón repetitivo. |

## Cómo Usar una Skill

1.  **Leer**: Abrir el archivo `SKILL.md` de la skill deseada.
2.  **Copiar**: Usar los templates proporcionados.
3.  **Verificar**: Seguir el checklist de la skill antes de darla por terminada.

---

_Mantenido por el Equipo de Desarrollo AppNotion._
