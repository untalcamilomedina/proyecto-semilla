# 🚨 Troubleshooting Guide - Proyecto Semilla
## Soluciones para Problemas Comunes

**Versión:** 0.5.0
**Última actualización:** 5 de septiembre de 2025

---

## 📋 Tabla de Contenidos

- [Problemas de Base de Datos](#-problemas-de-base-de-datos)
- [Problemas de Autenticación](#-problemas-de-autenticación)
- [Problemas de Performance](#-problemas-de-performance)
- [Problemas de Rate Limiting](#-problemas-de-rate-limiting)
- [Problemas de Docker](#-problemas-de-docker)
- [Problemas de Frontend](#-problemas-de-frontend)
- [Problemas de Seguridad](#-problemas-de-seguridad)
- [Checklist de Verificación](#-checklist-de-verificación)

---

## 🗄️ Problemas de Base de Datos

### **Sintoma: "Connection timeout"**

**Diagnóstico:**
```bash
# Verificar conectividad con PostgreSQL
docker-compose exec db pg_isready -h localhost -p 5432

# Verificar logs del contenedor
docker-compose logs db
```

**Soluciones:**

1. **Verificar estado del contenedor:**
   ```bash
   docker-compose ps
   # Debe mostrar: proyecto_semilla_db Up (healthy)
   ```

2. **Reiniciar servicios de base de datos:**
   ```bash
   docker-compose restart db
   ```

3. **Verificar variables de entorno:**
   ```bash
   # En .env
   DATABASE_URL=postgresql://user:password@db:5432/proyecto_semilla
   ```

4. **Verificar conectividad de red:**
   ```bash
   docker-compose exec backend nc -zv db 5432
   ```

### **Sintoma: "Too many connections"**

**Diagnóstico:**
```sql
-- Verificar conexiones activas
SELECT count(*) FROM pg_stat_activity;

-- Verificar límites de configuración
SHOW max_connections;
```

**Soluciones:**

1. **Aumentar pool de conexiones:**
   ```python
   # backend/app/core/database.py
   SQLALCHEMY_POOL_SIZE = 20
   SQLALCHEMY_MAX_OVERFLOW = 30
   ```

2. **Implementar connection pooling:**
   ```python
   from sqlalchemy.pool import QueuePool
   engine = create_engine(
       DATABASE_URL,
       poolclass=QueuePool,
       pool_size=20,
       max_overflow=30
   )
   ```

3. **Verificar leaks de conexiones:**
   ```python
   # Asegurar que todas las sesiones se cierren
   async with AsyncSessionLocal() as session:
       try:
           # Tu código aquí
           await session.commit()
       finally:
           await session.close()
   ```

### **Sintoma: "Table does not exist"**

**Diagnóstico:**
```sql
-- Verificar tablas existentes
SELECT table_name FROM information_schema.tables
WHERE table_schema = 'public';
```

**Soluciones:**

1. **Ejecutar migraciones:**
   ```bash
   docker-compose exec backend alembic upgrade head
   ```

2. **Verificar estado de migraciones:**
   ```bash
   docker-compose exec backend alembic current
   ```

3. **Resetear base de datos (desarrollo):**
   ```bash
   docker-compose down -v
   docker-compose up -d db
   docker-compose exec backend alembic upgrade head
   ```

---

## 🔐 Problemas de Autenticación

### **Sintoma: "Invalid token"**

**Diagnóstico:**
```bash
# Verificar token en headers
curl -H "Authorization: Bearer YOUR_TOKEN" \
     -H "X-Tenant-ID: YOUR_TENANT_ID" \
     https://api.proyecto-semilla.dev/v1/users/profile
```

**Soluciones:**

1. **Refresh token expirado:**
   ```bash
   curl -X POST "https://api.proyecto-semilla.dev/v1/auth/refresh" \
        -H "Content-Type: application/json" \
        -d '{"refresh_token": "your_refresh_token"}'
   ```

2. **Token malformado:**
   - Verificar que el token tenga el formato correcto: `Bearer <token>`
   - Asegurar que no haya espacios extra

3. **Tenant ID incorrecto:**
   ```bash
   # Verificar tenant ID válido
   curl -H "Authorization: Bearer YOUR_TOKEN" \
        https://api.proyecto-semilla.dev/v1/tenants
   ```

### **Sintoma: "User not found"**

**Diagnóstico:**
```sql
-- Verificar usuario en base de datos
SELECT id, email, is_active FROM users WHERE email = 'user@example.com';
```

**Soluciones:**

1. **Usuario inactivo:**
   ```sql
   UPDATE users SET is_active = true WHERE email = 'user@example.com';
   ```

2. **Usuario pertenece a tenant diferente:**
   ```sql
   -- Verificar tenant del usuario
   SELECT u.email, t.name as tenant_name
   FROM users u
   JOIN tenants t ON u.tenant_id = t.id
   WHERE u.email = 'user@example.com';
   ```

---

## ⚡ Problemas de Performance

### **Sintoma: "Slow API responses"**

**Diagnóstico:**
```bash
# Verificar response time
curl -w "@curl-format.txt" -o /dev/null -s \
     "https://api.proyecto-semilla.dev/v1/articles"

# curl-format.txt
# time_namelookup:  %{time_namelookup}\n
# time_connect: %{time_connect}\n
# time_appconnect: %{time_appconnect}\n
# time_pretransfer: %{time_pretransfer}\n
# time_redirect: %{time_redirect}\n
# time_starttransfer: %{time_starttransfer}\n
# ----------\n
# time_total: %{time_total}\n
```

**Soluciones:**

1. **Verificar índices de base de datos:**
   ```sql
   -- Verificar índices existentes
   SELECT indexname FROM pg_indexes WHERE tablename = 'articles';

   -- Crear índices faltantes
   CREATE INDEX CONCURRENTLY idx_articles_tenant_status
   ON articles (tenant_id, status);
   ```

2. **Verificar cache hit rates:**
   ```bash
   # Verificar Redis cache
   docker-compose exec redis redis-cli info stats
   ```

3. **Optimizar queries N+1:**
   ```python
   # ❌ Código problemático
   articles = await session.execute(
       select(Article).where(Article.tenant_id == tenant_id)
   )

   for article in articles:
       author = await session.execute(
           select(User).where(User.id == article.author_id)
       )

   # ✅ Código optimizado
   articles = await session.execute(
       select(Article, User)
       .join(User, Article.author_id == User.id)
       .where(Article.tenant_id == tenant_id)
   )
   ```

### **Sintoma: "High memory usage"**

**Diagnóstico:**
```bash
# Verificar uso de memoria del contenedor
docker stats proyecto_semilla_backend

# Verificar logs de aplicación
docker-compose logs backend | grep -i memory
```

**Soluciones:**

1. **Configurar límites de memoria:**
   ```yaml
   # docker-compose.yml
   backend:
     deploy:
       resources:
         limits:
           memory: 1G
         reservations:
           memory: 512M
   ```

2. **Optimizar configuración de Python:**
   ```python
   # Configuración Gunicorn
   workers = multiprocessing.cpu_count() * 2 + 1
   worker_class = "uvicorn.workers.UvicornWorker"
   worker_connections = 1000
   max_requests = 1000
   max_requests_jitter = 50
   ```

---

## 🛡️ Problemas de Rate Limiting

### **Sintoma: "Rate limit exceeded"**

**Diagnóstico:**
```bash
# Verificar headers de rate limiting
curl -I "https://api.proyecto-semilla.dev/v1/articles"

# Headers esperados:
# X-RateLimit-Limit: 100
# X-RateLimit-Remaining: 95
# X-RateLimit-Reset: 1630785600
```

**Soluciones:**

1. **Aumentar límites de rate limiting:**
   ```python
   # backend/app/core/rate_limiting.py
   DEFAULT_RATE_LIMITS = {
       "requests_per_minute": 200,
       "burst_limit": 300,
       "window_seconds": 60
   }
   ```

2. **Configurar límites por endpoint:**
   ```python
   @router.get("/articles")
   @limiter.limit("100/minute")
   async def get_articles():
       pass
   ```

3. **Implementar exponential backoff:**
   ```javascript
   // Frontend - exponential backoff
   async function apiCall(retryCount = 0) {
     try {
       return await fetch('/api/articles');
     } catch (error) {
       if (error.status === 429 && retryCount < 3) {
         const delay = Math.pow(2, retryCount) * 1000;
         await new Promise(resolve => setTimeout(resolve, delay));
         return apiCall(retryCount + 1);
       }
       throw error;
     }
   }
   ```

---

## 🐳 Problemas de Docker

### **Sintoma: "Container unhealthy"**

**Diagnóstico:**
```bash
# Verificar estado de contenedores
docker-compose ps

# Verificar logs del contenedor problemático
docker-compose logs backend

# Verificar health check
docker-compose exec backend curl -f http://localhost:8000/health
```

**Soluciones:**

1. **Reiniciar contenedor específico:**
   ```bash
   docker-compose restart backend
   ```

2. **Verificar health check endpoint:**
   ```python
   # backend/app/api/v1/endpoints/health.py
   @router.get("/health")
   async def health_check():
       return {
           "status": "healthy",
           "timestamp": datetime.utcnow(),
           "version": "0.5.0"
       }
   ```

3. **Verificar dependencias:**
   ```bash
   # Verificar que PostgreSQL esté listo
   docker-compose exec backend nc -zv db 5432

   # Verificar que Redis esté listo
   docker-compose exec backend nc -zv redis 6379
   ```

### **Sintoma: "Port already in use"**

**Diagnóstico:**
```bash
# Verificar qué proceso usa el puerto
lsof -i :8000

# En macOS
netstat -an | grep 8000
```

**Soluciones:**

1. **Liberar puerto:**
   ```bash
   # Matar proceso que usa el puerto
   kill -9 $(lsof -t -i:8000)

   # O cambiar puerto en docker-compose.yml
   ports:
     - "8001:8000"
   ```

2. **Verificar configuración de puertos:**
   ```yaml
   # docker-compose.yml
   backend:
     ports:
       - "8000:8000"
     environment:
       - PORT=8000
   ```

---

## 🌐 Problemas de Frontend

### **Sintoma: "API connection failed"**

**Diagnóstico:**
```bash
# Verificar conectividad con API
curl -f "http://localhost:8000/health"

# Verificar CORS headers
curl -I "http://localhost:8000/api/v1/articles"
```

**Soluciones:**

1. **Configurar CORS correctamente:**
   ```python
   # backend/app/main.py
   from fastapi.middleware.cors import CORSMiddleware

   app.add_middleware(
       CORSMiddleware,
       allow_origins=["http://localhost:3000"],
       allow_credentials=True,
       allow_methods=["*"],
       allow_headers=["*"],
   )
   ```

2. **Verificar API URL en frontend:**
   ```typescript
   // frontend/src/lib/api-client.ts
   const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';
   ```

3. **Verificar proxy configuration:**
   ```json
   // frontend/package.json
   {
     "proxy": "http://localhost:8000"
   }
   ```

### **Sintoma: "Build failed"**

**Diagnóstico:**
```bash
# Verificar logs de build
npm run build

# Verificar dependencias
npm ls --depth=0
```

**Soluciones:**

1. **Limpiar cache de build:**
   ```bash
   rm -rf .next
   npm run build
   ```

2. **Actualizar dependencias:**
   ```bash
   npm update
   npm audit fix
   ```

3. **Verificar TypeScript errors:**
   ```bash
   npx tsc --noEmit
   ```

---

## 🔒 Problemas de Seguridad

### **Sintoma: "Security audit failed"**

**Diagnóstico:**
```bash
# Ejecutar security audit
docker-compose exec backend python -m pip-audit

# Verificar dependencias vulnerables
npm audit
```

**Soluciones:**

1. **Actualizar dependencias vulnerables:**
   ```bash
   # Python
   pip install --upgrade -r requirements.txt

   # Node.js
   npm update
   npm audit fix
   ```

2. **Configurar security headers:**
   ```python
   # backend/app/middleware/security.py
   from fastapi.middleware.httpsredirect import HTTPSRedirectMiddleware
   from fastapi.middleware.trustedhost import TrustedHostMiddleware

   app.add_middleware(HTTPSRedirectMiddleware)
   app.add_middleware(TrustedHostMiddleware, allowed_hosts=["*.proyecto-semilla.dev"])
   ```

### **Sintoma: "Threat detected"**

**Diagnóstico:**
```bash
# Verificar logs de amenazas
docker-compose logs backend | grep -i threat

# Verificar configuración de WAF
docker-compose exec backend cat /etc/nginx/conf.d/waf.conf
```

**Soluciones:**

1. **Configurar reglas de WAF:**
   ```nginx
   # nginx.conf
   location / {
       modsecurity on;
       modsecurity_rules_file /etc/nginx/modsec/main.conf;
   }
   ```

2. **Implementar rate limiting avanzado:**
   ```python
   # backend/app/core/rate_limiting.py
   @limiter.limit("10/minute", key_func=get_remote_address)
   async def login(request: Request, credentials: LoginRequest):
       pass
   ```

---

## 📋 Checklist de Verificación

### **Pre-Deployment Checklist**

- [ ] **Base de Datos:**
  - [ ] Todas las migraciones aplicadas
  - [ ] Índices de performance creados
  - [ ] Datos de seed ejecutados
  - [ ] Conexiones de pool configuradas

- [ ] **Backend:**
  - [ ] Health check endpoint funcionando
  - [ ] Variables de entorno configuradas
  - [ ] Logs configurados correctamente
  - [ ] Rate limiting activo

- [ ] **Frontend:**
  - [ ] Build exitoso sin errores
  - [ ] API client configurado correctamente
  - [ ] Environment variables configuradas
  - [ ] PWA features funcionando

- [ ] **Seguridad:**
  - [ ] HTTPS configurado
  - [ ] CORS configurado correctamente
  - [ ] Security headers activos
  - [ ] Audit logging habilitado

- [ ] **Performance:**
  - [ ] Response times <100ms P95
  - [ ] Memory usage <80%
  - [ ] Cache hit rate >90%
  - [ ] Database connections optimizadas

### **Post-Deployment Verification**

```bash
# Health check completo
curl -f https://api.proyecto-semilla.dev/health

# API endpoints principales
curl -f https://api.proyecto-semilla.dev/api/v1/articles

# Frontend loading
curl -f https://proyecto-semilla.dev

# Performance test
ab -n 1000 -c 10 https://api.proyecto-semilla.dev/api/v1/articles
```

---

## 📞 Contacto y Soporte

### **Canales de Soporte**
- **📧 Email:** support@proyecto-semilla.dev
- **💬 Discord:** [discord.gg/proyecto-semilla](https://discord.gg/proyecto-semilla)
- **🐛 Issues:** [GitHub Issues](../../issues)
- **📚 Documentación:** [docs.proyecto-semilla.dev](https://docs.proyecto-semilla.dev)

### **Información para Reportes de Bug**
```markdown
**Bug Report Template:**

**Environment:**
- OS: [e.g., macOS 12.0]
- Browser: [e.g., Chrome 95]
- API Version: [e.g., 0.5.0]

**Steps to reproduce:**
1. Go to '...'
2. Click on '...'
3. See error

**Expected behavior:**
[Describe what you expected to happen]

**Actual behavior:**
[Describe what actually happened]

**Error logs:**
```
[Error logs here]
```

**Additional context:**
[Add any other context about the problem]
```

---

*"Esta guía de troubleshooting se actualiza automáticamente con cada fix implementado. Última actualización: 5 de septiembre de 2025"*

🇨🇴 **Proyecto Semilla** - Troubleshooting Guide v0.5.0