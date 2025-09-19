# Documentación del Flujo de Configuración Inicial

## Resumen Ejecutivo

Este documento describe el flujo completo de configuración inicial del sistema Proyecto Semilla, incluyendo la creación automática de usuarios hardcodeados, procesos de instalación y puntos críticos que requieren atención.

## Arquitectura del Flujo de Configuración

### Componentes Principales

1. **Scripts de Instalación**
   - `scripts/install.py` - Instalador interactivo principal
   - `scripts/setup.sh` - Setup simplificado
   - `scripts/verify_installation.py` - Verificación post-instalación

2. **Scripts de Datos Iniciales**
   - `backend/app/initial_data.py` - Creación de datos básicos
   - `backend/scripts/seed_data.py` - Creación de datos de desarrollo/demostración

3. **Configuración de Entorno**
   - Variables de entorno (`.env`)
   - Docker Compose para servicios
   - Migraciones de base de datos

## Flujo de Configuración Detallado

### Fase 1: Verificación de Prerrequisitos

```bash
# Verificación automática en install.py
- Docker y Docker Compose instalados
- Dependencias Python (alembic, etc.)
- Permisos adecuados para archivos
```

**Punto Crítico**: Si Docker no está corriendo, la instalación falla inmediatamente.

### Fase 2: Configuración de Variables de Entorno

#### Archivo `.env` Principal
```bash
# Generado por scripts/install.py o setup.sh
DB_PASSWORD=changeme123
DB_HOST=db
DB_PORT=5432
DB_NAME=proyecto_semilla
JWT_SECRET=<auto-generado>
CORS_ORIGINS=http://localhost:7701,http://localhost:7777
DEBUG=true
NEXT_PUBLIC_API_URL=http://localhost:7777
LOG_LEVEL=INFO
```

#### Archivo `frontend/.env.local`
```bash
# Generado por setup.sh
NEXT_PUBLIC_API_URL=http://localhost:7777
NEXT_PUBLIC_DEMO_EMAIL=admin@example.com
NEXT_PUBLIC_DEMO_PASSWORD=admin123
NEXT_PUBLIC_DEFAULT_TENANT_ID=00000000-0000-0000-0000-000000000001
```

**Punto Crítico**: Las credenciales hardcodeadas se exponen en variables de entorno del frontend.

### Fase 3: Configuración de Base de Datos

#### Servicios Docker
```bash
# Levantados automáticamente
- PostgreSQL (db)
- Redis (redis)
```

#### Migraciones de Base de Datos
```bash
# Ejecutadas via Docker
docker-compose exec backend alembic upgrade head
```

**Punto Crítico**: Las migraciones deben ejecutarse correctamente antes de crear usuarios.

### Fase 4: Creación de Usuarios Hardcodeados

#### Usuario 1: admin@example.com (initial_data.py)
```python
# backend/app/initial_data.py
admin_user = User(
    id='00000000-0000-0000-0000-000000000002',
    tenant_id=default_tenant.id,
    email='admin@example.com',
    hashed_password=get_password_hash('admin123'),  # ⚠️ HARDCODEADO
    first_name='Admin',
    last_name='User',
    full_name='Admin User',
    is_active=True,
    is_verified=True
)
```

#### Usuario 2: admin@proyectosemilla.dev (seed_data.py)
```python
# backend/scripts/seed_data.py
admin_password = os.getenv("SEED_ADMIN_PASSWORD", "ChangeMeSecure123!")
user = User(
    tenant_id=tenant.id,
    email="admin@proyectosemilla.dev",
    hashed_password=get_password_hash(admin_password),
    # ... otros campos
)
```

#### Usuario 3: demo@demo-company.com (seed_data.py)
```python
# backend/scripts/seed_data.py
demo_password = os.getenv("SEED_DEMO_PASSWORD", "demo123")
user = User(
    tenant_id=tenant.id,
    email="demo@demo-company.com",
    hashed_password=get_password_hash(demo_password),
    # ... otros campos
)
```

**Punto Crítico**: Tres usuarios diferentes creados por diferentes scripts con diferentes propósitos.

### Fase 5: Verificación de Estado del Sistema

#### Endpoint `/api/v1/auth/setup-status`
```python
# backend/app/api/v1/endpoints/auth.py
@router.get("/setup-status")
async def get_setup_status(db: AsyncSession = Depends(get_db)):
    # ⚠️ EXCLUSIÓN HARDCODEADA
    hardcoded_emails = ["admin@proyectosemilla.dev", "demo@demo-company.com", "admin@example.com"]

    user_count_result = await db.execute(
        select(func.count(User.id)).where(User.email.not_in(hardcoded_emails))
    )
    real_user_count = user_count_result.scalar()

    return {
        "needs_setup": real_user_count == 0,
        "real_user_count": real_user_count,
        "total_user_count": total_user_count,
        "message": "System needs initial setup" if real_user_count == 0 else "System is already configured"
    }
```

**Punto Crítico**: La lógica de setup-status depende de excluir usuarios hardcodeados.

## Secuencia de Ejecución Típica

### Instalación Automática (install.py)
1. ✅ Verificar prerrequisitos
2. ✅ Configurar variables de entorno
3. ✅ Crear archivo `.env`
4. ✅ Levantar servicios Docker (DB + Redis)
5. ✅ Ejecutar migraciones de BD
6. ✅ Crear usuarios hardcodeados (initial_data.py)
7. ✅ Verificar instalación
8. ✅ Mostrar credenciales finales

### Instalación Simplificada (setup.sh)
1. ✅ Verificar Docker corriendo
2. ✅ Crear `.env` básico
3. ✅ Crear `frontend/.env.local` (con credenciales hardcodeadas)
4. ✅ Levantar DB + Redis
5. ✅ Ejecutar migraciones
6. ✅ Instrucciones para usuario

### Desarrollo con Seed Data
```bash
# Ejecución manual opcional
python backend/scripts/seed_data.py
```
Crea usuarios adicionales de desarrollo y roles.

## Estados del Sistema

### Estado 1: Sistema Sin Configurar
- `real_user_count == 0`
- `needs_setup == true`
- Frontend muestra formulario de registro inicial
- Usuario puede crear cuenta de superadmin

### Estado 2: Sistema Configurado
- `real_user_count > 0`
- `needs_setup == false`
- Sistema operativo normal
- Usuarios hardcodeados existen pero no cuentan como "reales"

## Puntos de Riesgo Identificados

### 1. Exposición de Credenciales
- **Ubicación**: `frontend/.env.local`
- **Riesgo**: Credenciales visibles en navegador (NEXT_PUBLIC_*)
- **Impacto**: Ataque de diccionario, acceso no autorizado

### 2. Dependencias Múltiples
- **Problema**: Tres scripts diferentes crean usuarios hardcodeados
- **Riesgo**: Inconsistencias, duplicados, conflictos
- **Impacto**: Comportamiento impredecible del sistema

### 3. Lógica de Exclusión Frágil
- **Ubicación**: `get_setup_status()`
- **Riesgo**: Lista hardcodeada de emails
- **Impacto**: Bypass potencial de validaciones

### 4. Contraseñas por Defecto Inseguras
- **Problema**: Valores por defecto débiles
- **Riesgo**: Ataques de fuerza bruta exitosos
- **Impacto**: Compromiso de cuenta administrativa

## Recomendaciones de Mejora

### Inmediatas
1. **Eliminar Variables NEXT_PUBLIC con Credenciales**
2. **Implementar Variables de Entorno Obligatorias**
3. **Mejorar Generación de Contraseñas Seguras**
4. **Unificar Creación de Usuarios Hardcodeados**

### Mediano Plazo
5. **Implementar Sistema de Usuarios del Sistema**
6. **Crear Setup Interactivo Seguro**
7. **Agregar Validaciones de Seguridad**
8. **Implementar Auditoría de Creación**

### Largo Plazo
9. **Migración Completa a Usuarios Dinámicos**
10. **Eliminar Dependencias Hardcodeadas**

## Checklist de Verificación

### Pre-Instalación
- [ ] Docker y Docker Compose instalados
- [ ] Puertos 5432, 6379, 7777, 7701, 8001 disponibles
- [ ] Permisos de escritura en directorio del proyecto

### Durante Instalación
- [ ] Variables de entorno configuradas correctamente
- [ ] Servicios Docker levantados exitosamente
- [ ] Migraciones de BD ejecutadas sin errores
- [ ] Usuarios hardcodeados creados correctamente

### Post-Instalación
- [ ] Endpoint `/api/v1/auth/setup-status` retorna estado correcto
- [ ] Frontend accesible en puerto correcto
- [ ] Login funciona con credenciales hardcodeadas
- [ ] No hay errores en logs de servicios

## Conclusión

El flujo de configuración inicial es complejo y tiene múltiples puntos de riesgo relacionados con usuarios hardcodeados. Se requiere una refactorización significativa para mejorar la seguridad y mantenibilidad del sistema.