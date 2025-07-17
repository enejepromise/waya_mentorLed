# children/authentication.py

import jwt
from rest_framework.authentication import BaseAuthentication
from rest_framework.exceptions import AuthenticationFailed
from django.conf import settings
from children.models import Child


class ChildJWTAuthentication(BaseAuthentication):
    def authenticate(self, request):
        auth_header = request.headers.get('Authorization')

        if not auth_header or not auth_header.startswith('Bearer '):
            return None

        token = auth_header.split(" ")[1]

        try:
            payload = jwt.decode(token, settings.SECRET_KEY, algorithms=["HS256"])
            child_id = payload.get("child_id")

            if not child_id:
                raise AuthenticationFailed("Token missing child_id")

            child = Child.objects.get(id=child_id)

            # Set request.child here
            request.child = child

            return (child, token)

        except jwt.ExpiredSignatureError:
            raise AuthenticationFailed("Token expired")
        except jwt.InvalidTokenError:
            raise AuthenticationFailed("Invalid token")
        except Child.DoesNotExist:
            raise AuthenticationFailed("Child not found")
