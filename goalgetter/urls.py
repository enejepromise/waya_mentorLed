from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import GoalViewSet, GoalSummaryView

router = DefaultRouter()
router.register(r'goals', GoalViewSet, basename='goal')

urlpatterns = [
    path('goals/summary/', GoalSummaryView.as_view(), name='goal-summary'),  # must be first
    path('', include(router.urls)),
]
