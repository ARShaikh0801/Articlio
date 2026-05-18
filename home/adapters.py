from allauth.socialaccount.adapter import DefaultSocialAccountAdapter
from allauth.account.adapter import DefaultAccountAdapter
from django.contrib.auth import get_user_model
import re

User = get_user_model()


class ArticlioAccountAdapter(DefaultAccountAdapter):
    """
    Custom account adapter.
    Redirects first-time OAuth users to the profile-completion page.
    """

    def get_login_redirect_url(self, request):
        user = request.user
        if hasattr(user, 'social_profile_completed') and not user.social_profile_completed:
            return '/complete-profile'
        return '/'


class ArticlioSocialAccountAdapter(DefaultSocialAccountAdapter):
    """
    Custom adapter for social (OAuth) logins.

    When a brand-new user signs up via Google / GitHub we need to:
    1. Populate `name` and `username` from what the provider gives us.
    2. Set `verified = True` - the provider already verified the email.
    3. Default `role` to 'reader' (the user will choose on the next page).
    4. Mark `social_profile_completed = False` so middleware redirects them
       to the profile-completion page on their first login.

    For returning users whose email already exists, we auto-connect the
    social account to the existing user (skipping allauth's ugly default
    signup form).
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

    def pre_social_login(self, request, sociallogin):
        """
        Auto-connect a social login to an existing user with the same email.

        Without this, allauth shows its default '/accounts/3rdparty/signup/'
        page when the email already exists, asking the user to manually link
        accounts. Since OAuth providers verify emails, it's safe to auto-merge.
        """
        if sociallogin.is_existing:
            return

        email = None
        if sociallogin.account.extra_data.get('email'):
            email = sociallogin.account.extra_data['email']
        elif sociallogin.email_addresses:
            email = sociallogin.email_addresses[0].email

        if not email:
            return

        try:
            existing_user = User.objects.get(email=email)
        except User.DoesNotExist:
            return  # New user — let save_user handle it

        # Auto-connect the social account to the existing user
        sociallogin.connect(request, existing_user)

    def save_user(self, request, sociallogin, form=None):
        user = super().save_user(request, sociallogin, form)

        extra_data = sociallogin.account.extra_data
        social_name = (
            extra_data.get('name')
            or f"{extra_data.get('given_name', '')} {extra_data.get('family_name', '')}".strip()
            or extra_data.get('login', '')
            or user.email.split('@')[0]
        )

        user.name = social_name
        user.username = self._generate_username(extra_data, user.email)
        user.verified = True
        user.role = 'reader'
        user.social_profile_completed = False
        user.save()

        return user