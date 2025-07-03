from rest_framework import serializers
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError as DjangoValidationError
from django.contrib.auth import get_user_model
from django.utils.translation import gettext_lazy as _
from allauth.account import app_settings
from users.models import EmailVerification
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from django.contrib.auth.tokens import default_token_generator
from django.conf import settings
from users.utils import send_email


User = get_user_model()

class UserRegistrationSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(required=app_settings.SIGNUP_FIELDS['email']['required'])
    password = serializers.CharField(write_only=True, required=True, style={'input_type': 'password'})
    password2 = serializers.CharField(write_only=True, required=True, label='Confirm password', style={'input_type': 'password'})
    terms_accepted = serializers.BooleanField(required=True)

    class Meta:
        model = User
        fields = ['email', 'full_name', 'password', 'password2', 'role', 'terms_accepted', 'avatar']
        extra_kwargs = {
            'role': {'default': User.ROLE_PARENT},
            'avatar': {'required': False, 'allow_null': True},
        }

    def validate_email(self, value):
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError(_("A user with this email already exists."))
        return value

    def validate_terms_accepted(self, value):
        if not value:
            raise serializers.ValidationError(_("You must accept the Terms and Conditions."))
        return value

    def validate(self, attrs):
        if attrs.get('password') != attrs.get('password2'):
            raise serializers.ValidationError({"password": _("Password fields didn't match.")})

        try:
            validate_password(attrs.get('password'))
        except DjangoValidationError as e:
            raise serializers.ValidationError({"password": list(e.messages)})

        return attrs

    def create(self, validated_data):
        validated_data.pop('password2')
        password = validated_data.pop('password')
        user = User(**validated_data)
        user.set_password(password)
        user.save()

        token = EmailVerification.objects.create(user=user)

        return user


class UserLoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)


class PasswordChangeSerializer(serializers.Serializer):
    old_password = serializers.CharField(write_only=True, required=True)
    new_password = serializers.CharField(write_only=True, required=True)

    def validate_new_password(self, value):
        user = self.context['request'].user
        try:
            validate_password(value, user=user)
        except DjangoValidationError as e:
            raise serializers.ValidationError(list(e.messages))
        return value

    def validate(self, attrs):
        user = self.context['request'].user
        if not user.check_password(attrs.get('old_password')):
            raise serializers.ValidationError({"old_password": _("Old password is not correct.")})
        return attrs

    def save(self, **kwargs):
        user = self.context['request'].user
        user.set_password(self.validated_data['new_password'])
        user.save()
        return user


class PasswordResetRequestSerializer(serializers.Serializer):
    email = serializers.EmailField()

    def create(self, validated_data):
        email = validated_data['email']
        request = self.context.get('request')

        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            # Always return success for security reasons
            return {}

        uid = urlsafe_base64_encode(force_bytes(user.pk))
        token = default_token_generator.make_token(user)
        domain = getattr(settings, 'DOMAIN', None) or request.get_host()

        # Change this to match your frontend route for resetting passwords
        reset_link = f"https://{domain}/auth/reset-password-confirm/?uidb64={uid}&token={token}"

        try:
            send_email(
                subject="Reset Your Waya Password",
                message=f"Hello {user.full_name},\n\nClick the link to reset your password:\n{reset_link}\n\nIf you didn't request this, ignore this email.",
                to_email=user.email
            )
        except Exception as e:
            raise serializers.ValidationError({"email": f"Failed to send reset email: {str(e)}"})

        return {}

class PasswordResetConfirmSerializer(serializers.Serializer):
    new_password1 = serializers.CharField(write_only=True, required=True)
    new_password2 = serializers.CharField(write_only=True, required=True)

    def validate(self, attrs):
        if attrs.get('new_password1') != attrs.get('new_password2'):
            raise serializers.ValidationError({"new_password2": _("Password fields didn't match.")})

        user = self.context.get('user')
        try:
            validate_password(attrs.get('new_password1'), user=user)
        except DjangoValidationError as e:
            raise serializers.ValidationError({"new_password1": list(e.messages)})

        return attrs

    def save(self, **kwargs):
        user = self.context.get('user')
        user.set_password(self.validated_data['new_password1'])
        user.save()
        return user


class EmailVerificationSerializer(serializers.Serializer):
    uidb64 = serializers.CharField()
    token = serializers.CharField()