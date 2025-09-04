# 🏗️ Estándares de Desarrollo - Proyecto Semilla

[![Versión](https://img.shields.io/badge/versión-1.0.0-green.svg)](https://proyectosemilla.dev)
[![Inglés](https://img.shields.io/badge/Language-English-blue.svg)](#english-version)
[![Español](https://img.shields.io/badge/Idioma-Español-green.svg)](#versión-en-español)

Este documento define los estándares de desarrollo para **Proyecto Semilla**, garantizando consistencia, calidad y mantenibilidad del código.

---

## 🇪🇸 Versión en Español

### 📋 Tabla de Contenidos

1. [Principios Fundamentales](#-principios-fundamentales)
2. [Estándares de Código](#-estándares-de-código)
3. [Arquitectura y Patrones](#-arquitectura-y-patrones)
4. [Seguridad](#-seguridad)
5. [Testing](#-testing)
6. [Documentación](#-documentación)
7. [Control de Versiones](#-control-de-versiones)
8. [Integración con Agentes](#-integración-con-agentes)

### 🎯 Principios Fundamentales

#### 1. **Calidad por Diseño**
- Código limpio desde el primer commit
- Prevención sobre corrección
- Automatización de verificaciones de calidad

#### 2. **Seguridad por Defecto**
- Security-first approach en toda implementación
- Row-Level Security obligatorio para datos multi-tenant
- Validación exhaustiva de inputs

#### 3. **Transparencia Total**
- Código autodocumentado
- Documentación siempre actualizada
- Procesos públicos y trazables

#### 4. **Comunidad Primero**
- Estándares que faciliten contribuciones
- Onboarding sencillo para nuevos desarrolladores
- Feedback loop continuo

### 📝 Estándares de Código

#### Lenguajes y Convenciones

##### Python (Backend)
```python
# ✅ CORRECTO
class UserService:
    """Service for managing user operations."""
    
    def __init__(self, db: AsyncSession) -> None:
        self.db = db
    
    async def create_user(
        self, 
        user_data: UserCreate, 
        tenant_id: UUID
    ) -> UserResponse:
        """Create a new user with proper tenant isolation."""
        # Validar tenant context
        if not await self._validate_tenant_context(tenant_id):
            raise HTTPException(
                status_code=403,
                detail="Invalid tenant context"
            )
        
        # Implementación...
        pass
    
    async def _validate_tenant_context(self, tenant_id: UUID) -> bool:
        """Private method to validate tenant access."""
        # Validación RLS
        pass

# ❌ INCORRECTO - Español en código
class ServicioUsuario:
    def crear_usuario(self, datos_usuario):
        # Sin type hints, sin validaciones, sin documentación
        pass
```

**Herramientas Obligatorias**:
- **Linting**: `ruff check .` (configurado en pyproject.toml)
- **Formatting**: `ruff format .`
- **Type Checking**: `mypy app/` (strict mode)
- **Import Sorting**: `ruff check --select I`

**Configuración pyproject.toml**:
```toml
[tool.ruff]
line-length = 88
target-version = "py311"

[tool.ruff.lint]
select = [
    "E",  # pycodestyle errors
    "W",  # pycodestyle warnings
    "F",  # pyflakes
    "I",  # isort
    "B",  # flake8-bugbear
    "C4", # flake8-comprehensions
    "UP", # pyupgrade
    "S",  # bandit security
]

[tool.mypy]
strict = true
python_version = "3.11"
```

##### TypeScript (Frontend)
```typescript
// ✅ CORRECTO
interface UserProfile {
  id: string;
  email: string;
  firstName: string;
  lastName: string;
  tenantId: string;
  createdAt: string;
  updatedAt: string;
}

interface CreateUserRequest {
  email: string;
  firstName: string;
  lastName: string;
  password: string;
}

class UserApiService {
  private readonly apiClient: ApiClient;

  constructor(apiClient: ApiClient) {
    this.apiClient = apiClient;
  }

  async createUser(userData: CreateUserRequest): Promise<UserProfile> {
    // Validación client-side
    if (!this.validateEmail(userData.email)) {
      throw new ValidationError('Invalid email format');
    }

    const response = await this.apiClient.post<UserProfile>(
      '/api/v1/users',
      userData
    );

    return response.data;
  }

  private validateEmail(email: string): boolean {
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    return emailRegex.test(email);
  }
}

// ❌ INCORRECTO - Español + sin tipos
class ServicioUsuarios {
  async crearUsuario(datos: any): Promise<any> {
    // Sin validaciones, sin tipos, sin error handling
    return fetch('/api/usuarios', { method: 'POST', body: datos });
  }
}
```

**Herramientas Obligatorias**:
- **Linting**: `eslint` con TypeScript rules
- **Formatting**: `prettier`
- **Type Checking**: `tsc --noEmit`
- **Testing**: `jest` + `@testing-library/react`

#### Naming Conventions

##### Variables y Funciones
```python
# ✅ CORRECTO
user_count: int = 10
tenant_isolation_enabled: bool = True

async def get_user_by_email(email: str) -> Optional[User]:
    pass

async def validate_tenant_permissions(
    tenant_id: UUID, 
    user_id: UUID
) -> bool:
    pass

# ❌ INCORRECTO
userCount = 10  # camelCase en Python
usuarioActivo = True  # Español

def obtenerUsuario(correo):  # Español + sin tipos
    pass
```

##### Clases y Modelos
```python
# ✅ CORRECTO
class UserService:
    pass

class TenantConfiguration:
    pass

class AuthenticationError(Exception):
    pass

# ❌ INCORRECTO
class servicioUsuario:  # lowercase
class ConfiguracionTenant:  # Español
```

##### Constantes
```python
# ✅ CORRECTO
DEFAULT_PAGE_SIZE: int = 20
MAX_RETRY_ATTEMPTS: int = 3
JWT_TOKEN_EXPIRY_HOURS: int = 24

# ❌ INCORRECTO
PageSize = 20  # No es constante real
TAMAÑO_PAGINA = 20  # Español
```

### 🏛️ Arquitectura y Patrones

#### Estructura de Directorios (Backend)
```
backend/
├── app/
│   ├── api/
│   │   └── v1/
│   │       ├── endpoints/
│   │       │   ├── __init__.py
│   │       │   ├── auth.py
│   │       │   ├── users.py
│   │       │   ├── tenants.py
│   │       │   └── roles.py
│   │       └── router.py
│   ├── core/
│   │   ├── __init__.py
│   │   ├── config.py
│   │   ├── database.py
│   │   ├── security.py
│   │   └── middleware.py
│   ├── models/
│   │   ├── __init__.py
│   │   ├── base.py
│   │   ├── user.py
│   │   ├── tenant.py
│   │   └── role.py
│   ├── schemas/
│   │   ├── __init__.py
│   │   ├── auth.py
│   │   ├── user.py
│   │   └── tenant.py
│   ├── services/
│   │   ├── __init__.py
│   │   ├── user_service.py
│   │   ├── tenant_service.py
│   │   └── auth_service.py
│   └── utils/
│       ├── __init__.py
│       ├── validators.py
│       └── helpers.py
├── tests/
├── alembic/
└── requirements.txt
```

#### Patrones Obligatorios

##### 1. Repository Pattern
```python
# ✅ CORRECTO - Repository con async/await
from abc import ABC, abstractmethod
from typing import Optional, List
from uuid import UUID

class UserRepository(ABC):
    """Abstract repository for user operations."""
    
    @abstractmethod
    async def create(self, user: User) -> User:
        pass
    
    @abstractmethod
    async def get_by_id(self, user_id: UUID) -> Optional[User]:
        pass
    
    @abstractmethod
    async def get_by_tenant(
        self, 
        tenant_id: UUID, 
        skip: int = 0, 
        limit: int = 100
    ) -> List[User]:
        pass

class SqlAlchemyUserRepository(UserRepository):
    """SQLAlchemy implementation of user repository."""
    
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def create(self, user: User) -> User:
        self.db.add(user)
        await self.db.commit()
        await self.db.refresh(user)
        return user
    
    async def get_by_id(self, user_id: UUID) -> Optional[User]:
        return await self.db.get(User, user_id)
```

##### 2. Service Layer Pattern
```python
# ✅ CORRECTO - Service con dependency injection
class UserService:
    """Business logic for user operations."""
    
    def __init__(
        self,
        user_repo: UserRepository,
        auth_service: AuthService,
        tenant_service: TenantService
    ):
        self.user_repo = user_repo
        self.auth_service = auth_service
        self.tenant_service = tenant_service
    
    async def create_user(
        self,
        user_data: UserCreate,
        current_user: User
    ) -> UserResponse:
        """Create user with full validation and authorization."""
        
        # 1. Validar permisos
        if not await self.tenant_service.can_create_users(
            current_user.tenant_id
        ):
            raise InsufficientPermissionsError()
        
        # 2. Validar datos de entrada
        if await self.user_repo.get_by_email(user_data.email):
            raise UserAlreadyExistsError()
        
        # 3. Crear usuario
        hashed_password = self.auth_service.hash_password(
            user_data.password
        )
        
        user = User(
            email=user_data.email,
            hashed_password=hashed_password,
            tenant_id=current_user.tenant_id,
            # ... otros campos
        )
        
        created_user = await self.user_repo.create(user)
        
        # 4. Log de auditoría
        await self.audit_service.log_user_creation(
            created_by=current_user.id,
            user_id=created_user.id
        )
        
        return UserResponse.from_orm(created_user)
```

##### 3. Dependency Injection Pattern
```python
# dependencies.py - ✅ CORRECTO
async def get_user_repository(
    db: AsyncSession = Depends(get_db)
) -> UserRepository:
    return SqlAlchemyUserRepository(db)

async def get_user_service(
    user_repo: UserRepository = Depends(get_user_repository),
    auth_service: AuthService = Depends(get_auth_service),
    tenant_service: TenantService = Depends(get_tenant_service)
) -> UserService:
    return UserService(user_repo, auth_service, tenant_service)

# En endpoints
@router.post("/users/", response_model=UserResponse)
async def create_user(
    user_data: UserCreate,
    user_service: UserService = Depends(get_user_service),
    current_user: User = Depends(get_current_user)
) -> UserResponse:
    return await user_service.create_user(user_data, current_user)
```

### 🔒 Seguridad

#### Row-Level Security (RLS) Obligatorio

##### Configuración Base de Datos
```sql
-- ✅ CORRECTO - Política RLS para usuarios
CREATE POLICY tenant_isolation ON users
    FOR ALL
    TO application_role
    USING (tenant_id = current_setting('app.current_tenant_id')::UUID);

-- ✅ CORRECTO - Función helper para contexto
CREATE OR REPLACE FUNCTION set_tenant_context(tenant_uuid UUID)
RETURNS void AS $$
BEGIN
    PERFORM set_config('app.current_tenant_id', tenant_uuid::text, true);
END;
$$ LANGUAGE plpgsql;
```

##### Implementación en Código
```python
# ✅ CORRECTO - Dependency que configura contexto RLS
async def get_tenant_context(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
) -> TenantContext:
    """Set tenant context for RLS."""
    
    # Configurar contexto de tenant en la sesión
    await db.execute(
        text("SELECT set_tenant_context(:tenant_id)"),
        {"tenant_id": current_user.tenant_id}
    )
    
    return TenantContext(
        tenant_id=current_user.tenant_id,
        user_id=current_user.id
    )

# ✅ CORRECTO - Uso en endpoints
@router.get("/users/", response_model=List[UserResponse])
async def get_users(
    db: AsyncSession = Depends(get_db),
    tenant_context: TenantContext = Depends(get_tenant_context),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000)
) -> List[UserResponse]:
    """Get users with automatic RLS filtering."""
    
    # La consulta automáticamente filtra por tenant gracias a RLS
    result = await db.execute(
        select(User)
        .offset(skip)
        .limit(limit)
        .order_by(User.created_at.desc())
    )
    
    users = result.scalars().all()
    return [UserResponse.from_orm(user) for user in users]
```

#### Validación de Input Obligatoria

```python
# ✅ CORRECTO - Validación exhaustiva con Pydantic
from pydantic import BaseModel, validator, EmailStr, Field
from typing import Optional
import re

class UserCreate(BaseModel):
    """Schema for user creation with comprehensive validation."""
    
    email: EmailStr = Field(
        ...,
        description="User email address",
        max_length=254
    )
    
    password: str = Field(
        ...,
        min_length=8,
        max_length=128,
        description="Password with minimum security requirements"
    )
    
    first_name: str = Field(
        ...,
        min_length=1,
        max_length=50,
        description="User first name"
    )
    
    last_name: str = Field(
        ...,
        min_length=1,
        max_length=50,
        description="User last name"
    )
    
    @validator('password')
    def validate_password_strength(cls, v):
        """Validate password meets security requirements."""
        if not re.search(r'[A-Z]', v):
            raise ValueError('Password must contain at least one uppercase letter')
        if not re.search(r'[a-z]', v):
            raise ValueError('Password must contain at least one lowercase letter')
        if not re.search(r'[0-9]', v):
            raise ValueError('Password must contain at least one digit')
        if not re.search(r'[!@#$%^&*(),.?":{}|<>]', v):
            raise ValueError('Password must contain at least one special character')
        return v
    
    @validator('first_name', 'last_name')
    def validate_name_format(cls, v):
        """Validate names contain only allowed characters."""
        if not re.match(r'^[a-zA-ZáéíóúÁÉÍÓÚñÑ\s-]+$', v):
            raise ValueError('Name contains invalid characters')
        return v.strip()

# ❌ INCORRECTO - Sin validación
class UserCreateBad(BaseModel):
    email: str
    password: str
    name: str  # Sin validaciones, vulnerable
```

### 🧪 Testing

#### Cobertura Mínima Obligatoria
- **Unit Tests**: 85%
- **Integration Tests**: 70%
- **Critical Paths**: 95%
- **Security Tests**: 100%

#### Estructura de Tests
```python
# ✅ CORRECTO - Test completo con fixtures
import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

class TestUserEndpoints:
    """Comprehensive tests for user endpoints."""
    
    @pytest.fixture
    async def user_data(self):
        return {
            "email": "test@proyectosemilla.dev",
            "password": "SecurePass123!",
            "first_name": "Test",
            "last_name": "User"
        }
    
    @pytest.fixture
    async def authenticated_client(
        self, 
        async_client: AsyncClient,
        test_user: User
    ) -> AsyncClient:
        """Client with authentication headers."""
        token = create_access_token(
            subject=test_user.id,
            tenant_id=test_user.tenant_id
        )
        async_client.headers.update({
            "Authorization": f"Bearer {token}"
        })
        return async_client
    
    async def test_create_user_success(
        self,
        authenticated_client: AsyncClient,
        user_data: dict,
        db_session: AsyncSession
    ):
        """Test successful user creation."""
        
        # Act
        response = await authenticated_client.post(
            "/api/v1/users/",
            json=user_data
        )
        
        # Assert
        assert response.status_code == 201
        
        user_response = response.json()
        assert user_response["email"] == user_data["email"]
        assert user_response["first_name"] == user_data["first_name"]
        assert "password" not in user_response  # Security check
        
        # Verify in database
        user_in_db = await db_session.get(User, user_response["id"])
        assert user_in_db is not None
        assert user_in_db.email == user_data["email"]
    
    async def test_create_user_duplicate_email(
        self,
        authenticated_client: AsyncClient,
        user_data: dict,
        existing_user: User
    ):
        """Test duplicate email validation."""
        
        # Use existing user's email
        user_data["email"] = existing_user.email
        
        # Act
        response = await authenticated_client.post(
            "/api/v1/users/",
            json=user_data
        )
        
        # Assert
        assert response.status_code == 400
        assert "already exists" in response.json()["detail"]
    
    async def test_create_user_tenant_isolation(
        self,
        authenticated_client: AsyncClient,
        user_data: dict,
        different_tenant_client: AsyncClient
    ):
        """Test RLS tenant isolation."""
        
        # Create user with first tenant
        response1 = await authenticated_client.post(
            "/api/v1/users/",
            json=user_data
        )
        assert response1.status_code == 201
        user1_id = response1.json()["id"]
        
        # Try to access with different tenant
        response2 = await different_tenant_client.get(
            f"/api/v1/users/{user1_id}"
        )
        
        # Should not be able to access
        assert response2.status_code == 404

    @pytest.mark.security
    async def test_sql_injection_protection(
        self,
        authenticated_client: AsyncClient
    ):
        """Test SQL injection attack prevention."""
        
        malicious_email = "test@example.com'; DROP TABLE users; --"
        
        response = await authenticated_client.post(
            "/api/v1/users/",
            json={
                "email": malicious_email,
                "password": "SecurePass123!",
                "first_name": "Test",
                "last_name": "User"
            }
        )
        
        # Should fail validation, not execute SQL
        assert response.status_code == 422

# ❌ INCORRECTO - Test básico sin validaciones
async def test_create_user():
    response = await client.post("/users", json={"email": "test"})
    assert response.status_code == 200  # Sin validar contenido
```

### 📚 Documentación

#### Docstrings Obligatorios
```python
# ✅ CORRECTO - Google Style Docstrings
class UserService:
    """Service for managing user operations with multi-tenant support.
    
    This service provides comprehensive user management functionality
    including creation, updates, and tenant-aware queries with proper
    Row-Level Security (RLS) integration.
    
    Attributes:
        user_repo: Repository for user data operations.
        auth_service: Service for authentication operations.
        logger: Structured logger instance.
    """
    
    def __init__(
        self,
        user_repo: UserRepository,
        auth_service: AuthService
    ) -> None:
        """Initialize UserService with required dependencies.
        
        Args:
            user_repo: Repository instance for user operations.
            auth_service: Service instance for authentication.
        """
        self.user_repo = user_repo
        self.auth_service = auth_service
        self.logger = get_logger(__name__)
    
    async def create_user(
        self,
        user_data: UserCreate,
        current_user: User
    ) -> UserResponse:
        """Create a new user with proper validation and authorization.
        
        This method performs comprehensive validation including:
        - Email uniqueness verification
        - Password strength validation  
        - Tenant permission checks
        - RLS context configuration
        
        Args:
            user_data: Validated user creation data.
            current_user: Currently authenticated user performing the operation.
            
        Returns:
            UserResponse: Created user data with sensitive fields excluded.
            
        Raises:
            UserAlreadyExistsError: If email is already registered.
            InsufficientPermissionsError: If user cannot create users.
            ValidationError: If user data fails validation.
            
        Example:
            >>> user_service = UserService(user_repo, auth_service)
            >>> user_data = UserCreate(
            ...     email="new@proyectosemilla.dev",
            ...     password="SecurePass123!",
            ...     first_name="New",
            ...     last_name="User"
            ... )
            >>> result = await user_service.create_user(user_data, admin_user)
            >>> print(result.email)
            "new@proyectosemilla.dev"
        """
        # Implementation...
        pass
```

#### OpenAPI Documentation
```python
# ✅ CORRECTO - Comprehensive OpenAPI docs
@router.post(
    "/users/",
    response_model=UserResponse,
    status_code=201,
    summary="Create a new user",
    description="""
    Create a new user in the current tenant context.
    
    This endpoint performs the following operations:
    1. Validates user permissions to create users
    2. Checks for email uniqueness within tenant
    3. Validates password strength requirements
    4. Creates user with proper tenant association
    5. Returns sanitized user data (no password)
    
    **Required Permissions**: `users:create`
    **RLS Context**: Automatically applied based on authenticated user
    """,
    responses={
        201: {
            "description": "User created successfully",
            "content": {
                "application/json": {
                    "example": {
                        "id": "123e4567-e89b-12d3-a456-426614174000",
                        "email": "user@proyectosemilla.dev",
                        "first_name": "John",
                        "last_name": "Doe",
                        "is_active": True,
                        "created_at": "2024-01-01T12:00:00Z"
                    }
                }
            }
        },
        400: {"description": "Invalid input data or email already exists"},
        403: {"description": "Insufficient permissions"},
        422: {"description": "Validation error"}
    },
    tags=["users"]
)
async def create_user(
    user_data: UserCreate = Body(
        ...,
        example={
            "email": "newuser@proyectosemilla.dev", 
            "password": "SecurePass123!",
            "first_name": "New",
            "last_name": "User"
        }
    ),
    current_user: User = Depends(get_current_user),
    user_service: UserService = Depends(get_user_service)
) -> UserResponse:
    """Create user endpoint with comprehensive documentation."""
    return await user_service.create_user(user_data, current_user)
```

### 🔄 Control de Versiones

#### Conventional Commits Obligatorios
```bash
# ✅ CORRECTO
feat(auth): add JWT refresh token functionality
fix(users): resolve RLS policy for cross-tenant queries  
docs(api): update OpenAPI specs for user endpoints
test(security): add SQL injection prevention tests
chore(deps): update SQLAlchemy to 2.0.25
refactor(services): extract common validation logic

# ❌ INCORRECTO
Update user stuff
Fixed bug
Added feature
WIP
```

#### Branch Naming
```bash
# ✅ CORRECTO
feat/jwt-refresh-tokens
fix/rls-cross-tenant-query
docs/api-documentation-update
test/security-sql-injection
hotfix/critical-auth-vulnerability

# ❌ INCORRECTO  
dev
john-changes
bugfix
update
```

### 🤖 Integración con Agentes

#### Claude Code Auditor Integration
```yaml
# En .github/workflows/claude-agents.yml
- name: Run Code Standards Validation
  run: |
    # Verificar adherencia a estándares
    python scripts/validate_standards.py \
      --check-docstrings \
      --check-type-hints \
      --check-security-patterns \
      --check-test-coverage \
      --standards-file=DEVELOPMENT_STANDARDS.md
```

#### Pre-commit Hooks
```yaml
# .pre-commit-config.yaml
repos:
  - repo: https://github.com/astral-sh/ruff-pre-commit
    rev: v0.1.6
    hooks:
      - id: ruff
        args: [--fix, --exit-non-zero-on-fix]
      - id: ruff-format

  - repo: https://github.com/pre-commit/mirrors-mypy
    rev: v1.7.1
    hooks:
      - id: mypy
        args: [--strict]
        additional_dependencies: [types-all]

  - repo: local
    hooks:
      - id: validate-development-standards
        name: Validate Development Standards
        entry: python scripts/validate_standards.py
        language: python
        stages: [commit]
        pass_filenames: false
```

---

## 🇺🇸 English Version

### 📋 Table of Contents

1. [Core Principles](#-core-principles-en)
2. [Code Standards](#-code-standards-en)
3. [Architecture & Patterns](#-architecture--patterns-en)
4. [Security](#-security-en)
5. [Testing](#-testing-en)
6. [Documentation](#-documentation-en)
7. [Version Control](#-version-control-en)

### 🎯 Core Principles {#core-principles-en}

#### 1. **Quality by Design**
- Clean code from first commit
- Prevention over correction
- Automated quality checks

#### 2. **Security by Default**  
- Security-first approach in all implementations
- Mandatory Row-Level Security for multi-tenant data
- Comprehensive input validation

#### 3. **Total Transparency**
- Self-documented code
- Always up-to-date documentation
- Public and traceable processes

#### 4. **Community First**
- Standards that facilitate contributions
- Simple onboarding for new developers
- Continuous feedback loop

### 📝 Code Standards {#code-standards-en}

*(English content follows same structure as Spanish version with English explanations)*

### 🔒 Security {#security-en}

#### Mandatory RLS Implementation
All multi-tenant data must implement Row-Level Security with proper context management.

#### Input Validation Requirements
All user inputs must be validated using Pydantic schemas with comprehensive validation rules.

### 🧪 Testing {#testing-en}

#### Minimum Coverage Requirements
- **Unit Tests**: 85%
- **Integration Tests**: 70% 
- **Critical Paths**: 95%
- **Security Tests**: 100%

---

## 📊 Métricas de Calidad

### KPIs de Desarrollo
- **Code Coverage**: > 85%
- **Type Coverage**: > 95%
- **Security Score**: A+ (Bandit + Safety)
- **Performance**: < 100ms API response time
- **Documentation**: 100% public API documented

### Automatización
- ✅ Pre-commit hooks configurados
- ✅ CI/CD pipeline con validaciones
- ✅ Claude Code Auditor integrado
- ✅ Métricas automáticas en PRs

---

## 🎯 Cumplimiento y Enforcement

### Validación Automática
```python
# scripts/validate_standards.py
def validate_development_standards():
    """Validate code against development standards."""
    
    checks = [
        check_docstring_coverage(),
        check_type_hint_coverage(),
        check_security_patterns(),
        check_test_coverage(),
        check_naming_conventions(),
        check_architectural_patterns()
    ]
    
    failures = [check for check in checks if not check.passed]
    
    if failures:
        print("❌ Development standards validation failed:")
        for failure in failures:
            print(f"  - {failure.message}")
        sys.exit(1)
    
    print("✅ All development standards validation passed!")
```

### Integración con PR Reviews
Cada PR debe pasar todas las validaciones antes del merge:

1. ✅ Linting y formatting
2. ✅ Type checking
3. ✅ Security analysis  
4. ✅ Test coverage
5. ✅ Documentation updates
6. ✅ Standards compliance

---

*Este documento es validado automáticamente por Claude Code Auditor Agent y actualizado con cada release.*

**Versión**: 1.0.0 | **Última actualización**: 2024-09-04 | **Próxima revisión**: v0.2.0

---

**📧 Contacto**: dev-standards@proyectosemilla.dev  
**📚 Documentación**: [docs.proyectosemilla.dev/standards](https://docs.proyectosemilla.dev/standards)  
**🔧 Issues**: [GitHub Issues](https://github.com/proyecto-semilla/proyecto-semilla/issues)