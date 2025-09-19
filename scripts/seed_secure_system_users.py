#!/usr/bin/env python3
"""
Secure System Users Seeding Script
Creates system users using environment variables instead of hardcoded values
"""

import asyncio
import os
import sys
from pathlib import Path
from typing import Optional

# Add backend to path
backend_dir = Path(__file__).parent.parent / "backend"
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
from app.core.config import settings
from uuid import uuid4


async def create_tenant(db: AsyncSession) -> Tenant:
    """Create or get the main tenant"""
    print("🌱 Checking for main tenant...")

    tenant_result = await db.execute(
        select(Tenant).where(Tenant.slug == "proyecto-semilla")
    )
    tenant = tenant_result.scalar_one_or_none()

    if tenant:
        print(f"✅ Main tenant already exists: {tenant.name}")
        return tenant

    print("🌱 Creating main tenant...")
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


async def create_super_admin_role(db: AsyncSession, tenant: Tenant) -> Role:
    """Create super admin role if it doesn't exist"""
    print("👑 Checking for super admin role...")

    role_result = await db.execute(
        select(Role).where(Role.name == "Super Admin", Role.tenant_id == tenant.id)
    )
    role = role_result.scalar_one_or_none()

    if role:
        print("✅ Super admin role already exists")
        return role

    print("👑 Creating super admin role...")
    permissions = [
        "users:*", "roles:*", "tenants:*", "articles:*", "system:*"
    ]
    role = Role(
        tenant_id=tenant.id,
        name="Super Admin",
        description="Control total del sistema",
        permissions=str(permissions).replace("'", '"'),
        hierarchy_level=1000,
        color="#FF0000",
        is_default=False
    )
    db.add(role)
    await db.commit()
    await db.refresh(role)
    print(f"✅ Created role: {role.name} (ID: {role.id})")
    return role


async def create_secure_system_admin(db: AsyncSession, tenant: Tenant, admin_role: Role) -> Optional[User]:
    """Create system admin user securely"""
    print("🦸 Setting up system administrator...")

    # Validate required environment variables
    admin_email = settings.SEED_ADMIN_EMAIL
    admin_password = settings.SEED_ADMIN_PASSWORD

    if not admin_email:
        print("❌ SEED_ADMIN_EMAIL environment variable is required")
        return None

    if not admin_password:
        print("❌ SEED_ADMIN_PASSWORD environment variable is required")
        return None

    # Check if user already exists
    existing_result = await db.execute(select(User).where(User.email == admin_email))
    existing_user = existing_result.scalar_one_or_none()

    if existing_user:
        print(f"✅ System admin already exists: {admin_email}")

        # Ensure user has system flag
        await SystemUserService.mark_as_system_user(db, str(existing_user.id), "admin")

        # Ensure user has admin role
        role_exists = await db.execute(
            select(UserRole).where(
                UserRole.user_id == existing_user.id,
                UserRole.role_id == admin_role.id
            )
        )
        if not role_exists.scalar_one_or_none():
            user_role = UserRole(user_id=existing_user.id, role_id=admin_role.id)
            db.add(user_role)
            await db.commit()

        return existing_user

    print("🦸 Creating system administrator...")

    # Validate password strength
    if len(admin_password) < 12:
        print("❌ Admin password must be at least 12 characters long")
        return None

    # Create user
    hashed_password = get_password_hash(admin_password)
    user = User(
        tenant_id=tenant.id,
        email=admin_email,
        hashed_password=hashed_password,
        first_name=settings.SEED_ADMIN_FIRST_NAME,
        last_name=settings.SEED_ADMIN_LAST_NAME,
        full_name=f"{settings.SEED_ADMIN_FIRST_NAME} {settings.SEED_ADMIN_LAST_NAME}",
        is_active=True,
        is_verified=True
    )

    db.add(user)
    await db.commit()
    await db.refresh(user)

    # Assign admin role
    user_role = UserRole(user_id=user.id, role_id=admin_role.id)
    db.add(user_role)
    await db.commit()

    # Mark as system user
    await SystemUserService.mark_as_system_user(db, str(user.id), "admin")

    print(f"✅ Created system admin: {admin_email}")
    print(f"   Name: {user.full_name}")
    print(f"   Role: Super Admin")
    print("   ⚠️  Remember to change the password in production!"

    return user


async def create_secure_demo_user(db: AsyncSession, tenant: Tenant) -> Optional[User]:
    """Create demo user securely"""
    print("🎭 Setting up demo user...")

    demo_email = settings.SEED_DEMO_EMAIL
    demo_password = settings.SEED_DEMO_PASSWORD

    if not demo_email or not demo_password:
        print("ℹ️  Demo user setup skipped - SEED_DEMO_EMAIL and SEED_DEMO_PASSWORD not set")
        return None

    # Check if user already exists
    existing_result = await db.execute(select(User).where(User.email == demo_email))
    existing_user = existing_result.scalar_one_or_none()

    if existing_user:
        print(f"✅ Demo user already exists: {demo_email}")
        await SystemUserService.mark_as_system_user(db, str(existing_user.id), "demo")
        return existing_user

    print("🎭 Creating demo user...")

    # Validate password strength
    if len(demo_password) < 8:
        print("❌ Demo password must be at least 8 characters long")
        return None

    # Create user
    hashed_password = get_password_hash(demo_password)
    user = User(
        tenant_id=tenant.id,
        email=demo_email,
        hashed_password=hashed_password,
        first_name=settings.SEED_DEMO_FIRST_NAME,
        last_name=settings.SEED_DEMO_LAST_NAME,
        full_name=f"{settings.SEED_DEMO_FIRST_NAME} {settings.SEED_DEMO_LAST_NAME}",
        is_active=True,
        is_verified=True
    )

    db.add(user)
    await db.commit()
    await db.refresh(user)

    # Mark as system user
    await SystemUserService.mark_as_system_user(db, str(user.id), "demo")

    print(f"✅ Created demo user: {demo_email}")
    print(f"   Name: {user.full_name}")

    return user


async def validate_system_users(db: AsyncSession) -> bool:
    """Validate that system users were created correctly"""
    print("🔍 Validating system users...")

    system_users_count = await SystemUserService.get_system_users_count(db)
    if system_users_count == 0:
        print("❌ No system users found")
        return False

    system_users_info = await SystemUserService.get_system_users_info(db)

    admin_found = any(user["flag_type"] == "admin" for user in system_users_info)
    if not admin_found:
        print("❌ No admin system user found")
        return False

    print(f"✅ Found {system_users_count} system users")
    for user in system_users_info:
        print(f"   • {user['email']} ({user['flag_type']})")

    return True


async def seed_secure_system_users():
    """Main seeding function"""
    print("🚀 Starting secure system users seeding...")
    print("=" * 50)

    db = await get_db().__anext__()

    try:
        # Create/get tenant
        tenant = await create_tenant(db)

        # Create admin role
        admin_role = await create_super_admin_role(db, tenant)

        # Create system users
        admin_user = await create_secure_system_admin(db, tenant, admin_role)
        demo_user = await create_secure_demo_user(db, tenant)

        # Validate setup
        if await validate_system_users(db):
            print("\n" + "=" * 50)
            print("🎉 Secure system users seeding completed!")
            print("=" * 50)

            print("\n📋 Summary:")
            if admin_user:
                print(f"   Admin: {admin_user.email}")
            if demo_user:
                print(f"   Demo: {demo_user.email}")
            print(f"   Migration enabled: {settings.HARDCODED_USERS_MIGRATION_ENABLED}")

            if settings.SEED_ADMIN_PASSWORD == "admin123":
                print("\n⚠️  WARNING: Using default admin password!")
                print("   Set SEED_ADMIN_PASSWORD environment variable for security")
        else:
            print("❌ System users validation failed")
            return False

    except Exception as e:
        print(f"❌ Seeding failed: {e}")
        await db.rollback()
        raise
    finally:
        await db.close()

    return True


async def main():
    """Entry point"""
    try:
        success = await seed_secure_system_users()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n⚠️ Seeding cancelled by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Seeding failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())