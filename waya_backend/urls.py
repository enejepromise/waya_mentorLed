from django.contrib import admin
from django.urls import path, include
from users.views import home

urlpatterns = [
    path('admin/', admin.site.urls),

    # Core API endpoints
    path('api/', include('users.urls')),
    path('api/children/', include('children.urls')),
    path('api/taskmaster/', include('taskmaster.urls')),

    # Authentication endpoints under /api/auth/
    path('api/auth/registration/', include('dj_rest_auth.registration.urls')),
    path('api/auth/', include('dj_rest_auth.urls')),  # login, logout, password reset, etc.

    # Social authentication endpoints under /api/social/
    path('api/social/', include('allauth.socialaccount.urls')),

    path('', home, name='home'),
]