from django.contrib import admin
from django.urls import path, include
from django.shortcuts import redirect

def redirect_root(request):  
    return redirect('/users/')
urlpatterns = [
    path('admin/', admin.site.urls),
    path('users/', include('users.urls')),
    path('children/', include('children.urls')),
    path('taskmaster/', include('taskmaster.urls')),
    path('', redirect_root),
    
]
