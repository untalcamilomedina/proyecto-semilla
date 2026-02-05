---
name: scaffold-page
description: Genera páginas Next.js App Router con i18n, layout consistente y patrones del proyecto.
author: AppNotion Dev Team
version: 1.0.0
---

# Skill: Scaffold de Página Next.js

Esta skill estandariza la creación de nuevas páginas en el frontend, asegurando consistencia con la arquitectura App Router de Next.js 14+, integración con i18n (next-intl), y adherencia al design system Glass Minimalist.

## Prerrequisitos

- [ ] Definir ruta de la página (ej. `/settings/security`).
- [ ] Definir si es Client Component o Server Component.
- [ ] Tener el namespace i18n creado (ver skill `add-i18n-keys`).

## Cuándo Usar

- Al crear nuevas secciones del dashboard.
- Al agregar páginas dentro de grupos existentes (`(auth)`, `(dashboard)`).
- Al crear flujos multi-paso (wizards).

## Arquitectura de Rutas del Proyecto

```
frontend/src/app/
├── (auth)/                    # Grupo: páginas públicas de autenticación
│   ├── layout.tsx             # Layout con AuthLayout
│   ├── login/page.tsx
│   └── signup/page.tsx
├── (dashboard)/               # Grupo: páginas protegidas
│   ├── layout.tsx             # Layout con Sidebar
│   ├── DashboardClientLayout.tsx
│   ├── page.tsx               # Dashboard home
│   ├── members/page.tsx
│   ├── roles/page.tsx
│   ├── billing/page.tsx
│   ├── settings/page.tsx
│   ├── audit-logs/page.tsx
│   ├── api-keys/page.tsx
│   └── tools/
│       └── notion-er/page.tsx
├── onboarding/                # Flujo de onboarding
│   ├── layout.tsx
│   └── [step]/page.tsx
└── layout.tsx                 # Root layout
```

## Proceso

### Paso 1: Determinar Ubicación y Tipo

| Tipo de Página | Ubicación | Layout Heredado |
|----------------|-----------|-----------------|
| Dashboard protegida | `(dashboard)/[nombre]/` | Sidebar + Auth |
| Autenticación | `(auth)/[nombre]/` | AuthLayout |
| Pública (landing) | `(marketing)/[nombre]/` | Marketing layout |
| Herramienta/Tool | `(dashboard)/tools/[nombre]/` | Sidebar |

### Paso 2: Crear Archivo de Página

**Ubicación:** `frontend/src/app/(dashboard)/[nombre]/page.tsx`

### Paso 3: Elegir Template según Tipo

---

## Templates

### Template A: Página de Listado (CRUD)

Ideal para: Members, Roles, API Keys, etc.

```tsx
"use client";

import { useState } from "react";
import { useTranslations } from "next-intl";
import { Plus, IconName } from "lucide-react";
import { GlassButton } from "@/components/ui/glass/GlassButton";

/**
 * [FeatureName]Page
 * [Descripción breve de la página].
 *
 * @vibe Elite - High-density information with premium aesthetics.
 */
export default function FeatureNamePage() {
    const t = useTranslations("featureName");
    const [isCreateOpen, setIsCreateOpen] = useState(false);

    return (
        <div className="space-y-10 animate-in fade-in slide-in-from-bottom-2 duration-500">
            {/* Header Section */}
            <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-6">
                <div className="flex items-center gap-4">
                    <div className="p-3 rounded-2xl bg-blue-500/10 border border-blue-500/20">
                        <IconName className="h-6 w-6 text-blue-400" />
                    </div>
                    <div>
                        <h1 className="text-2xl font-bold text-white/90">
                            {t("title")}
                        </h1>
                        <p className="text-sm text-white/40">
                            {t("description")}
                        </p>
                    </div>
                </div>

                <GlassButton
                    onClick={() => setIsCreateOpen(true)}
                    className="h-11 px-6"
                >
                    <Plus className="mr-2 h-4 w-4" />
                    {t("createButton")}
                </GlassButton>
            </div>

            {/* Content Section */}
            <div className="relative">
                {/* Decorative glow */}
                <div className="absolute -top-40 -right-40 w-80 h-80 bg-blue-500/5 rounded-full blur-[100px] pointer-events-none" />

                {/* Table/List Component */}
                {/* <FeatureTable /> */}
            </div>

            {/* Modals */}
            {/* <CreateFeatureModal open={isCreateOpen} onOpenChange={setIsCreateOpen} /> */}
        </div>
    );
}
```

### Template B: Página de Detalle/Configuración

Ideal para: Settings, Profile, Billing details.

```tsx
"use client";

import { useTranslations } from "next-intl";
import { Settings } from "lucide-react";
import { GlassCard } from "@/components/ui/glass/GlassCard";

/**
 * [FeatureName]Page
 * [Descripción breve].
 */
export default function FeatureNamePage() {
    const t = useTranslations("featureName");

    return (
        <div className="space-y-8 animate-in fade-in slide-in-from-bottom-2 duration-500">
            {/* Header */}
            <div className="flex items-center gap-4">
                <div className="p-3 rounded-2xl bg-zinc-500/10 border border-zinc-500/20">
                    <Settings className="h-6 w-6 text-zinc-400" />
                </div>
                <div>
                    <h1 className="text-2xl font-bold text-white/90">
                        {t("title")}
                    </h1>
                    <p className="text-sm text-white/40">
                        {t("description")}
                    </p>
                </div>
            </div>

            {/* Content Cards */}
            <div className="grid gap-6 md:grid-cols-2">
                <GlassCard>
                    <h2 className="text-lg font-semibold text-white/80 mb-4">
                        {t("section1.title")}
                    </h2>
                    {/* Section content */}
                </GlassCard>

                <GlassCard>
                    <h2 className="text-lg font-semibold text-white/80 mb-4">
                        {t("section2.title")}
                    </h2>
                    {/* Section content */}
                </GlassCard>
            </div>
        </div>
    );
}
```

### Template C: Página Server Component (Data Fetching)

Ideal para: Páginas que necesitan datos del servidor antes de renderizar.

```tsx
import { getTranslations } from "next-intl/server";
import { Metadata } from "next";
import { FeatureClient } from "./FeatureClient";

export const metadata: Metadata = {
    title: "Feature Name | AppNotion",
    description: "Feature description for SEO",
};

async function getData() {
    // Fetch data from API
    const res = await fetch(`${process.env.API_URL}/endpoint`, {
        cache: "no-store", // o 'force-cache' para datos estáticos
    });

    if (!res.ok) throw new Error("Failed to fetch data");
    return res.json();
}

export default async function FeatureNamePage() {
    const t = await getTranslations("featureName");
    const data = await getData();

    return (
        <div className="space-y-8">
            <h1 className="text-2xl font-bold text-white/90">
                {t("title")}
            </h1>

            {/* Client Component para interactividad */}
            <FeatureClient initialData={data} />
        </div>
    );
}
```

### Template D: Página con Tabs

Ideal para: Settings con múltiples secciones, Profile.

```tsx
"use client";

import { useState } from "react";
import { useTranslations } from "next-intl";
import { cn } from "@/lib/utils";

const TABS = ["general", "security", "notifications"] as const;
type Tab = typeof TABS[number];

export default function SettingsPage() {
    const t = useTranslations("settings");
    const [activeTab, setActiveTab] = useState<Tab>("general");

    return (
        <div className="space-y-8">
            {/* Header */}
            <div>
                <h1 className="text-2xl font-bold text-white/90">
                    {t("title")}
                </h1>
                <p className="text-sm text-white/40">{t("description")}</p>
            </div>

            {/* Tab Navigation */}
            <div className="flex gap-1 p-1 bg-white/5 rounded-xl w-fit">
                {TABS.map((tab) => (
                    <button
                        key={tab}
                        onClick={() => setActiveTab(tab)}
                        className={cn(
                            "px-4 py-2 rounded-lg text-sm font-medium transition-all",
                            activeTab === tab
                                ? "bg-white/10 text-white"
                                : "text-white/50 hover:text-white/70"
                        )}
                    >
                        {t(`tabs.${tab}`)}
                    </button>
                ))}
            </div>

            {/* Tab Content */}
            <div className="mt-6">
                {activeTab === "general" && <GeneralSettings />}
                {activeTab === "security" && <SecuritySettings />}
                {activeTab === "notifications" && <NotificationSettings />}
            </div>
        </div>
    );
}
```

---

## Pasos Post-Creación

### Paso 4: Agregar Keys i18n

Usar skill `add-i18n-keys` para agregar las traducciones necesarias.

**Mínimo requerido:**
```json
{
  "featureName": {
    "title": "Page Title",
    "description": "Page description"
  }
}
```

### Paso 5: Agregar a Navegación (si aplica)

Editar `frontend/src/components/layout/sidebar.tsx`:

```tsx
const navItems = [
  // ... existing items
  {
    href: "/feature-name",
    icon: IconName,
    label: t("nav.featureName"),
  },
];
```

### Paso 6: Agregar Metadata (SEO)

Para páginas públicas, agregar metadata:

```tsx
import { Metadata } from "next";

export const metadata: Metadata = {
    title: "Page Title | AppNotion",
    description: "Page description for search engines",
    openGraph: {
        title: "Page Title",
        description: "Description for social sharing",
    },
};
```

---

## Checklist de Verificación

### Estructura
- [ ] Archivo `page.tsx` creado en ubicación correcta
- [ ] `"use client"` presente si usa hooks/estado
- [ ] JSDoc con descripción y `@vibe` tag

### i18n
- [ ] `useTranslations` o `getTranslations` implementado
- [ ] Keys agregadas a `en.json` y `es.json`
- [ ] No hay textos hardcodeados

### Estilo
- [ ] Usa componentes Glass (`GlassCard`, `GlassButton`)
- [ ] Animación de entrada: `animate-in fade-in slide-in-from-bottom-2`
- [ ] Responsive: funciona en móvil (`flex-col sm:flex-row`)
- [ ] Glow decorativo donde aplica

### Accesibilidad
- [ ] Headings jerárquicos (`h1` > `h2` > `h3`)
- [ ] Iconos tienen `aria-hidden="true"` o texto alternativo
- [ ] Botones tienen texto descriptivo

---

## Errores Comunes

### Error: "useTranslations is not a function"

**Causa:** Usar hook en Server Component sin `'use client'`.

**Solución:** Agregar `"use client";` al inicio o usar `getTranslations`.

### Error: Página no aparece en navegación

**Causa:** Falta agregar entrada en sidebar.

**Solución:** Editar `sidebar.tsx` y agregar el item de navegación.

### Error: Layout incorrecto

**Causa:** Página fuera del grupo de rutas correcto.

**Solución:** Mover a `(dashboard)/` para sidebar, `(auth)/` para auth layout.

---

## Referencias

- [Estructura de rutas](../../frontend/src/app/)
- [Componentes Glass](../../frontend/src/components/ui/glass/)
- [Skill add-i18n-keys](../add-i18n-keys/SKILL.md)
- [Next.js App Router Docs](https://nextjs.org/docs/app)

---

*Última actualización: 2025-02-04*
