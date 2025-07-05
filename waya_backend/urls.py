from django.contrib import admin
from django.urls import path, include, re_path # Make sure re_path is imported if you're using it (though not strictly necessary for this fix)
from django.views.generic.base import RedirectView
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView, SpectacularRedocView

# Commented out drf_yasg parts as you're using drf_spectacular
# from drf_yasg.views import get_schema_view
# from drf_yasg import openapi

# # Schema View Setup (drf_yasg - commented out)
# schema_view = get_schema_view(
#     openapi.Info(
#         title="Waya API Documentation",
#         default_version='v1',
#         description="Comprehensive API documentation for Waya backend project",
#         terms_of_service="https://www.google.com/policies/terms/",
#         contact=openapi.Contact(email="your_email@example.com"),
#         license=openapi.License(name="BSD License"),
#     ),
#     public=True,
#     permission_classes=[permissions.AllowAny],
# )

urlpatterns = [
    path('admin/', admin.site.urls),

    # CORRECTED API URLS:
    # Each API path now explicitly starts with 'api/' at the top level
    # instead of nesting an 'include' that then adds another 'api/'
    path('api/users/', include('users.urls')),
    path('api/children/', include('children.urls')),
    path('api/taskmaster/', include('taskmaster.urls')),
    path('api/familywallet/', include('familywallet.urls')),
    path('api/insighttracker/', include('insighttracker.urls')),
    path('api/chorequest/', include('chorequest.urls')),
    path('api/moneymaze/', include('moneymaze.urls')),

    # IMPORTANT: Corrected these paths.
    # Assuming moneymaze.urls and notifications.urls don't *also* expect 'api/'
    # as their base prefix within their own urls.py files.
    # If moneymaze.urls expects just '/moneymaze/', then this is correct.
    # If notifications.urls expects just '/parents/notifications/', then this is correct.
    path('api/moneymaze/', include('moneymaze.urls')),
    path('api/parents/notifications/', include('notifications.urls')),

    # CORRECTED DRF-SPECTACULAR URLs:
    # These are also directly at the top level, prefixed with 'api/'
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    path('api/schema/swagger-ui/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
    path('api/schema/redoc/', SpectacularRedocView.as_view(url_name='schema'), name='redoc'),


    # # Swagger and Redoc URLs (drf_yasg - commented out)
    # # Ensure these remain commented out if you are fully switching to drf-spectacular
    # re_path(r'^swagger(?P<format>\.json|\.yaml)$', schema_view.without_ui(cache_timeout=0), name='schema-json'),
    # path('swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    # path('redoc/', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),

    # Redirect base URL to /api/
    path('', RedirectView.as_view(url='/api/', permanent=False)),
]