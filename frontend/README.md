# ⚛️ Frontend - Proyecto Semilla

Este directorio contiene el código del frontend desarrollado en **Next.js**.

## 🏗️ Estructura (Planeada)

```
frontend/
├── app/                        # App Router (Next.js 14+)
│   ├── globals.css            # Estilos globales con Tailwind
│   ├── layout.tsx             # Layout raíz
│   ├── loading.tsx            # Loading UI
│   ├── error.tsx              # Error UI
│   ├── page.tsx               # Página de inicio
│   ├── (auth)/                # Grupo de rutas de autenticación
│   │   ├── login/
│   │   │   └── page.tsx       # Página de login
│   │   ├── register/
│   │   │   └── page.tsx       # Página de registro
│   │   └── layout.tsx         # Layout de auth
│   ├── (dashboard)/           # Grupo de rutas del dashboard
│   │   ├── dashboard/
│   │   │   └── page.tsx       # Dashboard principal
│   │   ├── users/
│   │   │   ├── page.tsx       # Lista de usuarios
│   │   │   ├── create/
│   │   │   │   └── page.tsx   # Crear usuario
│   │   │   └── [id]/
│   │   │       ├── page.tsx   # Detalle de usuario
│   │   │       └── edit/
│   │   │           └── page.tsx # Editar usuario
│   │   ├── roles/
│   │   │   └── page.tsx       # Gestión de roles
│   │   └── layout.tsx         # Layout del dashboard
│   └── api/                   # API Routes (si se necesita)
│       └── auth/
│           └── route.ts
├── components/                 # Componentes reutilizables
│   ├── ui/                    # Componentes base (shadcn/ui)
│   │   ├── button.tsx
│   │   ├── input.tsx
│   │   ├── card.tsx
│   │   └── ...
│   ├── auth/
│   │   ├── LoginForm.tsx
│   │   ├── RegisterForm.tsx
│   │   └── AuthGuard.tsx
│   ├── dashboard/
│   │   ├── Sidebar.tsx
│   │   ├── Header.tsx
│   │   └── StatsCard.tsx
│   ├── users/
│   │   ├── UserTable.tsx
│   │   ├── UserForm.tsx
│   │   └── UserCard.tsx
│   └── common/
│       ├── Loading.tsx
│       ├── ErrorBoundary.tsx
│       └── Layout.tsx
├── lib/                       # Utilidades y configuración
│   ├── auth.ts               # Lógica de autenticación
│   ├── api.ts                # Cliente API
│   ├── utils.ts              # Utilidades generales
│   ├── validations.ts        # Esquemas de validación (Zod)
│   └── constants.ts          # Constantes
├── hooks/                     # Custom React hooks
│   ├── useAuth.ts
│   ├── useUsers.ts
│   ├── useTenants.ts
│   └── useApi.ts
├── store/                     # Estado global (Zustand/React Query)
│   ├── authStore.ts
│   ├── userStore.ts
│   └── tenantStore.ts
├── types/                     # Definiciones de tipos TypeScript
│   ├── auth.ts
│   ├── user.ts
│   ├── tenant.ts
│   └── api.ts
├── locales/                   # Internacionalización
│   ├── es.json               # Español
│   ├── en.json               # Inglés
│   └── pt.json               # Portugués (futuro)
├── public/                    # Archivos estáticos
│   ├── images/
│   ├── icons/
│   └── favicon.ico
├── styles/                    # Estilos adicionales
│   └── components.css
├── __tests__/                 # Tests
│   ├── components/
│   ├── pages/
│   └── utils/
├── package.json
├── next.config.js
├── tailwind.config.js
├── tsconfig.json
├── jest.config.js
├── .eslintrc.json
└── Dockerfile
```

## 🚀 Stack Tecnológico

- **Framework**: Next.js 14+ (App Router)
- **Lenguaje**: TypeScript
- **Estilos**: Tailwind CSS + shadcn/ui
- **Estado**: Zustand + TanStack Query (React Query)
- **Forms**: React Hook Form + Zod
- **Internacionalización**: next-intl
- **Testing**: Jest + React Testing Library + Playwright
- **Linting**: ESLint + Prettier

## 📋 Características Planificadas

### ✅ Fase 1 (v0.1.0 - v0.3.0)
- [ ] Configuración de Next.js con App Router
- [ ] Sistema de autenticación con JWT
- [ ] Dashboard responsivo con Tailwind CSS
- [ ] Componentes base con shadcn/ui
- [ ] CRUD de usuarios y tenants
- [ ] Gestión de roles y permisos
- [ ] Validación de formularios
- [ ] Manejo de errores y loading states

### 🔮 Fases Futuras
- [ ] Internacionalización completa
- [ ] Temas personalizables por tenant
- [ ] Sistema de módulos/plugins
- [ ] Dashboard de analytics
- [ ] PWA capabilities
- [ ] Modo offline

## 🎨 Design System

### 🎭 Principios de Diseño
- **Mobile First**: Diseño responsivo desde móviles
- **Accesibilidad**: WCAG 2.1 AA compliance
- **Consistencia**: Sistema de componentes uniforme
- **Performance**: Optimización para Core Web Vitals

### 🎨 Colores (Planeados)
```css
:root {
  /* Primary Colors */
  --primary: 220 14.3% 95.9%;
  --primary-foreground: 220.9 39.3% 11%;
  
  /* Secondary Colors */
  --secondary: 220 14.3% 95.9%;
  --secondary-foreground: 220.9 39.3% 11%;
  
  /* Accent Colors */
  --accent: 220 14.3% 95.9%;
  --accent-foreground: 220.9 39.3% 11%;
  
  /* Status Colors */
  --success: 142 76% 36%;
  --warning: 38 92% 50%;
  --error: 0 72% 51%;
  --info: 213 94% 68%;
}
```

### 🧩 Componentes Base
- **Botones**: Variants (primary, secondary, outline, ghost)
- **Cards**: Para contenido agrupado
- **Forms**: Inputs, selects, textareas con validación
- **Navigation**: Sidebar, breadcrumbs, pagination
- **Feedback**: Alerts, toasts, modals
- **Data Display**: Tables, lists, stats cards

## 🔧 Desarrollo Local

```bash
# Una vez implementado, estos serán los comandos:

# Instalar dependencias
npm install

# Configurar variables de entorno
cp .env.example .env.local

# Ejecutar en modo desarrollo
npm run dev

# Ejecutar tests
npm run test
npm run test:e2e

# Build para producción
npm run build
npm run start

# Linting
npm run lint
npm run format

# Type checking
npm run type-check
```

## 🌐 Internacionalización

### Idiomas Soportados
- 🇪🇸 **Español**: Idioma principal
- 🇺🇸 **English**: Idioma secundario
- 🇧🇷 **Português**: Planificado para el futuro

### Implementación
```typescript
// Ejemplo de uso de next-intl
import { useTranslations } from 'next-intl';

export default function WelcomeMessage() {
  const t = useTranslations('Dashboard');
  
  return (
    <h1>{t('welcome', { name: user.name })}</h1>
  );
}
```

## 🔐 Seguridad Frontend

### Mejores Prácticas
- **Content Security Policy (CSP)**: Prevenir XSS
- **Input Sanitization**: Validar y limpiar inputs
- **JWT Storage**: Manejo seguro de tokens
- **Route Protection**: Guardas de autenticación
- **Environment Variables**: Separar secrets

### Validación
```typescript
// Ejemplo con Zod
import { z } from 'zod';

export const UserSchema = z.object({
  email: z.string().email('Email inválido'),
  password: z.string().min(8, 'Mínimo 8 caracteres'),
  firstName: z.string().min(1, 'Nombre requerido'),
  lastName: z.string().min(1, 'Apellido requerido'),
});

export type UserFormData = z.infer<typeof UserSchema>;
```

---

*Este directorio será poblado durante la Fase 1 del desarrollo.*