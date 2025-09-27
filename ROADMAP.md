# 🗺️ Roadmap - Proyecto Semilla

**Documento Público para la Comunidad**  
**Versión**: 1.0  
**Fecha**: Septiembre 2024  

---

## 🎯 Visión General

Desarrollar **Proyecto Semilla**, la primera plataforma SaaS Vibecoding-native del mundo, pionera en permitir que LLMs construyan aplicaciones enterprise siguiendo mejores prácticas y arquitecturas auto-documentadas.

---

## 📌 Estado Actual del MVP (Auditoría Septiembre 2025)

**Resumen**
- Backend FastAPI operativo para autenticación y CRUD básicos de usuarios/tenants, pero numerosos contratos REST aún no existen o devuelven datos incompletos.
- Frontend Next.js presenta UI para dashboard, usuarios, tenants y roles; varias vistas consumen endpoints inexistentes (`/dashboard/*`, artículos, categorías) o con payload distinto al que espera el backend.
- Suite de testing Pytest parcialmente configurada; fixtures dependen de settings ausentes y el entorno de pruebas no crea la base de datos, por lo que las ejecuciones fallan.
- Contenedor Docker-compose funcional en teoría, pero requiere `.env` con `DB_PASSWORD` y `JWT_SECRET`; no hay plantilla ni validación clara para entornos locales.

**Qué funciona hoy**
- Autenticación JWT con cookies HTTP-only (`/api/v1/auth/login|logout|me`).
- CRUD base de usuarios y tenants mediante SQLAlchemy y FastAPI (`/api/v1/users`, `/api/v1/tenants`).
- Middleware multi-tenant y capa de seguridad (rate limiting básico, logging estructurado).
- UI de login y panel administrativo con Zustand para estado de sesión.

**Gaps detectados**
- Endpoints `dashboard/*`, artículos, categorías, roles avanzados y módulo MCP declarados en el cliente sin implementación en el backend.
- Desfase de esquemas: frontend espera campos `domain/logo` en tenants y `full_name/password` en usuarios, mientras el backend requiere `description/settings`, `first_name/last_name/tenant_id`.
- Cambio de tenant (`switchTenant`) mapea a rutas distintas entre frontend/backend.
- Tests: faltan valores `TEST_USER_*`, login de fixtures usa JSON en lugar de formulario y no se crean tablas en SQLite.
- Documentación y scripts no explican variables obligatorias ni flujo de arranque.

---

## 🗂️ Plan de Sprints para estabilizar el MVP

### 🔍 Sprint 0 – Auditoría y alineación (completo)
- Inventario de endpoints reales vs. consumidos por el frontend.
- Identificación de discrepancias en esquemas y variables de entorno.
- Validación del estado de la suite de tests y dependencias Docker.

### 🛠️ Sprint 1 – Contratos Backend ⇔ Frontend (Objetivo: 1 semana)
- [x] Implementar endpoints mínimos que el dashboard necesita (`dashboard/metrics`, `dashboard/users-over-time`, `dashboard/recent-users`).
- [x] Ajustar schemas de tenants/usuarios y el frontend para homogenizar campos requeridos.
- [x] Unificar ruta de cambio de tenant (`/api/v1/tenants/switch/{id}`) y actualizar el cliente.
- [x] Añadir respuestas coherentes en CRUD de roles (UUIDs válidos, timestamps reales) y cubrir permisos JSON.

### 🧪 Sprint 2 – Entorno de pruebas y configuración (Objetivo: 1 semana)
- Introducir `.env.example` y documentación de variables críticas (`DB_PASSWORD`, `JWT_SECRET`, `TEST_USER_*`).
- Corregir fixtures Pytest: login vía formulario, creación de tablas SQLite, inclusión de la app en `PYTHONPATH`.
- Ejecutar smoke tests locales y documentar resultados.

### 🧩 Sprint 3 – Funcionalidades faltantes del dashboard (Objetivo: 1-2 semanas)
- Deliverable: métricas reales y tablas operativas en frontend.
- Implementar servicios de artículos/categorías **o** depurar la UI para que refleje solo lo disponible.
- Revisar flujos de roles/permissions y exponer endpoints de asignación que el cliente ya invoca.

### 📦 Sprint 4 – Preparación Docker y QA (Objetivo: 1 semana)
- Validar `docker-compose` end-to-end con las nuevas variables y seeds.
- Añadir chequeos automatizados (scripts) para health de backend/frontend.
- Documentar pasos de despliegue y criterios de aceptación para prueba final.

> Nota: No se montarán entornos de test aislados hasta completar los sprints 1-3; cada sprint incluirá validaciones manuales y documentación incremental. En cuanto concluya Sprint 4 se habilitará el stack Docker para que lo puedas probar.

### Principios Vibecoding-Native
- **🤖 LLM-First Architecture**: Diseñado para que los AIs entiendan y extiendan el sistema
- **📚 Machine-Readable Documentation**: Docs que leen humanos y LLMs por igual
- **🔒 AI-Verifiable Security**: Mejores prácticas que los LLMs pueden validar automáticamente
- **🧩 Self-Documenting Code**: Cada módulo se explica a sí mismo para facilitar Vibecoding
- **🔧 Self-Maintenance System**: El sistema se mantiene automáticamente con Vibecoding
- **🔮 Predictive Intelligence**: IA que predice y previene problemas antes de que ocurran

---

## 📚 Stack Tecnológico

```yaml
Backend:
  - Framework: FastAPI (Python 3.11+)
  - Base de Datos: PostgreSQL 15+
  - Seguridad: Row-Level Security (RLS)
  - ORM: SQLAlchemy 2.0+
  - Cache: Redis
  - Testing: Pytest

Frontend:
  - Framework: Next.js 14+ (App Router)
  - Lenguaje: TypeScript
  - Estilos: Tailwind CSS
  - Componentes: shadcn/ui
  - Internacionalización: next-intl

DevOps:
  - Containerización: Docker + Docker Compose
  - CI/CD: GitHub Actions
  - Documentación: Markdown + GitHub Pages
```

---

## 🚀 Fases de Desarrollo

## **FASE 1: LA FUNDACIÓN** 🏗️
**Versiones**: v0.1.0 - v0.3.0  
**Duración Estimada**: 3-4 meses  
**Objetivo**: Establecer la base sólida del sistema multi-tenant

### v0.1.0 - "Genesis" 🌱
**Estado**: ✅ **COMPLETADO**

**Características Implementadas**:
- ✅ Instalador interactivo (CLI)
- ✅ Contenerización completa con Docker
- ✅ Estructura de base de datos con RLS
- ✅ Autenticación JWT + Refresh Tokens
- ✅ CRUD básico de tenants y usuarios
- ✅ 15+ endpoints funcionales
- ✅ Documentación OpenAPI/Swagger

### v0.2.0 - "Vibecoding Core" 🤖 ⭐ **NUEVA PRIORIDAD**
**Estado**: 🚀 **INICIANDO DESARROLLO**

**Objetivo**: Integración nativa con LLMs y Model Context Protocol

**Características Planificadas**:
- **MCP Protocol Integration**: Comunicación directa con Claude, GPT, y otros LLMs
- **SDK para LLMs**: Herramientas para que AIs construyan módulos siguiendo patrones
- **AI Documentation System**: Documentación que se actualiza automáticamente
- **Code Understanding Engine**: LLMs pueden entender la arquitectura completa

### v0.3.0 - "AI-First Development" 🧠
**Estado**: 📅 **PLANIFICADO** (después de MCP Core)

**Objetivo**: Desarrollo asistido completamente por IA

**Características Planificadas**:
- **Module Generator**: "Claude, créame un sistema de facturación"
- **Auto-Testing with LLMs**: Tests generados y ejecutados por AI
- **AI-Driven Customization**: Personalización por comandos naturales
- **Smart Refactoring**: Mejoras automáticas de código via LLMs
- **Self-Maintenance System**: Sistema que se mantiene automáticamente con Vibecoding
- **Predictive Updates**: Actualizaciones inteligentes de dependencias y versiones
- **Auto-Healing Architecture**: Recuperación automática de fallos con IA

---

## **FASE 2: FLEXIBILIDAD Y PERSONALIZACIÓN** 🎨
**Versiones**: v0.4.0 - v0.6.0  
**Duración Estimada**: 3-4 meses  
**Objetivo**: Hacer el sistema adaptable a diferentes casos de uso

### v0.4.0 - "Customization" ⚙️
**Características Planificadas**:
- Gestor de atributos personalizados
- API para atributos dinámicos
- SDK Multi-lenguaje (JavaScript/TypeScript, PHP)

### v0.5.0 - "Localization" 🌍
**Características Planificadas**:
- Sistema de alias para entidades
- Internacionalización completa (ES/EN/PT)
- Traducciones contextuales

### v0.6.0 - "Branding & UX" 🎨
**Características Planificadas**:
- White Label System
- Personal Workspaces
- Smart Onboarding System
- Interface de usuario mejorada

### v0.6.5 - "Intelligent Maintenance" 🔧 ⭐ **NUEVA CARACTERÍSTICA**
**Estado**: 📅 **VISION FUTURE** (Q1 2026)

**Objetivo**: Sistema de mantenimiento completamente automatizado con Vibecoding

**Características Planificadas**:
- **Self-Healing Architecture**: Recuperación automática de fallos con IA
- **Predictive Maintenance**: Detección y solución de problemas antes de que ocurran
- **Auto-Update System**: Actualizaciones inteligentes de dependencias y versiones
- **Dependency Intelligence**: Monitoreo automático de vulnerabilidades y compatibilidad
- **Performance Self-Optimization**: Ajustes automáticos de performance con ML
- **AI-Driven Troubleshooting**: Diagnóstico y resolución automática de problemas

---

## **FASE 3: ECOSISTEMA Y ESCALABILIDAD** 🚀
**Versiones**: v0.7.0 - v0.9.0  
**Duración Estimada**: 4-5 meses  
**Objetivo**: Crear un ecosistema extensible y auto-sostenible

### v0.7.0 - "Modules" 🧩
**Características Planificadas**:
- Arquitectura de módulos/plugins
- Sistema de carga dinámica
- Marketplace preparation

### v0.8.0 - "Marketplace" 🏪
**Características Planificadas**:
- Marketplace de módulos
- SDK Ecosystem completo (Go, Ruby, etc.)
- Sistema de actualizaciones automáticas

### v0.9.0 - "Enterprise" 🏢
**Características Planificadas**:
- Características enterprise avanzadas
- Integraciones externas (Stripe, SendGrid, etc.)
- Analytics y métricas avanzadas

---

## 📊 Métricas de Éxito

### Technical Metrics
- **Code Coverage**: > 80%
- **API Response Time**: < 200ms (p95)
- **Build Success Rate**: > 95%

### Community Metrics
- **GitHub Stars**: > 1,000 (año 1)
- **Monthly Active Developers**: > 100
- **Community Contributions**: > 50 PRs
- **Spanish Content**: > 70% documentation coverage

---

## 🤝 Cómo Contribuir

### Para Desarrolladores
- 🔍 Busca issues etiquetados como "good-first-issue"
- 📚 Mejora la documentación
- 🌐 Ayuda con traducciones
- 🧪 Añade tests

### Para la Comunidad
- ⭐ Dale una estrella al repositorio
- 🐛 Reporta bugs con detalle
- 💡 Propón nuevas funcionalidades
- 📢 Comparte el proyecto

---

## 📞 Enlaces Importantes

- **Repositorio**: [github.com/untalcamilomedina/proyecto-semilla](https://github.com/untalcamilomedina/proyecto-semilla)
- **Issues**: [GitHub Issues](https://github.com/untalcamilomedina/proyecto-semilla/issues)
- **Discusiones**: [GitHub Discussions](https://github.com/untalcamilomedina/proyecto-semilla/discussions)
- **Documentación**: [README.md](./README.md)
- **Contribuir**: [CONTRIBUTING.md](./CONTRIBUTING.md)

---

*Este roadmap se actualiza continuamente basado en feedback de la comunidad y necesidades del proyecto.*

**¡Bienvenido a Proyecto Semilla! 🌱**
