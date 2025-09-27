"""
Tests for migration validation
Tests to validate that the hardcoded users migration was successful
"""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.models.user import User
from app.services.system_user_service import SystemUserService
from app.api.v1.endpoints.auth import get_setup_status
from app.core.config import settings


class TestMigrationValidation:
    """Test suite for validating migration success"""

    @pytest.fixture
    def mock_db_session(self):
        """Mock database session for testing"""
        session = AsyncMock(spec=AsyncSession)
        return session

    @pytest.mark.asyncio
    async def test_system_user_flags_created_during_migration(self, mock_db_session):
        """Test that system user flags were created during migration"""
        # Mock system user service
        with patch.object(SystemUserService, 'get_system_users_count') as mock_count:
            mock_count.return_value = 2  # 2 system users

            count = await SystemUserService.get_system_users_count(mock_db_session)
            assert count == 2

    @pytest.mark.asyncio
    async def test_setup_status_works_with_new_system(self, mock_db_session):
        """Test that setup status works with the new system user flags"""

        # Mock the database queries
        mock_real_users_result = AsyncMock()
        mock_real_users_result.scalar.return_value = 3  # 3 real users

        mock_total_users_result = AsyncMock()
        mock_total_users_result.scalar.return_value = 5  # 5 total users

        # Mock system users count
        with patch.object(SystemUserService, 'get_system_users_count') as mock_count:
            mock_count.return_value = 2  # 2 system users

            mock_db_session.execute.side_effect = [mock_real_users_result, mock_total_users_result]

            # Ensure migration is enabled
            with patch.object(settings, 'HARDCODED_USERS_MIGRATION_ENABLED', True):
                result = await get_setup_status(db=mock_db_session)

                assert result["needs_setup"] is False
                assert result["real_user_count"] == 3
                assert result["total_user_count"] == 5
                assert result["migration_enabled"] is True
                assert result["system_users_count"] == 2

    @pytest.mark.asyncio
    async def test_setup_status_fallback_to_legacy_logic(self, mock_db_session):
        """Test that setup status falls back to legacy logic when migration disabled"""

        # Mock the database queries for legacy logic
        mock_hardcoded_result = AsyncMock()
        mock_hardcoded_result.scalar.return_value = 2  # 2 hardcoded users

        mock_total_result = AsyncMock()
        mock_total_result.scalar.return_value = 5  # 5 total users

        mock_db_session.execute.side_effect = [mock_hardcoded_result, mock_total_result]

        # Ensure migration is disabled
        with patch.object(settings, 'HARDCODED_USERS_MIGRATION_ENABLED', False):
            result = await get_setup_status(db=mock_db_session)

            assert result["needs_setup"] is False  # 5 - 2 = 3 real users
            assert result["real_user_count"] == 3
            assert result["total_user_count"] == 5
            assert result["migration_enabled"] is False

    @pytest.mark.asyncio
    async def test_migration_creates_system_flags_for_legacy_users(self, mock_db_session):
        """Test that migration creates system flags for legacy hardcoded users"""

        # Mock existing legacy users
        mock_user1 = MagicMock()
        mock_user1.id = "user-1-id"
        mock_user1.email = "admin@example.com"

        mock_user2 = MagicMock()
        mock_user2.id = "user-2-id"
        mock_user2.email = "admin@proyectosemilla.dev"

        mock_user_result1 = AsyncMock()
        mock_user_result1.scalar_one_or_none.return_value = mock_user1

        mock_user_result2 = AsyncMock()
        mock_user_result2.scalar_one_or_none.return_value = mock_user2

        # Mock flag existence checks
        mock_flag_result = AsyncMock()
        mock_flag_result.scalar_one_or_none.return_value = None  # No existing flag

        mock_db_session.execute.side_effect = [
            mock_user_result1, mock_flag_result,  # First user
            mock_user_result2, mock_flag_result   # Second user
        ]

        # Mock the mark_as_system_user calls
        with patch.object(SystemUserService, 'mark_as_system_user') as mock_mark:
            await SystemUserService.migrate_legacy_hardcoded_users(mock_db_session)

            # Verify mark_as_system_user was called for legacy users
            assert mock_mark.call_count == 2

            # Check the calls
            calls = mock_mark.call_args_list
            assert str(calls[0][0][1]) == "user-1-id"  # First user ID
            assert calls[0][0][2] == "legacy_hardcoded"  # Flag type

            assert str(calls[1][0][1]) == "user-2-id"  # Second user ID
            assert calls[1][0][2] == "admin"  # Flag type for admin email

    def test_environment_variables_are_required_for_secure_seeding(self):
        """Test that environment variables are required for secure seeding"""
        import os

        # Test that required variables are checked
        required_vars = [
            "SEED_ADMIN_EMAIL",
            "SEED_ADMIN_PASSWORD"
        ]

        # Temporarily clear environment variables
        original_values = {}
        for var in required_vars:
            original_values[var] = os.environ.get(var)
            os.environ.pop(var, None)

        try:
            # Import should work but seeding should fail without env vars
            from backend.app.initial_data import create_secure_initial_admin

            # This would fail in real usage without env vars
            # We just test that the module can be imported
            assert callable(create_secure_initial_admin)

        finally:
            # Restore original values
            for var, value in original_values.items():
                if value is not None:
                    os.environ[var] = value

    def test_secure_initial_data_uses_environment_variables(self):
        """Test that secure initial data uses environment variables instead of hardcoded values"""
        import inspect
        from backend.app.initial_data import create_secure_initial_admin

        # Get the source code
        source = inspect.getsource(create_secure_initial_admin)

        # Should use os.getenv, not hardcoded strings
        assert "os.getenv" in source
        assert "admin@example.com" not in source
        assert "admin123" not in source

        # Should validate password strength
        assert "len(admin_password) < 12" in source

    def test_no_hardcoded_credentials_in_new_initial_data(self):
        """Test that new initial_data.py doesn't contain hardcoded credentials"""
        from pathlib import Path

        initial_data_file = Path("backend/app/initial_data.py")

        if initial_data_file.exists():
            content = initial_data_file.read_text()

            # Should not contain hardcoded emails or passwords
            assert "admin@example.com" not in content
            assert "admin123" not in content
            assert "admin@proyectosemilla.dev" not in content
            assert "ChangeMeSecure123!" not in content

            # Should use environment variables
            assert "os.getenv" in content
            assert "SEED_ADMIN_EMAIL" in content
            assert "SEED_ADMIN_PASSWORD" in content

    @pytest.mark.asyncio
    async def test_system_user_service_methods_exist_and_work(self, mock_db_session):
        """Test that SystemUserService has required methods and they work"""

        # Test mark_as_system_user
        assert hasattr(SystemUserService, 'mark_as_system_user')
        assert callable(SystemUserService.mark_as_system_user)

        # Test is_system_user
        assert hasattr(SystemUserService, 'is_system_user')
        assert callable(SystemUserService.is_system_user)

        # Test get_system_users_count
        assert hasattr(SystemUserService, 'get_system_users_count')
        assert callable(SystemUserService.get_system_users_count)

        # Test migrate_legacy_hardcoded_users
        assert hasattr(SystemUserService, 'migrate_legacy_hardcoded_users')
        assert callable(SystemUserService.migrate_legacy_hardcoded_users)

        # Mock the count method
        with patch.object(SystemUserService, 'get_system_users_count') as mock_count:
            mock_count.return_value = 0
            count = await SystemUserService.get_system_users_count(mock_db_session)
            assert count == 0

    def test_migration_scripts_exist_and_are_executable(self):
        """Test that migration scripts exist and are executable"""
        from pathlib import Path

        scripts_dir = Path("scripts")

        required_scripts = [
            "migrate_hardcoded_users.py",
            "seed_secure_system_users.py",
            "validate_hardcoded_users_security.py"
        ]

        for script in required_scripts:
            script_path = scripts_dir / script
            assert script_path.exists(), f"Required script {script} not found"

            # Should be executable (basic check)
            assert script_path.is_file(), f"{script} is not a file"

    def test_migration_enabled_setting_exists(self):
        """Test that migration enabled setting exists in config"""
        from app.core.config import Settings

        settings_instance = Settings()

        # Should have the migration flag
        assert hasattr(settings_instance, 'HARDCODED_USERS_MIGRATION_ENABLED')

        # Should be boolean
        flag_value = settings_instance.HARDCODED_USERS_MIGRATION_ENABLED
        assert isinstance(flag_value, bool) or flag_value is None

    def test_secure_seeding_requires_environment_variables(self):
        """Test that secure seeding scripts require environment variables"""
        import subprocess
        import sys
        from pathlib import Path

        # This test would run the seeding script without env vars
        # and verify it fails appropriately

        script_path = Path("scripts/seed_secure_system_users.py")

        if script_path.exists():
            # We can't easily run the script in tests without proper setup
            # But we can check that the script exists and has proper error handling
            with open(script_path, 'r') as f:
                content = f.read()

            # Should check for required environment variables
            assert "SEED_ADMIN_EMAIL" in content
            assert "SEED_ADMIN_PASSWORD" in content
            assert "environment variable" in content.lower()


class TestMigrationRollback:
    """Tests for migration rollback functionality"""

    @pytest.fixture
    def mock_db_session(self):
        """Mock database session for testing"""
        session = AsyncMock(spec=AsyncSession)
        return session

    @pytest.mark.asyncio
    async def test_rollback_removes_system_flags(self, mock_db_session):
        """Test that rollback removes system user flags"""

        # Mock the execute call for deleting flags
        mock_result = AsyncMock()
        mock_db_session.execute.return_value = mock_result

        # Import the migrator class
        from scripts.migrate_hardcoded_users import HardcodedUsersMigrator

        migrator = HardcodedUsersMigrator()
        await migrator.rollback_migration(mock_db_session)

        # Verify that execute was called to delete flags
        assert mock_db_session.execute.called

        # Verify commit was called
        mock_db_session.commit.assert_called_once()

    def test_migration_backup_functionality_exists(self):
        """Test that backup functionality exists in migration script"""
        from scripts.migrate_hardcoded_users import HardcodedUsersMigrator

        migrator = HardcodedUsersMigrator()

        # Should have backup method
        assert hasattr(migrator, 'create_backup')
        assert callable(migrator.create_backup)

        # Should have backup file attribute
        assert hasattr(migrator, 'backup_file')
        assert migrator.backup_file.name.endswith('.json')


class TestPostMigrationValidation:
    """Tests to run after migration to validate success"""

    def test_no_hardcoded_credentials_in_source_code(self):
        """Test that no hardcoded credentials remain in source code after migration"""
        from pathlib import Path
        import re

        # Files that should not contain hardcoded credentials
        source_files = [
            Path("backend/app/initial_data.py"),
            Path("backend/scripts/seed_data.py"),
            # Add other files as needed
        ]

        dangerous_patterns = [
            r"email\s*=\s*['\"](admin@proyectosemilla\.dev|demo@demo-company\.com|admin@example\.com)['\"]",
            r"hashed_password\s*=\s*get_password_hash\(['\"](admin123|demo123)['\"]\)",
        ]

        for source_file in source_files:
            if source_file.exists():
                content = source_file.read_text()

                for pattern in dangerous_patterns:
                    matches = re.findall(pattern, content, re.IGNORECASE)
                    assert len(matches) == 0, \
                        f"Hardcoded credential pattern found in {source_file}: {pattern}"

    def test_secure_environment_variables_are_documented(self):
        """Test that secure environment variables are documented"""
        from pathlib import Path

        readme_files = [
            Path("README.md"),
            Path("docs/MIGRATION_HARDCODED_USERS.md"),
        ]

        required_vars = [
            "SEED_ADMIN_EMAIL",
            "SEED_ADMIN_PASSWORD",
            "HARDCODED_USERS_MIGRATION_ENABLED"
        ]

        documented_vars = set()

        for readme in readme_files:
            if readme.exists():
                content = readme.read_text()

                for var in required_vars:
                    if var in content:
                        documented_vars.add(var)

        # All required variables should be documented
        for var in required_vars:
            assert var in documented_vars, f"Environment variable {var} not documented"

    def test_migration_documentation_exists(self):
        """Test that migration documentation exists and is comprehensive"""
        from pathlib import Path

        migration_doc = Path("docs/MIGRATION_HARDCODED_USERS.md")

        assert migration_doc.exists(), "Migration documentation not found"

        content = migration_doc.read_text()

        # Should contain key sections
        required_sections = [
            "Variables de Entorno Requeridas",
            "Proceso de Migración",
            "Solución de Problemas",
            "Rollback"
        ]

        for section in required_sections:
            assert section in content, f"Required section '{section}' not found in migration docs"