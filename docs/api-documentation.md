# 📚 API Documentation - Proyecto Semilla
## Interactive API Documentation with Examples

**Versión:** 0.5.0
**Última actualización:** 5 de septiembre de 2025
**Base URL:** `https://api.proyecto-semilla.dev/v1`

---

## 🚀 Acceso Rápido

- **📖 Swagger UI:** [https://api.proyecto-semilla.dev/docs](https://api.proyecto-semilla.dev/docs)
- **📋 ReDoc:** [https://api.proyecto-semilla.dev/redoc](https://api.proyecto-semilla.dev/redoc)
- **🔗 OpenAPI JSON:** [https://api.proyecto-semilla.dev/openapi.json](https://api.proyecto-semilla.dev/openapi.json)

---

## 🔐 Autenticación

Todas las APIs requieren autenticación JWT. Incluya el token en el header:

```http
Authorization: Bearer <your_jwt_token>
X-Tenant-ID: <tenant_uuid>
```

### Obtener Token JWT

```bash
curl -X POST "https://api.proyecto-semilla.dev/v1/auth/login" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@example.com",
    "password": "password123"
  }'
```

**Respuesta:**
```json
{
  "access_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
  "token_type": "bearer",
  "expires_in": 3600
}
```

---

## 📋 Endpoints Principales

### 📰 Articles API

#### Listar Artículos
```http
GET /api/v1/articles
```

**Parámetros de Query:**
- `skip` (integer, opcional): Número de artículos a saltar (default: 0)
- `limit` (integer, opcional): Número máximo de artículos (default: 100, max: 1000)
- `status_filter` (string, opcional): Filtrar por estado (`draft`, `published`, `review`)
- `category_id` (UUID, opcional): Filtrar por categoría

**Ejemplo:**
```bash
curl -X GET "https://api.proyecto-semilla.dev/v1/articles?limit=10&status_filter=published" \
  -H "Authorization: Bearer <token>" \
  -H "X-Tenant-ID: <tenant_id>"
```

**Respuesta:**
```json
[
  {
    "id": "550e8400-e29b-41d4-a716-446655440000",
    "tenant_id": "550e8400-e29b-41d4-a716-446655440001",
    "title": "Mi Primer Artículo",
    "slug": "mi-primer-articulo",
    "content": "Contenido completo del artículo...",
    "excerpt": "Resumen del artículo...",
    "author_id": "550e8400-e29b-41d4-a716-446655440002",
    "category_id": "550e8400-e29b-41d4-a716-446655440003",
    "seo_title": "Título SEO",
    "seo_description": "Descripción SEO",
    "featured_image": "https://example.com/image.jpg",
    "status": "published",
    "is_featured": true,
    "view_count": 150,
    "comment_count": 5,
    "like_count": 25,
    "tags": ["tutorial", "beginners"],
    "published_at": "2025-09-05T10:00:00Z",
    "created_at": "2025-09-05T09:00:00Z",
    "updated_at": "2025-09-05T10:00:00Z",
    "author_name": "Juan Pérez",
    "category_name": "Tutoriales"
  }
]
```

#### Crear Artículo
```http
POST /api/v1/articles
```

**Body:**
```json
{
  "title": "Nuevo Artículo",
  "slug": "nuevo-articulo",
  "content": "Contenido del artículo en formato Markdown o HTML",
  "excerpt": "Resumen breve del artículo",
  "category_id": "550e8400-e29b-41d4-a716-446655440003",
  "seo_title": "Título para SEO",
  "seo_description": "Descripción para SEO",
  "featured_image": "https://example.com/image.jpg",
  "status": "draft",
  "is_featured": false,
  "tags": ["tutorial", "react"]
}
```

**Ejemplo con curl:**
```bash
curl -X POST "https://api.proyecto-semilla.dev/v1/articles" \
  -H "Authorization: Bearer <token>" \
  -H "X-Tenant-ID: <tenant_id>" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Mi Nuevo Artículo",
    "slug": "mi-nuevo-articulo",
    "content": "Contenido del artículo...",
    "status": "draft"
  }'
```

#### Obtener Artículo por ID
```http
GET /api/v1/articles/{article_id}
```

**Parámetros de Path:**
- `article_id` (UUID, requerido): ID del artículo

**Ejemplo:**
```bash
curl -X GET "https://api.proyecto-semilla.dev/v1/articles/550e8400-e29b-41d4-a716-446655440000" \
  -H "Authorization: Bearer <token>" \
  -H "X-Tenant-ID: <tenant_id>"
```

#### Actualizar Artículo
```http
PUT /api/v1/articles/{article_id}
```

**Body (solo campos a actualizar):**
```json
{
  "title": "Título Actualizado",
  "status": "published",
  "tags": ["tutorial", "updated"]
}
```

#### Eliminar Artículo
```http
DELETE /api/v1/articles/{article_id}
```

#### Estadísticas de Artículos
```http
GET /api/v1/articles/stats/overview
```

**Respuesta:**
```json
{
  "total_articles": 25,
  "published_articles": 20,
  "draft_articles": 5,
  "total_views": 1250,
  "total_comments": 45,
  "total_likes": 180
}
```

---

### 👥 Users API

#### Listar Usuarios
```http
GET /api/v1/users
```

**Parámetros de Query:**
- `skip` (integer): Paginación
- `limit` (integer): Límite de resultados
- `role_id` (UUID): Filtrar por rol

#### Crear Usuario
```http
POST /api/v1/users
```

**Body:**
```json
{
  "email": "nuevo@usuario.com",
  "first_name": "Juan",
  "last_name": "Pérez",
  "password": "SecurePass123!",
  "role_id": "550e8400-e29b-41d4-a716-446655440004"
}
```

#### Obtener Perfil de Usuario
```http
GET /api/v1/users/profile
```

#### Actualizar Perfil
```http
PUT /api/v1/users/profile
```

---

### 🏢 Tenants API

#### Listar Tenants
```http
GET /api/v1/tenants
```

#### Crear Tenant
```http
POST /api/v1/tenants
```

**Body:**
```json
{
  "name": "Mi Empresa",
  "slug": "mi-empresa",
  "description": "Descripción de la empresa",
  "is_active": true
}
```

---

### 🔐 Authentication API

#### Login
```http
POST /api/v1/auth/login
```

**Body:**
```json
{
  "email": "user@example.com",
  "password": "password123"
}
```

#### Refresh Token
```http
POST /api/v1/auth/refresh
```

**Body:**
```json
{
  "refresh_token": "refresh_token_here"
}
```

#### Logout
```http
POST /api/v1/auth/logout
```

---

## 📊 Rate Limiting

La API implementa rate limiting inteligente:

- **Requests por minuto:** 100 (configurable por endpoint)
- **Burst limit:** 200 requests
- **Headers de respuesta:**
  - `X-RateLimit-Limit`: Límite total
  - `X-RateLimit-Remaining`: Requests restantes
  - `X-RateLimit-Reset`: Timestamp de reset

```http
HTTP/1.1 429 Too Many Requests
X-RateLimit-Limit: 100
X-RateLimit-Remaining: 0
X-RateLimit-Reset: 1630785600
Retry-After: 60
```

---

## 🛡️ Security Features

### Threat Detection
- **ML-based analysis** de patrones maliciosos
- **IP reputation checking**
- **Request pattern analysis**
- **Automated blocking** de amenazas

### Input Validation
- **Enterprise-grade validation** con sanitización
- **SQL injection prevention**
- **XSS protection**
- **Input length limits**

### Audit Logging
- **Complete audit trail** de todas las operaciones
- **Compliance-ready logging**
- **Real-time monitoring**

---

## 🚨 Error Handling

### Códigos de Error Comunes

| Código | Descripción | Solución |
|--------|-------------|----------|
| 400 | Bad Request | Verificar datos enviados |
| 401 | Unauthorized | Verificar token JWT |
| 403 | Forbidden | Verificar permisos |
| 404 | Not Found | Verificar ID del recurso |
| 429 | Too Many Requests | Esperar y reintentar |
| 500 | Internal Server Error | Contactar soporte |

### Ejemplo de Error
```json
{
  "detail": "Article with this slug already exists",
  "error_code": "ARTICLE_SLUG_EXISTS",
  "timestamp": "2025-09-05T10:00:00Z"
}
```

---

## 📱 SDKs y Librerías

### JavaScript/TypeScript SDK
```javascript
import { ProyectoSemillaAPI } from '@proyecto-semilla/sdk';

const api = new ProyectoSemillaAPI({
  baseURL: 'https://api.proyecto-semilla.dev/v1',
  tenantId: 'your-tenant-id'
});

// Login
const tokens = await api.auth.login('user@example.com', 'password');

// Get articles
const articles = await api.articles.list({ limit: 10 });

// Create article
const newArticle = await api.articles.create({
  title: 'My Article',
  content: 'Article content...',
  status: 'draft'
});
```

### Python SDK
```python
from proyecto_semilla import APIClient

client = APIClient(
    base_url="https://api.proyecto-semilla.dev/v1",
    tenant_id="your-tenant-id"
)

# Login
tokens = client.auth.login("user@example.com", "password")

# Get articles
articles = client.articles.list(limit=10)

# Create article
article = client.articles.create({
    "title": "My Article",
    "content": "Article content...",
    "status": "draft"
})
```

---

## 🔧 Troubleshooting

### Problemas Comunes

#### "Connection timeout"
```bash
# Verificar conectividad
curl -v https://api.proyecto-semilla.dev/health

# Verificar DNS
nslookup api.proyecto-semilla.dev
```

#### "Rate limit exceeded"
```bash
# Esperar el tiempo indicado
sleep 60
curl -X GET "https://api.proyecto-semilla.dev/v1/articles" \
  -H "Authorization: Bearer <token>"
```

#### "Invalid token"
```bash
# Refresh token
curl -X POST "https://api.proyecto-semilla.dev/v1/auth/refresh" \
  -H "Content-Type: application/json" \
  -d '{"refresh_token": "your_refresh_token"}'
```

---

## 📈 Monitoring & Analytics

### Health Check Endpoint
```http
GET /health
```

**Respuesta:**
```json
{
  "status": "healthy",
  "timestamp": "2025-09-05T10:00:00Z",
  "version": "0.5.0",
  "services": {
    "database": "healthy",
    "redis": "healthy",
    "external_apis": "healthy"
  },
  "metrics": {
    "uptime": "99.9%",
    "response_time_p95": "45ms",
    "error_rate": "0.01%"
  }
}
```

### Metrics Endpoint
```http
GET /metrics
```

Proporciona métricas en formato Prometheus para monitoring avanzado.

---

## 🌐 Webhooks & Integrations

### Configurar Webhooks
```http
POST /api/v1/webhooks
```

**Body:**
```json
{
  "url": "https://your-app.com/webhook",
  "events": ["article.published", "user.created"],
  "secret": "your-webhook-secret"
}
```

### Eventos Disponibles
- `article.created`
- `article.updated`
- `article.published`
- `article.deleted`
- `user.created`
- `user.updated`
- `tenant.created`

---

## 📞 Soporte

### Canales de Soporte
- **📧 Email:** support@proyecto-semilla.dev
- **💬 Discord:** [discord.gg/proyecto-semilla](https://discord.gg/proyecto-semilla)
- **📚 Documentación:** [docs.proyecto-semilla.dev](https://docs.proyecto-semilla.dev)

### Reportar Issues
- **🐛 Bug Reports:** [GitHub Issues](../../issues)
- **💡 Feature Requests:** [GitHub Discussions](../../discussions)
- **🔒 Security Issues:** security@proyecto-semilla.dev

---

*"Esta documentación se mantiene automáticamente sincronizada con el código. Última actualización: 5 de septiembre de 2025"*

🇨🇴 **Proyecto Semilla** - Documentación API v0.5.0