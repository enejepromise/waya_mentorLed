# earning_meter/urls.py

from django.urls import path
from .views import EarningMeterView

urlpatterns = [
    path('dashboard/', EarningMeterView.as_view(), name='child-earning-meter'),
]
