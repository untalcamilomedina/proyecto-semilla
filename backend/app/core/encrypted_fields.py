"""
Encrypted Fields Mixin for SQLAlchemy models
Provides automatic encryption/decryption for sensitive fields
"""

from sqlalchemy import Column, String, Text
from sqlalchemy.ext.declarative import declared_attr
from sqlalchemy.orm import validates
from typing import Any, Optional
import json


class EncryptedFieldMixin:
    """
    Mixin to add encrypted field functionality to SQLAlchemy models
    """

    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)
        # Add validation for encrypted fields
        for field_name in getattr(cls, '_encrypted_fields', []):
            setattr(cls, field_name, declared_attr(lambda self, field=field_name: Column(Text, nullable=True)))

    @staticmethod
    def _get_encryption_manager():
        """Get the data encryption manager"""
        from app.core.security_policies import data_encryption_manager
        return data_encryption_manager

    def _encrypt_value(self, value: Any, key_type: str = "user_data") -> str:
        """Encrypt a value"""
        if value is None:
            return None
        if isinstance(value, (dict, list)):
            value = json.dumps(value)
        elif not isinstance(value, str):
            value = str(value)

        return self._get_encryption_manager().encrypt_sensitive_data(value, key_type)

    def _decrypt_value(self, encrypted_value: str, key_type: str = "user_data") -> Any:
        """Decrypt a value"""
        if encrypted_value is None:
            return None

        decrypted = self._get_encryption_manager().decrypt_sensitive_data(encrypted_value, key_type)

        # Try to parse as JSON
        try:
            return json.loads(decrypted)
        except (json.JSONDecodeError, TypeError):
            return decrypted


class EncryptedStringField(Column):
    """
    Custom column type for encrypted strings
    """

    def __init__(self, *args, key_type: str = "user_data", **kwargs):
        super().__init__(String, *args, **kwargs)
        self.key_type = key_type

    def process_bind_param(self, value, dialect):
        """Encrypt value before storing"""
        if value is None:
            return None
        from app.core.security_policies import data_encryption_manager
        return data_encryption_manager.encrypt_sensitive_data(str(value), self.key_type)

    def process_result_value(self, value, dialect):
        """Decrypt value when retrieving"""
        if value is None:
            return None
        from app.core.security_policies import data_encryption_manager
        return data_encryption_manager.decrypt_sensitive_data(value, self.key_type)


class EncryptedTextField(Column):
    """
    Custom column type for encrypted text
    """

    def __init__(self, *args, key_type: str = "user_data", **kwargs):
        super().__init__(Text, *args, **kwargs)
        self.key_type = key_type

    def process_bind_param(self, value, dialect):
        """Encrypt value before storing"""
        if value is None:
            return None
        from app.core.security_policies import data_encryption_manager
        return data_encryption_manager.encrypt_sensitive_data(str(value), self.key_type)

    def process_result_value(self, value, dialect):
        """Decrypt value when retrieving"""
        if value is None:
            return None
        from app.core.security_policies import data_encryption_manager
        return data_encryption_manager.decrypt_sensitive_data(value, self.key_type)


# Example usage in models:
"""
class SensitiveUserData(Base, EncryptedFieldMixin):
    __tablename__ = "sensitive_user_data"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    tenant_id = Column(UUID(as_uuid=True), ForeignKey("tenants.id"), nullable=False)

    # Encrypted fields
    ssn = EncryptedStringField(255, key_type="user_data")  # Social Security Number
    credit_card = EncryptedStringField(255, key_type="financial_data")  # Credit card info
    medical_history = EncryptedTextField(key_type="health_data")  # Medical data

    # Regular fields
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    data_type = Column(String(50), nullable=False)  # 'ssn', 'credit_card', 'medical'

    # Metadata
    encrypted_at = Column(DateTime(timezone=True), nullable=False, default=datetime.utcnow)
    created_at = Column(DateTime(timezone=True), nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime(timezone=True), nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)
"""


# Utility functions for manual encryption/decryption
def encrypt_field_value(value: Any, key_type: str = "user_data") -> str:
    """Utility function to encrypt a field value"""
    from app.core.security_policies import data_encryption_manager
    if value is None:
        return None
    if isinstance(value, (dict, list)):
        value = json.dumps(value)
    elif not isinstance(value, str):
        value = str(value)
    return data_encryption_manager.encrypt_sensitive_data(value, key_type)


def decrypt_field_value(encrypted_value: str, key_type: str = "user_data") -> Any:
    """Utility function to decrypt a field value"""
    from app.core.security_policies import data_encryption_manager
    if encrypted_value is None:
        return None
    decrypted = data_encryption_manager.decrypt_sensitive_data(encrypted_value, key_type)
    try:
        return json.loads(decrypted)
    except (json.JSONDecodeError, TypeError):
        return decrypted


# Migration helper for existing data
def migrate_unencrypted_data(model_class, field_name: str, key_type: str = "user_data"):
    """
    Migrate unencrypted data to encrypted format
    This should be run as a one-time migration
    """
    from app.core.database import get_db
    import asyncio

    async def migrate():
        async for db in get_db():
            # Get all records with unencrypted data
            records = await db.execute(f"SELECT id, {field_name} FROM {model_class.__tablename__} WHERE {field_name} IS NOT NULL")
            rows = records.fetchall()

            for row in rows:
                record_id = row[0]
                unencrypted_value = row[1]

                # Skip if already encrypted (simple heuristic)
                if unencrypted_value and not unencrypted_value.startswith('gAAAAA'):  # Fernet prefix
                    encrypted_value = encrypt_field_value(unencrypted_value, key_type)

                    # Update the record
                    await db.execute(
                        f"UPDATE {model_class.__tablename__} SET {field_name} = $1 WHERE id = $2",
                        (encrypted_value, record_id)
                    )

            await db.commit()
            break

    # Run migration
    asyncio.run(migrate())