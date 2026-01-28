from allauth.socialaccount.adapter import DefaultSocialAccountAdapter
from allauth.socialaccount.models import SocialAccount

class CustomSocialAccountAdapter(DefaultSocialAccountAdapter):
    """
    Custom adapter to handle specific logic during social login/signup.
    """

    def populate_user(self, request, sociallogin, data):
        """
        Populate user instance with data from social provider.
        """
        user = super().populate_user(request, sociallogin, data)
        # Add custom logic here if needed, e.g. grabbing specific metadata
        return user

    def save_user(self, request, sociallogin, form=None):
        """
        Called when a user is being saved during the signup flow.
        """
        user = super().save_user(request, sociallogin, form)
        
        # If connecting Notion, we might want to store extra data from extra_data
        if sociallogin.account.provider == 'notion':
            # Example: Store workspace_name or workspace_icon if available in extra_data
            pass
            
        return user
