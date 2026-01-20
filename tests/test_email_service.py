import pytest
from django.core import mail
from core.models import User
from core.services.email import EmailService
from multitenant.models import Tenant
from core.models import Membership

@pytest.mark.django_db(transaction=True)
class TestEmailService:
    def test_send_welcome_email(self):
        user = User.objects.create_user(email="test@example.com", username="testuser", password="password")
        
        EmailService.send_welcome_email(user)
        
        assert len(mail.outbox) == 1
        assert mail.outbox[0].subject == "Welcome to Acme SaaS!"
        assert "test@example.com" in mail.outbox[0].body
        assert "test@example.com" in mail.outbox[0].to

    def test_send_invite_email(self):
        inviter = User.objects.create_user(email="inviter@example.com", username="inviter", password="password")
        invitee = User.objects.create_user(email="invitee@example.com", username="invitee", password="password")
        tenant = Tenant.objects.create(name="Test Org", slug="test-org")
        from core.models import Role
        role = Role.objects.create(organization=tenant, name="Member", slug="member")
        membership = Membership.objects.create(
            user=invitee,
            organization=tenant,
            role=role,
            is_active=False
        )
        # Mocking context attributes that might be missing if model doesn't support them directly
        membership.invited_by = inviter
        invite_url = "http://localhost:3000/invite/accept"
        
        EmailService.send_invite_email(membership, invite_url, inviter=inviter)
        
        assert len(mail.outbox) == 1
        # Check specific message
        message = mail.outbox[0]
        assert "Invitation to join" in message.subject
        assert "inviter@example.com has invited you" in message.body
        assert invite_url in message.body
