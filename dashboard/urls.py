from django.urls import path
from .views import ChildListCreateView

urlpatterns = [
    path('children/', ChildListCreateView.as_view(), name='children'),
]
