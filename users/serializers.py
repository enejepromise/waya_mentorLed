from rest_framework import serializers
from django.contrib.auth import authenticate
from django.contrib.auth.password_validation import validate_password
from .models import User

# Common error message constants
PASSWORD_MISMATCH_ERROR = {"password": "Password fields didn't match."}
TERMS_NOT_ACCEPTED_ERROR = {"terms_accepted": "You must accept the terms and conditions."}
INVALID_LOGIN_ERROR = "Invalid email or password."


class RegisterSerializer(serializers.ModelSerializer):
    """
    Serializer for user registration.
    Handles user creation, password validation, and ensures required fields are present.
    """
    password = serializers.CharField(
        write_only=True,
        required=True,
        validators=[validate_password],
        min_length=8,
        style={'input_type': 'password'}
    )
    confirm_password = serializers.CharField(
        write_only=True,
        required=True,
        min_length=8,
        style={'input_type': 'password'}
    )
    avatar = serializers.ImageField(required=False)

    class Meta:
        model = User
        fields = ('email', 'fullname', 'password', 'confirm_password', 'avatar', 'terms_accepted')

    def validate(self, attrs):
        """
        Custom validation to check that password and confirm_password match,
        and that the user accepts the terms.
        """
        if attrs['password'] != attrs['confirm_password']:
            raise serializers.ValidationError(PASSWORD_MISMATCH_ERROR)

        if not attrs.get('terms_accepted'):
            raise serializers.ValidationError(TERMS_NOT_ACCEPTED_ERROR)

        return attrs

    def create(self, validated_data):
        """
        Create and return a new User instance, with an encrypted password.
        """
        validated_data.pop('confirm_password')
        password = validated_data.pop('password')
        user = User.objects.create_user(password=password, **validated_data)
        return user


class LoginSerializer(serializers.Serializer):
    """
    Serializer for user login.
    Authenticates user using email and password.
    """
    email = serializers.EmailField()
    password = serializers.CharField(
        write_only=True,
        style={'input_type': 'password'}
    )

    def validate(self, data):
        """
        Validate that the user credentials are correct and the account is active.
        """
        user = authenticate(email=data['email'], password=data['password'])
        if not user:
            raise serializers.ValidationError(INVALID_LOGIN_ERROR)
        if not user.is_active:
            raise serializers.ValidationError("This user account is inactive.")

        data['user'] = user
        return data


class UserProfileSerializer(serializers.ModelSerializer):
    """
    Serializer for displaying and partially updating user profile.
    """
    class Meta:
        model = User
        fields = ('id', 'email', 'fullname', 'avatar', 'terms_accepted')
        read_only_fields = ('email', 'terms_accepted')


class ChangePasswordSerializer(serializers.Serializer):
    """
    Serializer for changing user password.
    Requires the old password and confirmation of the new password.
    """
    old_password = serializers.CharField(
        required=True,
        style={'input_type': 'password'}
    )
    new_password = serializers.CharField(
        required=True,
        validators=[validate_password],
        min_length=8,
        style={'input_type': 'password'}
    )
    confirm_new_password = serializers.CharField(
        required=True,
        min_length=8,
        style={'input_type': 'password'}
    )

    def validate(self, attrs):
        """
        Ensure the new passwords match.
        """
        if attrs['new_password'] != attrs['confirm_new_password']:
            raise serializers.ValidationError(PASSWORD_MISMATCH_ERROR)
        return attrs


class PasswordResetRequestSerializer(serializers.Serializer):
    """
    Serializer for requesting password reset via email.
    """
    email = serializers.EmailField()


class PasswordResetConfirmSerializer(serializers.Serializer):
    """
    Serializer for confirming new password during reset process.
    """
    new_password = serializers.CharField(
        write_only=True,
        validators=[validate_password],
        min_length=8,
        style={'input_type': 'password'}
    )
    confirm_new_password = serializers.CharField(
        write_only=True,
        min_length=8,
        style={'input_type': 'password'}
    )

    def validate(self, attrs):
        """
        Validate that the new passwords match.
        """
        if attrs['new_password'] != attrs['confirm_new_password']:
            raise serializers.ValidationError(PASSWORD_MISMATCH_ERROR)
        return attrs

# ---------- For Google and Facebook OAuth ---------- #
# These are handled by dj-rest-auth + allauth integrations.
# Install packages:
# pip install dj-rest-auth[with_social] social-auth-app-django
# Add to settings.py:
# 'dj_rest_auth.registration', 'allauth', 'allauth.socialaccount',
# 'allauth.socialaccount.providers.google', 'allauth.socialaccount.providers.facebook'

# Then include these URLs in urls.py:
# path('auth/', include('dj_rest_auth.urls')),
# path('auth/registration/', include('dj_rest_auth.registration.urls')),
# path('auth/', include('allauth.socialaccount.urls'))

# Google/Facebook login happens via frontend using a social token. 
# The frontend sends the token to an endpoint like:
# POST /auth/social/login/ with {'access_token': '...'}
# The system will return JWT tokens for the user.

# Make sure to configure social providers in the Django admin panel
# (Sites and SocialApp models).

# Done!
