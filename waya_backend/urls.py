# waya_backend/urls.py

from django.contrib import admin
from django.urls import path, include
from users.views import home


urlpatterns = [
    path('admin/', admin.site.urls),

    # App routes
    path('api/users/', include('users.urls')),          # user registration, login, google login etc.
    path('api/children/', include('children.urls')),    # child create, login, list, etc.
    path('api/tasks/', include('taskmaster.urls')),
    path('', home, name='home'),
]