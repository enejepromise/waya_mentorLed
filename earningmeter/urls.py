
from django.urls import path
from .views import EarningMeterView, SummaryView

urlpatterns = [
    path('dashboard/', EarningMeterView.as_view(), name='earning-meter-dashboard'),
    path('summary/', SummaryView.as_view(), name='earning-meter-summary'),
]

