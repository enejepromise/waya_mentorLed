from django.urls import path
from users.views import (
    RegisterView, VerifyEmail, LoginView,
    ChangePasswordView, LogoutView,
    ForgotPasswordView, ResetPasswordConfirmView
)

urlpatterns = [
    path('register/', RegisterView.as_view(), name='register'),
    path('email-verify/', VerifyEmail.as_view(), name='email-verify'),
    path('login/', LoginView.as_view(), name='login'),
    path('change-password/', ChangePasswordView.as_view(), name='change-password'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('forgot-password/', ForgotPasswordView.as_view(), name='forgot-password'),
    #path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),

    path('reset-password-confirm/', ResetPasswordConfirmView.as_view(), name='reset-password-confirm'),
]
