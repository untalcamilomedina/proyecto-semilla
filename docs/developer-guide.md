# 🚀 **Proyecto Semilla - Guía para Desarrolladores**

**Versión**: 0.2.0
**Última actualización**: Septiembre 2025
**Proyecto**: Primera plataforma SaaS Vibecoding-native

---

## 📋 **Tabla de Contenidos**

- [🏗️ Arquitectura General](#-arquitectura-general)
  - [Flujo de Autenticación](#-flujo-de-autenticación)
- [🛠️ Configuración del Entorno](#-configuración-del-entorno)
- [🔧 Desarrollo con Vibecoding](#-desarrollo-con-vibecoding)
- [🧪 Testing y Calidad](#-testing-y-calidad)
- [📚 Documentación Automática](#-documentación-automática)
- [🚀 Deployment y CI/CD](#-deployment-y-cicd)
- [🤝 Contribuir al Proyecto](#-contribuir-al-proyecto)
- [🔧 Troubleshooting](#-troubleshooting)

---

## 🏗️ **Arquitectura General**

### **Componentes Principales**

```
Proyecto Semilla v0.2.0
├── 🔧 Backend (FastAPI + PostgreSQL + Redis)
│   ├── API REST completa (/api/v1/)
│   ├── Multi-tenancy con RLS
│   ├── Autenticación segura con Cookies HttpOnly
│   └── Vibecoding CORE integrado
│
├── 🤖 Vibecoding CORE
│   ├── SDK Python (1,230+ líneas)
│   ├── MCP Server (940+ líneas)
│   ├── Auto-Documentation (930+ líneas)
│   └── Integration Testing (700+ líneas)
│
├── 🎨 Frontend (React + TypeScript)
│   ├── CMS Module operativo
│   ├── Theme system
│   └── Responsive design
│
└── 🧪 Testing Suite (80%+ coverage)
    ├── Unit tests
    ├── Integration tests
    ├── Performance tests
    └── E2E validation
```

### **Principios Arquitecturales**

1. **Type Safety First**: 100% validación automática
2. **Vibecoding-Native**: LLMs como ciudadanos de primera clase
3. **Enterprise-Grade**: Calidad production-ready
4. **Modular Architecture**: Componentes desacoplados
5. **Auto-Documentation**: Documentación viva

### **Flujo de Autenticación**

El sistema de autenticación se basa en cookies `HttpOnly` para mayor seguridad, evitando el almacenamiento de tokens en `localStorage`.

1.  **Inicialización**: Al cargar la aplicación, el componente `AuthInitializer` se activa.
2.  **Verificación de Sesión**: Llama a la función `initialize` del `auth-store`, que comprueba la existencia de una cookie de sesión (`access_token`).
3.  **Validación de Sesión**: Si la cookie existe, se realiza una petición al endpoint `/api/v1/auth/me`. El navegador adjunta la cookie `HttpOnly` de forma automática.
    -   **Éxito**: El estado global de Zustand se hidrata con la información del usuario, estableciendo la sesión como activa.
    -   **Fallo**: Si la petición falla (ej. token expirado), se limpia cualquier estado de sesión residual.
4.  **Inicio de Sesión Manual**:
    -   El usuario envía sus credenciales a través de un formulario que realiza una petición `POST` directa al endpoint `/api/v1/auth/login` usando `fetch`.
    -   El backend valida las credenciales y, si son correctas, establece una cookie `HttpOnly` en la respuesta.
    -   El frontend actualiza el estado de Zustand con los datos del usuario y redirige al dashboard.
5.  **Peticiones Autenticadas**: Para las peticiones subsiguientes a endpoints protegidos, el navegador adjunta automáticamente la cookie de sesión. El `api-client` está configurado con `withCredentials: true` para facilitar este proceso.
6.  **Cierre de Sesión**: Al llamar a `logout`, se realiza una petición al backend para invalidar la cookie y se limpia el estado de Zustand.

---

## 🛠️ **Configuración del Entorno**

### **Prerrequisitos**

```bash
# Sistema operativo
✅ macOS 12+, Ubuntu 20.04+, Windows 10+

# Lenguajes y herramientas
✅ Python 3.11+
✅ Node.js 18+
✅ Docker & Docker Compose
✅ Git

# Opcional pero recomendado
✅ Claude Code (para Vibecoding)
✅ PostgreSQL 15+ (para desarrollo local)
✅ Redis 7+ (para desarrollo local)
```

### **Instalación Rápida**

```bash
# 1. Clonar el repositorio
git clone https://github.com/proyecto-semilla/proyecto-semilla.git
cd proyecto-semilla

# 2. Configurar entorno Python
python -m venv venv
source venv/bin/activate  # En Windows: venv\Scripts\activate
pip install -r requirements.txt

# 3. Configurar entorno Node.js
cd modules/cms/frontend
npm install
cd ../../..

# 4. Levantar infraestructura
docker-compose up -d

# 5. Ejecutar setup inicial
python scripts/setup_dev.py

# 6. Verificar instalación
python scripts/health_check.py
```

### **Variables de Entorno**

```bash
# .env
DEBUG=True
SECRET_KEY=your-secret-key-here
DATABASE_URL=postgresql://user:password@localhost:5432/proyecto_semilla
REDIS_URL=redis://localhost:6379/0
API_V1_STR=/api/v1
BACKEND_CORS_ORIGINS=["http://localhost:3000", "http://localhost:3001"]
```

---

## 🔧 **Desarrollo con Vibecoding**

### **Flujo de Desarrollo Vibecoding**

```python
# 1. Importar SDK
from proyecto_semilla import ProyectoSemillaClient, AutoDocumentation
from proyecto_semilla.models import ModuleSpec, ModuleCategory

# 2. Crear cliente
client = ProyectoSemillaClient(
    base_url="http://localhost:7777",
    api_key="your-api-key"
)

# 3. Definir módulo
spec = ModuleSpec(
    name="ecommerce_module",
    display_name="E-commerce Module",
    description="Módulo completo de e-commerce",
    category=ModuleCategory.ECOMMERCE,
    features=["products", "cart", "checkout", "orders"],
    entities=[{
        "name": "Product",
        "fields": [
            {"name": "name", "type": "string", "required": True},
            {"name": "price", "type": "float", "required": True}
        ]
    }]
)

# 4. Generar módulo
result = await client.generate_module(spec)
print(f"✅ Módulo generado: {result.files_created} archivos")

# 5. Actualizar documentación
docs_system = AutoDocumentation(client)
await docs_system.update_module_docs("ecommerce_module")
```

### **MCP Integration con Claude**

```json
// Configuración Claude Code
{
  "mcpServers": {
    "proyecto-semilla": {
      "command": "python",
      "args": ["-m", "mcp.server"],
      "env": {
        "API_URL": "http://localhost:7777",
        "API_KEY": "your-api-key"
      }
    }
  }
}
```

### **Comandos Vibecoding Disponibles**

```bash
# Generar módulo desde especificación
claude "Genera un módulo de inventario con productos, categorías y stock"

# Actualizar documentación
claude "Actualiza la documentación del módulo de usuarios"

# Ejecutar tests
claude "Ejecuta los tests del módulo de pagos"

# Optimizar performance
claude "Optimiza la performance del endpoint de productos"
```

---

## 🧪 **Testing y Calidad**

### **Estructura de Tests**

```
tests/
├── __init__.py
├── conftest.py                    # Configuración global
├── test_health.py                # Health checks
├── test_auth.py                  # Autenticación
├── test_tenants_crud.py          # CRUD tenants
├── test_users_crud.py            # CRUD users
├── test_integration.py           # Tests end-to-end
├── test_performance.py           # Performance testing
└── fixtures/                     # Datos de prueba
    ├── users.py
    └── tenants.py
```

### **Ejecutar Tests**

```bash
# Todos los tests
pytest

# Tests específicos
pytest tests/test_auth.py -v

# Tests con coverage
pytest --cov=app --cov-report=html

# Tests de performance
pytest tests/test_performance.py -v

# Tests de integración
pytest tests/test_integration.py -v
```

### **Calidad de Código**

```bash
# Linting
ruff check .

# Type checking
mypy app/

# Security scanning
bandit -r app/

# Format code
black .
isort .
```

---

## 📚 **Documentación Automática**

### **Sistema de Templates**

```python
# docs/templates/module_readme.md
# Template Jinja2 para documentación automática

# {{ display_name }}

**{{ description }}**

## ✨ Características
{% for feature in features %}
- ✅ {{ feature }}
{% endfor %}

## 🏗️ Arquitectura
### Entidades
{% for entity in entities %}
- 📋 **{{ entity.name }}**: {{ entity.description }}
{% endfor %}
```

### **Generación Automática**

```python
# Actualizar documentación de módulo
docs_result = await docs_system.update_module_docs("ecommerce")
# ✅ README.md generado
# ✅ API docs creados
# ✅ Índice actualizado

# Generar documentación completa
full_result = await docs_system.generate_full_docs()
# ✅ Procesamiento masivo
# ✅ Validación automática
```

### **Validación de Documentación**

```python
# Validar documentación
validation = await docs_system.validate_docs("ecommerce")
assert validation["readme_exists"] is True
assert validation["api_docs_exist"] is True
assert validation["all_valid"] is True
```

---

## 🚀 **Deployment y CI/CD**

### **Entornos**

```bash
# Desarrollo
docker-compose -f docker-compose.dev.yml up

# Staging
docker-compose -f docker-compose.staging.yml up

# Producción
docker-compose -f docker-compose.prod.yml up
```

### **CI/CD Pipeline**

```yaml
# .github/workflows/ci.yml
name: CI/CD Pipeline

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'
      - name: Install dependencies
        run: pip install -r requirements.txt
      - name: Run tests
        run: pytest --cov=app --cov-fail-under=80
      - name: Type checking
        run: mypy app/
```

### **Deployment Automático**

```bash
# Deploy a staging
git push origin main

# Deploy a producción (manual approval)
gh workflow run deploy-prod.yml
```

---

## 🤝 **Contribuir al Proyecto**

### **Flujo de Trabajo**

```bash
# 1. Crear rama para feature
git checkout -b feature/nueva-funcionalidad

# 2. Desarrollar siguiendo estándares
# - Type hints en todo el código
# - Tests para nueva funcionalidad
# - Documentación automática
# - Vibecoding-first approach

# 3. Ejecutar tests
pytest --cov=app --cov-fail-under=80

# 4. Commit siguiendo conventional commits
git commit -m "feat: agregar nueva funcionalidad"

# 5. Push y crear PR
git push origin feature/nueva-funcionalidad
```

### **Estándares de Código**

```python
# ✅ Correcto - Type hints completos
def create_tenant(name: str, settings: dict) -> Tenant:
    """Crear nuevo tenant con configuración."""
    pass

# ❌ Incorrecto - Sin type hints
def create_tenant(name, settings):
    pass
```

### **Conventional Commits**

```bash
# Features
git commit -m "feat: agregar sistema de notificaciones"

# Fixes
git commit -m "fix: corregir validación de email"

# Documentation
git commit -m "docs: actualizar guía de instalación"

# Tests
git commit -m "test: agregar tests para módulo de pagos"
```

---

## 🔧 **Troubleshooting**

### **Problemas Comunes**

#### **1. Error de Conexión a Base de Datos**
```bash
# Verificar que PostgreSQL esté corriendo
docker ps | grep postgres

# Reiniciar servicios
docker-compose down
docker-compose up -d

# Verificar conexión
python -c "from app.core.database import engine; print('✅ Conexión OK')"
```

#### **2. Tests Fallando**
```bash
# Limpiar cache de pytest
pytest --cache-clear

# Ejecutar tests específicos
pytest tests/test_auth.py::test_login_success -v

# Verificar coverage
pytest --cov=app --cov-report=term-missing
```

#### **3. MCP Server No Conecta**
```bash
# Verificar configuración
cat ~/.claude/config.json

# Reiniciar MCP server
pkill -f mcp.server
python -m mcp.server

# Verificar logs
tail -f logs/mcp_server.log
```

#### **4. Performance Issues**
```bash
# Ejecutar performance tests
pytest tests/test_performance.py -v

# Verificar métricas
python scripts/performance_monitor.py

# Optimizar queries
python scripts/query_optimizer.py
```

### **Debugging Avanzado**

```python
# Habilitar debug logging
import logging
logging.basicConfig(level=logging.DEBUG)

# Verificar estado del sistema
from app.core.health import get_system_health
health = await get_system_health()
print(health)

# Debug MCP communication
from mcp.server import debug_mcp_connection
await debug_mcp_connection()
```

---

## 📞 **Soporte y Comunidad**

### **Canales de Comunicación**

- **📧 Email**: developers@proyecto-semilla.dev
- **💬 Discord**: [Proyecto Semilla Community](https://discord.gg/proyecto-semilla)
- **🐛 Issues**: [GitHub Issues](https://github.com/proyecto-semilla/proyecto-semilla/issues)
- **📚 Docs**: [Documentación Completa](https://docs.proyecto-semilla.dev)

### **Recursos Adicionales**

- **🎯 Vibecoding Guide**: `docs/vibecoding/getting-started.md`
- **🧪 Testing Guide**: `docs/testing/testing-guide.md`
- **🚀 Deployment Guide**: `docs/deployment/deployment-guide.md`
- **🔧 API Reference**: `http://localhost:7777/docs`

---

## 🎯 **Próximos Pasos**

### **Roadmap Inmediato**
1. **📊 Analytics Dashboard** - Métricas de uso en tiempo real
2. **🔧 SDKs Adicionales** - JavaScript, Go para más LLMs
3. **📈 Scale Testing** - Validación con cargas reales
4. **🎨 UI/UX Polish** - Experiencia de usuario final

### **Contribuciones Bienvenidas**
- 🐛 Bug fixes
- ✨ New features
- 📚 Documentation improvements
- 🧪 Additional tests
- 🎨 UI/UX enhancements

---

**🌱 Proyecto Semilla - Construyendo el futuro del desarrollo SaaS con Vibecoding**

**¡Tu contribución acelera la revolución del desarrollo asistido por IA!** 🚀