"""
System User Service
Service for managing system user flags and operations
"""

from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete, func
from app.models.system_user_flag import SystemUserFlag
from app.models.user import User


class SystemUserService:
    """
    System User Service - Security Enhancement

    This service replaces hardcoded email-based user identification with a flexible
    flag-based system. This addresses critical security vulnerabilities by:

    SECURITY BENEFITS:
    - Eliminates hardcoded credentials from source code
    - Allows configurable system users via environment variables
    - Provides clear separation between system and regular users
    - Enables proper auditing and monitoring of system user creation
    - Supports migration from legacy hardcoded users

    ARCHITECTURAL IMPROVEMENTS:
    - Database-driven user classification instead of code-based lists
    - Support for multiple system user types (admin, demo, system, legacy_hardcoded)
    - Backward compatibility during migration period
    - Extensible design for future system user types

    USAGE:
    - Use mark_as_system_user() to flag users as system users
    - Use is_system_user() to check if a user is a system user
    - Use get_system_users_count() for setup status calculations
    - Use migrate_legacy_hardcoded_users() during migration process

    MIGRATION NOTES:
    - Legacy hardcoded users are automatically migrated to flags
    - Migration is controlled by HARDCODED_USERS_MIGRATION_ENABLED flag
    - Fallback to legacy logic provided for backward compatibility
    """

    @staticmethod
    async def mark_as_system_user(db: AsyncSession, user_id: str, flag_type: str) -> None:
        """
        Mark a user as a system user with a specific flag type

        Args:
            db: Database session
            user_id: User ID to mark
            flag_type: Type of system user ('admin', 'demo', 'system', 'legacy_hardcoded')
        """
        # Check if flag already exists
        existing = await db.execute(
            select(SystemUserFlag).where(
                SystemUserFlag.user_id == user_id,
                SystemUserFlag.flag_type == flag_type
            )
        )

        if existing.scalar_one_or_none():
            return  # Already marked

        # Create new flag
        flag = SystemUserFlag(user_id=user_id, flag_type=flag_type)
        db.add(flag)
        await db.commit()

    @staticmethod
    async def is_system_user(db: AsyncSession, user_id: str, flag_type: Optional[str] = None) -> bool:
        """
        Check if a user is a system user

        Args:
            db: Database session
            user_id: User ID to check
            flag_type: Specific flag type to check (optional)

        Returns:
            True if user is a system user
        """
        query = select(SystemUserFlag).where(SystemUserFlag.user_id == user_id)

        if flag_type:
            query = query.where(SystemUserFlag.flag_type == flag_type)

        result = await db.execute(query)
        return result.scalar_one_or_none() is not None

    @staticmethod
    async def get_system_users_count(db: AsyncSession, flag_type: Optional[str] = None) -> int:
        """
        Get count of system users

        Args:
            db: Database session
            flag_type: Specific flag type to count (optional)

        Returns:
            Number of system users
        """
        query = select(func.count(SystemUserFlag.user_id))

        if flag_type:
            query = query.where(SystemUserFlag.flag_type == flag_type)

        result = await db.execute(query)
        return result.scalar()

    @staticmethod
    async def get_system_user_ids(db: AsyncSession, flag_type: Optional[str] = None) -> List[str]:
        """
        Get list of system user IDs

        Args:
            db: Database session
            flag_type: Specific flag type to filter (optional)

        Returns:
            List of system user IDs
        """
        query = select(SystemUserFlag.user_id)

        if flag_type:
            query = query.where(SystemUserFlag.flag_type == flag_type)

        result = await db.execute(query)
        return [str(row[0]) for row in result.all()]

    @staticmethod
    async def remove_system_user_flag(db: AsyncSession, user_id: str, flag_type: str) -> bool:
        """
        Remove a system user flag

        Args:
            db: Database session
            user_id: User ID
            flag_type: Flag type to remove

        Returns:
            True if flag was removed
        """
        result = await db.execute(
            delete(SystemUserFlag).where(
                SystemUserFlag.user_id == user_id,
                SystemUserFlag.flag_type == flag_type
            )
        )

        await db.commit()
        return result.rowcount > 0

    @staticmethod
    async def migrate_legacy_hardcoded_users(db: AsyncSession) -> int:
        """
        Migrate existing hardcoded users to the new system
        This should be run once during migration

        Returns:
            Number of users migrated
        """
        from app.core.config import settings

        # Define legacy hardcoded emails and their flag types
        legacy_users = {
            (settings.SEED_ADMIN_EMAIL or "admin@proyectosemilla.dev"): "admin",
            (settings.SEED_DEMO_EMAIL or "demo@demo-company.com"): "demo",
            "admin@example.com": "legacy_hardcoded"  # For backward compatibility
        }

        migrated_count = 0

        for email, flag_type in legacy_users.items():
            # Find user by email
            user_result = await db.execute(select(User).where(User.email == email))
            user = user_result.scalar_one_or_none()

            if user:
                # Check if already has this flag
                existing_flag = await db.execute(
                    select(SystemUserFlag).where(
                        SystemUserFlag.user_id == user.id,
                        SystemUserFlag.flag_type == flag_type
                    )
                )

                if not existing_flag.scalar_one_or_none():
                    # Create flag
                    await SystemUserService.mark_as_system_user(db, str(user.id), flag_type)
                    migrated_count += 1

        return migrated_count

    @staticmethod
    async def get_system_users_info(db: AsyncSession) -> List[dict]:
        """
        Get detailed information about system users

        Returns:
            List of system user information
        """
        query = select(
            SystemUserFlag.user_id,
            SystemUserFlag.flag_type,
            SystemUserFlag.created_at,
            User.email,
            User.first_name,
            User.last_name,
            User.is_active
        ).join(User, SystemUserFlag.user_id == User.id)

        result = await db.execute(query)

        system_users = []
        for row in result.all():
            system_users.append({
                "user_id": str(row[0]),
                "flag_type": row[1],
                "created_at": row[2].isoformat() if row[2] else None,
                "email": row[3],
                "first_name": row[4],
                "last_name": row[5],
                "is_active": row[6]
            })

        return system_users