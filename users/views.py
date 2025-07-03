import requests
# from drf_yasg.utils import swagger_auto_schema
# from drf_yasg import openapi

from django.conf import settings
from django.contrib.auth import authenticate, get_user_model
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import send_mail
from django.http import HttpResponseRedirect, JsonResponse
#from django.shortcuts import get_object_or_404
from django.urls import reverse
from .utils import send_email
from django.utils.encoding import force_str, force_bytes
from django.utils.http import urlsafe_base64_decode, urlsafe_base64_encode
from django.contrib.sites.shortcuts import get_current_site
from rest_framework import generics, status, permissions
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken

from dj_rest_auth.registration.views import SocialLoginView

#from allauth.socialaccount.adapter import get_adapter
from allauth.socialaccount.helpers import complete_social_login
# from allauth.socialaccount.models import SocialAccount
from allauth.socialaccount.providers.google.views import GoogleOAuth2Adapter
#from allauth.socialaccount.providers.oauth2.client import OAuth2Client
#from .models import SocialLoginAccount
from users.models import EmailVerification
from users.serializers import (
    UserRegistrationSerializer,
    UserLoginSerializer,
    PasswordChangeSerializer,
    PasswordResetRequestSerializer,
    PasswordResetConfirmSerializer,
    EmailVerificationSerializer,
)

User = get_user_model()

class UserRegistrationView(generics.CreateAPIView):
    serializer_class = UserRegistrationSerializer
    # @swagger_auto_schema(
    #     operation_description="Register a new user",
    #     request_body=UserRegistrationSerializer,
    #     responses={201: "Registration successful"},
    # )

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            #user.is_active = False
            user.is_active = True
            user.is_verified = True
            user.save()

            domain = getattr(settings, 'DOMAIN', None) or get_current_site(request).domain
            uidb64 = urlsafe_base64_encode(force_bytes(str(user.id)))
            email_verification = user.email_verifications.order_by('-created_at').first()

            if email_verification:
                token = email_verification.token
                #verification_link = f"https://{domain}{reverse('verify-email')}?uidb64={uidb64}&token={token}"(for testing the backend)
                verification_link = f"https://{domain}/auth/verify-email/?uidb64={uidb64}&token={token}"


                try:
                    # Django's SMTP email system (commented out)
                    # send_mail(
                    #     subject="Verify Your Waya Account",
                    #     message=f"Click the link to verify your email: {verification_link}",
                    #     from_email=settings.DEFAULT_FROM_EMAIL,
                    #     recipient_list=[user.email],
                    #     fail_silently=False,
                    # )

                    # SendGrid implementation
                    send_email(
                        subject="Verify Your Waya Account",
                        message=f"Click the link to verify your email: {verification_link}",
                        to_email=user.email
                    )

                except Exception as e:
                    return Response(
                        {"error": "User created but failed to send verification email.", "details": str(e)},
                        status=status.HTTP_500_INTERNAL_SERVER_ERROR
                    )

            return Response(
                {'message': 'Registration successful! Check your email to verify your account.'},
                status=status.HTTP_201_CREATED
            )

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class UserLoginView(generics.GenericAPIView):
    serializer_class = UserLoginSerializer
    permission_classes = [AllowAny]

    # @extend_schema(
    #     summary="User Login",
    #     description="Authenticates a user with email and password, returning access and refresh tokens upon successful login.",
    #     request=UserLoginSerializer, # Defines the expected request body
    #     responses={
    #         200: UserLoginResponseSerializer, # Defines the successful (200 OK) response body
    #         401: {
    #             'description': 'Unauthorized - Invalid credentials',
    #             'examples': {
    #                 'Invalid Credentials': OpenApiExample(
    #                     'Error Example',
    #                     value={"detail": "Invalid credentials"},
    #                     response_only=True,
    #                     media_type="application/json",
    #                 )
    #             }
    #         },
    #         403: {
    #             'description': 'Forbidden - Email not verified',
    #             'examples': {
    #                 'Email Not Verified': OpenApiExample(
    #                     'Verification Error Example',
    #                     value={"detail": "Email not verified. Please verify your email before logging in."},
    #                     response_only=True,
    #                     media_type="application/json",
    #                 )
    #             }
    #         },
    #     },
    #     tags=['Authentication', 'Users'], # Optional: Helps organize in Swagger UI
    # )
    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        user = authenticate(
            email=serializer.validated_data['email'],
            password=serializer.validated_data['password']
        )

        if user:
            if not user.is_verified:
                return Response(
                    {"detail": "Email not verified. Please verify your email before logging in."},
                    status=status.HTTP_403_FORBIDDEN
                )

            refresh = RefreshToken.for_user(user)
            # Make sure this dictionary perfectly matches your UserLoginResponseSerializer
            response_data = {
                'id': str(user.id),
                'name': user.full_name,
                'email': user.email,
                'avatar': user.avatar.url if user.avatar else None,
                'token': str(refresh.access_token),
                'refresh': str(refresh),
            }
            return Response(response_data, status=status.HTTP_200_OK)

        return Response({"detail": "Invalid credentials"}, status=status.HTTP_401_UNAUTHORIZED)




def post(self, request):
    serializer = self.get_serializer(data=request.data)
    serializer.is_valid(raise_exception=True)

    user = authenticate(
        email=serializer.validated_data['email'],
        password=serializer.validated_data['password']
    )

    if user:
        if not user.is_verified:
            return Response(
                {"detail": "Email not verified. Please verify your email before logging in."},
                status=status.HTTP_403_FORBIDDEN
            )

        refresh = RefreshToken.for_user(user)
        return Response({
            'id': str(user.id),
            'name': user.full_name,
            'email': user.email,
            'avatar': user.avatar.url if user.avatar else None,
            'token': str(refresh.access_token),
            'refresh': str(refresh),
        }, status=status.HTTP_200_OK)

    return Response({"detail": "Invalid credentials"}, status=status.HTTP_401_UNAUTHORIZED)


class PasswordChangeView(generics.UpdateAPIView):
    serializer_class = PasswordChangeSerializer
    permission_classes = [permissions.IsAuthenticated]

    # @swagger_auto_schema(
    #     operation_description="Change password for logged-in user",
    #     request_body=PasswordChangeSerializer,
    #     responses={200: "Password changed successfully"},
    # )

    def get_object(self):
        return self.request.user

class PasswordResetRequestView(generics.GenericAPIView):
    serializer_class = PasswordResetRequestSerializer
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(request=request)
        return Response({"message": "Password reset email sent successfully."}, status=status.HTTP_200_OK)

class PasswordResetConfirmView(generics.GenericAPIView):
    serializer_class = PasswordResetConfirmSerializer
    permission_classes = [AllowAny]

    # @swagger_auto_schema(
    #     operation_description="Reset password with token and UID",
    #     request_body=PasswordResetConfirmSerializer,
    #     responses={200: "Password has been reset successfully"},
    # )

    def post(self, request, uidb64, token):
        try:
            uid = force_str(urlsafe_base64_decode(uidb64))
            user = User.objects.get(pk=uid)
        except (TypeError, ValueError, OverflowError, User.DoesNotExist):
            return Response({"detail": "Invalid link."}, status=status.HTTP_400_BAD_REQUEST)

        if not default_token_generator.check_token(user, token):
            return Response({"detail": "Invalid or expired token."}, status=status.HTTP_400_BAD_REQUEST)

        serializer = self.get_serializer(data=request.data, context={'user': user})
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response({"message": "Password has been reset successfully."})


class EmailVerificationView(APIView):
    serializer_class = EmailVerificationSerializer
    permission_classes = [AllowAny]

    # @swagger_auto_schema(
    #     operation_description="Verify user email using uidb64 and token",
    #     request_body=EmailVerificationSerializer,
    #     responses={200: "Email verified successfully!", 400: "Invalid or expired token"},
    # )

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)

        uidb64 = serializer.validated_data['uidb64']
        token = serializer.validated_data['token']

        try:
            uid = force_str(urlsafe_base64_decode(uidb64))
            user = User.objects.get(pk=uid)
            verification = EmailVerification.objects.get(user=user, token=token, verified=False)
        except (User.DoesNotExist, EmailVerification.DoesNotExist, ValueError, TypeError, OverflowError):
            return Response({"detail": "Invalid verification link."}, status=status.HTTP_400_BAD_REQUEST)

        if verification.is_expired():
            return Response({"detail": "Verification link has expired."}, status=status.HTTP_400_BAD_REQUEST)

        user.is_verified = True
        user.is_active = True
        user.save()
        verification.mark_as_verified()

        return Response({"message": "Email verified successfully!"}, status=status.HTTP_200_OK)


class ForgotPasswordView(generics.GenericAPIView):
    serializer_class = PasswordResetRequestSerializer
    permission_classes = [AllowAny]

    # @swagger_auto_schema(
    #     operation_description="Request password reset email",
    #     request_body=PasswordResetRequestSerializer,
    #     responses={200: openapi.Response('Password reset email sent')}
    # )

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        return Response({"detail": "Password reset email sent."})


class ResetPasswordConfirmView(generics.GenericAPIView):
    serializer_class = PasswordResetConfirmSerializer
    permission_classes = [AllowAny]

    # @swagger_auto_schema(
    #     operation_description="Reset password with token and UID",
    #     request_body=PasswordResetConfirmSerializer,
    #     responses={200: openapi.Response('Password has been reset successfully')}
    # )

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data, context={'user': None})
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response({"detail": "Password has been reset successfully."})


def home(request):
    return JsonResponse({"message": "Welcome to the Waya Backend API"})


class GoogleLoginView(SocialLoginView):
    adapter_class = GoogleOAuth2Adapter

    # @swagger_auto_schema(
    #     operation_description="Login with Google OAuth2 access token",
    #     request_body=openapi.Schema(
    #         type=openapi.TYPE_OBJECT,
    #         required=['access_token'],
    #         properties={
    #             'access_token': openapi.Schema(type=openapi.TYPE_STRING, description='Google OAuth2 access token'),
    #         },
    #     ),
    #     responses={
    #         200: openapi.Response('Login successful', schema=openapi.Schema(
    #             type=openapi.TYPE_OBJECT,
    #             properties={
    #                 'detail': openapi.Schema(type=openapi.TYPE_STRING),
    #                 'user_id': openapi.Schema(type=openapi.TYPE_STRING),
    #                 'email': openapi.Schema(type=openapi.TYPE_STRING),
    #             }
    #         )),
    #         400: 'Bad request',
    #         403: 'Forbidden',
    #     }
    # )

    def post(self, request, *args, **kwargs):
        access_token = request.data.get("access_token")
        if not access_token:
            return Response({"error": "Access token is required"}, status=status.HTTP_400_BAD_REQUEST)

        adapter = self.adapter_class()
        app = adapter.get_provider().get_app(self.request)
        token = adapter.parse_token({'access_token': access_token})
        token.app = app

        # Get Google user info using the access token
        try:
            login = adapter.complete_login(self.request, app, token, response=requests.Response())
            login.token = token
            login.state = SocialLoginView.serializer_class().validate(request.data)
            login.lookup()
        except Exception as e:
            return Response({"error": "Failed to complete Google login."}, status=status.HTTP_400_BAD_REQUEST)

        # Get the Google email
        google_email = login.account.extra_data.get("email")
        if not google_email:
            return Response({"error": "Unable to retrieve email from Google account"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            # Try to match to an existing local user
            existing_user = User.objects.get(email=google_email)

            if not existing_user.verified:
                return Response({"error": "Account not verified."}, status=status.HTTP_403_FORBIDDEN)

            if not existing_user.role:
                # Redirect to select role if verified
                login.user = existing_user
                complete_social_login(self.request, login)
                return HttpResponseRedirect(
                    f"https://waya-fawn.vercel.app/user-role?user_id={existing_user.id}"
                )

            if existing_user.role != "parent":
                return Response({"error": "Only parents are allowed to log in here."}, status=status.HTTP_403_FORBIDDEN)

            # All good – proceed to login
            login.user = existing_user
            complete_social_login(self.request, login)
            return Response({
                "detail": "Login successful.",
                "user_id": existing_user.id,
                "email": existing_user.email
            }, status=status.HTTP_200_OK)

        except User.DoesNotExist:
            # No existing user → Google login not allowed for unregistered users
            return Response({
                "error": "This Google account is not registered as a parent. Please sign up through the registration flow."
            }, status=status.HTTP_403_FORBIDDEN)

        return super().post(request, *args, **kwargs)


class ResendVerificationEmailView(APIView):

    # @swagger_auto_schema(
    #     operation_description="Resend verification email to user",
    #     request_body=openapi.Schema(
    #         type=openapi.TYPE_OBJECT,
    #         required=['email'],
    #         properties={
    #             'email': openapi.Schema(type=openapi.TYPE_STRING, format='email', description='User email address'),
    #         },
    #     ),
    #     responses={
    #         200: openapi.Response('Verification email resent'),
    #         400: 'Bad request',
    #         404: 'User not found',
    #     }
    # )
    def post(self, request):
        email = request.data.get("email")
        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            return Response({'error': 'User not found.'}, status=status.HTTP_404_NOT_FOUND)

        if user.is_verified:
            return Response({'message': 'Email already verified.'}, status=status.HTTP_400_BAD_REQUEST)

        token = default_token_generator.make_token(user)
        uid = urlsafe_base64_encode(force_bytes(user.pk))
        verify_url = f"http://domain/api/auth/verify-email/{uid}/{token}/"

        send_mail(
            subject="Resend: Verify your Email",
            message=f"Click the link to verify your account: {verify_url}",
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[user.email]
        )

        return Response({'message': 'Verification email resent!'}, status=status.HTTP_200_OK)