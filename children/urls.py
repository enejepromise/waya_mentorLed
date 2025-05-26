from django.urls import path
from .views import (
    ChildCreateView,
    ChildListView,
    ChildDetailView,
    ChildUpdateView,
    ChildDeleteView,
    ChildLoginView,  # added
)

urlpatterns = [
    path('create/', ChildCreateView.as_view(), name='child-create'),
    path('list/', ChildListView.as_view(), name='child-list'),
    path('<uuid:pk>/', ChildDetailView.as_view(), name='child-detail'),
    path('<uuid:pk>/update/', ChildUpdateView.as_view(), name='child-update'),
    path('<uuid:pk>/delete/', ChildDeleteView.as_view(), name='child-delete'),
    path('login/', ChildLoginView.as_view(), name='child-login'),  # added
]
