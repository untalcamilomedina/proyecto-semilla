import asyncio
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db
from app.core.security import get_password_hash
from app.models.tenant import Tenant
from app.models.user import User

async def seed_data():
    db: AsyncSession = await get_db().__anext__()
    try:
        # Create default tenant
        default_tenant = Tenant(id='00000000-0000-0000-0000-000000000001', name='Default Tenant', slug='default', description='Default tenant for new users', is_active=True)
        db.add(default_tenant)
        await db.commit()

        # Create admin user
        admin_user = User(
            id='00000000-0000-0000-0000-000000000002',
            tenant_id=default_tenant.id,
            email='admin@example.com',
            hashed_password=get_password_hash('admin123'),
            first_name='Admin',
            last_name='User',
            full_name='Admin User',
            is_active=True,
            is_verified=True
        )
        db.add(admin_user)
        await db.commit()
        print("Admin user created successfully")
    finally:
        await db.close()

if __name__ == "__main__":
    asyncio.run(seed_data())