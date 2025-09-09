#!/usr/bin/env python3
"""
Script para configurar la base de datos con datos iniciales
"""

import asyncio
import os
import sys
from pathlib import Path

# Add backend to path
backend_dir = Path(__file__).parent.parent
sys.path.insert(0, str(backend_dir))

# Load environment variables
from dotenv import load_dotenv
load_dotenv(backend_dir.parent / ".env")

async def setup_database():
    """Setup database tables and initial data"""
    try:
        # Import modules that depend on .env being present
        from app.core.config import settings
        from app.core.database import create_tables, engine
        from app.core.security import get_password_hash
        from app.models.tenant import Tenant
        from app.models.user import User
        from app.models.role import Role
        from app.models.user_role import UserRole

        # Create tables
        print("Creando tablas de base de datos...")
        async with engine.begin() as conn:
            from app.models import Tenant, User, Role, UserRole, RefreshToken, Article, Comment, Category
            await conn.run_sync(Tenant.metadata.create_all)
            await conn.run_sync(User.metadata.create_all)
            await conn.run_sync(Role.metadata.create_all)
            await conn.run_sync(UserRole.metadata.create_all)
            await conn.run_sync(RefreshToken.metadata.create_all)
            await conn.run_sync(Article.metadata.create_all)
            await conn.run_sync(Comment.metadata.create_all)
            await conn.run_sync(Category.metadata.create_all)

        print("✅ Tablas de base de datos creadas")

        # Create initial data
        await create_initial_data()
        return True

    except Exception as e:
        print(f"❌ Error configurando base de datos: {e}")
        return False

async def create_initial_data():
    """Create initial tenant, roles, and super admin"""
    print("Creando datos iniciales...")

    # Import modules that depend on .env being present
    from app.core.config import settings
    from app.core.database import engine
    from app.core.security import get_password_hash
    from app.models.tenant import Tenant
    from app.models.user import User
    from app.models.role import Role
    from app.models.user_role import UserRole

    async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

    async with async_session() as session:
        try:
            # Create initial tenant
            tenant = Tenant(
                name="Proyecto Semilla",
                slug="proyecto-semilla",
                description="Plataforma SaaS multi-tenant de Proyecto Semilla",
                settings=json.dumps({
                    "theme": "default",
                    "features": ["auth", "tenants", "users", "articles"]
                })
            )
            session.add(tenant)
            await session.commit()
            await session.refresh(tenant)

            # Create admin role
            admin_role = Role(
                tenant_id=tenant.id,
                name="admin",
                description="Administrator with full access",
                permissions=json.dumps([
                    "users:read", "users:write", "users:delete",
                    "tenants:read", "tenants:write",
                    "roles:read", "roles:write",
                    "articles:read", "articles:write", "articles:delete",
                    "system:admin"
                ]),
                hierarchy_level=100,
                is_default=False
            )
            session.add(admin_role)
            await session.commit()
            await session.refresh(admin_role)

            # Create user role
            user_role = Role(
                tenant_id=tenant.id,
                name="user",
                description="Standard user role",
                permissions=json.dumps([
                    "users:read",
                    "tenants:read",
                    "articles:read", "articles:write"
                ]),
                hierarchy_level=10,
                is_default=True
            )
            session.add(user_role)
            await session.commit()
            await session.refresh(user_role)

            # Create super admin user
            admin_email = "admin@proyectosemilla.dev"
            admin_password = os.getenv('SEED_ADMIN_PASSWORD', 'default_password')
            hashed_password = get_password_hash(admin_password)

            admin_user = User(
                tenant_id=tenant.id,
                email=admin_email,
                hashed_password=hashed_password,
                first_name="Super",
                last_name="Admin",
                full_name="Super Admin",
                is_active=True,
                is_verified=True,
                preferences=json.dumps({
                    "language": "es",
                    "theme": "dark"
                })
            )
            session.add(admin_user)
            await session.commit()
            await session.refresh(admin_user)

            # Assign admin role
            user_role_association = UserRole(
                user_id=admin_user.id,
                role_id=admin_role.id
            )
            session.add(user_role_association)
            await session.commit()

            print("✅ Datos iniciales creados correctamente")
            print(f"📧 Admin Email: {admin_email}")
            print(f"🔑 Admin Password: {admin_password}")

        except Exception as e:
            await session.rollback()
            raise e

if __name__ == "__main__":
    from sqlalchemy.ext.asyncio import AsyncSession
    from sqlalchemy.orm import sessionmaker
    import json

    asyncio.run(setup_database())