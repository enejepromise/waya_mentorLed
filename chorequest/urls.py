from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ChoreQuestViewSet  # adjust path as needed

router = DefaultRouter()
router.register(r'chorequest', ChoreQuestViewSet, basename='chore-quest')

urlpatterns = [
    path('', include(router.urls)),
]
