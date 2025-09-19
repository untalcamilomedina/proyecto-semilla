#!/usr/bin/env python3
"""
Migration script for hardcoded users
Safely migrates existing hardcoded users to the new system user flag system
"""

import asyncio
import sys
import os
from pathlib import Path
from typing import List, Dict, Any
import json

# Add backend to path
backend_dir = Path(__file__).parent.parent / "backend"
sys.path.insert(0, str(backend_dir))

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, text
from app.core.database import get_db
from app.services.system_user_service import SystemUserService
from app.models.user import User
from app.core.config import settings


class HardcodedUsersMigrator:
    """Handles migration of hardcoded users to system user flags"""

    def __init__(self):
        self.backup_file = Path("/tmp/hardcoded_users_migration_backup.json")
        self.migrated_users: List[Dict[str, Any]] = []

    async def create_backup(self, db: AsyncSession) -> None:
        """Create backup of current hardcoded users state"""
        print("📦 Creating backup of hardcoded users...")

        # Define hardcoded emails to backup
        hardcoded_emails = [
            settings.SEED_ADMIN_EMAIL or "admin@proyectosemilla.dev",
            settings.SEED_DEMO_EMAIL or "demo@demo-company.com",
            "admin@example.com"  # Legacy
        ]

        backup_data = {
            "timestamp": str(asyncio.get_event_loop().time()),
            "hardcoded_emails": hardcoded_emails,
            "users": []
        }

        for email in hardcoded_emails:
            user_result = await db.execute(
                select(User.id, User.email, User.first_name, User.last_name, User.is_active)
                .where(User.email == email)
            )
            user_row = user_result.first()

            if user_row:
                user_data = {
                    "id": str(user_row[0]),
                    "email": user_row[1],
                    "first_name": user_row[2],
                    "last_name": user_row[3],
                    "is_active": user_row[4]
                }
                backup_data["users"].append(user_data)

        # Save backup
        with open(self.backup_file, 'w') as f:
            json.dump(backup_data, f, indent=2, default=str)

        print(f"✅ Backup created: {self.backup_file}")
        print(f"   Backed up {len(backup_data['users'])} users")

    async def migrate_users(self, db: AsyncSession) -> int:
        """Migrate hardcoded users to system flags"""
        print("🔄 Migrating hardcoded users to system flags...")

        migrated_count = await SystemUserService.migrate_legacy_hardcoded_users(db)

        if migrated_count > 0:
            print(f"✅ Migrated {migrated_count} users to system flags")
            self.migrated_users = await SystemUserService.get_system_users_info(db)
        else:
            print("ℹ️  No users needed migration")

        return migrated_count

    async def validate_migration(self, db: AsyncSession) -> bool:
        """Validate that migration was successful"""
        print("🔍 Validating migration...")

        # Check that system user flags exist
        system_users_count = await SystemUserService.get_system_users_count(db)
        if system_users_count == 0:
            print("❌ No system user flags found after migration")
            return False

        # Check that setup status works with new system
        from app.api.v1.endpoints.auth import get_setup_status
        try:
            status_result = await get_setup_status(db=db)
            if "migration_enabled" not in status_result:
                print("❌ Setup status not returning migration info")
                return False
        except Exception as e:
            print(f"❌ Setup status failed: {e}")
            return False

        print("✅ Migration validation passed")
        return True

    async def enable_migration_flag(self) -> None:
        """Enable the migration feature flag"""
        print("🚩 Enabling migration feature flag...")

        env_file = Path(".env")
        if not env_file.exists():
            print("⚠️  .env file not found, creating with migration enabled")
            with open(env_file, 'w') as f:
                f.write("HARDCODED_USERS_MIGRATION_ENABLED=true\n")
            return

        # Read current .env
        with open(env_file, 'r') as f:
            lines = f.readlines()

        # Check if flag already exists
        flag_found = False
        for i, line in enumerate(lines):
            if line.startswith("HARDCODED_USERS_MIGRATION_ENABLED"):
                lines[i] = "HARDCODED_USERS_MIGRATION_ENABLED=true\n"
                flag_found = True
                break

        if not flag_found:
            lines.append("HARDCODED_USERS_MIGRATION_ENABLED=true\n")

        # Write back
        with open(env_file, 'w') as f:
            f.writelines(lines)

        print("✅ Migration feature flag enabled")

    async def rollback_migration(self, db: AsyncSession) -> None:
        """Rollback migration if needed"""
        print("🔙 Rolling back migration...")

        # Remove all system user flags
        await db.execute(text("DELETE FROM system_user_flags"))
        await db.commit()

        # Disable migration flag
        env_file = Path(".env")
        if env_file.exists():
            with open(env_file, 'r') as f:
                lines = f.readlines()

            for i, line in enumerate(lines):
                if line.startswith("HARDCODED_USERS_MIGRATION_ENABLED"):
                    lines[i] = "HARDCODED_USERS_MIGRATION_ENABLED=false\n"
                    break

            with open(env_file, 'w') as f:
                f.writelines(lines)

        print("✅ Migration rolled back")

    async def show_migration_summary(self, db: AsyncSession) -> None:
        """Show summary of migration results"""
        print("\n" + "="*60)
        print("📋 MIGRATION SUMMARY")
        print("="*60)

        system_users = await SystemUserService.get_system_users_info(db)

        print(f"Total system users: {len(system_users)}")
        for user in system_users:
            print(f"  • {user['email']} ({user['flag_type']}) - {'Active' if user['is_active'] else 'Inactive'}")

        print(f"\nMigration enabled: {settings.HARDCODED_USERS_MIGRATION_ENABLED}")
        print(f"Backup file: {self.backup_file}")

        if self.backup_file.exists():
            print("✅ Backup available for rollback")
        else:
            print("⚠️  No backup file found")


async def main():
    """Main migration function"""
    if len(sys.argv) < 2:
        print("Usage: python migrate_hardcoded_users.py [migrate|rollback|status|backup]")
        print("  migrate - Run the migration")
        print("  rollback - Rollback the migration")
        print("  status - Show migration status")
        print("  backup - Create backup only")
        sys.exit(1)

    command = sys.argv[1]

    # Validate environment
    if command in ["migrate", "rollback"] and not os.getenv("DB_PASSWORD"):
        print("❌ DB_PASSWORD environment variable is required")
        sys.exit(1)

    migrator = HardcodedUsersMigrator()
    db = await get_db().__anext__()

    try:
        if command == "backup":
            await migrator.create_backup(db)
        elif command == "migrate":
            await migrator.create_backup(db)
            migrated_count = await migrator.migrate_users(db)
            if migrated_count > 0:
                if await migrator.validate_migration(db):
                    await migrator.enable_migration_flag()
                    print("🎉 Migration completed successfully!")
                else:
                    print("❌ Migration validation failed")
                    sys.exit(1)
            else:
                print("ℹ️  No migration needed")
        elif command == "rollback":
            await migrator.rollback_migration(db)
            print("✅ Migration rolled back")
        elif command == "status":
            await migrator.show_migration_summary(db)
        else:
            print(f"Unknown command: {command}")
            sys.exit(1)

    except Exception as e:
        print(f"❌ Migration failed: {e}")
        sys.exit(1)
    finally:
        await db.close()


if __name__ == "__main__":
    asyncio.run(main())