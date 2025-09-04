# 🐍 Backend - Proyecto Semilla

Este directorio contiene el código del backend desarrollado en **FastAPI**.

## 🏗️ Estructura (Planeada)

```
backend/
├── app/
│   ├── __init__.py
│   ├── main.py                 # Punto de entrada de la aplicación
│   ├── core/
│   │   ├── __init__.py
│   │   ├── config.py           # Configuración de la aplicación
│   │   ├── security.py         # JWT, hashing, etc.
│   │   └── database.py         # Conexión a PostgreSQL
│   ├── models/
│   │   ├── __init__.py
│   │   ├── tenant.py           # Modelo de Tenant
│   │   ├── user.py             # Modelo de Usuario
│   │   ├── role.py             # Modelo de Rol
│   │   └── permission.py       # Modelo de Permiso
│   ├── schemas/
│   │   ├── __init__.py
│   │   ├── tenant.py           # Schemas Pydantic para Tenant
│   │   ├── user.py             # Schemas Pydantic para Usuario
│   │   └── auth.py             # Schemas de autenticación
│   ├── api/
│   │   ├── __init__.py
│   │   ├── deps.py             # Dependencias comunes
│   │   ├── v1/
│   │   │   ├── __init__.py
│   │   │   ├── router.py       # Router principal v1
│   │   │   ├── auth.py         # Endpoints de autenticación
│   │   │   ├── users.py        # Endpoints de usuarios
│   │   │   ├── tenants.py      # Endpoints de tenants
│   │   │   └── roles.py        # Endpoints de roles
│   ├── services/
│   │   ├── __init__.py
│   │   ├── auth_service.py     # Lógica de autenticación
│   │   ├── user_service.py     # Lógica de usuarios
│   │   └── tenant_service.py   # Lógica de tenants
│   ├── utils/
│   │   ├── __init__.py
│   │   ├── permissions.py      # Decoradores de permisos
│   │   └── helpers.py          # Funciones auxiliares
│   └── tests/
│       ├── __init__.py
│       ├── test_auth.py
│       ├── test_users.py
│       └── test_tenants.py
├── alembic/                    # Migraciones de base de datos
│   ├── env.py
│   ├── script.py.mako
│   └── versions/
├── requirements.txt            # Dependencias de producción
├── requirements-dev.txt        # Dependencias de desarrollo
├── alembic.ini                 # Configuración de Alembic
├── pytest.ini                 # Configuración de pytest
├── pyproject.toml             # Configuración del proyecto
└── Dockerfile                 # Imagen Docker para producción
```

## 🚀 Stack Tecnológico

- **Framework**: FastAPI 0.104+
- **Base de Datos**: PostgreSQL 15+ con SQLAlchemy 2.0
- **Migraciones**: Alembic
- **Autenticación**: JWT con python-jose
- **Testing**: Pytest + httpx
- **Linting**: Ruff
- **Type Checking**: mypy

## 📋 Características Planificadas

### ✅ Fase 1 (v0.1.0 - v0.3.0)
- [ ] Configuración básica de FastAPI
- [ ] Conexión a PostgreSQL con SQLAlchemy
- [ ] Modelos de Tenant, User, Role, Permission
- [ ] Autenticación JWT
- [ ] Row-Level Security (RLS)
- [ ] CRUD de Tenants y Usuarios
- [ ] Sistema de permisos granulares
- [ ] Tests unitarios y de integración

### 🔮 Fases Futuras
- [ ] Sistema de atributos personalizados
- [ ] Internacionalización de mensajes
- [ ] Sistema de módulos/plugins
- [ ] API de analytics
- [ ] Integración con servicios externos

## 🔧 Desarrollo Local

```bash
# Una vez implementado, estos serán los comandos:

# Instalar dependencias
pip install -r requirements-dev.txt

# Configurar variables de entorno
cp .env.example .env

# Ejecutar migraciones
alembic upgrade head

# Ejecutar en modo desarrollo
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Ejecutar tests
pytest

# Linting
ruff check .
ruff format .
mypy .
```

## 🏛️ Arquitectura

### Principios
- **Clean Architecture**: Separación clara entre capas
- **Dependency Injection**: Usando FastAPI Depends
- **Repository Pattern**: Para acceso a datos
- **Service Layer**: Lógica de negocio separada
- **Security First**: RLS, validación, sanitización

### Multi-tenancy
- **Row-Level Security (RLS)** en PostgreSQL
- **Tenant Context** en cada request
- **Aislamiento completo** de datos entre tenants
- **Performance optimizado** con índices apropiados

---

*Este directorio será poblado durante la Fase 1 del desarrollo.*