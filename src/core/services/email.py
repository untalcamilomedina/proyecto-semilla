from django.conf import settings
from django.core.mail import send_mail
from django.template.loader import render_to_string


class EmailService:
    @staticmethod
    def send_welcome_email(user):
        """
        Send a welcome email to a new user.
        """
        subject = "Welcome to Acme SaaS!"
        context = {
            "user": user, 
            "site_name": "Acme SaaS",
            "frontend_url": getattr(settings, "FRONTEND_URL", "http://localhost:3000")
        }
        html_message = render_to_string("emails/welcome.html", context)
        plain_message = render_to_string("emails/welcome.txt", context)
        
        send_mail(
            subject=subject,
            message=plain_message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[user.email],
            html_message=html_message,
        )

    @staticmethod
    def send_invite_email(membership, invite_url, inviter=None):
        """
        Send an invitation email to join a workspace.
        """
        subject = f"Invitation to join {membership.organization.name} on Acme SaaS"
        context = {
            "inviter": inviter,
            "organization": membership.organization,
            "invite_url": invite_url,
            "site_name": "Acme SaaS"
        }
        html_message = render_to_string("emails/invite.html", context)
        plain_message = render_to_string("emails/invite.txt", context)

        send_mail(
            subject=subject,
            message=plain_message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[membership.user.email],
            html_message=html_message,
        )
