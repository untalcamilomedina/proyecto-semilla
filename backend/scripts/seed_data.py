#!/usr/bin/env python3
"""
Proyecto Semilla - Seed Data Script
Creates initial data for development and testing
"""

import asyncio
import sys
from pathlib import Path

# Add backend to path
backend_dir = Path(__file__).parent.parent
sys.path.insert(0, str(backend_dir))

from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db
from app.core.security import get_password_hash
from app.models.tenant import Tenant
from app.models.user import User
from app.models.role import Role
from app.models.user_role import UserRole
from uuid import uuid4


async def create_initial_tenant(db: AsyncSession) -> Tenant:
    """Create the initial tenant"""
    print("🌱 Creating initial tenant...")

    tenant = Tenant(
        name="Proyecto Semilla",
        slug="proyecto-semilla",
        description="Plataforma SaaS multi-tenant de Proyecto Semilla",
        settings='{"theme": "default", "features": ["auth", "tenants", "users"]}'
    )

    db.add(tenant)
    await db.commit()
    await db.refresh(tenant)

    print(f"✅ Created tenant: {tenant.name} (ID: {tenant.id})")
    return tenant


async def create_admin_role(db: AsyncSession, tenant: Tenant) -> Role:
    """Create admin role"""
    print("👑 Creating admin role...")

    role = Role(
        tenant_id=tenant.id,
        name="admin",
        description="Administrator with full access",
        permissions='["users:read", "users:write", "tenants:read", "tenants:write", "roles:read", "roles:write"]',
        hierarchy_level=100,
        is_default=False
    )

    db.add(role)
    await db.commit()
    await db.refresh(role)

    print(f"✅ Created role: {role.name} (ID: {role.id})")
    return role


async def create_user_role(db: AsyncSession, tenant: Tenant) -> Role:
    """Create user role"""
    print("👤 Creating user role...")

    role = Role(
        tenant_id=tenant.id,
        name="user",
        description="Standard user role",
        permissions='["users:read", "tenants:read"]',
        hierarchy_level=10,
        is_default=True
    )

    db.add(role)
    await db.commit()
    await db.refresh(role)

    print(f"✅ Created role: {role.name} (ID: {role.id})")
    return role


async def create_super_admin(db: AsyncSession, tenant: Tenant, admin_role: Role) -> User:
    """Create super admin user"""
    print("🦸 Creating super admin user...")

    # Hash password
    hashed_password = get_password_hash("admin123")

    user = User(
        tenant_id=tenant.id,
        email="admin@proyectosemilla.dev",
        hashed_password=hashed_password,
        first_name="Super",
        last_name="Admin",
        full_name="Super Admin",
        is_active=True,
        is_verified=True,
        preferences='{"language": "es", "theme": "dark"}'
    )

    db.add(user)
    await db.commit()
    await db.refresh(user)

    # Assign admin role
    user_role = UserRole(
        user_id=user.id,
        role_id=admin_role.id
    )

    db.add(user_role)
    await db.commit()

    print(f"✅ Created super admin: {user.email} (ID: {user.id})")
    print("🔐 Password: admin123 (CHANGE THIS IN PRODUCTION!)")
    return user


async def create_demo_tenant(db: AsyncSession) -> Tenant:
    """Create demo tenant for testing"""
    print("🎭 Creating demo tenant...")

    tenant = Tenant(
        name="Demo Company",
        slug="demo-company",
        description="Tenant de demostración para testing",
        settings='{"theme": "light", "features": ["auth", "tenants", "users"]}'
    )

    db.add(tenant)
    await db.commit()
    await db.refresh(tenant)

    print(f"✅ Created demo tenant: {tenant.name} (ID: {tenant.id})")
    return tenant


async def create_demo_user(db: AsyncSession, tenant: Tenant, user_role: Role) -> User:
    """Create demo user"""
    print("🎭 Creating demo user...")

    # Hash password
    hashed_password = get_password_hash("demo123")

    user = User(
        tenant_id=tenant.id,
        email="demo@demo-company.com",
        hashed_password=hashed_password,
        first_name="Demo",
        last_name="User",
        full_name="Demo User",
        is_active=True,
        is_verified=True,
        preferences='{"language": "es", "theme": "light"}'
    )

    db.add(user)
    await db.commit()
    await db.refresh(user)

    # Assign user role
    user_role_association = UserRole(
        user_id=user.id,
        role_id=user_role.id
    )

    db.add(user_role_association)
    await db.commit()

    print(f"✅ Created demo user: {user.email} (ID: {user.id})")
    print("🔐 Password: demo123")
    return user


async def seed_database():
    """Main seeding function"""
    print("🌱 Starting database seeding...")
    print("=" * 50)

    db = await get_db().__anext__()

    try:
        # Create initial tenant
        tenant = await create_initial_tenant(db)

        # Create roles
        admin_role = await create_admin_role(db, tenant)
        user_role = await create_user_role(db, tenant)

        # Create super admin
        await create_super_admin(db, tenant, admin_role)

        # Create demo data
        print("\n" + "=" * 30)
        print("🎭 Creating demo data...")
        print("=" * 30)

        demo_tenant = await create_demo_tenant(db)
        await create_demo_user(db, demo_tenant, user_role)

        print("\n" + "=" * 50)
        print("🎉 Database seeding completed successfully!")
        print("=" * 50)
        print("\n📋 Summary:")
        print("- Main tenant: Proyecto Semilla")
        print("- Super admin: admin@proyectosemilla.dev / admin123")
        print("- Demo tenant: Demo Company")
        print("- Demo user: demo@demo-company.com / demo123")
        print("\n⚠️  Remember to change default passwords in production!")

    except Exception as e:
        print(f"❌ Error during seeding: {e}")
        await db.rollback()
        raise
    finally:
        await db.close()


async def main():
    """Entry point"""
    try:
        await seed_database()
    except KeyboardInterrupt:
        print("\n⚠️ Seeding cancelled by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Seeding failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())