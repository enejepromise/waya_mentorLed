from django.shortcuts import redirect
from django.urls import reverse
from django.utils.deprecation import MiddlewareMixin

EXEMPT_PATHS = [
    '/admin/',
    '/api/auth/complete_role/',
    '/api/auth/login/',
    '/auth/google/',
    '/api/auth/token/',
    '/api/auth/token/refresh/',
    '/api/auth/register/',
    '/api/auth/verify-email/',
    '/api/auth/forgot-password/',
    '/api/auth/reset-password-confirm/',
    '/api/auth/profile/',
    '/api/child/login/',  # child login endpoint
]

class RoleRequiredMiddleware(MiddlewareMixin):
    """
    Only allow authenticated parent users to access non-exempt views 
    **if** they have selected a role.
    Child users are skipped.
    """
    def process_request(self, request):
        path = request.path_info

        # Skip middleware check for unauthenticated users
        if not request.user.is_authenticated:
            return None

        # Skip for child users if you've marked them (e.g., request.user.is_child)
        if hasattr(request.user, 'is_child') and request.user.is_child:
            return None

        # Skip for exempt paths
        if any(path.startswith(exempt) for exempt in EXEMPT_PATHS):
            return None

        # Redirect parent users who haven't selected a role yet
        if not getattr(request.user, 'role', None):
            return redirect(reverse('complete_role'))

        return None
