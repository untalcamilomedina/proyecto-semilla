# Migración de Usuarios Hardcodeados - Guía Completa

## Resumen Ejecutivo

Esta guía documenta el proceso completo de migración de usuarios hardcodeados a un sistema de usuarios dinámicos y seguros en Proyecto Semilla. La migración elimina todas las credenciales hardcodeadas y las reemplaza con un sistema configurable y seguro.

## Usuarios Hardcodeados Identificados

### Antes de la Migración
- **admin@example.com** (contraseña: `admin123`) - Usuario administrador inicial
- **admin@proyectosemilla.dev** (contraseña configurable) - Super administrador
- **demo@demo-company.com** (contraseña configurable) - Usuario de demostración

### Archivos Afectados
- `backend/app/initial_data.py` - Creación inicial hardcodeada
- `backend/scripts/seed_data.py` - Seeding de datos hardcodeado
- `backend/app/api/v1/endpoints/auth.py` - Lógica de exclusión hardcodeada
- Múltiples archivos de configuración y documentación

## Arquitectura de la Solución

### Nuevo Sistema de Usuarios del Sistema

#### Tabla `system_user_flags`
```sql
CREATE TABLE system_user_flags (
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    flag_type VARCHAR(50) NOT NULL, -- 'admin', 'demo', 'system', 'legacy_hardcoded'
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    PRIMARY KEY (user_id, flag_type)
);
```

#### Servicio SystemUserService
- `mark_as_system_user()` - Marca usuarios como del sistema
- `is_system_user()` - Verifica si un usuario es del sistema
- `get_system_users_count()` - Cuenta usuarios del sistema
- `migrate_legacy_hardcoded_users()` - Migra usuarios existentes

## Variables de Entorno Requeridas

### Variables Obligatorias
```bash
# Sistema - Variables requeridas para usuarios iniciales
SEED_ADMIN_EMAIL=admin@tu-dominio.com
SEED_ADMIN_PASSWORD=Tu_Password_Seguro_123!
SEED_DEMO_EMAIL=demo@tu-dominio.com  # Opcional
SEED_DEMO_PASSWORD=Demo_Password_123!  # Opcional
```

### Variables Opcionales
```bash
SEED_ADMIN_FIRST_NAME=Super
SEED_ADMIN_LAST_NAME=Admin
SEED_DEMO_FIRST_NAME=Demo
SEED_DEMO_LAST_NAME=User
```

## Proceso de Migración

### Fase 1: Preparación

#### 1.1 Backup de Datos
```bash
# Crear backup antes de cualquier cambio
python scripts/migrate_hardcoded_users.py backup
```

#### 1.2 Configurar Variables de Entorno
```bash
# Crear archivo .env con credenciales seguras
cat > .env << EOF
# Sistema - Variables requeridas
SEED_ADMIN_EMAIL=admin@tu-dominio.com
SEED_ADMIN_PASSWORD=Tu_Password_Seguro_123!
SEED_DEMO_EMAIL=demo@tu-dominio.com
SEED_DEMO_PASSWORD=Demo_Password_123!

# Sistema - Variables opcionales
SEED_ADMIN_FIRST_NAME=Super
SEED_ADMIN_LAST_NAME=Admin

# Feature flag para migración
HARDCODED_USERS_MIGRATION_ENABLED=true
EOF
```

### Fase 2: Migración de Base de Datos

#### 2.1 Ejecutar Migración de Alembic
```bash
# Aplicar migración para tabla system_user_flags
docker-compose run --rm backend alembic upgrade head
```

#### 2.2 Migrar Usuarios Existentes
```bash
# Migrar usuarios hardcodeados existentes
python scripts/migrate_hardcoded_users.py migrate
```

#### 2.3 Verificar Migración
```bash
# Verificar estado de la migración
python scripts/migrate_hardcoded_users.py status
```

### Fase 3: Seeding Seguro

#### 3.1 Ejecutar Seeding Seguro
```bash
# Crear usuarios del sistema de forma segura
python scripts/seed_secure_system_users.py
```

#### 3.2 Verificar Usuarios Creados
```bash
# Verificar que los usuarios del sistema existen
python scripts/migrate_hardcoded_users.py status
```

### Fase 4: Validación y Limpieza

#### 4.1 Ejecutar Validación de Seguridad
```bash
# Validar que no quedan credenciales hardcodeadas
python scripts/validate_hardcoded_users_security.py
```

#### 4.2 Limpiar Referencias Antiguas
```bash
# Remover archivos y configuraciones obsoletas
# (ver sección de limpieza más abajo)
```

## Scripts de Migración

### migrate_hardcoded_users.py
**Uso:**
```bash
python scripts/migrate_hardcoded_users.py [command]

Comandos disponibles:
- backup    Crear backup de usuarios hardcodeados
- migrate   Ejecutar migración completa
- rollback  Revertir migración (si es necesario)
- status    Mostrar estado de migración
```

### seed_secure_system_users.py
**Uso:**
```bash
python scripts/seed_secure_system_users.py
```

### validate_hardcoded_users_security.py
**Uso:**
```bash
python scripts/validate_hardcoded_users_security.py
```

## Validaciones de Seguridad

### Verificaciones Automáticas
- ✅ No hay credenciales hardcodeadas en código fuente
- ✅ Variables NEXT_PUBLIC no contienen secretos
- ✅ Contraseñas cumplen requisitos de seguridad
- ✅ Sistema de flags funciona correctamente
- ✅ Setup status excluye usuarios del sistema apropiadamente

### Verificaciones Manuales
- [ ] Login funciona con nuevas credenciales
- [ ] Setup status muestra "needs_setup: false"
- [ ] No hay errores en logs relacionados con usuarios
- [ ] API endpoints funcionan correctamente

## Limpieza Post-Migración

### Archivos a Remover/Modificar
```bash
# Remover configuraciones hardcodeadas del frontend
rm frontend/.env.local  # Contiene NEXT_PUBLIC_* hardcodeados
rm frontend/.env.local.example  # Contiene ejemplos inseguros

# Limpiar docker-compose.yml
# Remover variables NEXT_PUBLIC_* hardcodeadas

# Actualizar documentación
# Remover referencias a credenciales hardcodeadas en:
# - README.md
# - docs/*.md
# - scripts/setup.sh
# - scripts/install.py
```

### Variables de Entorno a Limpiar
```bash
# Remover estas variables de todos los archivos .env
NEXT_PUBLIC_DEMO_EMAIL=admin@example.com
NEXT_PUBLIC_DEMO_PASSWORD=admin123
```

## Solución de Problemas

### Problema: "SEED_ADMIN_EMAIL environment variable is required"
**Solución:** Asegurarse de que las variables de entorno están configuradas en `.env`

### Problema: "Migration validation failed"
**Solución:**
```bash
# Verificar estado
python scripts/migrate_hardcoded_users.py status

# Re-ejecutar migración
python scripts/migrate_hardcoded_users.py migrate
```

### Problema: "Setup status still shows needs_setup: true"
**Solución:** Verificar que `HARDCODED_USERS_MIGRATION_ENABLED=true` en `.env`

### Problema: Usuarios hardcodeados aún aparecen en logs
**Solución:** Reiniciar servicios después de la migración
```bash
docker-compose restart backend frontend
```

## Rollback (si es necesario)

### Rollback Completo
```bash
# Deshabilitar feature flag
echo "HARDCODED_USERS_MIGRATION_ENABLED=false" >> .env

# Revertir migración
python scripts/migrate_hardcoded_users.py rollback

# Restaurar desde backup (si existe)
# Nota: Requiere restauración manual de base de datos
```

### Rollback Parcial
- Mantener flags del sistema pero permitir credenciales antiguas
- Deshabilitar validaciones pero mantener nueva estructura

## Mejores Prácticas

### Seguridad
- ✅ Usar contraseñas de al menos 12 caracteres
- ✅ Cambiar contraseñas por defecto inmediatamente
- ✅ No exponer credenciales en variables NEXT_PUBLIC
- ✅ Usar HTTPS en producción
- ✅ Implementar rotación de credenciales

### Operaciones
- ✅ Hacer backups antes de migraciones
- ✅ Probar en ambiente de staging primero
- ✅ Monitorear logs durante migración
- ✅ Documentar cambios realizados
- ✅ Validar funcionalidad después de migración

### Desarrollo
- ✅ No introducir nuevas credenciales hardcodeadas
- ✅ Usar variables de entorno para configuración
- ✅ Implementar validaciones de seguridad en CI/CD
- ✅ Documentar requisitos de variables de entorno

## Monitoreo Post-Migración

### Métricas a Monitorear
- Número de usuarios del sistema
- Intentos de login con credenciales antiguas
- Estado del endpoint `/api/v1/auth/setup-status`
- Errores relacionados con autenticación

### Alertas Recomendadas
- Login con credenciales hardcodeadas detectadas
- Cambios en configuración de usuarios del sistema
- Errores en validaciones de seguridad

## Preguntas Frecuentes

### ¿Puedo mantener algunos usuarios hardcodeados?
No recomendado. Todos los usuarios hardcodeados representan riesgos de seguridad. Use el sistema de flags para identificar usuarios del sistema sin hardcodear credenciales.

### ¿Qué pasa si olvido configurar las variables de entorno?
La aplicación fallará al iniciar con errores claros indicando qué variables faltan.

### ¿Puedo cambiar las credenciales después de la migración?
Sí, use la interfaz de administración o API para cambiar contraseñas. Las variables de entorno solo se usan para seeding inicial.

### ¿Es reversible la migración?
Sí, el script incluye funcionalidad de rollback, pero se recomienda hacer backup completo antes de migrar.

## Conclusión

Esta migración elimina completamente los riesgos de seguridad asociados con usuarios hardcodeados mientras mantiene la funcionalidad del sistema. El nuevo sistema es más seguro, configurable y mantenible.

**Tiempo estimado de migración:** 2-4 horas
**Downtime requerido:** Mínimo (solo reinicio de servicios)
**Riesgo:** Bajo (con backups y validaciones)

---

*Documentación creada como parte de la migración de usuarios hardcodeados - Proyecto Semilla*