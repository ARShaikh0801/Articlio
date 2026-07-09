
import secrets

class CSPMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        nonce = secrets.token_urlsafe(16)
        request.csp_nonce = nonce

        response = self.get_response(request)

        response["Content-Security-Policy"] = (
            "default-src 'self'; "
            f"script-src 'self' https://cdn.jsdelivr.net https://cdnjs.cloudflare.com https://pagead2.googlesyndication.com https://www.googletagmanager.com 'nonce-{nonce}'; "
            "style-src 'self' https://cdn.jsdelivr.net https://cdnjs.cloudflare.com https://fonts.googleapis.com 'unsafe-inline'; "
            "img-src 'self' https: data:; "
            "font-src 'self' https://cdn.jsdelivr.net https://cdnjs.cloudflare.com https://fonts.gstatic.com; "
            "connect-src 'self' https://fonts.googleapis.com https://fonts.gstatic.com https://cdn.jsdelivr.net https://cdnjs.cloudflare.com https://www.google-analytics.com https://*.google-analytics.com; "
            "frame-src https://googleads.g.doubleclick.net;"
            "object-src 'none'; "
            "base-uri 'self'; "
            "frame-ancestors 'none';"
        )

        return response

from django.shortcuts import redirect
from django.urls import reverse

class ProfileCompletionMiddleware:
    """
    Ensures that OAuth users who haven't completed their profile
    are redirected to the profile completion page.
    """
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.user.is_authenticated:
            if hasattr(request.user, 'social_profile_completed') and not request.user.social_profile_completed:
                allowed_paths = [
                    reverse('complete_profile'),
                    reverse('handleLogout'),
                ]
                if request.path not in allowed_paths and not request.path.startswith('/static/') and not request.path.startswith('/admin/'):
                    return redirect('complete_profile')
                    
        response = self.get_response(request)
        return response
