# serializers/user.py
from rest_framework import serializers
from django.contrib.auth import authenticate
from django.contrib.auth.password_validation import validate_password
from users.models import User

PASSWORD_MISMATCH_ERROR = {"password": "Password fields didn't match."}
TERMS_NOT_ACCEPTED_ERROR = {"terms_accepted": "You must accept the terms and conditions."}


class RegisterSerializer(serializers.ModelSerializer):
    """
    Serializer for registering a new user.
    """
    password = serializers.CharField(write_only=True, validators=[validate_password])
    confirm_password = serializers.CharField(write_only=True)
    avatar = serializers.ImageField(required=False)

    class Meta:
        model = User
        fields = ['email', 'fullname', 'password', 'confirm_password', 'avatar', 'terms_accepted']

    def validate(self, attrs):
        if attrs['password'] != attrs['confirm_password']:
            raise serializers.ValidationError(PASSWORD_MISMATCH_ERROR)
        if not attrs.get('terms_accepted'):
            raise serializers.ValidationError(TERMS_NOT_ACCEPTED_ERROR)
        return attrs

    def create(self, validated_data):
        validated_data.pop('confirm_password')
        password = validated_data.pop('password')
        user = User.objects.create_user(password=password, **validated_data)
        return user


class LoginSerializer(serializers.Serializer):
    """
    Serializer for authenticating a user.
    """
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)

    def validate(self, data):
        user = authenticate(email=data['email'], password=data['password'])
        if not user or not user.is_active:
            raise serializers.ValidationError("Invalid email or password.")
        data['user'] = user
        return data


class UserProfileSerializer(serializers.ModelSerializer):
    """
    Serializer for user's profile.
    """
    class Meta:
        model = User
        fields = ['id', 'email', 'fullname', 'avatar', 'terms_accepted']
        read_only_fields = ['email', 'terms_accepted']


class ChangePasswordSerializer(serializers.Serializer):
    """
    Serializer to change a user's password.
    """
    old_password = serializers.CharField(write_only=True)
    new_password = serializers.CharField(write_only=True, validators=[validate_password])
    confirm_new_password = serializers.CharField(write_only=True)

    def validate(self, attrs):
        if attrs['new_password'] != attrs['confirm_new_password']:
            raise serializers.ValidationError(PASSWORD_MISMATCH_ERROR)
        return attrs


class PasswordResetRequestSerializer(serializers.Serializer):
    """
    Serializer to request a password reset link.
    """
    email = serializers.EmailField()


class PasswordResetConfirmSerializer(serializers.Serializer):
    """
    Serializer to confirm a new password during reset.
    """
    new_password = serializers.CharField(write_only=True, validators=[validate_password])
    confirm_new_password = serializers.CharField(write_only=True)

    def validate(self, attrs):
        if attrs['new_password'] != attrs['confirm_new_password']:
            raise serializers.ValidationError(PASSWORD_MISMATCH_ERROR)
        return attrs
