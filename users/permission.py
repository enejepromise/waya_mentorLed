from rest_framework.permissions import BasePermission
from users.models import User, Child
from rest_framework.views import APIView
from rest_framework.response import Response
from users.permission import IsParentUser
from rest_framework.permissions import BasePermission
from users.models import User
from children.models import Child

class IsParentUser(BasePermission):
    """
    Allows access only to users with role='parent'.
    """
    def has_permission(self, request, view):
        return request.user.is_authenticated and getattr(request.user, 'role', None) == User.ROLE_PARENT


class IsChildUser(BasePermission):
    """
    Allows access only to valid Child users (if you have a custom child auth method).
    """
    def has_permission(self, request, view):
        # If your child auth logic sets request.user to a Child instance:
        return isinstance(request.user, Child)


class ManageChildrenView(APIView):
    permission_classes = [IsParentUser]

    def get(self, request):
        # Only parents reach here
        children = request.user.children.all()
        return Response({"children": [child.username for child in children]})
