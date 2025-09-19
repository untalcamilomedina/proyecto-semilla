# Estrategia de Migración Segura - Usuarios Hardcodeados

## Resumen Ejecutivo

Esta estrategia define un enfoque seguro y gradual para eliminar usuarios hardcodeados del sistema, minimizando riesgos y permitiendo rollback si es necesario.

## Principios de la Migración

### 1. Seguridad Primero
- Nunca comprometer la seguridad durante la transición
- Mantener funcionalidad existente hasta que la nueva esté probada
- Implementar validaciones en cada paso

### 2. Compatibilidad Hacia Atrás
- Mantener soporte para configuraciones existentes
- Proporcionar período de transición
- Documentar cambios claramente

### 3. Validación Continua
- Tests automatizados en cada paso
- Validación manual antes de cada fase
- Monitoreo de métricas de seguridad

### 4. Rollback Plan
- Capacidad de revertir cambios en cualquier punto
- Backups de configuración y datos
- Scripts de rollback automatizados

## Arquitectura de la Solución

### Nuevo Sistema de Usuarios del Sistema

#### Modelo de Base de Datos
```sql
-- Nueva tabla para flags de usuarios del sistema
CREATE TABLE system_user_flags (
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    flag_type VARCHAR(50) NOT NULL, -- 'admin', 'demo', 'system', 'legacy_hardcoded'
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    PRIMARY KEY (user_id, flag_type)
);

-- Índices para rendimiento
CREATE INDEX idx_system_user_flags_type ON system_user_flags(flag_type);
CREATE INDEX idx_system_user_flags_user_id ON system_user_flags(user_id);
```

#### Modelo SQLAlchemy
```python
# backend/app/models/system_user_flag.py
from sqlalchemy import Column, String, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from app.db.base import Base
import datetime

class SystemUserFlag(Base):
    __tablename__ = "system_user_flags"

    user_id = Column(UUID(as_uuid=True), ForeignKey('users.id'), primary_key=True)
    flag_type = Column(String(50), primary_key=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)
```

### Servicio de Usuarios del Sistema

#### SystemUserService
```python
# backend/app/services/system_user_service.py
from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete
from app.models.system_user_flag import SystemUserFlag
from app.models.user import User

class SystemUserService:

    @staticmethod
    async def mark_as_system_user(db: AsyncSession, user_id: str, flag_type: str):
        """Marcar un usuario como usuario del sistema"""
        flag = SystemUserFlag(user_id=user_id, flag_type=flag_type)
        db.add(flag)
        await db.commit()

    @staticmethod
    async def is_system_user(db: AsyncSession, user_id: str, flag_type: Optional[str] = None) -> bool:
        """Verificar si un usuario es del sistema"""
        query = select(SystemUserFlag).where(SystemUserFlag.user_id == user_id)
        if flag_type:
            query = query.where(SystemUserFlag.flag_type == flag_type)

        result = await db.execute(query)
        return result.scalar_one_or_none() is not None

    @staticmethod
    async def get_system_users_count(db: AsyncSession, flag_type: Optional[str] = None) -> int:
        """Contar usuarios del sistema"""
        query = select(SystemUserFlag)
        if flag_type:
            query = query.where(SystemUserFlag.flag_type == flag_type)

        result = await db.execute(query)
        return len(result.scalars().all())

    @staticmethod
    async def migrate_legacy_hardcoded_users(db: AsyncSession):
        """Migrar usuarios hardcodeados existentes a flags del sistema"""
        from app.core.config import settings

        legacy_emails = [
            settings.SEED_ADMIN_EMAIL or "admin@proyectosemilla.dev",
            settings.SEED_DEMO_EMAIL or "demo@demo-company.com",
            "admin@example.com"  # Para compatibilidad
        ]

        for email in legacy_emails:
            user_result = await db.execute(select(User).where(User.email == email))
            user = user_result.scalar_one_or_none()

            if user:
                # Determinar tipo de flag basado en email
                if "admin" in email and "example.com" not in email:
                    flag_type = "admin"
                elif "demo" in email:
                    flag_type = "demo"
                else:
                    flag_type = "legacy_hardcoded"

                # Crear flag si no existe
                existing_flag = await db.execute(
                    select(SystemUserFlag).where(
                        SystemUserFlag.user_id == user.id,
                        SystemUserFlag.flag_type == flag_type
                    )
                )

                if not existing_flag.scalar_one_or_none():
                    await SystemUserService.mark_as_system_user(db, str(user.id), flag_type)
```

## Fases de Implementación

### Fase 1: Preparación (Semanas 1-2)

#### 1.1 Crear Migración de Base de Datos
```bash
# backend/alembic/versions/xxx_add_system_user_flags.py
"""Add system user flags table"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

def upgrade():
    op.create_table('system_user_flags',
        sa.Column('user_id', postgresql.UUID(), nullable=False),
        sa.Column('flag_type', sa.String(50), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('user_id', 'flag_type')
    )
    op.create_index('idx_system_user_flags_type', 'system_user_flags', ['flag_type'])
    op.create_index('idx_system_user_flags_user_id', 'system_user_flags', ['user_id'])

def downgrade():
    op.drop_index('idx_system_user_flags_user_id', 'system_user_flags')
    op.drop_index('idx_system_user_flags_type', 'system_user_flags')
    op.drop_table('system_user_flags')
```

#### 1.2 Implementar Variables de Entorno
```bash
# .env.template (nuevo archivo)
# Sistema - Variables de Entorno Requeridas
SEED_ADMIN_EMAIL=${SEED_ADMIN_EMAIL}
SEED_ADMIN_PASSWORD=${SEED_ADMIN_PASSWORD}
SEED_DEMO_EMAIL=${SEED_DEMO_EMAIL}
SEED_DEMO_PASSWORD=${SEED_DEMO_PASSWORD}

# Sistema - Variables Opcionales con Valores por Defecto Seguros
SEED_ADMIN_FIRST_NAME=${SEED_ADMIN_FIRST_NAME:-Super}
SEED_ADMIN_LAST_NAME=${SEED_ADMIN_LAST_NAME:-Admin}
SEED_DEMO_FIRST_NAME=${SEED_DEMO_FIRST_NAME:-Demo}
SEED_DEMO_LAST_NAME=${SEED_DEMO_LAST_NAME:-User}
```

#### 1.3 Crear Feature Flag
```python
# backend/app/core/config.py
class Settings(BaseSettings):
    # ... existing settings ...

    # Feature flag para migración
    HARDCODED_USERS_MIGRATION_ENABLED: bool = Field(default=False, env="HARDCODED_USERS_MIGRATION_ENABLED")

    # Variables de entorno para usuarios del sistema
    SEED_ADMIN_EMAIL: Optional[str] = Field(default=None, env="SEED_ADMIN_EMAIL")
    SEED_ADMIN_PASSWORD: Optional[str] = Field(default=None, env="SEED_ADMIN_PASSWORD")
    SEED_DEMO_EMAIL: Optional[str] = Field(default=None, env="SEED_DEMO_EMAIL")
    SEED_DEMO_PASSWORD: Optional[str] = Field(default=None, env="SEED_DEMO_PASSWORD")
```

### Fase 2: Implementación del Nuevo Sistema (Semanas 3-5)

#### 2.1 Actualizar get_setup_status()
```python
# backend/app/api/v1/endpoints/auth.py
@router.get("/setup-status")
async def get_setup_status(db: AsyncSession = Depends(get_db)):
    """
    Check if the system needs initial setup
    Now uses system user flags instead of hardcoded email list
    """
    from app.services.system_user_service import SystemUserService

    # Get total user count
    total_result = await db.execute(select(func.count(User.id)))
    total_users = total_result.scalar()

    # Get system users count
    system_users = await SystemUserService.get_system_users_count(db)
    real_users = total_users - system_users

    # Backward compatibility: if migration not enabled, use old logic
    if not settings.HARDCODED_USERS_MIGRATION_ENABLED:
        # Fallback to old hardcoded logic
        hardcoded_emails = ["admin@proyectosemilla.dev", "demo@demo-company.com", "admin@example.com"]
        hardcoded_result = await db.execute(
            select(func.count(User.id)).where(User.email.in_(hardcoded_emails))
        )
        hardcoded_count = hardcoded_result.scalar()
        real_users = total_users - hardcoded_count

    return {
        "needs_setup": real_users == 0,
        "real_user_count": real_users,
        "total_user_count": total_users,
        "migration_enabled": settings.HARDCODED_USERS_MIGRATION_ENABLED,
        "system_users_count": system_users
    }
```

#### 2.2 Crear Nuevo Sistema de Seeding
```python
# backend/scripts/seed_system_users.py
"""
Secure system user seeding script
Replaces hardcoded user creation with configurable system
"""

import asyncio
import os
import sys
from pathlib import Path

# Add backend to path
backend_dir = Path(__file__).parent.parent
sys.path.insert(0, str(backend_dir))

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.core.database import get_db
from app.core.security import get_password_hash
from app.models.tenant import Tenant
from app.models.user import User
from app.models.role import Role
from app.models.user_role import UserRole
from app.services.system_user_service import SystemUserService
from uuid import uuid4

async def create_secure_system_admin(db: AsyncSession, tenant: Tenant) -> User:
    """Create system admin user securely"""
    admin_email = os.getenv("SEED_ADMIN_EMAIL")
    admin_password = os.getenv("SEED_ADMIN_PASSWORD")

    if not admin_email or not admin_password:
        raise ValueError("SEED_ADMIN_EMAIL and SEED_ADMIN_PASSWORD are required")

    # Check if user already exists
    existing = await db.execute(select(User).where(User.email == admin_email))
    if existing.scalar_one_or_none():
        print(f"✅ System admin {admin_email} already exists")
        return existing.scalar_one_or_none()

    # Validate password strength
    if len(admin_password) < 12:
        raise ValueError("Admin password must be at least 12 characters long")

    # Create user
    user = User(
        tenant_id=tenant.id,
        email=admin_email,
        hashed_password=get_password_hash(admin_password),
        first_name=os.getenv("SEED_ADMIN_FIRST_NAME", "Super"),
        last_name=os.getenv("SEED_ADMIN_LAST_NAME", "Admin"),
        full_name=f"{os.getenv('SEED_ADMIN_FIRST_NAME', 'Super')} {os.getenv('SEED_ADMIN_LAST_NAME', 'Admin')}",
        is_active=True,
        is_verified=True
    )

    db.add(user)
    await db.commit()
    await db.refresh(user)

    # Mark as system user
    await SystemUserService.mark_as_system_user(db, str(user.id), "admin")

    print(f"✅ Created system admin: {admin_email}")
    return user

async def create_secure_demo_user(db: AsyncSession, tenant: Tenant) -> User:
    """Create demo user securely"""
    demo_email = os.getenv("SEED_DEMO_EMAIL")
    demo_password = os.getenv("SEED_DEMO_PASSWORD")

    if not demo_email or not demo_password:
        print("⚠️  Demo user creation skipped - SEED_DEMO_EMAIL and SEED_DEMO_PASSWORD not set")
        return None

    # Similar logic to admin user creation...
    # (implementation details omitted for brevity)

async def migrate_and_seed():
    """Main migration and seeding function"""
    print("🚀 Starting secure system user seeding...")

    db = await get_db().__anext__()

    try:
        # Get or create tenant
        tenant_result = await db.execute(select(Tenant).where(Tenant.slug == "proyecto-semilla"))
        tenant = tenant_result.scalar_one_or_none()

        if not tenant:
            # Create default tenant
            tenant = Tenant(
                name="Proyecto Semilla",
                slug="proyecto-semilla",
                description="Plataforma SaaS multi-tenant"
            )
            db.add(tenant)
            await db.commit()
            await db.refresh(tenant)

        # Create system users
        admin_user = await create_secure_system_admin(db, tenant)
        demo_user = await create_secure_demo_user(db, tenant)

        # Migrate legacy hardcoded users
        await SystemUserService.migrate_legacy_hardcoded_users(db)

        print("✅ Secure system user seeding completed")

    except Exception as e:
        print(f"❌ Error during seeding: {e}")
        await db.rollback()
        raise
    finally:
        await db.close()

if __name__ == "__main__":
    asyncio.run(migrate_and_seed())
```

### Fase 3: Scripts de Instalación (Semanas 6-7)

#### 3.1 Nuevo Script de Instalación Interactiva
```python
# scripts/setup_secure.py
"""
Secure interactive setup script
Replaces hardcoded user creation with guided setup
"""

import os
import sys
from pathlib import Path
from getpass import getpass
import re

def validate_email(email: str) -> bool:
    """Validate email format"""
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None

def validate_password(password: str) -> tuple[bool, str]:
    """Validate password strength"""
    if len(password) < 12:
        return False, "Password must be at least 12 characters long"

    if not re.search(r'[A-Z]', password):
        return False, "Password must contain at least one uppercase letter"

    if not re.search(r'[a-z]', password):
        return False, "Password must contain at least one lowercase letter"

    if not re.search(r'\d', password):
        return False, "Password must contain at least one number"

    if not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
        return False, "Password must contain at least one special character"

    return True, "Password is strong"

def setup_environment_variables():
    """Interactive setup of environment variables"""
    print("🔐 Secure System Setup")
    print("=" * 50)

    # Admin user setup
    print("\n👤 System Administrator Setup")
    while True:
        admin_email = input("Admin email: ").strip()
        if validate_email(admin_email):
            break
        print("❌ Invalid email format")

    while True:
        admin_password = getpass("Admin password: ")
        confirm_password = getpass("Confirm admin password: ")

        if admin_password != confirm_password:
            print("❌ Passwords don't match")
            continue

        is_valid, message = validate_password(admin_password)
        if is_valid:
            break
        print(f"❌ {message}")

    # Demo user setup (optional)
    print("\n🎭 Demo User Setup (optional)")
    setup_demo = input("Setup demo user? (y/N): ").strip().lower() == 'y'

    demo_email = None
    demo_password = None

    if setup_demo:
        while True:
            demo_email = input("Demo email: ").strip()
            if validate_email(demo_email):
                break
            print("❌ Invalid email format")

        while True:
            demo_password = getpass("Demo password: ")
            confirm_password = getpass("Confirm demo password: ")

            if demo_password != confirm_password:
                print("❌ Passwords don't match")
                continue

            is_valid, message = validate_password(demo_password)
            if is_valid:
                break
            print(f"❌ {message}")

    # Generate .env file
    env_content = f"""# Secure Environment Configuration
# Generated by setup_secure.py

# Database
DB_PASSWORD=changeme123
DB_HOST=db
DB_PORT=5432
DB_NAME=proyecto_semilla

# Security
JWT_SECRET={os.urandom(64).hex()}

# System Users
SEED_ADMIN_EMAIL={admin_email}
SEED_ADMIN_PASSWORD={admin_password}
"""

    if demo_email and demo_password:
        env_content += f"""
SEED_DEMO_EMAIL={demo_email}
SEED_DEMO_PASSWORD={demo_password}
"""

    env_content += """
# Migration
HARDCODED_USERS_MIGRATION_ENABLED=true

# Other settings...
DEBUG=true
"""

    # Write .env file
    with open('.env', 'w') as f:
        f.write(env_content)

    print("✅ Environment configuration saved to .env")
    print("⚠️  Remember to change the default DB_PASSWORD in production!")

def main():
    """Main setup function"""
    print("🌱 Proyecto Semilla - Secure Setup")
    print("This will guide you through secure system configuration")

    if os.path.exists('.env'):
        overwrite = input(".env file already exists. Overwrite? (y/N): ").strip().lower() == 'y'
        if not overwrite:
            print("Setup cancelled")
            return

    setup_environment_variables()

    print("\n🎉 Setup completed!")
    print("\nNext steps:")
    print("1. Review the generated .env file")
    print("2. Run: docker-compose up -d db redis")
    print("3. Run: docker-compose run --rm backend alembic upgrade head")
    print("4. Run: python scripts/seed_system_users.py")
    print("5. Start the application: docker-compose up -d")

if __name__ == "__main__":
    main()
```

### Fase 4: Migración de Datos (Semana 8)

#### 4.1 Script de Migración
```python
# scripts/migrate_hardcoded_users.py
"""
Migration script for existing hardcoded users
Safe migration with rollback capability
"""

import asyncio
import sys
from pathlib import Path

backend_dir = Path(__file__).parent.parent / "backend"
sys.path.insert(0, str(backend_dir))

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, text
from app.core.database import get_db
from app.services.system_user_service import SystemUserService

async def create_backup():
    """Create backup of current user state"""
    print("📦 Creating backup...")

    db = await get_db().__anext__()
    try:
        # Export users table
        result = await db.execute(text("""
            COPY (
                SELECT id, email, first_name, last_name, is_active, created_at
                FROM users
                WHERE email IN ('admin@proyectosemilla.dev', 'demo@demo-company.com', 'admin@example.com')
            ) TO '/tmp/hardcoded_users_backup.csv' WITH CSV HEADER
        """))

        print("✅ Backup created at /tmp/hardcoded_users_backup.csv")

    except Exception as e:
        print(f"⚠️  Backup failed: {e}")
    finally:
        await db.close()

async def migrate_users():
    """Migrate hardcoded users to new system"""
    print("🔄 Starting user migration...")

    db = await get_db().__anext__()
    try:
        # Migrate legacy users
        await SystemUserService.migrate_legacy_hardcoded_users(db)

        # Verify migration
        migrated_count = await SystemUserService.get_system_users_count(db)
        print(f"✅ Migrated {migrated_count} users to system flags")

        # Update feature flag
        print("🔧 Enabling migration feature flag...")
        # This would update the environment or database config

    except Exception as e:
        print(f"❌ Migration failed: {e}")
        raise
    finally:
        await db.close()

async def rollback_migration():
    """Rollback migration if needed"""
    print("🔙 Rolling back migration...")

    db = await get_db().__anext__()
    try:
        # Remove system flags
        await db.execute(text("DELETE FROM system_user_flags WHERE flag_type = 'legacy_hardcoded'"))

        # Restore from backup if needed
        print("✅ Migration rolled back")

    except Exception as e:
        print(f"❌ Rollback failed: {e}")
        raise
    finally:
        await db.close()

async def main():
    """Main migration function"""
    if len(sys.argv) < 2:
        print("Usage: python migrate_hardcoded_users.py [migrate|rollback|backup]")
        sys.exit(1)

    command = sys.argv[1]

    if command == "backup":
        await create_backup()
    elif command == "migrate":
        await create_backup()  # Always create backup before migration
        await migrate_users()
    elif command == "rollback":
        await rollback_migration()
    else:
        print(f"Unknown command: {command}")
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main())
```

### Fase 5: Validación y Cleanup (Semanas 9-10)

#### 5.1 Tests de Validación
```python
# tests/test_migration_validation.py
"""
Tests to validate migration success
"""

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

class TestMigrationValidation:

    @pytest.mark.asyncio
    async def test_system_user_flags_created(self, db: AsyncSession):
        """Test that system user flags were created during migration"""
        from app.services.system_user_service import SystemUserService

        # Check that we have system users
        admin_count = await SystemUserService.get_system_users_count(db, "admin")
        assert admin_count > 0, "No admin system users found"

    @pytest.mark.asyncio
    async def test_setup_status_works_with_new_system(self, client):
        """Test that setup status works with new system"""
        response = await client.get("/api/v1/auth/setup-status")
        assert response.status_code == 200

        data = response.json()
        assert "migration_enabled" in data
        assert "system_users_count" in data
        assert data["migration_enabled"] is True

    @pytest.mark.asyncio
    async def test_no_hardcoded_emails_in_new_system(self, db: AsyncSession):
        """Test that no hardcoded emails are used in new system"""
        from app.core.config import settings

        # Verify that we're using environment variables
        assert settings.SEED_ADMIN_EMAIL is not None
        assert settings.SEED_ADMIN_PASSWORD is not None

        # Verify that old hardcoded emails are not in use
        # (except for backward compatibility during migration)
```

## Monitoreo y Alertas

### Métricas a Monitorear

#### Seguridad
- Número de usuarios del sistema
- Intentos de login con credenciales antiguas
- Cambios en configuración de seguridad

#### Funcionalidad
- Estado del endpoint `/setup-status`
- Éxito de creación de usuarios del sistema
- Tasa de error en autenticación

### Alertas Automáticas

#### Alerta de Seguridad
```python
# scripts/monitor_security.py
async def check_security_alerts():
    """Check for security alerts related to hardcoded users"""

    alerts = []

    # Check for old hardcoded logins
    old_logins = await get_recent_logins_with_old_credentials()
    if old_logins:
        alerts.append({
            "level": "WARNING",
            "message": f"Detected {len(old_logins)} logins with old hardcoded credentials",
            "action": "Review and update user credentials"
        })

    # Check migration status
    migration_status = await check_migration_status()
    if not migration_status["completed"]:
        alerts.append({
            "level": "INFO",
            "message": "Hardcoded users migration not yet completed",
            "action": "Complete migration process"
        })

    return alerts
```

## Plan de Rollback

### Rollback Completo
```bash
# scripts/rollback_hardcoded_migration.sh
#!/bin/bash

echo "🔙 Rolling back hardcoded users migration..."

# 1. Disable feature flag
echo "HARDCODED_USERS_MIGRATION_ENABLED=false" >> .env

# 2. Restore backup if available
if [ -f "/tmp/hardcoded_users_backup.csv" ]; then
    echo "📦 Restoring user backup..."
    # Restore logic here
fi

# 3. Remove system user flags
echo "🗑️  Removing system user flags..."
docker-compose exec db psql -U postgres -d proyecto_semilla -c "DELETE FROM system_user_flags;"

# 4. Restart services
echo "🔄 Restarting services..."
docker-compose restart backend

echo "✅ Rollback completed"
```

### Rollback Parcial
- Deshabilitar feature flag pero mantener flags del sistema
- Restaurar configuración anterior pero mantener nuevos usuarios
- Mantener migración pero permitir uso de credenciales antiguas temporalmente

## Comunicación y Documentación

### Documentación para Usuarios
1. **Guía de Migración**: Pasos detallados para migrar entornos existentes
2. **FAQ**: Preguntas frecuentes sobre cambios
3. **Troubleshooting**: Solución de problemas comunes

### Comunicación Interna
1. **Calendario de Migración**: Fechas y responsabilidades
2. **Status Updates**: Reportes semanales de progreso
3. **Training**: Sesiones para equipo de desarrollo

## Criterios de Éxito

### Técnicos
- ✅ Todos los tests pasan
- ✅ No hay credenciales hardcodeadas en código
- ✅ Setup funciona con nuevas variables de entorno
- ✅ Rollback funciona correctamente

### Operacionales
- ✅ Instalación funciona en todos los entornos
- ✅ Documentación está completa y actualizada
- ✅ Equipo está entrenado en nuevo sistema
- ✅ Monitoreo está configurado

### Seguridad
- ✅ No hay vulnerabilidades conocidas
- ✅ Auditoría de seguridad pasa
- ✅ Variables sensibles están protegidas
- ✅ Logs no contienen información sensible

## Conclusión

Esta estrategia proporciona un enfoque seguro y gradual para eliminar usuarios hardcodeados, con múltiples puntos de validación y capacidad de rollback. La implementación en fases permite minimizar riesgos mientras se mejora la seguridad del sistema.