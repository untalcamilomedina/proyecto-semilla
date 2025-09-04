# 🧪 Tests - Proyecto Semilla

Este directorio contiene todos los tests del proyecto, organizados por tipo y componente.

## 🏗️ Estructura de Testing

```
tests/
├── README.md                   # Este archivo
├── conftest.py                 # Configuración global de pytest
├── pytest.ini                 # Configuración de pytest
├── requirements.txt            # Dependencias para testing
├── unit/                       # Tests unitarios
│   ├── __init__.py
│   ├── backend/               # Tests unitarios del backend
│   │   ├── __init__.py
│   │   ├── test_auth.py       # Tests de autenticación
│   │   ├── test_users.py      # Tests de usuarios
│   │   ├── test_tenants.py    # Tests de tenants
│   │   ├── test_permissions.py # Tests de permisos
│   │   ├── test_models.py     # Tests de modelos
│   │   └── test_services.py   # Tests de servicios
│   └── frontend/              # Tests unitarios del frontend
│       ├── components/        # Tests de componentes React
│       │   ├── AuthForm.test.tsx
│       │   ├── UserCard.test.tsx
│       │   └── Dashboard.test.tsx
│       ├── hooks/             # Tests de custom hooks
│       │   ├── useAuth.test.ts
│       │   └── useApi.test.ts
│       └── utils/             # Tests de utilidades
│           ├── validation.test.ts
│           └── helpers.test.ts
├── integration/               # Tests de integración
│   ├── __init__.py
│   ├── api/                   # Tests de API completos
│   │   ├── test_auth_flow.py  # Flujo completo de auth
│   │   ├── test_user_crud.py  # CRUD completo de usuarios
│   │   └── test_permissions.py # Sistema de permisos end-to-end
│   ├── database/              # Tests de base de datos
│   │   ├── test_migrations.py # Tests de migraciones
│   │   ├── test_rls.py        # Tests de Row-Level Security
│   │   └── test_performance.py # Tests de performance de BD
│   └── frontend/              # Tests de integración frontend
│       ├── pages/             # Tests de páginas completas
│       └── flows/             # Tests de flujos de usuario
├── e2e/                       # Tests end-to-end
│   ├── playwright.config.ts   # Configuración Playwright
│   ├── fixtures/              # Datos de prueba para E2E
│   ├── pages/                 # Page Objects
│   │   ├── LoginPage.ts
│   │   ├── DashboardPage.ts
│   │   └── UserManagementPage.ts
│   ├── tests/                 # Tests E2E
│   │   ├── auth.spec.ts       # Tests de autenticación E2E
│   │   ├── user-management.spec.ts # Gestión de usuarios E2E
│   │   ├── tenant-switching.spec.ts # Cambio de tenant E2E
│   │   └── permissions.spec.ts # Tests de permisos E2E
│   └── utils/                 # Utilidades para E2E
│       ├── helpers.ts
│       └── fixtures.ts
├── performance/               # Tests de performance
│   ├── locustfile.py          # Tests de carga con Locust
│   ├── api-benchmarks.py      # Benchmarks de API
│   └── database-benchmarks.py # Benchmarks de BD
├── security/                  # Tests de seguridad
│   ├── test_authentication.py # Tests de seguridad auth
│   ├── test_authorization.py  # Tests de autorización
│   ├── test_sql_injection.py  # Tests anti SQL injection
│   ├── test_xss_protection.py # Tests anti XSS
│   └── test_rls_security.py   # Tests de seguridad RLS
├── fixtures/                  # Datos de prueba compartidos
│   ├── __init__.py
│   ├── users.json            # Usuarios de prueba
│   ├── tenants.json          # Tenants de prueba
│   ├── roles.json            # Roles de prueba
│   └── database.sql          # Datos de BD para tests
└── utils/                     # Utilidades para testing
    ├── __init__.py
    ├── factories.py          # Factories para crear objetos de prueba
    ├── helpers.py            # Funciones auxiliares
    ├── assertions.py         # Aserciones custom
    └── mocks.py              # Mocks y stubs
```

## 🎯 Estrategia de Testing

### 🧪 Pirámide de Testing

```
           /\
          /  \
         / E2E \ (Pocos, Lentos, Costosos)
        /______\
       /        \
      /Integration\ (Algunos, Medianos)
     /____________\
    /              \
   /   Unit Tests   \ (Muchos, Rápidos, Baratos)
  /________________\
```

**Distribución objetivo**:
- **70%** Unit Tests
- **20%** Integration Tests  
- **10%** End-to-End Tests

### 📊 Métricas de Calidad

| Métrica | Target | Herramienta |
|---------|--------|-------------|
| **Cobertura de Código** | >80% | pytest-cov, c8 |
| **Mutation Testing** | >70% | mutmut |
| **Performance** | <200ms API | pytest-benchmark |
| **Security** | 0 vulnerabilities | bandit, safety |
| **Flakiness** | <1% tests flaky | pytest-rerunfailures |

## 🐍 Testing Backend (Python)

### ⚙️ Configuración pytest

```python
# conftest.py
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.main import app
from app.core.config import settings
from app.core.database import get_db

# Base de datos de prueba
SQLALCHEMY_DATABASE_URL = "postgresql://test:test@localhost/test_db"
engine = create_engine(SQLALCHEMY_DATABASE_URL)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

@pytest.fixture(scope="function")
def db_session():
    """Fixture para sesión de base de datos de prueba."""
    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.close()

@pytest.fixture(scope="function")
def client(db_session):
    """Fixture para cliente de prueba FastAPI."""
    def override_get_db():
        try:
            yield db_session
        finally:
            db_session.close()
    
    app.dependency_overrides[get_db] = override_get_db
    yield TestClient(app)
    app.dependency_overrides.clear()

@pytest.fixture
def authenticated_client(client, test_user):
    """Cliente autenticado para pruebas."""
    response = client.post("/auth/login", json={
        "email": test_user.email,
        "password": "testpass123"
    })
    token = response.json()["access_token"]
    client.headers.update({"Authorization": f"Bearer {token}"})
    return client
```

### 🧪 Ejemplos de Tests Unitarios

```python
# tests/unit/backend/test_auth.py
import pytest
from app.services.auth_service import AuthService
from app.schemas.auth import UserCreate

class TestAuthService:
    def test_create_user_success(self, db_session):
        """Test crear usuario exitosamente."""
        auth_service = AuthService(db_session)
        user_data = UserCreate(
            email="test@example.com",
            password="securepass123",
            first_name="Test",
            last_name="User"
        )
        
        user = auth_service.create_user(user_data, tenant_id="tenant-123")
        
        assert user.email == "test@example.com"
        assert user.first_name == "Test"
        assert user.last_name == "User"
        assert user.hashed_password != "securepass123"  # Debe estar hasheada

    def test_create_user_duplicate_email(self, db_session):
        """Test error al crear usuario con email duplicado."""
        auth_service = AuthService(db_session)
        user_data = UserCreate(email="duplicate@example.com", password="pass123")
        
        # Crear primer usuario
        auth_service.create_user(user_data, tenant_id="tenant-123")
        
        # Intentar crear segundo usuario con mismo email
        with pytest.raises(ValueError, match="Email already registered"):
            auth_service.create_user(user_data, tenant_id="tenant-123")
```

### 🔗 Ejemplos de Tests de Integración

```python
# tests/integration/api/test_auth_flow.py
import pytest

class TestAuthenticationFlow:
    def test_complete_auth_flow(self, client, db_session):
        """Test flujo completo de autenticación."""
        
        # 1. Registrar usuario
        register_data = {
            "email": "newuser@example.com",
            "password": "newpass123",
            "first_name": "New",
            "last_name": "User"
        }
        response = client.post("/auth/register", json=register_data)
        assert response.status_code == 201
        
        # 2. Login
        login_data = {"email": "newuser@example.com", "password": "newpass123"}
        response = client.post("/auth/login", json=login_data)
        assert response.status_code == 200
        
        token_data = response.json()
        assert "access_token" in token_data
        assert "refresh_token" in token_data
        
        # 3. Acceder a recurso protegido
        headers = {"Authorization": f"Bearer {token_data['access_token']}"}
        response = client.get("/users/me", headers=headers)
        assert response.status_code == 200
        
        user_data = response.json()
        assert user_data["email"] == "newuser@example.com"
        
        # 4. Refresh token
        refresh_data = {"refresh_token": token_data["refresh_token"]}
        response = client.post("/auth/refresh", json=refresh_data)
        assert response.status_code == 200
        
        # 5. Logout
        response = client.post("/auth/logout", headers=headers)
        assert response.status_code == 200
        
        # 6. Verificar que token ya no funciona
        response = client.get("/users/me", headers=headers)
        assert response.status_code == 401
```

## ⚛️ Testing Frontend (TypeScript/React)

### ⚙️ Configuración Jest

```typescript
// jest.config.js
const nextJest = require('next/jest')

const createJestConfig = nextJest({
  dir: './',
})

const customJestConfig = {
  setupFilesAfterEnv: ['<rootDir>/jest.setup.js'],
  moduleNameMapping: {
    '^@/components/(.*)$': '<rootDir>/components/$1',
    '^@/lib/(.*)$': '<rootDir>/lib/$1',
    '^@/hooks/(.*)$': '<rootDir>/hooks/$1',
  },
  testEnvironment: 'jest-environment-jsdom',
  collectCoverageFrom: [
    'components/**/*.{js,jsx,ts,tsx}',
    'lib/**/*.{js,jsx,ts,tsx}',
    'hooks/**/*.{js,jsx,ts,tsx}',
    '!**/*.d.ts',
    '!**/node_modules/**',
  ],
  coverageThreshold: {
    global: {
      branches: 80,
      functions: 80,
      lines: 80,
      statements: 80,
    },
  },
}

module.exports = createJestConfig(customJestConfig)
```

### 🧪 Ejemplo de Test de Componente

```typescript
// tests/unit/frontend/components/AuthForm.test.tsx
import { render, screen, fireEvent, waitFor } from '@testing-library/react'
import { AuthForm } from '@/components/auth/AuthForm'
import { useAuth } from '@/hooks/useAuth'

// Mock del hook useAuth
jest.mock('@/hooks/useAuth')

describe('AuthForm', () => {
  const mockLogin = jest.fn()
  
  beforeEach(() => {
    (useAuth as jest.Mock).mockReturnValue({
      login: mockLogin,
      isLoading: false,
      error: null,
    })
  })

  it('renders login form correctly', () => {
    render(<AuthForm type="login" />)
    
    expect(screen.getByLabelText(/email/i)).toBeInTheDocument()
    expect(screen.getByLabelText(/password/i)).toBeInTheDocument()
    expect(screen.getByRole('button', { name: /sign in/i })).toBeInTheDocument()
  })

  it('submits form with correct data', async () => {
    render(<AuthForm type="login" />)
    
    const emailInput = screen.getByLabelText(/email/i)
    const passwordInput = screen.getByLabelText(/password/i)
    const submitButton = screen.getByRole('button', { name: /sign in/i })
    
    fireEvent.change(emailInput, { target: { value: 'test@example.com' } })
    fireEvent.change(passwordInput, { target: { value: 'password123' } })
    fireEvent.click(submitButton)
    
    await waitFor(() => {
      expect(mockLogin).toHaveBeenCalledWith({
        email: 'test@example.com',
        password: 'password123',
      })
    })
  })

  it('displays error message when login fails', async () => {
    (useAuth as jest.Mock).mockReturnValue({
      login: mockLogin,
      isLoading: false,
      error: 'Invalid credentials',
    })

    render(<AuthForm type="login" />)
    
    expect(screen.getByText('Invalid credentials')).toBeInTheDocument()
  })
})
```

## 🎭 Testing End-to-End (Playwright)

### ⚙️ Configuración Playwright

```typescript
// playwright.config.ts
import { defineConfig, devices } from '@playwright/test'

export default defineConfig({
  testDir: './tests/e2e',
  fullyParallel: true,
  forbidOnly: !!process.env.CI,
  retries: process.env.CI ? 2 : 0,
  workers: process.env.CI ? 1 : undefined,
  reporter: 'html',
  
  use: {
    baseURL: 'http://localhost:3000',
    trace: 'on-first-retry',
    screenshot: 'only-on-failure',
  },

  projects: [
    {
      name: 'chromium',
      use: { ...devices['Desktop Chrome'] },
    },
    {
      name: 'firefox',
      use: { ...devices['Desktop Firefox'] },
    },
    {
      name: 'webkit',
      use: { ...devices['Desktop Safari'] },
    },
    {
      name: 'Mobile Chrome',
      use: { ...devices['Pixel 5'] },
    },
  ],

  webServer: {
    command: 'npm run dev',
    url: 'http://localhost:3000',
    reuseExistingServer: !process.env.CI,
  },
})
```

### 🎭 Ejemplo de Test E2E

```typescript
// tests/e2e/tests/user-management.spec.ts
import { test, expect } from '@playwright/test'
import { LoginPage } from '../pages/LoginPage'
import { DashboardPage } from '../pages/DashboardPage'
import { UserManagementPage } from '../pages/UserManagementPage'

test.describe('User Management', () => {
  test('admin can create, edit and delete users', async ({ page }) => {
    const loginPage = new LoginPage(page)
    const dashboardPage = new DashboardPage(page)
    const userManagementPage = new UserManagementPage(page)

    // Login como admin
    await loginPage.goto()
    await loginPage.login('admin@example.com', 'admin123')
    await expect(dashboardPage.welcomeMessage).toBeVisible()

    // Navegar a gestión de usuarios
    await dashboardPage.navigateToUsers()
    await expect(userManagementPage.usersTable).toBeVisible()

    // Crear nuevo usuario
    await userManagementPage.clickCreateUser()
    await userManagementPage.fillUserForm({
      firstName: 'Jane',
      lastName: 'Doe',
      email: 'jane.doe@example.com',
      role: 'Editor',
    })
    await userManagementPage.submitUserForm()

    // Verificar que el usuario aparece en la tabla
    await expect(userManagementPage.getUserRow('jane.doe@example.com')).toBeVisible()

    // Editar usuario
    await userManagementPage.editUser('jane.doe@example.com')
    await userManagementPage.fillUserForm({ firstName: 'Jane Updated' })
    await userManagementPage.submitUserForm()

    // Verificar cambios
    await expect(userManagementPage.getUserCell('jane.doe@example.com', 'name'))
      .toContainText('Jane Updated Doe')

    // Eliminar usuario
    await userManagementPage.deleteUser('jane.doe@example.com')
    await userManagementPage.confirmDelete()

    // Verificar que el usuario ya no existe
    await expect(userManagementPage.getUserRow('jane.doe@example.com')).not.toBeVisible()
  })
})
```

## 🔒 Testing de Seguridad

### 🛡️ Test de Row-Level Security

```python
# tests/security/test_rls_security.py
import pytest
from sqlalchemy import text

class TestRowLevelSecurity:
    def test_tenant_isolation(self, db_session, test_users):
        """Test que los usuarios no pueden acceder a datos de otros tenants."""
        tenant_1_user = test_users['tenant_1_user']
        tenant_2_user = test_users['tenant_2_user']
        
        # Configurar contexto para tenant 1
        db_session.execute(text(
            "SET app.current_tenant_id = :tenant_id"
        ), {"tenant_id": tenant_1_user.tenant_id})
        
        # Intentar acceder a datos del tenant 1
        result = db_session.execute(text("SELECT * FROM users")).fetchall()
        tenant_1_users = [row for row in result]
        
        # Verificar que solo se obtienen usuarios del tenant 1
        for user_row in tenant_1_users:
            assert str(user_row.tenant_id) == tenant_1_user.tenant_id
        
        # Cambiar contexto a tenant 2
        db_session.execute(text(
            "SET app.current_tenant_id = :tenant_id"
        ), {"tenant_id": tenant_2_user.tenant_id})
        
        # Verificar que ahora solo se ven usuarios del tenant 2
        result = db_session.execute(text("SELECT * FROM users")).fetchall()
        tenant_2_users = [row for row in result]
        
        for user_row in tenant_2_users:
            assert str(user_row.tenant_id) == tenant_2_user.tenant_id
        
        # Verificar que no hay overlap
        tenant_1_emails = {user.email for user in tenant_1_users}
        tenant_2_emails = {user.email for user in tenant_2_users}
        assert tenant_1_emails.isdisjoint(tenant_2_emails)
```

## 📊 Performance Testing

### ⚡ Tests de Carga con Locust

```python
# tests/performance/locustfile.py
from locust import HttpUser, task, between
import random

class ProjectSemillaUser(HttpUser):
    wait_time = between(1, 3)
    
    def on_start(self):
        """Ejecutado al inicio de cada usuario simulado."""
        # Login
        response = self.client.post("/auth/login", json={
            "email": f"user{random.randint(1, 100)}@example.com",
            "password": "testpass123"
        })
        if response.status_code == 200:
            token = response.json()["access_token"]
            self.client.headers.update({"Authorization": f"Bearer {token}"})

    @task(3)
    def view_dashboard(self):
        """Simular visita al dashboard - tarea más común."""
        self.client.get("/api/dashboard/stats")

    @task(2)
    def view_users(self):
        """Simular visualización de lista de usuarios."""
        self.client.get("/api/users/?page=1&limit=20")

    @task(1)
    def create_user(self):
        """Simular creación de usuario - menos frecuente."""
        user_data = {
            "email": f"newuser{random.randint(1000, 9999)}@example.com",
            "password": "newpass123",
            "first_name": f"User{random.randint(1, 100)}",
            "last_name": "Test"
        }
        self.client.post("/api/users/", json=user_data)

    @task(1)
    def update_profile(self):
        """Simular actualización de perfil."""
        profile_data = {
            "first_name": f"Updated{random.randint(1, 100)}",
            "preferences": {"theme": random.choice(["light", "dark"])}
        }
        self.client.put("/api/users/me", json=profile_data)
```

## 🚀 Comandos de Testing

### 🐍 Backend Testing
```bash
# Ejecutar todos los tests
pytest

# Tests con coverage
pytest --cov=app --cov-report=html

# Tests específicos
pytest tests/unit/backend/test_auth.py
pytest tests/integration/api/test_user_crud.py

# Tests de performance
pytest tests/performance/ --benchmark-only

# Tests de seguridad
pytest tests/security/

# Tests con output verbose
pytest -v tests/unit/

# Ejecutar tests en paralelo
pytest -n 4 tests/
```

### ⚛️ Frontend Testing
```bash
# Ejecutar todos los tests
npm test

# Tests en modo watch
npm run test:watch

# Tests con coverage
npm run test:coverage

# Tests específicos
npm test -- AuthForm.test.tsx

# Tests de componentes específicos
npm test -- --testPathPattern=components
```

### 🎭 E2E Testing
```bash
# Ejecutar tests E2E
npx playwright test

# Tests en modo headed (con browser visible)
npx playwright test --headed

# Tests específicos
npx playwright test auth.spec.ts

# Tests en navegador específico
npx playwright test --project=chromium

# Debug mode
npx playwright test --debug

# Generar reporte
npx playwright show-report
```

## 📊 Métricas y Reporting

### 📈 Coverage Reports
- **Backend**: Coverage.py con reporte HTML
- **Frontend**: Jest coverage con reporte HTML  
- **Integración**: Codecov para tracking histórico

### 📝 Test Reports
- **Unit/Integration**: pytest-html para reportes detallados
- **E2E**: Playwright HTML reporter con screenshots
- **Performance**: Locust web UI para métricas en tiempo real

### 🔍 Quality Gates
```yaml
# .github/workflows/test.yml
quality_gates:
  coverage:
    minimum: 80%
  performance:
    api_response_time: 200ms
    page_load_time: 2s
  security:
    vulnerabilities: 0
  flakiness:
    max_flaky_percentage: 1%
```

## 🚀 Estado de Desarrollo

### ✅ Fase 1 (v0.1.0-v0.3.0)
- [ ] Configuración básica de pytest y Jest
- [ ] Tests unitarios para auth, users, tenants
- [ ] Tests de integración para APIs principales
- [ ] Tests básicos de seguridad (RLS, auth)
- [ ] Setup de coverage reporting

### 🔮 Fases Futuras
- [ ] Tests E2E completos con Playwright
- [ ] Performance testing con Locust
- [ ] Security testing automatizado
- [ ] Visual regression testing
- [ ] Mutation testing
- [ ] Contract testing para APIs

---

*El testing será implementado progresivamente, asegurando calidad desde la Fase 1 y expandiendo la cobertura en fases posteriores.*