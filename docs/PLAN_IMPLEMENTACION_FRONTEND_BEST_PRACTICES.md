# 🚀 PLAN DE IMPLEMENTACIÓN FRONTEND - MEJORES PRÁCTICAS

## 📋 METODOLOGÍA DE TRABAJO

### 1. Estrategia de Commits (Conventional Commits)
```bash
# Formato de commits
<tipo>(<alcance>): <descripción>

# Tipos permitidos:
feat:     Nueva funcionalidad
fix:      Corrección de bug
docs:     Documentación
style:    Formato (no afecta lógica)
refactor: Refactorización
test:     Añadir tests
chore:    Tareas de mantenimiento
```

### 2. Flujo de Desarrollo por Feature
```bash
# 1. Crear branch para cada feature
git checkout -b feat/authentication-system

# 2. Desarrollar con commits atómicos
git add src/components/auth/login-form.tsx
git commit -m "feat(auth): add login form component with validation"

# 3. Documentar mientras desarrollas
git add docs/AUTHENTICATION.md
git commit -m "docs(auth): add authentication flow documentation"

# 4. Añadir tests
git add __tests__/auth/login.test.tsx
git commit -m "test(auth): add login form unit tests"

# 5. Merge con squash
git checkout main
git merge --squash feat/authentication-system
git commit -m "feat(auth): implement complete authentication system"
```

---

## 🏗️ ESTRUCTURA DE PROYECTO CON MEJORES PRÁCTICAS

```
frontend/
├── src/
│   ├── app/                      # Next.js App Router
│   │   ├── (auth)/               # Grupo de rutas públicas
│   │   │   ├── login/
│   │   │   ├── register/
│   │   │   └── layout.tsx
│   │   ├── (dashboard)/          # Grupo de rutas protegidas
│   │   │   ├── dashboard/
│   │   │   └── layout.tsx
│   │   └── api/                  # API Routes (si necesario)
│   ├── components/
│   │   ├── auth/                 # Componentes de autenticación
│   │   ├── forms/                # Formularios reutilizables
│   │   ├── layouts/              # Layouts compartidos
│   │   └── ui/                   # Componentes UI base
│   ├── hooks/                    # Custom hooks
│   ├── lib/                      # Utilidades y configuraciones
│   ├── services/                 # Servicios API
│   ├── stores/                   # Estado global (Zustand)
│   ├── types/                    # TypeScript types/interfaces
│   └── utils/                    # Funciones helper
├── __tests__/                    # Tests
├── docs/                         # Documentación técnica
└── .github/                      # CI/CD workflows
```

---

## 📅 PLAN DÍA POR DÍA CON MEJORES PRÁCTICAS

### DÍA 1: Setup y Autenticación Base

#### 🎯 Objetivo: Configuración inicial y login funcional

#### 📝 Tareas:
```bash
# 1. Setup inicial
npm install -D @types/node @typescript-eslint/parser @typescript-eslint/eslint-plugin
npm install -D prettier eslint-config-prettier husky lint-staged
npm install -D @testing-library/react @testing-library/jest-dom jest

# 2. Configurar pre-commit hooks
npx husky-init && npm install
npx husky add .pre-commit "npm run lint && npm run test"
```

#### 📦 Archivos a crear:

##### `.eslintrc.json`
```json
{
  "extends": [
    "next/core-web-vitals",
    "plugin:@typescript-eslint/recommended",
    "prettier"
  ],
  "rules": {
    "@typescript-eslint/no-unused-vars": "error",
    "@typescript-eslint/no-explicit-any": "warn"
  }
}
```

##### `prettier.config.js`
```javascript
module.exports = {
  semi: true,
  trailingComma: 'es5',
  singleQuote: true,
  printWidth: 80,
  tabWidth: 2,
};
```

##### `src/types/auth.types.ts`
```typescript
export interface User {
  id: string;
  email: string;
  firstName: string;
  lastName: string;
  tenantId: string;
  roles: Role[];
}

export interface Role {
  id: string;
  name: string;
  permissions: string[];
}

export interface LoginRequest {
  email: string;
  password: string;
}

export interface LoginResponse {
  accessToken: string;
  refreshToken: string;
  user: User;
}

export interface AuthState {
  user: User | null;
  token: string | null;
  isAuthenticated: boolean;
  isLoading: boolean;
}
```

##### `src/services/auth.service.ts`
```typescript
import { apiClient } from '@/lib/api-client';
import type { LoginRequest, LoginResponse } from '@/types/auth.types';

class AuthService {
  private readonly BASE_PATH = '/auth';

  async login(credentials: LoginRequest): Promise<LoginResponse> {
    const response = await apiClient.post<LoginResponse>(
      `${this.BASE_PATH}/login`,
      credentials
    );
    return response.data;
  }

  async logout(): Promise<void> {
    await apiClient.post(`${this.BASE_PATH}/logout`);
  }

  async refreshToken(token: string): Promise<LoginResponse> {
    const response = await apiClient.post<LoginResponse>(
      `${this.BASE_PATH}/refresh`,
      { refreshToken: token }
    );
    return response.data;
  }

  async validateToken(): Promise<boolean> {
    try {
      await apiClient.get(`${this.BASE_PATH}/validate`);
      return true;
    } catch {
      return false;
    }
  }
}

export const authService = new AuthService();
```

#### 🧪 Tests:
##### `__tests__/services/auth.service.test.ts`
```typescript
import { authService } from '@/services/auth.service';
import { apiClient } from '@/lib/api-client';

jest.mock('@/lib/api-client');

describe('AuthService', () => {
  describe('login', () => {
    it('should call API with correct credentials', async () => {
      const mockResponse = {
        data: {
          accessToken: 'token',
          refreshToken: 'refresh',
          user: { id: '1', email: 'test@test.com' }
        }
      };
      
      (apiClient.post as jest.Mock).mockResolvedValue(mockResponse);
      
      const result = await authService.login({
        email: 'test@test.com',
        password: 'password123'
      });
      
      expect(apiClient.post).toHaveBeenCalledWith(
        '/auth/login',
        { email: 'test@test.com', password: 'password123' }
      );
      expect(result).toEqual(mockResponse.data);
    });
  });
});
```

#### 📝 Documentación:
##### `docs/AUTHENTICATION.md`
```markdown
# Authentication System

## Overview
JWT-based authentication with refresh tokens.

## Flow
1. User submits credentials to `/auth/login`
2. Backend validates and returns tokens
3. Frontend stores tokens in httpOnly cookies
4. All requests include Authorization header
5. Tokens refresh automatically before expiry

## Security Considerations
- Tokens stored in httpOnly cookies
- CSRF protection enabled
- XSS prevention through input sanitization
- Rate limiting on auth endpoints
```

#### 📊 Commits del Día 1:
```bash
git commit -m "chore: setup eslint, prettier, and testing infrastructure"
git commit -m "feat(types): add authentication type definitions"
git commit -m "feat(auth): implement auth service with login/logout"
git commit -m "test(auth): add unit tests for auth service"
git commit -m "docs(auth): document authentication flow and security"
```

---

### DÍA 2: Formularios de Login/Register con Testing

#### 📦 Componentes a crear:

##### `src/components/forms/form-field.tsx`
```typescript
import { Control, FieldPath, FieldValues } from 'react-hook-form';
import {
  FormControl,
  FormField,
  FormItem,
  FormLabel,
  FormMessage,
} from '@/components/ui/form';
import { Input } from '@/components/ui/input';

interface FormFieldProps<T extends FieldValues> {
  control: Control<T>;
  name: FieldPath<T>;
  label: string;
  placeholder?: string;
  type?: string;
  disabled?: boolean;
}

export function FormTextField<T extends FieldValues>({
  control,
  name,
  label,
  placeholder,
  type = 'text',
  disabled = false,
}: FormFieldProps<T>) {
  return (
    <FormField
      control={control}
      name={name}
      render={({ field }) => (
        <FormItem>
          <FormLabel>{label}</FormLabel>
          <FormControl>
            <Input
              {...field}
              type={type}
              placeholder={placeholder}
              disabled={disabled}
              data-testid={`input-${name}`}
            />
          </FormControl>
          <FormMessage />
        </FormItem>
      )}
    />
  );
}
```

##### `src/components/auth/login-form.tsx`
```typescript
'use client';

import { useState } from 'react';
import { useRouter } from 'next/navigation';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import * as z from 'zod';
import { Button } from '@/components/ui/button';
import { Form } from '@/components/ui/form';
import { FormTextField } from '@/components/forms/form-field';
import { useAuthStore } from '@/stores/auth-store';
import { authService } from '@/services/auth.service';
import { toast } from 'sonner';
import { Loader2 } from 'lucide-react';

const loginSchema = z.object({
  email: z.string().email('Email inválido'),
  password: z.string().min(6, 'Mínimo 6 caracteres'),
});

type LoginFormData = z.infer<typeof loginSchema>;

export function LoginForm() {
  const router = useRouter();
  const [isLoading, setIsLoading] = useState(false);
  const { setAuth } = useAuthStore();

  const form = useForm<LoginFormData>({
    resolver: zodResolver(loginSchema),
    defaultValues: {
      email: '',
      password: '',
    },
  });

  const onSubmit = async (data: LoginFormData) => {
    setIsLoading(true);
    try {
      const response = await authService.login(data);
      
      // Store auth data
      setAuth({
        user: response.user,
        token: response.accessToken,
      });
      
      // Store refresh token in httpOnly cookie (via API)
      document.cookie = `refreshToken=${response.refreshToken}; path=/; httpOnly; secure; sameSite=strict`;
      
      toast.success('Login exitoso');
      router.push('/dashboard');
    } catch (error: any) {
      toast.error(error.response?.data?.message || 'Error al iniciar sesión');
      console.error('Login error:', error);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <Form {...form}>
      <form onSubmit={form.handleSubmit(onSubmit)} className="space-y-4">
        <FormTextField
          control={form.control}
          name="email"
          label="Email"
          type="email"
          placeholder="usuario@ejemplo.com"
          disabled={isLoading}
        />
        
        <FormTextField
          control={form.control}
          name="password"
          label="Contraseña"
          type="password"
          placeholder="••••••••"
          disabled={isLoading}
        />

        <Button
          type="submit"
          className="w-full"
          disabled={isLoading}
        >
          {isLoading && <Loader2 className="mr-2 h-4 w-4 animate-spin" />}
          {isLoading ? 'Iniciando sesión...' : 'Iniciar Sesión'}
        </Button>
      </form>
    </Form>
  );
}
```

#### 🧪 Tests:
##### `__tests__/components/auth/login-form.test.tsx`
```typescript
import { render, screen, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { LoginForm } from '@/components/auth/login-form';
import { authService } from '@/services/auth.service';

jest.mock('@/services/auth.service');
jest.mock('next/navigation', () => ({
  useRouter: () => ({
    push: jest.fn(),
  }),
}));

describe('LoginForm', () => {
  it('should render form fields', () => {
    render(<LoginForm />);
    
    expect(screen.getByLabelText(/email/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/contraseña/i)).toBeInTheDocument();
    expect(screen.getByRole('button', { name: /iniciar sesión/i })).toBeInTheDocument();
  });

  it('should validate email format', async () => {
    render(<LoginForm />);
    const user = userEvent.setup();
    
    const emailInput = screen.getByTestId('input-email');
    const submitButton = screen.getByRole('button', { name: /iniciar sesión/i });
    
    await user.type(emailInput, 'invalid-email');
    await user.click(submitButton);
    
    await waitFor(() => {
      expect(screen.getByText(/email inválido/i)).toBeInTheDocument();
    });
  });

  it('should call authService on valid submission', async () => {
    const mockLogin = jest.fn().mockResolvedValue({
      accessToken: 'token',
      refreshToken: 'refresh',
      user: { id: '1', email: 'test@test.com' }
    });
    
    (authService.login as jest.Mock) = mockLogin;
    
    render(<LoginForm />);
    const user = userEvent.setup();
    
    await user.type(screen.getByTestId('input-email'), 'test@test.com');
    await user.type(screen.getByTestId('input-password'), 'password123');
    await user.click(screen.getByRole('button', { name: /iniciar sesión/i }));
    
    await waitFor(() => {
      expect(mockLogin).toHaveBeenCalledWith({
        email: 'test@test.com',
        password: 'password123'
      });
    });
  });
});
```

#### 📊 Commits del Día 2:
```bash
git commit -m "feat(forms): add reusable form field component"
git commit -m "feat(auth): implement login form with validation"
git commit -m "test(auth): add comprehensive login form tests"
git commit -m "feat(auth): add loading states and error handling"
```

---

### DÍA 3-4: CRUD de Usuarios con TDD

#### 🎯 Test-Driven Development (TDD) Approach

##### 1. Escribir test primero:
```typescript
// __tests__/services/users.service.test.ts
describe('UsersService', () => {
  it('should fetch paginated users', async () => {
    const users = await usersService.getAll(1, 10);
    expect(users.data).toHaveLength(10);
    expect(users.total).toBeGreaterThan(0);
  });
});
```

##### 2. Implementar servicio:
```typescript
// src/services/users.service.ts
import { apiClient } from '@/lib/api-client';
import type { User, PaginatedResponse } from '@/types';

class UsersService {
  private readonly BASE_PATH = '/users';

  async getAll(page = 1, limit = 10): Promise<PaginatedResponse<User>> {
    const response = await apiClient.get<User[]>(this.BASE_PATH, {
      params: {
        skip: (page - 1) * limit,
        limit,
      },
    });
    
    return {
      data: response.data,
      total: parseInt(response.headers['x-total-count'] || '0'),
      page,
      limit,
    };
  }

  async getById(id: string): Promise<User> {
    const response = await apiClient.get<User>(`${this.BASE_PATH}/${id}`);
    return response.data;
  }

  async create(data: Partial<User>): Promise<User> {
    const response = await apiClient.post<User>(this.BASE_PATH, data);
    return response.data;
  }

  async update(id: string, data: Partial<User>): Promise<User> {
    const response = await apiClient.put<User>(`${this.BASE_PATH}/${id}`, data);
    return response.data;
  }

  async delete(id: string): Promise<void> {
    await apiClient.delete(`${this.BASE_PATH}/${id}`);
  }
}

export const usersService = new UsersService();
```

##### 3. Implementar hook con React Query:
```typescript
// src/hooks/use-users.ts
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { usersService } from '@/services/users.service';
import { toast } from 'sonner';

export function useUsers(page = 1, limit = 10) {
  return useQuery({
    queryKey: ['users', page, limit],
    queryFn: () => usersService.getAll(page, limit),
    staleTime: 5 * 60 * 1000, // 5 minutes
  });
}

export function useUser(id: string) {
  return useQuery({
    queryKey: ['user', id],
    queryFn: () => usersService.getById(id),
    enabled: !!id,
  });
}

export function useCreateUser() {
  const queryClient = useQueryClient();
  
  return useMutation({
    mutationFn: usersService.create,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['users'] });
      toast.success('Usuario creado exitosamente');
    },
    onError: (error: any) => {
      toast.error(error.response?.data?.message || 'Error al crear usuario');
    },
  });
}

export function useUpdateUser() {
  const queryClient = useQueryClient();
  
  return useMutation({
    mutationFn: ({ id, data }: { id: string; data: Partial<User> }) =>
      usersService.update(id, data),
    onSuccess: (_, variables) => {
      queryClient.invalidateQueries({ queryKey: ['users'] });
      queryClient.invalidateQueries({ queryKey: ['user', variables.id] });
      toast.success('Usuario actualizado exitosamente');
    },
    onError: (error: any) => {
      toast.error(error.response?.data?.message || 'Error al actualizar usuario');
    },
  });
}

export function useDeleteUser() {
  const queryClient = useQueryClient();
  
  return useMutation({
    mutationFn: usersService.delete,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['users'] });
      toast.success('Usuario eliminado exitosamente');
    },
    onError: (error: any) => {
      toast.error(error.response?.data?.message || 'Error al eliminar usuario');
    },
  });
}
```

#### 📊 Commits del Día 3-4:
```bash
# Día 3
git commit -m "test(users): add TDD tests for users service"
git commit -m "feat(users): implement users service with CRUD operations"
git commit -m "feat(users): add React Query hooks for data fetching"
git commit -m "test(users): add integration tests for user hooks"

# Día 4
git commit -m "feat(users): add user list component with pagination"
git commit -m "feat(users): implement user creation form"
git commit -m "feat(users): add user edit dialog with validation"
git commit -m "test(users): add E2E tests for user management flow"
```

---

## 📈 MÉTRICAS DE CALIDAD

### Coverage Mínimo Requerido:
```json
{
  "jest": {
    "coverageThreshold": {
      "global": {
        "branches": 80,
        "functions": 80,
        "lines": 80,
        "statements": 80
      }
    }
  }
}
```

### Performance Budget:
```javascript
// next.config.js
module.exports = {
  experimental: {
    webVitalsAttribution: ['CLS', 'LCP', 'FCP', 'FID', 'TTFB'],
  },
  // Límites de bundle
  webpack: (config) => {
    config.performance = {
      maxAssetSize: 100000, // 100kb
      maxEntrypointSize: 300000, // 300kb
    };
    return config;
  },
};
```

---

## 🔄 CI/CD Pipeline

### `.github/workflows/frontend-ci.yml`
```yaml
name: Frontend CI

on:
  push:
    branches: [main, develop]
  pull_request:
    branches: [main]

jobs:
  test:
    runs-on: ubuntu-latest
    
    steps:
      - uses: actions/checkout@v3
      
      - name: Setup Node.js
        uses: actions/setup-node@v3
        with:
          node-version: '18'
          cache: 'npm'
      
      - name: Install dependencies
        run: npm ci
        working-directory: ./frontend
      
      - name: Run linter
        run: npm run lint
        working-directory: ./frontend
      
      - name: Run type check
        run: npm run type-check
        working-directory: ./frontend
      
      - name: Run tests
        run: npm run test:ci
        working-directory: ./frontend
      
      - name: Build
        run: npm run build
        working-directory: ./frontend
      
      - name: Upload coverage
        uses: codecov/codecov-action@v3
        with:
          directory: ./frontend/coverage
```

---

## 📚 DOCUMENTACIÓN CONTINUA

### Estructura de Documentación:
```
docs/
├── ARCHITECTURE.md          # Decisiones arquitectónicas
├── API.md                   # Documentación de API
├── COMPONENTS.md            # Catálogo de componentes
├── TESTING.md               # Estrategia de testing
├── DEPLOYMENT.md            # Guía de despliegue
└── CHANGELOG.md             # Registro de cambios
```

### Storybook para Componentes:
```bash
# Instalar Storybook
npx storybook@latest init

# Crear stories para cada componente
# src/components/auth/login-form.stories.tsx
```

---

## 🎯 DEFINICIÓN DE "HECHO" (DoD)

Para considerar una feature completa:

✅ **Código:**
- [ ] Implementación completa de la funcionalidad
- [ ] TypeScript sin errores
- [ ] Sin warnings de ESLint
- [ ] Código formateado con Prettier

✅ **Testing:**
- [ ] Tests unitarios con >80% coverage
- [ ] Tests de integración para flujos críticos
- [ ] Tests E2E para happy path

✅ **Documentación:**
- [ ] JSDoc en funciones públicas
- [ ] README actualizado si es necesario
- [ ] Storybook para componentes nuevos

✅ **Review:**
- [ ] Code review aprobado
- [ ] QA testing pasado
- [ ] Performance dentro del budget

✅ **Git:**
- [ ] Commits siguiendo conventional commits
- [ ] Branch actualizado con main
- [ ] PR con descripción completa

---

## 🚀 RESULTADO ESPERADO

Al seguir este plan con mejores prácticas:

1. **Código Mantenible:** Clean Code, SOLID principles
2. **Alta Calidad:** >80% test coverage
3. **Documentado:** Cada feature documentada
4. **Trazable:** Historial de commits claro
5. **Escalable:** Arquitectura modular
6. **Performante:** Optimizado y medido

**Tiempo Total:** 10 días con calidad profesional

---

*Plan creado siguiendo estándares de la industria*
*Fecha: 11 de Septiembre de 2025*