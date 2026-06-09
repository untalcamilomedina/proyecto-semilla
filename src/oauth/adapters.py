from allauth.socialaccount.adapter import DefaultSocialAccountAdapter


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
        return super().save_user(request, sociallogin, form)
