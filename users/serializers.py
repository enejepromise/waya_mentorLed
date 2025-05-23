from rest_framework import serializers
from django.contrib.auth.password_validation import validate_password
from django.contrib.auth import authenticate
from users.models import User
from django.utils.encoding import smart_str, force_bytes
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.contrib.auth.tokens import default_token_generator
from .models import Child
from .utils import make_pin  # Assumes you have this utility function to hash PINs


class UserRegistrationSerializer(serializers.ModelSerializer):
    """
    Serializer for registering a new parent user.
    Includes validation for password match, role, and terms agreement.
    """
    password = serializers.CharField(write_only=True)
    confirm_password = serializers.CharField(write_only=True)
    terms_condition = serializers.BooleanField(write_only=True)
    avatar = serializers.ImageField(required=False)

    class Meta:
        model = User
        fields = ['full_name', 'email', 'role', 'password', 'confirm_password', 'terms_condition', 'avatar']

    def validate(self, data):
        """
        Ensure password confirmation matches, role is valid for self-registration, and terms are accepted.
        """
        if data['password'] != data['confirm_password']:
            raise serializers.ValidationError("Passwords do not match.")
        if data['role'] == 'child':
            # Prevent children from self-registering
            raise serializers.ValidationError("Children cannot register themselves.")
        if not data.get('terms_condition'):
            raise serializers.ValidationError("You must agree to the terms and conditions.")
        # Use Django's built-in password validators for strong passwords
        validate_password(data['password'])
        return data

    def create(self, validated_data):
        """
        Remove confirm_password and terms_condition before user creation.
        """
        validated_data.pop('confirm_password')
        validated_data.pop('terms_condition')
        return User.objects.create_user(**validated_data)


class EmailVerificationSerializer(serializers.Serializer):
    """
    Serializer for verifying email with UID and token.
    """
    uidb64 = serializers.CharField()
    token = serializers.CharField()


class LoginSerializer(serializers.Serializer):
    """
    Serializer for logging in a user using email and password.
    Ensures the account is verified.
    """
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)

    def validate(self, data):
        """
        Authenticate the user and check verification status.
        """
        user = authenticate(email=data['email'], password=data['password'])
        if not user:
            raise serializers.ValidationError("Invalid credentials.")
        if not user.is_verified:
            raise serializers.ValidationError("Email is not verified.")
        data['user'] = user
        return data


class ChangePasswordSerializer(serializers.Serializer):
    """
    Serializer for changing the current user's password.
    """
    old_password = serializers.CharField(write_only=True)
    new_password = serializers.CharField(write_only=True)

    def validate_new_password(self, value):
        """
        Validate the new password against Django's password rules.
        """
        validate_password(value)
        return value


class ResetPasswordSerializer(serializers.Serializer):
    """
    Serializer for resetting password using new credentials.
    """
    new_password = serializers.CharField(write_only=True, min_length=8)
    confirm_password = serializers.CharField(write_only=True)

    def validate(self, data):
        """
        Ensure both passwords match and validate password strength.
        """
        if data['new_password'] != data['confirm_password']:
            raise serializers.ValidationError("Passwords do not match.")
        validate_password(data['new_password'])
        return data


# ------------------- Child Serializers -------------------

class ChildSerializer(serializers.ModelSerializer):
    """
    Serializer for Child model excluding the PIN for security.
    """
    class Meta:
        model = Child
        fields = ['id', 'username', 'avatar', 'created_at']
        # Explicitly exclude pin from output for security
        extra_kwargs = {'pin': {'write_only': True}}


class ChildCreateSerializer(serializers.ModelSerializer):
    """
    Serializer for creating a Child.
    Validates username uniqueness and PIN format.
    Hashes PIN before saving.
    """
    pin = serializers.CharField(write_only=True)

    class Meta:
        model = Child
        fields = ['username', 'avatar', 'pin']

    def validate_username(self, value):
        """
        Ensure username is unique across children.
        """
        if Child.objects.filter(username=value).exists():
            raise serializers.ValidationError("Username already exists.")
        return value

    def validate_pin(self, value):
        """
        Ensure PIN is exactly 4 digits.
        """
        if not value.isdigit() or len(value) != 4:
            raise serializers.ValidationError("PIN must be exactly 4 digits.")
        return value

    def create(self, validated_data):
        """
        Hash the PIN and associate the child with the current parent user.
        """
        # 🔐 Hash the PIN securely before saving
        validated_data['pin'] = make_pin(validated_data['pin'])
        # Assign the parent from request context
        validated_data['parent'] = self.context['request'].user
        return super().create(validated_data)

    def update(self, instance, validated_data):
        """
        Hash the PIN if updated.
        """
        if 'pin' in validated_data:
            validated_data['pin'] = make_pin(validated_data['pin'])  # 🔐 Hash PIN on update
        return super().update(instance, validated_data)
