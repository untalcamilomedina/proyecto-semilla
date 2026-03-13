"""
Fernet-based field encryption for sensitive data stored in the database.

Uses Django's SECRET_KEY to derive an encryption key via PBKDF2.
All encrypted values are stored as base64-encoded strings prefixed with 'enc::'.
"""

from __future__ import annotations

import base64
import hashlib
import os

from cryptography.fernet import Fernet
from django.conf import settings
from django.db import models


def _derive_key() -> bytes:
    """Derive a Fernet key from Django SECRET_KEY using PBKDF2."""
    salt = hashlib.sha256(settings.SECRET_KEY.encode()).digest()[:16]
    key_material = hashlib.pbkdf2_hmac(
        "sha256",
        settings.SECRET_KEY.encode(),
        salt,
        iterations=100_000,
        dklen=32,
    )
    return base64.urlsafe_b64encode(key_material)


def encrypt_value(plaintext: str) -> str:
    """Encrypt a plaintext string and return prefixed ciphertext."""
    if not plaintext:
        return ""
    f = Fernet(_derive_key())
    ciphertext = f.encrypt(plaintext.encode("utf-8"))
    return f"enc::{ciphertext.decode('utf-8')}"


def decrypt_value(stored: str) -> str:
    """Decrypt a stored value. Returns plaintext or original if not encrypted."""
    if not stored or not stored.startswith("enc::"):
        return stored
    ciphertext = stored[5:]  # strip 'enc::' prefix
    f = Fernet(_derive_key())
    return f.decrypt(ciphertext.encode("utf-8")).decode("utf-8")


class EncryptedCharField(models.CharField):
    """CharField that encrypts values before saving to the database.

    Usage:
        api_key = EncryptedCharField(max_length=512, blank=True, default="")

    Values are stored as 'enc::<fernet_ciphertext>' in the DB.
    On read, they are automatically decrypted.
    """

    def get_prep_value(self, value: str | None) -> str:
        """Encrypt before saving to DB."""
        value = super().get_prep_value(value)
        if value and not value.startswith("enc::"):
            return encrypt_value(value)
        return value or ""

    def from_db_value(self, value: str | None, expression, connection) -> str:
        """Decrypt when reading from DB."""
        if value is None:
            return ""
        return decrypt_value(value)

    def value_from_object(self, obj) -> str:
        """Return decrypted value for serialization."""
        value = super().value_from_object(obj)
        return decrypt_value(value) if value else ""
