from rest_framework_simplejwt.authentication import JWTAuthentication
from django.contrib.auth.backends import BaseBackend
from users.models import Child
from rest_framework_simplejwt.exceptions import InvalidToken, AuthenticationFailed


class ChildBackend(BaseBackend):
    """
    Custom authentication backend for children using username and PIN.
    """

    def authenticate(self, request, username=None, pin=None, **kwargs):
        if username is None or pin is None:
            return None
        try:
            child = Child.objects.get(username=username)
            if child.check_pin(pin):
                # Return child object for authentication
                # Note: You may need to adapt this if your auth system expects a User model instance
                return child
        except Child.DoesNotExist:
            return None

    def get_user(self, user_id):
        try:
            return Child.objects.get(pk=user_id)
        except Child.DoesNotExist:
            return None
class ChildJWTAuthentication(JWTAuthentication):
    """
    Custom JWT authentication backend for children.
    Extracts child info from token claims and authenticates Child instance.
    """
    def get_user(self, validated_token):
        """
        Override to return Child instance instead of User.
        """
        child_id = validated_token.get('child_id')
        if not child_id:
            raise AuthenticationFailed('Child ID not found in token')

        try:
            child = Child.objects.get(id=child_id)
        except Child.DoesNotExist:
            raise AuthenticationFailed('Child not found')

        return child
