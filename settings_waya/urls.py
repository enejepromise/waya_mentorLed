from django.urls import path
from .views import (
    UserProfileView,
    ChildView,
    PasswordResetView,
    NotificationSettingsView,
    RewardSettingsView,
)

urlpatterns = [
    path('profile/', UserProfileView.as_view(), name='user-profile'),
    path('children/<uuid:child_id>/', ChildView.as_view(), name='child-detail'),
    path('password-reset/', PasswordResetView.as_view(), name='password-reset'),
    path('notification-settings/', NotificationSettingsView.as_view(), name='notification-settings'),
    path('reward-settings/', RewardSettingsView.as_view(), name='reward-settings'),
]
