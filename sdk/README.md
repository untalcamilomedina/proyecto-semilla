# 🛠️ SDKs - Proyecto Semilla

Este directorio contiene los Software Development Kits (SDKs) oficiales para interactuar con la API de Proyecto Semilla.

## 🎯 Filosofía de los SDKs

Los SDKs de Proyecto Semilla están diseñados para:
- **🚀 Simplicidad**: API intuitiva y fácil de usar
- **🔒 Seguridad**: Manejo seguro de credenciales y autenticación
- **⚡ Performance**: Conexiones optimizadas y caching inteligente
- **🧪 Testeable**: Fácil de mockear y testear
- **📚 Bien Documentado**: Documentación completa con ejemplos

## 🌐 SDKs Disponibles

### ✅ **Python SDK** (`sdk/python/`)
- **Target**: Aplicaciones Python, data science, automation
- **Características**: Type hints completos, async/await, pandas integration
- **Status**: Planeado para v0.2.0

### ✅ **TypeScript SDK** (`sdk/typescript/`)  
- **Target**: Aplicaciones Node.js, frontend frameworks
- **Características**: Types completos, tree-shaking, ESM/CJS support
- **Status**: Planeado para v0.4.0

### ✅ **PHP SDK** (`sdk/php/`)
- **Target**: WordPress plugins, Laravel apps, CMS integration  
- **Características**: PSR-4, Composer, Laravel service provider
- **Status**: Planeado para v0.4.0

### 🔮 **Futuros SDKs**
- **Go SDK**: Para microservicios y alta performance (v0.8.0)
- **Ruby SDK**: Para Rails applications (v0.8.0)
- **Java SDK**: Para aplicaciones enterprise (futuro)
- **.NET SDK**: Para ecosistema Microsoft (futuro)

## 📋 Estructura Estándar de SDKs

Cada SDK sigue una estructura consistente:

```
sdk/{language}/
├── README.md                 # Documentación específica
├── CHANGELOG.md             # Historial de cambios
├── pyproject.toml           # Configuración del proyecto (Python)
├── package.json             # Configuración del proyecto (JS/TS)
├── composer.json            # Configuración del proyecto (PHP)
├── src/                     # Código fuente
│   ├── client.{ext}         # Cliente principal
│   ├── auth/                # Módulo de autenticación
│   ├── resources/           # Recursos de la API
│   │   ├── users.{ext}      # Gestión de usuarios
│   │   ├── tenants.{ext}    # Gestión de tenants
│   │   └── roles.{ext}      # Gestión de roles
│   ├── models/              # Modelos de datos
│   ├── exceptions/          # Excepciones personalizadas
│   └── utils/               # Utilidades
├── tests/                   # Tests del SDK
├── examples/                # Ejemplos de uso
└── docs/                    # Documentación adicional
```

## 🚀 API Consistente Entre SDKs

### 🔧 Inicialización
```python
# Python
from proyecto_semilla import Client

client = Client(
    base_url="https://api.mi-app.com",
    api_key="ps_abc123...",
    tenant_id="tenant-uuid"  # Opcional, se puede set por request
)
```

```typescript
// TypeScript
import { ProyectoSemillaClient } from '@proyecto-semilla/sdk';

const client = new ProyectoSemillaClient({
  baseURL: 'https://api.mi-app.com',
  apiKey: 'ps_abc123...',
  tenantId: 'tenant-uuid' // Opcional
});
```

```php
<?php
// PHP
use ProyectoSemilla\Client;

$client = new Client([
    'base_url' => 'https://api.mi-app.com',
    'api_key' => 'ps_abc123...',
    'tenant_id' => 'tenant-uuid' // Opcional
]);
```

### 👥 Gestión de Usuarios
```python
# Python
users = await client.users.list(page=1, limit=10)
user = await client.users.create({
    "email": "nuevo@ejemplo.com",
    "first_name": "Juan",
    "last_name": "Pérez"
})
await client.users.update(user.id, {"first_name": "Juan Carlos"})
await client.users.delete(user.id)
```

```typescript
// TypeScript  
const users = await client.users.list({ page: 1, limit: 10 });
const user = await client.users.create({
  email: 'nuevo@ejemplo.com',
  firstName: 'Juan',
  lastName: 'Pérez'
});
await client.users.update(user.id, { firstName: 'Juan Carlos' });
await client.users.delete(user.id);
```

```php
<?php
// PHP
$users = $client->users()->list(['page' => 1, 'limit' => 10]);
$user = $client->users()->create([
    'email' => 'nuevo@ejemplo.com',
    'first_name' => 'Juan',
    'last_name' => 'Pérez'
]);
$client->users()->update($user->id, ['first_name' => 'Juan Carlos']);
$client->users()->delete($user->id);
```

## 🏗️ Características Técnicas

### 🔐 Autenticación
- **API Keys**: Soporte para API keys del tenant
- **JWT Tokens**: Manejo automático de refresh tokens
- **OAuth 2.0**: Para integraciones de terceros (futuro)
- **Rate Limiting**: Manejo inteligente de límites de rate

### ⚡ Performance
- **Connection Pooling**: Reutilización de conexiones HTTP
- **Caching**: Cache inteligente de responses frecuentes
- **Pagination**: Soporte automático para paginación
- **Bulk Operations**: Operaciones masivas optimizadas

### 🧪 Testing y Debugging
- **Mock Server**: Servidor mock para testing
- **Debug Mode**: Logging detallado de requests/responses
- **Retry Logic**: Reintentos automáticos con backoff exponencial
- **Error Handling**: Excepciones tipadas y descriptivas

### 📊 Observabilidad
- **Metrics**: Métricas de uso y performance
- **Logging**: Structured logging compatible con frameworks
- **Tracing**: Distributed tracing support (OpenTelemetry)

## 🔄 Versionado y Compatibilidad

### 📋 Política de Versionado
- **Semantic Versioning**: MAJOR.MINOR.PATCH
- **API Compatibility**: Compatibilidad hacia atrás dentro de MAJOR
- **Deprecation Policy**: 2 minor versions de aviso antes de breaking change
- **LTS Versions**: Versiones de soporte extendido cada año

### 🔄 Sincronización con API
| SDK Version | API Version | Core Version | Status |
|-------------|-------------|--------------|--------|
| 0.1.x | v1 | v0.1.x-v0.3.x | Development |
| 0.2.x | v1 | v0.4.x-v0.6.x | Planned |
| 0.3.x | v2 | v0.7.x-v0.9.x | Planned |

## 📚 Documentación y Ejemplos

### 🎯 Use Cases por SDK

**Python SDK - Casos de Uso**:
- 📊 Scripts de análisis de datos con pandas
- 🤖 Bots y automatización
- 🧠 Integración con ML/AI workflows
- 📈 Reportes y dashboards

**TypeScript SDK - Casos de Uso**:
- ⚛️ Aplicaciones React/Next.js
- 🟢 Aplicaciones Node.js/Express
- 📱 Apps móviles con React Native
- ⚡ Aplicaciones serverless

**PHP SDK - Casos de Uso**:
- 🔌 Plugins de WordPress
- 🎯 Aplicaciones Laravel/Symfony
- 🛒 Tiendas online (WooCommerce, Shopify)
- 🏢 Sistemas CMS personalizados

### 📖 Recursos de Aprendizaje
- **Quick Start Guides**: Guías de 5 minutos por SDK
- **Tutorials**: Tutoriales paso a paso
- **API Reference**: Documentación completa auto-generada
- **Code Examples**: Repositorio de ejemplos prácticos
- **Video Tutorials**: Canal de YouTube (futuro)

## 🤝 Contribuir a los SDKs

### 🔧 Setup de Desarrollo
```bash
# Clonar repositorio
git clone https://github.com/proyecto-semilla/proyecto-semilla.git
cd proyecto-semilla/sdk/{language}

# Instalar dependencias (ejemplo Python)
pip install -e .[dev]

# Ejecutar tests
pytest

# Ejecutar linter
ruff check .
```

### 📋 Guidelines
- **Code Style**: Seguir convenciones del lenguaje
- **Testing**: 100% cobertura para APIs públicas
- **Documentation**: Docstrings/JSDoc completos
- **Examples**: Al menos un ejemplo por método público
- **Backwards Compatibility**: No breaking changes sin MAJOR bump

## 🗺️ Roadmap de SDKs

### ✅ **Fase 1 (v0.1.0-v0.3.0)**: Fundación
- [ ] Python SDK básico con auth, users, tenants
- [ ] Documentación y ejemplos básicos
- [ ] CI/CD para testing y releases

### 🔮 **Fase 2 (v0.4.0-v0.6.0)**: Expansión
- [ ] TypeScript SDK completo
- [ ] PHP SDK para WordPress/Laravel
- [ ] Advanced features (bulk operations, webhooks)
- [ ] Mock server para testing

### 🚀 **Fase 3 (v0.7.0-v0.9.0)**: Ecosistema
- [ ] Go SDK para microservicios
- [ ] Ruby SDK para Rails
- [ ] CLI tool basado en SDKs
- [ ] Plugins oficiales para IDEs

---

## 📞 Soporte y Comunidad

- **📚 Documentación**: [docs.proyectosemilla.dev/sdks](https://docs.proyectosemilla.dev/sdks)
- **💬 Discord**: Canal #sdk-support
- **🐛 Issues**: [GitHub Issues](https://github.com/proyecto-semilla/proyecto-semilla/issues)
- **📧 Email**: sdk-support@proyectosemilla.dev

---

*Los SDKs son la puerta de entrada para que desarrolladores construyan sobre Proyecto Semilla. Nuestro compromiso es hacerlos excepcionales.*