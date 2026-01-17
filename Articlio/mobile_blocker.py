from django.shortcuts import redirect, render
from django.conf import settings

class BlockMobileMiddleware:

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):

        # allow static/media and the mobile-blocked page itself to pass through
        path = request.path or ''
        static_url = getattr(settings, 'STATIC_URL', '/static/')
        # normalize static_url to start with '/'
        if not static_url.startswith('/'):
            static_url = '/' + static_url
        # skip static, media, admin, and the mobile-blocked path itself
        if (path.startswith(static_url)
                or path.startswith('/media/')
                or path.startswith('/admin/')
                or path.startswith('/mobile-not-supported/')):
            return self.get_response(request)

        user_agent = request.META.get('HTTP_USER_AGENT', '').lower()
        mobile_keywords = [
            'mobile', 'android', 'iphone', 'ipad', 'opera mini',
            'blackberry', 'windows phone'
        ]

        if any(word in user_agent for word in mobile_keywords):
            return render(request, 'mobile_blocked.html')

        response = self.get_response(request)
        return response
