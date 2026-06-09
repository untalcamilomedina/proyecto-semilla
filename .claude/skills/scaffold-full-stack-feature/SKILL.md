---
name: scaffold-full-stack-feature
description: Guía maestra para crear una feature completa (Vertical Slice) desde el Backend hasta el Frontend.
author: AppNotion Architecture Team
version: 1.0.0
---

# Skill: Scaffold Full Stack Feature

Esta skill orquesta el uso de otras skills para construir una "Vertical Slice" completa. Sigue este proceso para agregar funcionalidades nuevas al sistema (ej. "Projects", "Tags", "Comments").

## Prerrequisitos

- [ ] Nombre de la feature (singular y plural). Ej: `project`, `projects`.
- [ ] Modelo de datos mental o esquema DB.

---

## Fase 1: Backend (API First)

### 1. Crear Módulo y API

Usa la skill `new-integration-module` o `scaffold-api-endpoint` según corresponda.

1.  **Modelo**: Definir en `models.py`.
2.  **Serializer**: Crear en `api.py` (o `serializers.py` si es módulo grande).
3.  **ViewSet**: Implementar CRUD en `api.py`.
4.  **Tests**: Usar skill `test-api-endpoint`.

### 2. Registrar URL

En `src/api/v1/urls.py`:

```python
router.register("projects", ProjectViewSet, basename="projects")
```

👉 **Resultado**: Endpoint funcional `http://localhost:8010/api/v1/projects/`.

---

## Fase 2: Frontend (Interface)

### 1. Definir Tipos

En `frontend/src/types/index.ts` o `frontend/src/types/api.ts` (si usas generación automática, ejecuta `npm run api:generate`).

### 2. Crear Página y UI

Usa la skill `scaffold-page`.

1.  **Crear Directorio**: `frontend/src/app/(dashboard)/projects/`.
2.  **Crear Page**: `page.tsx` usando el **Template A (Listado)** de `scaffold-page`.
3.  **Componentes**: Si necesitas custom UI, usa `create-design-component` para crear `ProjectCard.tsx` en `frontend/src/components/projects/`.

### 3. Conectar API

En `page.tsx`, usa los helpers de `lib/api.ts`:

```typescript
const { data, error } = useSWR("/api/v1/projects/", apiGet);
```

### 4. Configurar Navegación

En `frontend/src/components/layout/sidebar.tsx`, agrega la entrada:

```typescript
{
  href: "/projects",
  icon: Folder, // Lucide icon
  label: "Projects", // O t("nav.projects")
}
```

---

## Fase 3: Internacionalización (i18n)

Usa la skill `add-i18n-keys`.

1.  Editar `frontend/messages/en.json` y `es.json`.
2.  Agregar namespace `projects`:

```json
"projects": {
  "title": "Projects",
  "description": "Manage your creative projects.",
  "createButton": "New Project"
}
```

---

## Checklist de Finalización

- [ ] **Backend**: CRUD funciona en Postman/Swagger.
- [ ] **Tests**: `pytest` pasa en verde.
- [ ] **Frontend**: Página carga datos reales.
- [ ] **UI**: Usa componentes Glass (`GlassCard`, `GlassButton`).
- [ ] **i18n**: Labels traducidos en EN/ES.
- [ ] **Navegación**: Accesible desde Sidebar.

---

## Referencias Relacionadas

- [scaffold-api-endpoint](../scaffold-api-endpoint/SKILL.md)
- [scaffold-page](../scaffold-page/SKILL.md)
- [create-design-component](../create-design-component/SKILL.md)
- [add-i18n-keys](../add-i18n-keys/SKILL.md)
