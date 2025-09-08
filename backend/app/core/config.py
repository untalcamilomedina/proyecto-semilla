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
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 8  # 8 days

    # Server Configuration
    SERVER_NAME: str = "Proyecto Semilla"
    SERVER_HOST: AnyHttpUrl = "http://localhost"
    DEBUG: bool = True

    # CORS Configuration
    BACKEND_CORS_ORIGINS: List[AnyHttpUrl] = [
        "http://localhost:3000",  # Next.js dev server
        "http://localhost:3001",  # Next.js dev server (alternative port)
        "http://localhost:3002",  # Next.js dev server (alternative port)
        "http://localhost:8000",  # FastAPI server
    ]

    @field_validator("BACKEND_CORS_ORIGINS", mode="before")
    @classmethod
    def assemble_cors_origins(
        cls, v: Union[str, List[str]]
    ) -> Union[List[str], str]:
        if isinstance(v, str) and not v.startswith("["):
            return [i.strip() for i in v.split(",")]
        elif isinstance(v, (list, str)):
            return v
        raise ValueError(v)

    # Trusted Hosts
    ALLOWED_HOSTS: List[str] = ["localhost", "127.0.0.1"]

    # Database Configuration
    DATABASE_URL: str = os.getenv("DATABASE_URL", "postgresql://admin:changeme123@localhost:5432/proyecto_semilla")

    # Redis Configuration
    REDIS_URL: str = "redis://localhost:6379"
    
    # Rate Limiting Configuration
    RATE_LIMIT_REQUESTS: int = 100  # requests per window
    RATE_LIMIT_WINDOW: int = 60  # seconds

    # JWT Configuration
    JWT_SECRET: str = "your_jwt_secret_key_here_change_this_in_production"
    JWT_ALGORITHM: str = "HS256"
    REFRESH_TOKEN_EXPIRE_DAYS: int = 30

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

    class Config:
        env_file = ".env"
        case_sensitive = True


# Create global settings instance
settings = Settings()