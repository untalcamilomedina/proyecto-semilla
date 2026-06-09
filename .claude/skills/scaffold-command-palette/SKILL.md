---
name: scaffold-command-palette
description: Implementa el Command Palette (⌘K) estilo Notion/Spotlight para navegación rápida.
author: AppNotion Design Team
version: 1.0.0
---

# Skill: Scaffold Command Palette

Esta skill implementa el icónico Command Palette (⌘K / Ctrl+K) que define la experiencia de Notion, Slack, VS Code y otras apps premium. Permite navegación rápida, búsqueda y ejecución de comandos.

## Características

| Feature | Descripción |
|---------|-------------|
| **Keyboard-first** | Abre con ⌘K (Mac) / Ctrl+K (Windows) |
| **Fuzzy search** | Búsqueda tolerante a errores |
| **Categorías** | Agrupa comandos por tipo |
| **Recientes** | Muestra acciones recientes |
| **Extensible** | Fácil agregar nuevos comandos |
| **i18n** | Soporta múltiples idiomas |

## Prerrequisitos

- [ ] Instalar dependencia:
  ```bash
  npm install cmdk
  ```
- [ ] Namespace i18n `commandPalette` creado.

## Cuándo Usar

- En aplicaciones tipo dashboard/SaaS.
- Para mejorar la productividad del usuario.
- Cuando hay muchas acciones/páginas para navegar.

---

## Implementación Completa

### 1. Agregar Keys i18n

**Archivo:** `frontend/messages/en.json`

```json
{
  "commandPalette": {
    "placeholder": "Type a command or search...",
    "noResults": "No results found.",
    "groups": {
      "navigation": "Navigation",
      "actions": "Actions",
      "recent": "Recent",
      "settings": "Settings"
    },
    "commands": {
      "goToDashboard": "Go to Dashboard",
      "goToMembers": "Go to Members",
      "goToSettings": "Go to Settings",
      "goToBilling": "Go to Billing",
      "inviteMember": "Invite member",
      "createRole": "Create new role",
      "toggleTheme": "Toggle dark mode",
      "logout": "Log out"
    }
  }
}
```

**Archivo:** `frontend/messages/es.json`

```json
{
  "commandPalette": {
    "placeholder": "Escribe un comando o busca...",
    "noResults": "No se encontraron resultados.",
    "groups": {
      "navigation": "Navegación",
      "actions": "Acciones",
      "recent": "Recientes",
      "settings": "Configuración"
    },
    "commands": {
      "goToDashboard": "Ir al Dashboard",
      "goToMembers": "Ir a Miembros",
      "goToSettings": "Ir a Configuración",
      "goToBilling": "Ir a Facturación",
      "inviteMember": "Invitar miembro",
      "createRole": "Crear nuevo rol",
      "toggleTheme": "Cambiar tema oscuro",
      "logout": "Cerrar sesión"
    }
  }
}
```

### 2. Crear Componente Command Palette

**Archivo:** `frontend/src/components/command-palette/CommandPalette.tsx`

```tsx
"use client";

import { useCallback, useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { useTranslations } from "next-intl";
import { Command } from "cmdk";
import {
    Home,
    Users,
    Settings,
    CreditCard,
    UserPlus,
    Shield,
    Moon,
    Sun,
    LogOut,
    Search,
} from "lucide-react";
import { cn } from "@/lib/utils";

interface CommandItem {
    id: string;
    labelKey: string;
    icon: React.ReactNode;
    action: () => void;
    group: "navigation" | "actions" | "settings";
    keywords?: string[];
}

export function CommandPalette() {
    const [open, setOpen] = useState(false);
    const [search, setSearch] = useState("");
    const router = useRouter();
    const t = useTranslations("commandPalette");

    // Toggle con keyboard shortcut
    useEffect(() => {
        const down = (e: KeyboardEvent) => {
            if (e.key === "k" && (e.metaKey || e.ctrlKey)) {
                e.preventDefault();
                setOpen((open) => !open);
            }
            if (e.key === "Escape") {
                setOpen(false);
            }
        };

        document.addEventListener("keydown", down);
        return () => document.removeEventListener("keydown", down);
    }, []);

    const runCommand = useCallback((command: () => void) => {
        setOpen(false);
        setSearch("");
        command();
    }, []);

    // Definir comandos
    const commands: CommandItem[] = [
        // Navigation
        {
            id: "dashboard",
            labelKey: "commands.goToDashboard",
            icon: <Home className="h-4 w-4" />,
            action: () => router.push("/"),
            group: "navigation",
            keywords: ["home", "inicio"],
        },
        {
            id: "members",
            labelKey: "commands.goToMembers",
            icon: <Users className="h-4 w-4" />,
            action: () => router.push("/members"),
            group: "navigation",
            keywords: ["users", "team", "equipo"],
        },
        {
            id: "settings",
            labelKey: "commands.goToSettings",
            icon: <Settings className="h-4 w-4" />,
            action: () => router.push("/settings"),
            group: "navigation",
            keywords: ["config", "preferences"],
        },
        {
            id: "billing",
            labelKey: "commands.goToBilling",
            icon: <CreditCard className="h-4 w-4" />,
            action: () => router.push("/billing"),
            group: "navigation",
            keywords: ["payment", "subscription", "pago"],
        },
        // Actions
        {
            id: "invite-member",
            labelKey: "commands.inviteMember",
            icon: <UserPlus className="h-4 w-4" />,
            action: () => {
                router.push("/members");
                // Trigger modal open via URL param or state
            },
            group: "actions",
            keywords: ["add", "new", "agregar"],
        },
        {
            id: "create-role",
            labelKey: "commands.createRole",
            icon: <Shield className="h-4 w-4" />,
            action: () => router.push("/roles?action=create"),
            group: "actions",
            keywords: ["permission", "permiso"],
        },
        // Settings
        {
            id: "toggle-theme",
            labelKey: "commands.toggleTheme",
            icon: <Moon className="h-4 w-4" />,
            action: () => {
                document.documentElement.classList.toggle("dark");
            },
            group: "settings",
            keywords: ["dark", "light", "oscuro", "claro"],
        },
        {
            id: "logout",
            labelKey: "commands.logout",
            icon: <LogOut className="h-4 w-4" />,
            action: () => {
                // Implement logout
                router.push("/login");
            },
            group: "settings",
            keywords: ["salir", "exit"],
        },
    ];

    const groupedCommands = {
        navigation: commands.filter((c) => c.group === "navigation"),
        actions: commands.filter((c) => c.group === "actions"),
        settings: commands.filter((c) => c.group === "settings"),
    };

    if (!open) return null;

    return (
        <div className="fixed inset-0 z-50">
            {/* Backdrop */}
            <div
                className="absolute inset-0 bg-black/50 backdrop-blur-sm animate-in fade-in duration-200"
                onClick={() => setOpen(false)}
            />

            {/* Command Dialog */}
            <div className="absolute left-1/2 top-[20%] -translate-x-1/2 w-full max-w-lg">
                <Command
                    className={cn(
                        "rounded-xl border border-border bg-popover shadow-2xl",
                        "animate-in fade-in zoom-in-95 duration-200"
                    )}
                    loop
                >
                    {/* Search Input */}
                    <div className="flex items-center border-b border-border px-4">
                        <Search className="h-4 w-4 text-muted-foreground" />
                        <Command.Input
                            value={search}
                            onValueChange={setSearch}
                            placeholder={t("placeholder")}
                            className={cn(
                                "flex-1 h-12 bg-transparent px-3",
                                "text-foreground placeholder:text-muted-foreground",
                                "focus:outline-none"
                            )}
                        />
                        <kbd className="hidden sm:inline-flex h-5 items-center gap-1 rounded border border-border bg-muted px-1.5 text-[10px] font-medium text-muted-foreground">
                            ESC
                        </kbd>
                    </div>

                    {/* Results */}
                    <Command.List className="max-h-80 overflow-y-auto p-2">
                        <Command.Empty className="py-6 text-center text-sm text-muted-foreground">
                            {t("noResults")}
                        </Command.Empty>

                        {/* Navigation Group */}
                        {groupedCommands.navigation.length > 0 && (
                            <Command.Group
                                heading={t("groups.navigation")}
                                className="px-2 py-1.5 text-xs font-medium text-muted-foreground"
                            >
                                {groupedCommands.navigation.map((command) => (
                                    <CommandItem
                                        key={command.id}
                                        command={command}
                                        onSelect={() => runCommand(command.action)}
                                        t={t}
                                    />
                                ))}
                            </Command.Group>
                        )}

                        {/* Actions Group */}
                        {groupedCommands.actions.length > 0 && (
                            <Command.Group
                                heading={t("groups.actions")}
                                className="px-2 py-1.5 text-xs font-medium text-muted-foreground"
                            >
                                {groupedCommands.actions.map((command) => (
                                    <CommandItem
                                        key={command.id}
                                        command={command}
                                        onSelect={() => runCommand(command.action)}
                                        t={t}
                                    />
                                ))}
                            </Command.Group>
                        )}

                        {/* Settings Group */}
                        {groupedCommands.settings.length > 0 && (
                            <Command.Group
                                heading={t("groups.settings")}
                                className="px-2 py-1.5 text-xs font-medium text-muted-foreground"
                            >
                                {groupedCommands.settings.map((command) => (
                                    <CommandItem
                                        key={command.id}
                                        command={command}
                                        onSelect={() => runCommand(command.action)}
                                        t={t}
                                    />
                                ))}
                            </Command.Group>
                        )}
                    </Command.List>

                    {/* Footer */}
                    <div className="flex items-center justify-between border-t border-border px-4 py-2 text-xs text-muted-foreground">
                        <div className="flex gap-2">
                            <kbd className="rounded border border-border bg-muted px-1.5 py-0.5">↑↓</kbd>
                            <span>navigate</span>
                        </div>
                        <div className="flex gap-2">
                            <kbd className="rounded border border-border bg-muted px-1.5 py-0.5">↵</kbd>
                            <span>select</span>
                        </div>
                    </div>
                </Command>
            </div>
        </div>
    );
}

// Individual Command Item
function CommandItem({
    command,
    onSelect,
    t,
}: {
    command: CommandItem;
    onSelect: () => void;
    t: (key: string) => string;
}) {
    return (
        <Command.Item
            value={`${command.id} ${command.keywords?.join(" ") || ""}`}
            onSelect={onSelect}
            className={cn(
                "flex items-center gap-3 px-3 py-2.5 rounded-lg cursor-pointer",
                "text-sm text-foreground",
                "transition-colors duration-150",
                // Selected/hover state
                "aria-selected:bg-muted"
            )}
        >
            <span className="text-muted-foreground">{command.icon}</span>
            <span>{t(command.labelKey)}</span>
        </Command.Item>
    );
}
```

### 3. Agregar al Layout

**Archivo:** `frontend/src/app/(dashboard)/DashboardClientLayout.tsx`

Agregar el componente al layout:

```tsx
import { CommandPalette } from "@/components/command-palette/CommandPalette";

export default function DashboardClientLayout({ children }) {
    return (
        <div>
            {/* Existing layout */}
            <Sidebar />
            <main>{children}</main>

            {/* Command Palette - siempre montado, se muestra con ⌘K */}
            <CommandPalette />
        </div>
    );
}
```

### 4. Indicador Visual (Opcional)

Agregar hint en el sidebar o header:

```tsx
function KeyboardHint() {
    return (
        <button
            onClick={() => {
                // Dispatch keyboard event
                document.dispatchEvent(
                    new KeyboardEvent("keydown", { key: "k", metaKey: true })
                );
            }}
            className="flex items-center gap-2 px-3 py-1.5 rounded-lg bg-muted/50 hover:bg-muted transition-colors text-sm text-muted-foreground"
        >
            <Search className="h-4 w-4" />
            <span>Search</span>
            <kbd className="ml-auto text-xs bg-background border border-border rounded px-1.5 py-0.5">
                ⌘K
            </kbd>
        </button>
    );
}
```

---

## Variantes Avanzadas

### Con Recientes

```tsx
// Hook para manejar recientes
function useRecentCommands() {
    const [recents, setRecents] = useState<string[]>([]);

    useEffect(() => {
        const stored = localStorage.getItem("recentCommands");
        if (stored) setRecents(JSON.parse(stored));
    }, []);

    const addRecent = (commandId: string) => {
        const updated = [commandId, ...recents.filter((id) => id !== commandId)].slice(0, 5);
        setRecents(updated);
        localStorage.setItem("recentCommands", JSON.stringify(updated));
    };

    return { recents, addRecent };
}
```

### Con Búsqueda de Contenido

```tsx
// Agregar búsqueda de contenido dinámico
const [searchResults, setSearchResults] = useState<SearchResult[]>([]);

useEffect(() => {
    if (search.length < 2) {
        setSearchResults([]);
        return;
    }

    const debounce = setTimeout(async () => {
        const results = await searchContent(search);
        setSearchResults(results);
    }, 300);

    return () => clearTimeout(debounce);
}, [search]);
```

### Con Subcommands (Nested)

```tsx
const [pages, setPages] = useState<string[]>([]);

// En el Command.List
{pages.length === 0 && (
    // Root commands
)}

{pages[0] === "settings" && (
    // Settings subcommands
    <Command.Group heading="Settings">
        <Command.Item onSelect={() => setPages([])}>
            ← Back
        </Command.Item>
        {/* Sub-items */}
    </Command.Group>
)}
```

---

## Estilizado Adicional

### Dark Mode Optimizado

```tsx
className={cn(
    // Light mode
    "bg-white border-gray-200",
    // Dark mode
    "dark:bg-zinc-900 dark:border-zinc-800",
    // Backdrop
    "shadow-xl dark:shadow-2xl dark:shadow-black/50"
)}
```

### Glassmorphism Variant

```tsx
className={cn(
    "bg-white/80 dark:bg-zinc-900/80",
    "backdrop-blur-xl",
    "border border-white/20 dark:border-white/10"
)}
```

---

## Checklist de Verificación

### Funcionalidad
- [ ] Abre con ⌘K (Mac) / Ctrl+K (Windows)
- [ ] Cierra con ESC o click fuera
- [ ] Navegación con flechas ↑↓
- [ ] Selección con Enter
- [ ] Búsqueda funciona con fuzzy matching

### i18n
- [ ] Placeholder traducido
- [ ] Nombres de comandos traducidos
- [ ] Grupos traducidos
- [ ] "No results" traducido

### Accesibilidad
- [ ] Focus trap dentro del modal
- [ ] `role="dialog"` y `aria-modal="true"`
- [ ] Labels para screen readers
- [ ] Keyboard navigable

### UX
- [ ] Animación de entrada suave
- [ ] Feedback visual en hover/selected
- [ ] Keywords para búsqueda alternativa

---

## Errores Comunes

### Error: Shortcut no funciona

**Causa:** Otro elemento captura el evento primero.

**Solución:** Usar `e.preventDefault()` y verificar que el listener está en `document`.

### Error: Resultados no filtran

**Causa:** `value` en Command.Item no incluye texto buscable.

**Solución:** Incluir keywords en el value:
```tsx
value={`${command.id} ${command.keywords?.join(" ")}`}
```

### Error: Modal no cierra al navegar

**Causa:** No se cierra el estado al ejecutar comando.

**Solución:** Llamar `setOpen(false)` antes de `router.push()`.

---

## Referencias

- [cmdk Documentation](https://cmdk.paco.me/)
- [Notion Command Palette](https://www.notion.so/)
- [Raycast](https://www.raycast.com/)
- [Skill add-i18n-keys](../add-i18n-keys/SKILL.md)

---

*Última actualización: 2025-02-04*
