from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.exceptions import AuthenticationFailed
from children.models import Child

class ChildJWTAuthentication(JWTAuthentication):
    """
    Custom JWT authentication class for Child model,
    uses 'child_id' claim inside JWT.
    """

    def get_user(self, validated_token):
        child_id = validated_token.get('child_id')
        if not child_id:
            raise AuthenticationFailed('Token missing child_id claim')

        try:
            return Child.objects.get(id=child_id)
        except Child.DoesNotExist:
            raise AuthenticationFailed('Child not found for given token.')

    def authenticate(self, request):
        auth_result = super().authenticate(request)
        if auth_result is None:
            return None

        child = auth_result[0]
        request.child = child

        # Children aren't User instances, so return None user
        return (None, None)
