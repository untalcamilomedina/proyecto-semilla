---
name: add-i18n-keys
description: Guía para agregar traducciones i18n consistentemente (es-LA, en-US) usando next-intl.
author: AppNotion Dev Team
version: 1.0.0
---

# Skill: Agregar Claves de Internacionalización (i18n)

Esta skill estandariza el proceso de agregar nuevas traducciones al proyecto, asegurando consistencia entre idiomas y siguiendo las convenciones establecidas con `next-intl`.

## Prerrequisitos

- [ ] Conocer el namespace donde irá la traducción (ej. `auth`, `dashboard`, `billing`).
- [ ] Tener acceso a `frontend/messages/`.

## Cuándo Usar

- Al crear nuevos componentes que muestran texto al usuario.
- Al agregar nuevas páginas o secciones.
- Al modificar textos existentes en la UI.

**NO usar cuando:**
- El texto es técnico y no visible al usuario (logs, errores de consola).
- Son valores de configuración o constantes de código.

## Arquitectura i18n del Proyecto

```
frontend/
├── i18n.ts                    # Configuración next-intl
├── messages/
│   ├── en.json               # Inglés (US) - Fuente de verdad
│   └── es.json               # Español (Latinoamérica)
├── middleware.ts             # Detección de locale
└── src/
    └── components/           # Uso con useTranslations()
```

## Proceso

### Paso 1: Identificar el Namespace

Los namespaces agrupan traducciones por dominio funcional:

| Namespace | Uso | Ejemplo de Keys |
|-----------|-----|-----------------|
| `common` | Acciones globales, estados | `loading`, `save`, `cancel` |
| `auth` | Login, signup, sesión | `login`, `forgotPassword` |
| `nav` | Navegación, menús | `dashboard`, `settings` |
| `dashboard` | Página principal | `welcome`, `quickActions` |
| `members` | Gestión de miembros | `invite`, `role` |
| `roles` | Permisos y roles | `permissions`, `createRole` |
| `billing` | Facturación, planes | `currentPlan`, `cancelSubscription` |
| `onboarding` | Flujo de registro | `step1.title`, `step2.modules` |
| `settings` | Configuración | `language`, `theme` |
| `audit` | Logs de auditoría | `actor`, `action` |
| `keys` | API Keys | `createButton`, `revoked` |

### Paso 2: Definir la Key

**Convenciones de Naming:**

```
namespace.keyName           → Nivel 1 (simple)
namespace.group.keyName     → Nivel 2 (agrupado)
namespace.group.sub.keyName → Nivel 3 (máximo recomendado)
```

**Reglas:**
- Usar `camelCase` para keys: `loginDescription`, `noResults`
- Usar sustantivos o verbos en infinitivo: `save`, `delete`, `title`
- Ser descriptivo pero conciso: `emailPlaceholder` vs `theEmailInputPlaceholder`
- Agrupar por contexto: `step1.title`, `step1.description`

**Interpolación de Variables:**

```json
{
  "welcome": "Bienvenido, {name}",
  "count": "{count} miembros",
  "pagination": "Página {current} de {total}"
}
```

### Paso 3: Agregar a Archivos de Mensajes

**IMPORTANTE:** Siempre agregar a AMBOS archivos simultáneamente.

**Archivo:** `frontend/messages/en.json` (Fuente de verdad)

```json
{
  "myNamespace": {
    "myKey": "English text",
    "myGroup": {
      "nestedKey": "Nested English text with {variable}"
    }
  }
}
```

**Archivo:** `frontend/messages/es.json`

```json
{
  "myNamespace": {
    "myKey": "Texto en español",
    "myGroup": {
      "nestedKey": "Texto anidado en español con {variable}"
    }
  }
}
```

### Paso 4: Usar en Componente

**Hook `useTranslations`:**

```tsx
'use client';

import { useTranslations } from 'next-intl';

export function MyComponent() {
  const t = useTranslations('myNamespace');

  return (
    <div>
      <h1>{t('myKey')}</h1>
      <p>{t('myGroup.nestedKey', { variable: 'valor' })}</p>
    </div>
  );
}
```

**Para Server Components:**

```tsx
import { getTranslations } from 'next-intl/server';

export default async function MyPage() {
  const t = await getTranslations('myNamespace');

  return <h1>{t('title')}</h1>;
}
```

**Múltiples Namespaces:**

```tsx
const tCommon = useTranslations('common');
const tAuth = useTranslations('auth');

return (
  <>
    <button>{tCommon('save')}</button>
    <span>{tAuth('loginDescription')}</span>
  </>
);
```

## Templates

### Template: Nueva Sección Completa

**en.json:**
```json
{
  "newFeature": {
    "title": "Feature Title",
    "description": "Feature description text",
    "actions": {
      "create": "Create new",
      "edit": "Edit",
      "delete": "Delete"
    },
    "messages": {
      "success": "Operation completed successfully",
      "error": "An error occurred",
      "confirmDelete": "Are you sure you want to delete {name}?"
    },
    "empty": {
      "title": "No items yet",
      "description": "Create your first item to get started"
    }
  }
}
```

**es.json:**
```json
{
  "newFeature": {
    "title": "Título de la Función",
    "description": "Texto descriptivo de la función",
    "actions": {
      "create": "Crear nuevo",
      "edit": "Editar",
      "delete": "Eliminar"
    },
    "messages": {
      "success": "Operación completada exitosamente",
      "error": "Ocurrió un error",
      "confirmDelete": "¿Estás seguro de que deseas eliminar {name}?"
    },
    "empty": {
      "title": "No hay elementos todavía",
      "description": "Crea tu primer elemento para comenzar"
    }
  }
}
```

### Template: Componente con i18n

```tsx
'use client';

import { useTranslations } from 'next-intl';
import { Button } from '@/components/ui/button';

interface Props {
  itemName: string;
  onDelete: () => void;
}

export function DeleteConfirmation({ itemName, onDelete }: Props) {
  const t = useTranslations('newFeature');
  const tCommon = useTranslations('common');

  return (
    <div>
      <p>{t('messages.confirmDelete', { name: itemName })}</p>
      <div className="flex gap-2">
        <Button variant="outline">{tCommon('cancel')}</Button>
        <Button variant="destructive" onClick={onDelete}>
          {t('actions.delete')}
        </Button>
      </div>
    </div>
  );
}
```

## Consideraciones Regionales

### Español Latinoamericano (es-419)

| Evitar (España) | Usar (LATAM) |
|-----------------|--------------|
| Vosotros | Ustedes |
| Móvil | Celular |
| Ordenador | Computadora |
| Vale | OK / Está bien |
| Coger | Tomar / Agarrar |

### Formato de Fechas y Números

```tsx
import { useFormatter } from 'next-intl';

function MyComponent() {
  const format = useFormatter();

  // Fechas
  const date = format.dateTime(new Date(), {
    year: 'numeric',
    month: 'long',
    day: 'numeric'
  });

  // Números
  const price = format.number(1234.56, {
    style: 'currency',
    currency: 'USD'
  });
}
```

## Checklist de Verificación

### Obligatorio
- [ ] Key agregada en `en.json`
- [ ] Key agregada en `es.json` con traducción correcta
- [ ] Keys usan `camelCase`
- [ ] Variables usan formato `{variable}`
- [ ] Componente usa `useTranslations()` o `getTranslations()`

### Recomendado
- [ ] Textos siguen convenciones LATAM (no España)
- [ ] No hay textos hardcodeados en el componente
- [ ] Se reutilizan keys de `common` cuando aplica
- [ ] Plurales manejan caso singular y plural

## Errores Comunes

### Error: Key no encontrada en runtime

**Síntoma:** `Missing translation for key: "namespace.myKey"`

**Causa:** Key existe en un idioma pero no en el otro.

**Solución:** Verificar que la key existe en AMBOS archivos con la misma estructura.

### Error: Interpolación no funciona

**Síntoma:** Se muestra `{name}` literal en lugar del valor.

**Causa:** No se pasa el objeto de variables al llamar `t()`.

**Solución:**
```tsx
// ❌ Incorrecto
t('welcome')

// ✅ Correcto
t('welcome', { name: userName })
```

### Error: useTranslations en Server Component

**Síntoma:** `useTranslations is not a function` o error de hooks.

**Causa:** Usar hook en Server Component sin `'use client'`.

**Solución:** Usar `getTranslations` (async) para Server Components:
```tsx
// Server Component
const t = await getTranslations('namespace');
```

## Referencias

- [Configuración i18n](../../frontend/i18n.ts)
- [Mensajes EN](../../frontend/messages/en.json)
- [Mensajes ES](../../frontend/messages/es.json)
- [Documentación next-intl](https://next-intl-docs.vercel.app/)

---

*Última actualización: 2025-02-04*
