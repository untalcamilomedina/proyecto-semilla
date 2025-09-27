"""
Secure Initial Data Seeding
This module provides secure initial data seeding using environment variables.
No hardcoded credentials are used - all sensitive data comes from environment variables.
"""

import asyncio
import os
import sys
from pathlib import Path

# Add backend to path for imports
backend_dir = Path(__file__).parent
sys.path.insert(0, str(backend_dir))

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.core.database import get_db
from app.core.security import get_password_hash
from app.models.tenant import Tenant
from app.models.user import User
from app.services.system_user_service import SystemUserService


async def create_secure_initial_tenant(db: AsyncSession) -> Tenant:
    """Create initial tenant securely"""
    print("🌱 Creating initial tenant...")

    # Check if tenant already exists
    existing = await db.execute(
        select(Tenant).where(Tenant.slug == "proyecto-semilla")
    )
    if existing.scalar_one_or_none():
        print("✅ Initial tenant already exists")
        return existing.scalar_one()

    # Create tenant
    tenant = Tenant(
        name="Proyecto Semilla",
        slug="proyecto-semilla",
        description="Plataforma SaaS multi-tenant principal",
        is_active=True
    )
    db.add(tenant)
    await db.commit()
    await db.refresh(tenant)

    print(f"✅ Created initial tenant: {tenant.name}")
    return tenant


async def create_secure_initial_admin(db: AsyncSession, tenant: Tenant) -> User:
    """Create initial admin user securely using environment variables"""
    print("🦸 Creating initial admin user...")

    # Get credentials from environment variables
    admin_email = os.getenv("SEED_ADMIN_EMAIL")
    admin_password = os.getenv("SEED_ADMIN_PASSWORD")

    if not admin_email:
        raise ValueError("SEED_ADMIN_EMAIL environment variable is required")

    if not admin_password:
        raise ValueError("SEED_ADMIN_PASSWORD environment variable is required")

    # Validate password strength
    if len(admin_password) < 12:
        raise ValueError("Admin password must be at least 12 characters long")

    # Check if user already exists
    existing = await db.execute(select(User).where(User.email == admin_email))
    if existing.scalar_one_or_none():
        print(f"✅ Admin user already exists: {admin_email}")
        user = existing.scalar_one()
        # Ensure it's marked as system user
        await SystemUserService.mark_as_system_user(db, str(user.id), "admin")
        return user

    # Create admin user
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

    print(f"✅ Created secure admin user: {admin_email}")
    print("   ⚠️  Remember to change the password in production!"
    return user


async def seed_secure_initial_data():
    """
    Seed initial data securely using environment variables.
    This replaces the old hardcoded initial_data.py approach.
    """
    print("🚀 Starting secure initial data seeding...")
    print("=" * 50)

    db: AsyncSession = await get_db().__anext__()

    try:
        # Create initial tenant
        tenant = await create_secure_initial_tenant(db)

        # Create initial admin user
        admin_user = await create_secure_initial_admin(db, tenant)

        print("\n" + "=" * 50)
        print("🎉 Secure initial data seeding completed!")
        print("=" * 50)
        print("📋 Summary:")
        print(f"   Tenant: {tenant.name}")
        print(f"   Admin: {admin_user.email}")
        print("   Migration enabled: True"
        print("\n⚠️  IMPORTANT: Change default passwords in production!")

    except Exception as e:
        print(f"❌ Seeding failed: {e}")
        await db.rollback()
        raise
    finally:
        await db.close()


async def main():
    """Main entry point for secure seeding"""
    try:
        await seed_secure_initial_data()
        print("\n✅ Initial data seeding completed successfully")
    except Exception as e:
        print(f"\n❌ Initial data seeding failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())