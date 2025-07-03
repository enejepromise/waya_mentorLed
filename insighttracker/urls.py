from django.urls import path
from .views import InsightChoreView 

urlpatterns = [

    # Chore insight analytics endpoint
    path("chores/insights/", InsightChoreView.as_view(), name="chore-insights"),
]