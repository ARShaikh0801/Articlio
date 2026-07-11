
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
            "connect-src 'self' https://fonts.googleapis.com https://fonts.gstatic.com https://cdn.jsdelivr.net https://cdnjs.cloudflare.com https://www.google-analytics.com https://*.google-analytics.com https://www.googletagmanager.com https://www.google.com https://*.google.com; "
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

import uuid
from django.core.cache import cache

class VisitorTrackingMiddleware:
    """
    Tracks unique site visitors using a long-lived cookie.
    Uses cache to prevent redundant database hits on every request.
    """
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Ignore static, media and admin requests to avoid counting them
        path = request.path
        if path.startswith('/static/') or path.startswith('/media/') or path.startswith('/admin/'):
            return self.get_response(request)

        visitor_id = request.COOKIES.get('articlio_visitor_id')
        set_cookie = False
        if not visitor_id:
            visitor_id = str(uuid.uuid4())
            set_cookie = True

        cache_key = f"visitor_tracked_{visitor_id}"
        if not cache.get(cache_key):
            from home.models import Visitor
            try:
                Visitor.objects.get_or_create(visitor_id=visitor_id)
                cache.set(cache_key, True, timeout=86400)  # cache for 24 hours
            except Exception as e:
                # Fail gracefully if database or cache is temporarily down
                print(f"Error tracking visitor: {e}")

        response = self.get_response(request)
        if set_cookie:
            response.set_cookie('articlio_visitor_id', visitor_id, max_age=365*24*60*60, httponly=True, samesite='Lax')
        return response
