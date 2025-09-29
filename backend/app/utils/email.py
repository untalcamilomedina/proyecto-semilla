"""
Email utilities for Proyecto Semilla
Basic email functionality for password reset and notifications
"""

import logging
from typing import Optional
from app.core.config import settings

logger = logging.getLogger(__name__)


async def send_password_reset_email(email: str, reset_token: str) -> bool:
    """
    Send password reset email to user
    For now, this is a placeholder that logs the reset token
    In production, this would integrate with an email service like SendGrid, SES, etc.
    """
    try:
        # Generate reset URL (in production, this would be your frontend URL)
        reset_url = f"http://localhost:7701/reset-password?token={reset_token}"
        
        # Log the reset token for development (remove in production!)
        logger.info(f"Password reset email for {email}: {reset_url}")
        
        # In production, you would:
        # 1. Use an email service (SendGrid, SES, etc.)
        # 2. Send HTML email with proper styling
        # 3. Include security warnings and expiration time
        
        # For now, we'll just log it
        print(f"🔐 Password Reset Email")
        print(f"   To: {email}")
        print(f"   Reset URL: {reset_url}")
        print(f"   Token expires in 1 hour")
        
        return True
        
    except Exception as e:
        logger.error(f"Failed to send password reset email to {email}: {e}")
        return False


async def send_verification_email(email: str, user_id: str) -> bool:
    """
    Send email verification email to user
    """
    try:
        # Generate verification URL
        verification_url = f"http://localhost:7701/verify-email?user_id={user_id}"
        
        logger.info(f"Email verification for {email}: {verification_url}")
        
        print(f"📧 Email Verification")
        print(f"   To: {email}")
        print(f"   Verification URL: {verification_url}")
        
        return True
        
    except Exception as e:
        logger.error(f"Failed to send verification email to {email}: {e}")
        return False


async def send_welcome_email(email: str, first_name: str) -> bool:
    """
    Send welcome email to new user
    """
    try:
        logger.info(f"Welcome email for {email}")
        
        print(f"🎉 Welcome Email")
        print(f"   To: {email}")
        print(f"   Welcome {first_name} to Proyecto Semilla!")
        
        return True
        
    except Exception as e:
        logger.error(f"Failed to send welcome email to {email}: {e}")
        return False
