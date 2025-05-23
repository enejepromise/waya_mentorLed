from django.contrib.auth.tokens import default_token_generator
from django.contrib.sites.shortcuts import get_current_site
from django.core.mail import EmailMessage
from django.utils.encoding import force_bytes, smart_str
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.conf import settings
from django.urls import reverse
from users.tasks import send_email_task 
from rest_framework import generics, status, permissions, viewsets
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.throttling import UserRateThrottle
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.parsers import MultiPartParser, FormParser
from users.models import User, Child
from users.serializers import (
    UserRegistrationSerializer, EmailVerificationSerializer,
    LoginSerializer, ChangePasswordSerializer, ResetPasswordSerializer
)
from users.utils import make_pin
from users.permission import IsParentUser
from dashboard.serializers import ChildSerializer, ChildCreateSerializer




def generate_uid_token(user):
    """
    Generate a base64 encoded UID and password reset token for a given user.
    """
    uid = urlsafe_base64_encode(force_bytes(user.pk))
    token = default_token_generator.make_token(user)
    return uid, token


def get_tokens_for_user(user):
    """
    Return refresh and access JWT tokens for a user.
    """
    refresh = RefreshToken.for_user(user)
    return {
        'refresh': str(refresh),
        'access': str(refresh.access_token),
    }


def send_email(subject, message, recipient_email):
    """
    Send an email with the given subject and message.
    """
    email = EmailMessage(
        subject=subject,
        body=message,
        from_email=settings.DEFAULT_FROM_EMAIL,
        to=[recipient_email],
    )
    email.send(fail_silently=False)  # Fail loudly to catch errors in dev


# === Views ===

class RegisterView(generics.CreateAPIView):
    """
    Registers a new user and sends a verification email.
    """
    serializer_class = UserRegistrationSerializer

    def perform_create(self, serializer):
        user = serializer.save()
        uid, token = generate_uid_token(user)
        current_site = get_current_site(self.request).domain
        relative_link = reverse('email-verify')
        absurl = f"http://{current_site}{relative_link}?uidb64={uid}&token={token}"
        message = f"Click the link to verify your account: {absurl}"

        send_email_task.delay(
            subject='Verify your email',
            message=message,
            recipient_email=user.email,
        )



class VerifyEmail(APIView):
    """
    Verifies a user's email using a UID and token.
    """
    serializer_class = EmailVerificationSerializer

    def get(self, request):
        token = request.GET.get('token')
        uidb64 = request.GET.get('uidb64')

        try:
            uid = smart_str(urlsafe_base64_decode(uidb64))
            user = User.objects.get(pk=uid)

            if default_token_generator.check_token(user, token):
                user.is_verified = True
                user.save()
                return Response({'message': 'Email verified successfully'}, status=status.HTTP_200_OK)

            return Response({'error': 'Invalid or expired token'}, status=status.HTTP_400_BAD_REQUEST)

        except Exception:
            return Response({'error': 'Verification failed'}, status=status.HTTP_400_BAD_REQUEST)


class LoginView(APIView):
    serializer_class = LoginSerializer

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']

        # Generate JWT tokens for the authenticated user
        refresh = RefreshToken.for_user(user)
        access_token = str(refresh.access_token)
        refresh_token = str(refresh)

        return Response({
            'access': access_token,
            'refresh': refresh_token,
            'message': f'Welcome {user.full_name}, redirecting to dashboard...'
        }, status=status.HTTP_200_OK)

class ChangePasswordView(APIView):
    """
    Allows authenticated users to change their password.
    """
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = ChangePasswordSerializer

    def put(self, request):
        user = request.user
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)

        if not user.check_password(serializer.validated_data['old_password']):
            return Response({'error': 'Old password is incorrect'}, status=status.HTTP_400_BAD_REQUEST)

        user.set_password(serializer.validated_data['new_password'])
        user.save()
        return Response({'message': 'Password changed successfully'}, status=status.HTTP_200_OK)


class LogoutView(APIView):
    """
    Logs out a user by blacklisting their refresh token.
    """
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        try:
            refresh_token = request.data.get("refresh")
            token = RefreshToken(refresh_token)
            token.blacklist()
            return Response({"detail": "Logout successful"}, status=status.HTTP_205_RESET_CONTENT)
        except Exception:
            return Response({"error": "Invalid or expired token"}, status=status.HTTP_400_BAD_REQUEST)


class ForgotPasswordThrottle(UserRateThrottle):
    rate = '3/hour'


class ForgotPasswordView(APIView):
    """
    Sends a password reset link to a user's email if it exists.
    """
    throttle_classes = [ForgotPasswordThrottle]

    def post(self, request):
        email = request.data.get("email")
        try:
            user = User.objects.get(email=email)
            uid, token = generate_uid_token(user)
            domain = get_current_site(request).domain
            reset_link = f"http://{domain}/reset-password-confirm/?uidb64={uid}&token={token}"
            message = f"Click the link to reset your password: {reset_link}"

            send_email(
                subject="Password Reset Request",
                message=message,
                recipient_email=email,
            )

        except User.DoesNotExist:
            # Do not reveal if email exists for security
            pass

        return Response({"message": "If the email exists, a reset link has been sent."}, status=status.HTTP_200_OK)


class ForgotPasswordView(APIView):
    """
    Sends a password reset link to a user's email if it exists.
    """
    throttle_classes = [ForgotPasswordThrottle]

    def post(self, request):
        email = request.data.get("email")
        try:
            user = User.objects.get(email=email)
            uid, token = generate_uid_token(user)
            domain = get_current_site(request).domain
            reset_link = f"http://{domain}/reset-password-confirm/?uidb64={uid}&token={token}"
            message = f"Click the link to reset your password: {reset_link}"

        
            send_email_task.delay(
                subject="Password Reset Request",
                message=message,
                recipient_email=email,
            )

        except User.DoesNotExist:
            pass

        return Response({"message": "If the email exists, a reset link has been sent."}, status=status.HTTP_200_OK)

# === Child Views ===

class ChildViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing child accounts under a parent.
    Supports list, retrieve, create, update, and delete operations.
    Restricted to authenticated parents only.
    """
    permission_classes = [permissions.IsAuthenticated, IsParentUser]

    def get_queryset(self):
        # Only children of the logged-in parent
        return Child.objects.filter(parent=self.request.user)

    def get_serializer_class(self):
        # Use create serializer for create actions, otherwise regular serializer
        if self.action == 'create':
            return ChildCreateSerializer
        return ChildSerializer

    def perform_create(self, serializer):
        # Automatically assign the logged-in parent as child's parent
        serializer.save(parent=self.request.user)

    # retrieve, update, destroy methods are inherited and work as expected


class ParentChangePinView(APIView):
    """
    Allows parent to update a child's PIN securely.
    """
    permission_classes = [permissions.IsAuthenticated, IsParentUser]

    def patch(self, request, pk):
        pin = request.data.get('pin')
        if not pin or not pin.isdigit() or len(pin) != 4:
            return Response({"error": "PIN must be exactly 4 digits."}, status=status.HTTP_400_BAD_REQUEST)

        child = Child.objects.filter(pk=pk, parent=request.user).first()
        if not child:
            return Response({"error": "Child not found."}, status=status.HTTP_404_NOT_FOUND)

        child.pin = make_pin(pin)
        child.save()
        return Response({"message": "Child PIN updated successfully."})


class ChildAvatarUpdateView(APIView):
    """
    Allows a logged-in child to update their avatar (profile image).
    """
    permission_classes = [permissions.IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser]

    def patch(self, request):
        try:
            # Assuming you have a way to get Child instance from user (e.g., OneToOne or reverse relation)
            child = Child.objects.get(user=request.user)
        except Child.DoesNotExist:
            return Response({'error': 'Only children can update their avatar.'}, status=status.HTTP_404_NOT_FOUND)

        serializer = ChildSerializer(child, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response({
            'message': 'Avatar updated successfully.',
            'avatar': serializer.data.get('avatar')
        })
def get_child_tokens(child):
    """
    Generate JWT refresh and access tokens with custom claims for a child.
    """
    refresh = RefreshToken()

    # Add custom claims to the token payload
    refresh['child_id'] = str(child.id)
    refresh['username'] = child.username
    # You can add more claims if needed

    access = refresh.access_token
    return {
        'refresh': str(refresh),
        'access': str(access),
    }

class ChildLoginView(APIView):
    """
    Logs in a child using username and 4-digit PIN.
    Returns access and refresh tokens along with profile info.
    """
    def post(self, request):
        username = request.data.get('username')
        pin = request.data.get('pin')

        if not username or not pin:
            return Response({'error': 'Username and PIN are required.'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            child = Child.objects.get(username=username)
        except Child.DoesNotExist:
                 return Response({'error': 'Invalid credentials.'}, status=status.HTTP_400_BAD_REQUEST)

        if not child.check_pin(pin):
            return Response({'error': 'Invalid credentials.'}, status=status.HTTP_400_BAD_REQUEST)

        # Generate custom tokens for the child
        tokens = get_child_tokens(child)

        return Response({
            'message': 'Login successful.',
            'refresh': tokens['refresh'],
            'access': tokens['access'],
            'child': {
                'id': str(child.id),
                'username': child.username,
                'avatar': child.avatar.url if child.avatar else None
            }
        }, status=status.HTTP_200_OK)