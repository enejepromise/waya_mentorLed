# urls.py
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import GoalViewSet, GoalSummaryView

router = DefaultRouter()
router.register(r'goals', GoalViewSet, basename='goal')

urlpatterns = [
    # This will include all CRUD routes for GoalViewSet, including the custom 'contribute' action
    path('', include(router.urls)),

    # summary
    path('goals/summary/', GoalSummaryView.as_view(), name='goal-summary'),
]
