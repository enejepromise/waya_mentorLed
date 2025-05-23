# dashboard/urls.py
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from dashboard.views.child_views import (
    ChildViewSet,
    ParentChangePinView,
    ChildAvatarUpdateView,
    ChildLoginView,
)

router = DefaultRouter()
router.register(r'children', ChildViewSet, basename='children')

urlpatterns = [
    path('', include(router.urls)),
    path('children/<uuid:pk>/change-pin/', ParentChangePinView.as_view(), name='child-change-pin'),
    path('children/avatar/update/', ChildAvatarUpdateView.as_view(), name='child-avatar-update'),
    path('children/login/', ChildLoginView.as_view(), name='child-login'),
]
