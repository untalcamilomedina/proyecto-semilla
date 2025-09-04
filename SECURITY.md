# 🔐 Política de Seguridad - Proyecto Semilla

[![English](https://img.shields.io/badge/Language-English-blue.svg)](#english-version)
[![Español](https://img.shields.io/badge/Idioma-Español-green.svg)](#versión-en-español)

---

## 🇪🇸 Versión en Español

### 📋 Tabla de Contenidos

1. [Versiones Soportadas](#-versiones-soportadas)
2. [Reportar Vulnerabilidades](#-reportar-vulnerabilidades)
3. [Principios de Seguridad](#-principios-de-seguridad)
4. [Proceso de Respuesta](#-proceso-de-respuesta)
5. [Mejores Prácticas](#-mejores-prácticas)
6. [Reconocimientos](#-reconocimientos)

### 🛡️ Versiones Soportadas

Actualmente, **Proyecto Semilla** da soporte de seguridad a las siguientes versiones:

| Versión | Soporte de Seguridad | Estado |
| ------- | -------------------- | ------ |
| 0.9.x   | ✅ Completo          | Desarrollo futuro |
| 0.8.x   | ✅ Completo          | Desarrollo futuro |
| 0.7.x   | ✅ Completo          | Desarrollo futuro |
| 0.6.x   | ✅ Completo          | Desarrollo futuro |
| 0.5.x   | ✅ Completo          | Desarrollo futuro |
| 0.4.x   | ✅ Completo          | Desarrollo futuro |
| 0.3.x   | ✅ Completo          | Desarrollo futuro |
| 0.2.x   | ✅ Completo          | Desarrollo futuro |
| 0.1.x   | ✅ Completo          | Desarrollo actual |
| < 0.1   | ❌ Sin soporte       | Pre-release |

**Nota**: Como estamos en desarrollo activo, todas las versiones de desarrollo reciben parches de seguridad. Una vez que el proyecto alcance la estabilidad (v1.0.0), adoptaremos un modelo de soporte más tradicional.

### 🚨 Reportar Vulnerabilidades

La seguridad de **Proyecto Semilla** es nuestra máxima prioridad. Si descubres una vulnerabilidad de seguridad, te pedimos que sigas el proceso de divulgación responsable.

#### 📧 Canal Seguro de Reporte

**Por favor, NO reportes vulnerabilidades de seguridad a través de issues públicos de GitHub.**

En su lugar, envía un email a:
- **Email Principal**: security@proyecto-semilla.com
- **Email Alternativo**: admin@proyecto-semilla.com

#### 📝 Información a Incluir

Para ayudarnos a evaluar y corregir el problema rápidamente, por favor incluye tanto detalle como sea posible:

```markdown
**Descripción de la Vulnerabilidad**
- Tipo de problema (ej. buffer overflow, SQL injection, cross-site scripting, etc.)
- Ubicación completa de la ruta del código fuente relacionado con la manifestación del problema
- Cualquier configuración especial requerida para reproducir el problema
- Instrucciones paso a paso para reproducir el problema
- Prueba de concepto o código de explotación (si es posible)
- Impacto potencial del problema, incluyendo cómo un atacante podría explotar el problema

**Información del Sistema**
- Versión de Proyecto Semilla
- Sistema operativo
- Versión de Docker/Docker Compose
- Versión de PostgreSQL
- Navegador web (si aplica)

**Clasificación de Severidad (según tu criterio)**
- Crítica: Acceso completo al sistema
- Alta: Acceso a datos sensibles
- Media: Funcionalidad comprometida  
- Baja: Problemas menores de seguridad
```

### ⏱️ Proceso de Respuesta

#### Cronograma de Respuesta

| Tiempo | Acción |
|--------|---------|
| **24 horas** | Confirmación de recepción del reporte |
| **72 horas** | Evaluación inicial y clasificación de severidad |
| **7 días** | Plan de remediación y cronograma de parche |
| **30 días** | Publicación del parche (para vulnerabilidades no críticas) |
| **Inmediato** | Parche de emergencia (para vulnerabilidades críticas) |

#### 🔍 Proceso de Evaluación

1. **Triaje Inicial**
   - Confirmación de la vulnerabilidad
   - Clasificación de severidad usando CVSS 3.1
   - Asignación a investigador de seguridad

2. **Investigación Detallada**
   - Análisis del impacto
   - Identificación de sistemas afectados
   - Desarrollo de parche

3. **Testing y Verificación**
   - Pruebas del parche en entornos de desarrollo
   - Verificación de que la vulnerabilidad ha sido cerrada
   - Pruebas de regresión

4. **Despliegue**
   - Despliegue del parche
   - Notificación a usuarios afectados
   - Publicación del advisory de seguridad

### 🛡️ Principios de Seguridad

**Proyecto Semilla** está construido con seguridad como principio fundamental:

#### 🏗️ Seguridad por Diseño

- **Row-Level Security (RLS)**: Aislamiento completo entre tenants a nivel de base de datos
- **Principio de Menor Privilegio**: Usuarios y procesos tienen solo los permisos mínimos necesarios
- **Defensa en Profundidad**: Múltiples capas de seguridad
- **Fail-Safe Defaults**: Configuraciones seguras por defecto

#### 🔐 Autenticación y Autorización

```python
# Ejemplo de implementación segura
@require_permissions(["users:read"])
@rate_limit(requests=100, window=60)  # Rate limiting
async def get_users(
    current_user: User = Depends(get_current_active_user),
    tenant_context: TenantContext = Depends(get_tenant_context)
):
    # RLS automáticamente aplicado
    return await user_service.get_users(tenant_context.tenant_id)
```

#### 🛢️ Seguridad de Base de Datos

- **Conexiones Encriptadas**: TLS obligatorio para conexiones de base de datos
- **Credenciales Seguras**: Uso de variables de entorno y secretos
- **Backup Encriptado**: Respaldos cifrados con llaves rotatorias
- **Auditoría**: Logging completo de accesos y cambios

#### 🌐 Seguridad Web

- **HTTPS Obligatorio**: Redirección automática a HTTPS en producción
- **Cabeceras de Seguridad**: CSP, HSTS, X-Frame-Options, etc.
- **Validación de Input**: Sanitización y validación en frontend y backend
- **Protección CSRF**: Tokens CSRF en todas las formas

### 📋 Mejores Prácticas para Desarrolladores

#### 🔍 Code Review de Seguridad

Cada PR debe pasar por una revisión de seguridad que incluya:

- ✅ **Validación de Input**: ¿Se validan y sanitizan todos los inputs?
- ✅ **Autorización**: ¿Se verifican permisos antes de cada operación?
- ✅ **Logging**: ¿Se registran eventos de seguridad apropiadamente?
- ✅ **Secretos**: ¿No hay credenciales hardcodeadas?
- ✅ **SQL Injection**: ¿Se usan queries parametrizadas?
- ✅ **XSS**: ¿Se escapa output apropiadamente?

#### 🧪 Testing de Seguridad

```python
# Ejemplo de test de seguridad
async def test_unauthorized_access():
    """Test que usuarios sin permisos no pueden acceder a recursos."""
    client = TestClient(app)
    
    # Intentar acceso sin autenticación
    response = client.get("/api/users/")
    assert response.status_code == 401
    
    # Intentar acceso con usuario de otro tenant
    response = client.get("/api/users/", headers=unauthorized_headers)
    assert response.status_code == 403
```

#### 🔧 Configuración Segura

```yaml
# docker-compose.yml - Configuración de producción
services:
  db:
    environment:
      POSTGRES_PASSWORD_FILE: /run/secrets/db_password
    secrets:
      - db_password
    # Sin puertos expuestos externamente
    
  backend:
    environment:
      DATABASE_URL_FILE: /run/secrets/database_url
      JWT_SECRET_FILE: /run/secrets/jwt_secret
    secrets:
      - database_url
      - jwt_secret

secrets:
  db_password:
    external: true
  database_url:
    external: true
  jwt_secret:
    external: true
```

### 🏆 Programa de Reconocimientos

#### 🎖️ Hall of Fame

Reconocemos públicamente a los investigadores de seguridad que reportan vulnerabilidades de manera responsable:

<!-- Esta sección se actualizará automáticamente -->
- 🥇 **[Nombre]** - Vulnerabilidad crítica en autenticación (2024)
- 🥈 **[Nombre]** - SQL injection en API de usuarios (2024)
- 🥉 **[Nombre]** - XSS en panel de administración (2024)

#### 💝 Recompensas

Aunque somos un proyecto open-source sin fines de lucro, ofrecemos las siguientes recompensas:

- **🏆 Reconocimiento Público**: En README, redes sociales y conferencias
- **🎁 Swag Exclusivo**: Camisetas, stickers y merchandise del proyecto
- **💼 Referencias**: Referencias laborales para oportunidades de trabajo
- **🎤 Conferencias**: Invitaciones a hablar en eventos sobre tu descubrimiento

---

## 🇺🇸 English Version

### 📋 Table of Contents

1. [Supported Versions](#-supported-versions-en)
2. [Reporting Vulnerabilities](#-reporting-vulnerabilities-en)
3. [Security Principles](#-security-principles-en)
4. [Response Process](#-response-process-en)
5. [Best Practices](#-best-practices-en)
6. [Acknowledgments](#-acknowledgments-en)

### 🛡️ Supported Versions {#supported-versions-en}

Currently, **Proyecto Semilla** provides security support for the following versions:

| Version | Security Support | Status |
| ------- | ---------------- | ------ |
| 0.9.x   | ✅ Full          | Future development |
| 0.8.x   | ✅ Full          | Future development |
| 0.7.x   | ✅ Full          | Future development |
| 0.6.x   | ✅ Full          | Future development |
| 0.5.x   | ✅ Full          | Future development |
| 0.4.x   | ✅ Full          | Future development |
| 0.3.x   | ✅ Full          | Future development |
| 0.2.x   | ✅ Full          | Future development |
| 0.1.x   | ✅ Full          | Current development |
| < 0.1   | ❌ No support    | Pre-release |

**Note**: As we are in active development, all development versions receive security patches. Once the project reaches stability (v1.0.0), we will adopt a more traditional support model.

### 🚨 Reporting Vulnerabilities {#reporting-vulnerabilities-en}

The security of **Proyecto Semilla** is our top priority. If you discover a security vulnerability, we ask that you follow the responsible disclosure process.

#### 📧 Secure Reporting Channel

**Please do NOT report security vulnerabilities through public GitHub issues.**

Instead, send an email to:
- **Main Email**: security@proyecto-semilla.com
- **Alternative Email**: admin@proyecto-semilla.com

#### 📝 Information to Include

To help us assess and fix the issue quickly, please include as much detail as possible:

```markdown
**Vulnerability Description**
- Type of issue (e.g. buffer overflow, SQL injection, cross-site scripting, etc.)
- Full path location of source code related to the manifestation of the issue
- Any special configuration required to reproduce the issue
- Step-by-step instructions to reproduce the issue
- Proof-of-concept or exploit code (if possible)
- Impact of the issue, including how an attacker might exploit the issue

**System Information**
- Proyecto Semilla version
- Operating system
- Docker/Docker Compose version
- PostgreSQL version
- Web browser (if applicable)

**Severity Classification (your assessment)**
- Critical: Complete system access
- High: Access to sensitive data
- Medium: Compromised functionality
- Low: Minor security issues
```

### ⏱️ Response Process {#response-process-en}

#### Response Timeline

| Time | Action |
|------|--------|
| **24 hours** | Acknowledgment of report receipt |
| **72 hours** | Initial assessment and severity classification |
| **7 days** | Remediation plan and patch timeline |
| **30 days** | Patch release (for non-critical vulnerabilities) |
| **Immediate** | Emergency patch (for critical vulnerabilities) |

### 🛡️ Security Principles {#security-principles-en}

**Proyecto Semilla** is built with security as a fundamental principle:

#### 🏗️ Security by Design

- **Row-Level Security (RLS)**: Complete tenant isolation at database level
- **Principle of Least Privilege**: Users and processes have only minimum necessary permissions
- **Defense in Depth**: Multiple security layers
- **Fail-Safe Defaults**: Secure configurations by default

#### 🔐 Authentication and Authorization

```python
# Example of secure implementation
@require_permissions(["users:read"])
@rate_limit(requests=100, window=60)  # Rate limiting
async def get_users(
    current_user: User = Depends(get_current_active_user),
    tenant_context: TenantContext = Depends(get_tenant_context)
):
    # RLS automatically applied
    return await user_service.get_users(tenant_context.tenant_id)
```

### 🏆 Recognition Program {#acknowledgments-en}

#### 🎖️ Hall of Fame

We publicly recognize security researchers who report vulnerabilities responsibly:

<!-- This section will be updated automatically -->
- 🥇 **[Name]** - Critical authentication vulnerability (2024)
- 🥈 **[Name]** - SQL injection in users API (2024)
- 🥉 **[Name]** - XSS in admin panel (2024)

---

## 🔒 Configuración de Seguridad por Defecto

### 📋 Checklist de Seguridad

Para garantizar que tu instalación de **Proyecto Semilla** sea segura:

#### ✅ Configuración Inicial
- [ ] Cambiar credenciales por defecto
- [ ] Configurar HTTPS con certificados válidos
- [ ] Habilitar firewall y cerrar puertos innecesarios
- [ ] Configurar backup automático encriptado
- [ ] Habilitar logging de auditoría

#### ✅ Base de Datos
- [ ] Usar contraseñas fuertes para PostgreSQL
- [ ] Habilitar SSL/TLS para conexiones
- [ ] Configurar Row-Level Security (RLS)
- [ ] Implementar rotación de credenciales
- [ ] Limitar conexiones concurrentes

#### ✅ Aplicación
- [ ] Configurar JWT secrets aleatorios y seguros
- [ ] Habilitar rate limiting
- [ ] Configurar CORS apropiadamente
- [ ] Implementar Content Security Policy (CSP)
- [ ] Configurar cabeceras de seguridad

#### ✅ Infraestructura
- [ ] Mantener Docker y dependencias actualizadas
- [ ] Configurar monitoreo de seguridad
- [ ] Implementar alertas de seguridad
- [ ] Configurar respaldos regulares
- [ ] Documentar procedimientos de respuesta a incidentes

### 🚨 Alertas de Seguridad

Para recibir notificaciones de vulnerabilidades de seguridad:

1. **GitHub**: Habilitar alertas de seguridad en el repositorio
2. **Email**: Suscribirse a security-announcements@proyecto-semilla.com
3. **RSS**: Seguir nuestro feed de seguridad
4. **Discord**: Canal #security-announcements

---

## 📞 Contacto de Seguridad

### 👥 Equipo de Seguridad

- **Security Lead**: security-lead@proyecto-semilla.com
- **Incident Response**: incident-response@proyecto-semilla.com
- **General Security**: security@proyecto-semilla.com

### ⏰ Disponibilidad

- **Horario Normal**: Lunes a Viernes, 9:00 AM - 6:00 PM (GMT-5)
- **Emergencias Críticas**: 24/7 (respuesta en < 4 horas)
- **Reportes de Vulnerabilidad**: 24/7 (confirmación en < 24 horas)

---

*Última actualización: Septiembre 2024*  
*Last updated: September 2024*

*Este documento se actualiza regularmente. Para la versión más reciente, visita: https://github.com/proyecto-semilla/proyecto-semilla/blob/main/SECURITY.md*