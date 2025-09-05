# Proyecto Semilla MCP Server

**Model Context Protocol Server para desarrollo Vibecoding-native**

[![Version](https://img.shields.io/badge/version-0.1.0-blue.svg)](https://github.com/proyecto-semilla/proyecto-semilla)
[![Python](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/)

## 🚀 Descripción

El MCP Server de Proyecto Semilla permite que LLMs como Claude interactúen directamente con la plataforma para:

- ✅ **Generar módulos automáticamente** desde especificaciones naturales
- ✅ **Gestionar tenants y usuarios** programáticamente
- ✅ **Actualizar documentación** en tiempo real
- ✅ **Monitorear estado del sistema** y módulos
- ✅ **Deploy módulos** a tenants específicos

## 📦 Instalación

```bash
# Instalar dependencias
pip install mcp proyecto-semilla

# O instalar desde el proyecto
pip install -e ./mcp
```

## 🏁 Inicio Rápido

```python
from mcp.server import ProyectoSemillaMCPServer

# Inicializar servidor MCP
server = ProyectoSemillaMCPServer(
    instance_url="http://localhost:7777",
    api_key="your-api-key"  # O usa login
)

# El servidor está listo para recibir comandos MCP
```

## 🛠️ Herramientas Disponibles

### 1. `generate_module`
**Genera un módulo completo desde especificación natural**

```python
# Ejemplo de uso con Claude:
"Genera un módulo de e-commerce con productos, carrito y checkout"
```

**Parámetros:**
- `name`: Nombre del módulo (snake_case)
- `description`: Descripción human-readable
- `category`: Categoría (cms, inventory, crm, finance, etc.)
- `features`: Lista de features a implementar
- `entities`: Lista opcional de entidades

**Respuesta:**
```
✅ Module 'ecommerce' generated successfully!

📊 Generation Summary:
• Files Created: 15
• APIs Generated: 8
• UI Components: 6
• Execution Time: 3.2s

🎯 Features Implemented:
• Product management
• Shopping cart
• Checkout process
• Payment integration
```

### 2. `list_tenants`
**Obtiene lista de todos los tenants disponibles**

```python
# Lista tenants con detalles
tenants = await list_tenants()
```

**Respuesta:**
```
🏢 Available Tenants (3)

Demo Company
• Slug: demo-company
• Status: ✅ Active
• Created: 2025-01-15

Test Corp
• Slug: test-corp
• Status: ✅ Active
• Created: 2025-01-20
```

### 3. `create_user`
**Crea un nuevo usuario en un tenant específico**

```python
# Crear usuario
user = await create_user(
    email="newuser@example.com",
    password="securepass123",
    tenant_id="tenant-1",
    first_name="Juan",
    last_name="Pérez"
)
```

**Respuesta:**
```
✅ User created successfully!

👤 Juan Pérez
• Email: newuser@example.com
• Tenant: tenant-1
• Status: ✅ Active
• Email Verified: ❌ No
```

### 4. `get_module_status`
**Verifica el estado de un módulo generado**

```python
# Verificar estado
status = await get_module_status("ecommerce")
```

**Respuesta:**
```
📦 Module: ecommerce

Status: READY
Description: Module ready for deployment

📁 Files: 15
🔌 API Endpoints: 8
🖥️ UI Components: 6

🕒 Last Updated: 2025-09-05 15:30:00
```

### 5. `deploy_module`
**Despliega un módulo a un tenant específico**

```python
# Deploy módulo
success = await deploy_module("ecommerce", "tenant-1")
```

**Respuesta:**
```
✅ Module 'ecommerce' deployed successfully to tenant 'tenant-1'!

The module is now available for use in the specified tenant.
```

### 6. `update_documentation`
**Actualiza la documentación auto-generada del módulo**

```python
# Actualizar docs
result = await update_documentation("ecommerce")
```

**Respuesta:**
```
✅ Documentation updated for module 'ecommerce'!

📚 Files Updated: 3
• README.md generated/updated
• API documentation updated
• Main index updated
```

### 7. `analyze_codebase`
**Analiza la estructura actual del codebase**

```python
# Análisis completo
analysis = await analyze_codebase()
```

**Respuesta:**
```
🔍 Proyecto Semilla Codebase Analysis

🏥 System Health: HEALTHY
📊 Response Time: 0.15s
🏷️ Version: 0.1.0

🏢 Tenants: 3
✅ Active: 3

📦 Modules: 5
• Ready: 4
• Generating: 1

💡 Recommendations:
• System health is optimal
• Consider creating more demo tenants
• All modules are up to date
```

### 8. `generate_api_tests`
**Genera tests API comprehensivos para un módulo**

```python
# Generar tests
tests = await generate_api_tests("ecommerce")
```

*Nota: Esta funcionalidad estará disponible en futuras versiones*

### 9. `optimize_performance`
**Analiza y optimiza el performance del módulo**

```python
# Optimizar performance
optimizations = await optimize_performance("ecommerce")
```

*Nota: Esta funcionalidad estará disponible en futuras versiones*

## 📚 Recursos Disponibles

### 1. `proyecto-semilla://architecture`
**Información de arquitectura del sistema**

Contiene:
- Estado del sistema
- Información de tenants
- Arquitectura multi-tenant
- Sistema de módulos
- Integración Vibecoding

### 2. `proyecto-semilla://database/schema`
**Esquema de base de datos actual**

Incluye:
- Estructura de tablas core
- Relaciones y foreign keys
- Features de seguridad
- Índices de performance

### 3. `proyecto-semilla://api/endpoints`
**Lista completa de endpoints API disponibles**

Documenta:
- Endpoints de autenticación
- Gestión de tenants
- Gestión de usuarios
- Sistema de módulos
- Health checks

## 🔧 Configuración

### Configuración Básica
```python
server = ProyectoSemillaMCPServer(
    instance_url="http://localhost:7777",  # URL de tu instancia
    api_key="your-api-key",                # API key (opcional)
    auto_auth=True                         # Auto-refresh tokens
)
```

### Autenticación
```python
# Con API Key (recomendado para LLMs)
server = ProyectoSemillaMCPServer(
    instance_url="http://localhost:7777",
    api_key="sk-1234567890abcdef"
)

# Sin API Key (requiere login manual)
server = ProyectoSemillaMCPServer(
    instance_url="http://localhost:7777"
)
```

## 🧪 Testing

```bash
# Ejecutar tests del MCP Server
pytest mcp/tests/

# Tests específicos
pytest mcp/tests/test_server.py -v

# Con coverage
pytest --cov=mcp --cov-report=html
```

## 🤖 Integración con Claude Code

### Configuración en Claude
```json
{
  "mcpServers": {
    "proyecto-semilla": {
      "command": "python",
      "args": ["-m", "mcp.server"],
      "env": {
        "PROYECTO_SEMILLA_URL": "http://localhost:7777",
        "PROYECTO_SEMILLA_API_KEY": "your-api-key"
      }
    }
  }
}
```

### Comandos Disponibles en Claude
```bash
# Generar módulo
/generate_module name=ecommerce description="Tienda online" category=ecommerce features=["products","cart","checkout"]

# Listar tenants
/list_tenants

# Crear usuario
/create_user email=user@example.com password=pass123 tenant_id=tenant-1

# Verificar módulo
/get_module_status ecommerce

# Deploy módulo
/deploy_module ecommerce tenant-1

# Actualizar documentación
/update_documentation ecommerce

# Analizar codebase
/analyze_codebase
```

## 📋 Casos de Uso Típicos

### 1. Desarrollo de Nuevo Módulo
```bash
# Claude entiende lenguaje natural
"Claude, crea un sistema de inventario con productos, categorías y reportes de stock"
```

### 2. Gestión de Tenants
```bash
# Administrar múltiples tenants
"Claude, crea un nuevo tenant para Empresa XYZ y configura usuarios básicos"
```

### 3. Mantenimiento del Sistema
```bash
# Monitoreo y mantenimiento
"Claude, analiza el estado del sistema y sugiere optimizaciones"
```

### 4. Documentación Automática
```bash
# Mantener docs actualizadas
"Claude, actualiza toda la documentación del módulo de ventas"
```

## 🚨 Manejo de Errores

```python
# Errores comunes y soluciones
try:
    result = await generate_module(spec)
except AuthenticationError:
    print("❌ Error: Token expirado o inválido")
except ValidationError as e:
    print(f"❌ Error de validación: {e.message}")
except APIError as e:
    print(f"❌ Error de API: {e.status_code}")
except Exception as e:
    print(f"❌ Error inesperado: {str(e)}")
```

## 📈 Métricas de Performance

- **Tiempo de respuesta**: < 500ms para operaciones simples
- **Generación de módulos**: < 30s para módulos complejos
- **Uptime del servidor**: 99.9% (diseño stateless)
- **Concurrencia**: Soporta múltiples LLMs simultáneamente

## 🔒 Seguridad

- **Autenticación JWT** con refresh automático
- **API Keys** para acceso programático
- **Tenant isolation** en todas las operaciones
- **Rate limiting** integrado
- **Audit logging** de todas las operaciones

## 📞 Soporte

- 📧 **Email**: dev@proyectosemilla.dev
- 💬 **Discord**: [Proyecto Semilla Community](https://discord.gg/proyecto-semilla)
- 📖 **Docs**: [Documentación Técnica](https://docs.proyectosemilla.dev/mcp)

---

**🌱 Proyecto Semilla MCP Server - Conectando LLMs con el futuro del desarrollo SaaS** 🚀