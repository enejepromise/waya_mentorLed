from django.urls import path
from .views import (
    UserProfileView,
    ChildView,
    PasswordResetView,
    RewardView,
    NotificationListView, 
    MarkNotificationReadView
)

urlpatterns = [
    path('profile/', UserProfileView.as_view(), name='user-profile'),
    path('children/<int:child_id>/profile/', ChildView.as_view(), name='child-profile'),
    path('reset-password/', PasswordResetView.as_view(), name='reset-password'),
    path('rewards/', RewardView.as_view(), name='reward'),
    path("", NotificationListView.as_view(), name="notification-list"),
    path("<uuid:id>/read/", MarkNotificationReadView.as_view(), name="notification-read"),    
]
