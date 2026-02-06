---
name: scaffold-page
description: Genera páginas Next.js App Router con i18n, tokens semánticos de tema, a11y y patrones del proyecto BlockFlow.
author: BlockFlow Dev Team
version: 2.0.0
---

# Skill: Scaffold de Página Next.js

Estandariza la creación de nuevas páginas en el frontend, asegurando consistencia con App Router, i18n (next-intl), sistema de temas dual (light/dark), y design system Glass.

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
├── [locale]/                      # Raíz i18n (next-intl)
│   ├── (auth)/                    # Grupo: páginas públicas de autenticación
│   │   ├── login/page.tsx
│   │   └── signup/page.tsx
│   ├── (dashboard)/               # Grupo: páginas protegidas
│   │   ├── DashboardClientLayout.tsx
│   │   ├── dashboard/page.tsx
│   │   ├── members/page.tsx
│   │   ├── roles/page.tsx
│   │   ├── billing/page.tsx
│   │   ├── settings/page.tsx
│   │   ├── audit-logs/page.tsx
│   │   ├── api-keys/page.tsx
│   │   └── tools/notion-er/page.tsx
│   └── onboarding/                # Flujo de onboarding
│       ├── page.tsx
│       └── [step]/page.tsx
└── layout.tsx                     # Root layout
```

## Reglas de Estilo OBLIGATORIAS

### Tokens de Tema (CERO HARDCODING)

| Categoría | Tokens Permitidos |
|---|---|
| **Fondos** | `bg-background`, `bg-glass-bg`, `bg-glass-bg-hover`, `bg-glass-bg-strong`, `bg-glass-overlay`, `bg-surface-page`, `bg-surface-raised`, `bg-card`, `bg-muted`, `bg-popover`, `bg-sidebar` |
| **Texto** | `text-foreground`, `text-text-highlight`, `text-text-subtle`, `text-text-secondary`, `text-text-tertiary`, `text-text-quaternary`, `text-text-ghost`, `text-muted-foreground`, `text-card-foreground` |
| **Bordes** | `border-border`, `border-glass-border`, `border-glass-border-subtle`, `border-input` |
| **Brand** | `text-neon-text`, `bg-neon-bg`, `bg-neon-bg-strong`, `border-neon-border`, `shadow-neon` |
| **Error** | `text-error-text`, `bg-error-bg`, `border-error-border` |
| **Gradientes** | `text-gradient-heading`, `text-gradient-heading-r` |

**PROHIBIDO**: `text-white`, `bg-white/*`, `bg-zinc-*`, `text-zinc-*`, `bg-black/*`, `text-gray-*`, `border-gray-*`, `bg-slate-*`

**Excepciones**: Colores de feature/marca con opacity (`bg-blue-500/10`, `text-blue-400`, `bg-purple-500/10`).

### Navegación

```tsx
// CORRECTO
import { Link, useRouter, usePathname } from "@/lib/navigation";

// INCORRECTO
import Link from "next/link";
import { useRouter } from "next/navigation";
```

**Excepciones**: `redirect` y `useParams` desde `next/navigation`.

---

## Templates

### Template A: Página de Listado (CRUD)

```tsx
"use client";

import { useState } from "react";
import { useTranslations } from "next-intl";
import { Plus, IconName } from "lucide-react";
import { GlassButton } from "@/components/ui/glass/GlassButton";

export default function FeatureNamePage() {
    const t = useTranslations("featureName");
    const [isCreateOpen, setIsCreateOpen] = useState(false);

    return (
        <div className="space-y-10 animate-in fade-in slide-in-from-bottom-2 duration-500">
            {/* Header */}
            <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-6">
                <div className="flex items-center gap-4">
                    <div className="p-3 rounded-2xl bg-blue-500/10 border border-blue-500/20">
                        <IconName className="h-6 w-6 text-blue-400" />
                    </div>
                    <div>
                        <h1 className="text-2xl font-bold text-text-highlight">
                            {t("title")}
                        </h1>
                        <p className="text-sm text-text-tertiary">
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

            {/* Content */}
            <div className="relative">
                {/* Decorative glow - only dark mode */}
                <div className="hidden dark:block absolute -top-40 -right-40 w-80 h-80 bg-blue-500/5 rounded-full blur-[100px] pointer-events-none" />

                {/* <FeatureTable /> */}
            </div>
        </div>
    );
}
```

### Template B: Página de Detalle/Configuración

```tsx
"use client";

import { useTranslations } from "next-intl";
import { Settings } from "lucide-react";
import { GlassCard } from "@/components/ui/glass/GlassCard";

export default function FeatureNamePage() {
    const t = useTranslations("featureName");

    return (
        <div className="space-y-8 animate-in fade-in slide-in-from-bottom-2 duration-500">
            {/* Header */}
            <div className="flex items-center gap-4">
                <div className="p-3 rounded-2xl bg-neon-bg border border-neon-border">
                    <Settings className="h-6 w-6 text-neon-text" />
                </div>
                <div>
                    <h1 className="text-2xl font-bold text-text-highlight">
                        {t("title")}
                    </h1>
                    <p className="text-sm text-text-tertiary">
                        {t("description")}
                    </p>
                </div>
            </div>

            {/* Content Cards */}
            <div className="grid gap-6 md:grid-cols-2">
                <GlassCard className="p-6">
                    <h2 className="text-lg font-semibold text-foreground mb-4">
                        {t("section1.title")}
                    </h2>
                    {/* Section content */}
                </GlassCard>

                <GlassCard className="p-6">
                    <h2 className="text-lg font-semibold text-foreground mb-4">
                        {t("section2.title")}
                    </h2>
                    {/* Section content */}
                </GlassCard>
            </div>
        </div>
    );
}
```

### Template C: Página con Tabs

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
                <h1 className="text-2xl font-bold text-text-highlight">
                    {t("title")}
                </h1>
                <p className="text-sm text-text-tertiary">{t("description")}</p>
            </div>

            {/* Tab Navigation */}
            <div className="flex gap-1 p-1 bg-glass-bg rounded-xl w-fit">
                {TABS.map((tab) => (
                    <button
                        key={tab}
                        onClick={() => setActiveTab(tab)}
                        className={cn(
                            "px-4 py-2 rounded-lg text-sm font-medium transition-all",
                            activeTab === tab
                                ? "bg-glass-bg-hover text-foreground"
                                : "text-text-secondary hover:text-foreground"
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

### Template D: Formulario con GlassInput

```tsx
"use client";

import { useState } from "react";
import { useTranslations } from "next-intl";
import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { z } from "zod";
import { GlassInput } from "@/components/ui/glass/GlassInput";
import { GlassButton } from "@/components/ui/glass/GlassButton";
import { GlassCard } from "@/components/ui/glass/GlassCard";

const formSchema = z.object({
    name: z.string().min(2),
    email: z.string().email(),
});

type FormData = z.infer<typeof formSchema>;

export default function FormPage() {
    const t = useTranslations("formPage");
    const [isLoading, setIsLoading] = useState(false);

    const { register, handleSubmit, formState: { errors } } = useForm<FormData>({
        resolver: zodResolver(formSchema),
    });

    const onSubmit = async (data: FormData) => {
        setIsLoading(true);
        try {
            // API call here
        } catch (err) {
            // Error handling
        } finally {
            setIsLoading(false);
        }
    };

    return (
        <div className="space-y-8 animate-in fade-in slide-in-from-bottom-2 duration-500">
            <div>
                <h1 className="text-2xl font-bold text-text-highlight">{t("title")}</h1>
                <p className="text-sm text-text-tertiary">{t("description")}</p>
            </div>

            <GlassCard className="max-w-lg p-8">
                <form onSubmit={handleSubmit(onSubmit)} className="space-y-6">
                    <GlassInput
                        label={t("nameLabel")}
                        placeholder={t("namePlaceholder")}
                        error={errors.name?.message}
                        {...register("name")}
                    />
                    <GlassInput
                        label={t("emailLabel")}
                        type="email"
                        placeholder={t("emailPlaceholder")}
                        error={errors.email?.message}
                        {...register("email")}
                    />
                    <GlassButton type="submit" className="w-full" disabled={isLoading}>
                        {isLoading ? t("saving") : t("save")}
                    </GlassButton>
                </form>
            </GlassCard>
        </div>
    );
}
```

---

## Pasos Post-Creación

### Paso 4: Agregar Keys i18n

Usar skill `add-i18n-keys` para agregar las traducciones necesarias en `messages/en.json` y `messages/es.json`.

### Paso 5: Agregar a Navegación (si aplica)

Editar `frontend/src/components/layout/sidebar.tsx` y agregar el item usando `Link` de `@/lib/navigation`.

### Paso 6: Agregar Metadata (SEO)

Para páginas públicas, agregar metadata.

---

## Checklist de Verificación

### Estructura
- [ ] Archivo `page.tsx` creado en `[locale]/` path correcto
- [ ] `"use client"` presente si usa hooks/estado

### Tema (Zero Hardcoding)
- [ ] CERO uso de `text-white`, `bg-white/*`, `bg-zinc-*`, `text-zinc-*`, `bg-black/*`, `text-gray-*`
- [ ] Todos los colores usan tokens semánticos
- [ ] Glows decorativos con `hidden dark:block`

### i18n
- [ ] `useTranslations("namespace")` implementado
- [ ] Keys en `en.json` Y `es.json`
- [ ] Cero textos hardcodeados en español/inglés

### Navegación
- [ ] Imports de `Link`, `useRouter`, `usePathname` desde `@/lib/navigation`

### a11y
- [ ] Headings jerárquicos (`h1` > `h2` > `h3`)
- [ ] Inputs con labels asociados (`htmlFor`)
- [ ] Botones de ícono con `aria-label`

---

*Última actualización: 2026-02-05*
