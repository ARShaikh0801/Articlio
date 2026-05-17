from allauth.socialaccount.adapter import DefaultSocialAccountAdapter
from django.contrib.auth import get_user_model
import re

User = get_user_model()


class ArticlioSocialAccountAdapter(DefaultSocialAccountAdapter):
    """
    Custom adapter for social (OAuth) logins.

    When a brand-new user signs up via Google / GitHub we need to:
    1. Populate `name` and `username` from what the provider gives us.
    2. Set `verified = True` - the provider already verified the email.
    3. Default `role` to 'reader' (the user will choose on the next page).
    4. Mark `social_profile_completed = False` so middleware redirects them
       to the profile-completion page on their first login.
    """

    def _generate_username(self, extra_data, email):
        """Build a clean, unique username from social data."""
        # Try GitHub login, then given_name, then email prefix
        raw = (
            extra_data.get('login', '')            # GitHub
            or extra_data.get('given_name', '')     # Google
            or email.split('@')[0]
        )
        # Keep only alphanumeric, lowercase, max 10 chars
        base = re.sub(r'[^a-zA-Z0-9]', '', raw).lower()[:10]
        if not base:
            base = 'user'

        # Ensure uniqueness
        username = base
        counter = 1
        while User.objects.filter(username=username).exists():
            suffix = str(counter)
            username = base[:10 - len(suffix)] + suffix
            counter += 1

        return username

    def save_user(self, request, sociallogin, form=None):
        user = super().save_user(request, sociallogin, form)

        # Pull data from social account extra_data
        extra_data = sociallogin.account.extra_data
        social_name = (
            extra_data.get('name')
            or f"{extra_data.get('given_name', '')} {extra_data.get('family_name', '')}".strip()
            or extra_data.get('login', '')
            or user.email.split('@')[0]
        )

        user.name = social_name
        user.username = self._generate_username(extra_data, user.email)
        user.verified = True          # OAuth emails are already verified
        user.role = 'reader'          # Default - user picks on next page
        user.social_profile_completed = False
        user.save()

        return user

    def get_login_redirect_url(self, request):
        """Redirect first-time social users to the profile completion page."""
        user = request.user
        if hasattr(user, 'social_profile_completed') and not user.social_profile_completed:
            return '/complete-profile'
        return '/'

