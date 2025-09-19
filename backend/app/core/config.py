"""
Configuration settings for Proyecto Semilla Backend
Uses Pydantic settings for environment variable management
"""

import secrets
import os
from typing import List, Optional, Union

from pydantic import AnyHttpUrl, field_validator, ValidationInfo
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """
    Application settings with environment variable support
    """

    # API Configuration
    API_V1_STR: str = "/api/v1"
    SECRET_KEY: str = secrets.token_urlsafe(32)
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60  # 1 hour for better security

    # Server Configuration
    SERVER_NAME: str = "Proyecto Semilla"
    SERVER_HOST: AnyHttpUrl = "http://localhost"
    DEBUG: bool = True

    # CORS Configuration
    # Pydantic will automatically read a comma-separated string from the environment
    # variable `BACKEND_CORS_ORIGINS` and convert it into a list of strings.
    # The default list below is used if the environment variable is not set.
    BACKEND_CORS_ORIGINS: List[str] = [
        "http://localhost:3000",
        "http://localhost:8000",
        "http://localhost:7701",
        "http://localhost:7777",
    ]

    # This field is added to prevent Pydantic from throwing an "extra inputs not permitted"
    # error if a stray CORS_ORIGINS environment variable is present. It is not used by the application.
    CORS_ORIGINS: Optional[str] = None

    # Trusted Hosts
    ALLOWED_HOSTS: List[str] = ["localhost", "127.0.0.1", "proyecto-semilla.local", "api.proyecto-semilla.local", "backend"]

    # Database Configuration
    DB_HOST: str = os.getenv("DB_HOST", "db")
    DB_PORT: int = int(os.getenv("DB_PORT", "5432"))
    DB_NAME: str = os.getenv("DB_NAME", "proyecto_semilla")
    DB_USER: str = os.getenv("DB_USER", "admin")
    DB_PASSWORD: str = os.getenv("DB_PASSWORD", "")

    @property
    def DATABASE_URL(self) -> str:
        """Construct database URL from environment variables"""
        if not self.DB_PASSWORD:
            raise ValueError("DB_PASSWORD environment variable is required")
        return f"postgresql://{self.DB_USER}:{self.DB_PASSWORD}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"

    # Redis Configuration
    REDIS_URL: str = os.getenv("REDIS_URL", "redis://redis:6379")

    # Rate Limiting Configuration
    RATE_LIMIT_REQUESTS: int = int(os.getenv("RATE_LIMIT_REQUESTS", "100"))
    RATE_LIMIT_WINDOW: int = int(os.getenv("RATE_LIMIT_WINDOW", "60"))

    # JWT Configuration
    JWT_SECRET: str = os.getenv("JWT_SECRET", "")
    JWT_ALGORITHM: str = "HS256"
    REFRESH_TOKEN_EXPIRE_DAYS: int = int(os.getenv("REFRESH_TOKEN_EXPIRE_DAYS", "30"))

    @field_validator("JWT_SECRET", mode="after")
    @classmethod
    def validate_jwt_secret(cls, v: str) -> str:
        """Validate JWT secret is properly configured"""
        if not v or v == "your_jwt_secret_key_here_change_this_in_production":
            raise ValueError("JWT_SECRET must be set to a secure value in environment variables")
        if len(v) < 32:
            raise ValueError("JWT_SECRET must be at least 32 characters long")
        return v

    # Email Configuration (future)
    SMTP_TLS: bool = True
    SMTP_PORT: Optional[int] = None
    SMTP_HOST: Optional[str] = None
    SMTP_USER: Optional[str] = None
    SMTP_PASSWORD: Optional[str] = None
    EMAILS_FROM_EMAIL: Optional[str] = "noreply@proyectosemilla.dev"
    EMAILS_FROM_NAME: Optional[str] = "Proyecto Semilla"

    # Logging
    LOG_LEVEL: str = "INFO"
    LOG_FORMAT: str = "json"  # json or text

    # Frontend Configuration
    NEXT_PUBLIC_API_URL: str = "http://localhost:7777"

    # Cookie Configuration
    COOKIE_SECURE: bool = False  # Set to True in production with HTTPS
    COOKIE_DOMAIN: str = ""  # Empty for localhost, set to domain in production
    COOKIE_SAME_SITE: str = "lax"

    # Seed Data Configuration
    SEED_ADMIN_PASSWORD: str = "admin123"
    SEED_DEMO_PASSWORD: str = "demo123"

    class Config:
        env_file = ".env"
        case_sensitive = True


# Create global settings instance
settings = Settings()