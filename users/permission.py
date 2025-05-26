from rest_framework.permissions import BasePermission
from users.models import User, Child
from rest_framework.views import APIView
from rest_framework.response import Response
from users.permission import IsParentUser

class IsParentUser(BasePermission):
    """
    Allows access only to users with role='parent'.
    """
    def has_permission(self, request, view):
        return request.user.is_authenticated and hasattr(request.user, 'role') and request.user.role == User.ROLE_PARENT


class IsChildUser(BasePermission):
    """
    Allows access only to users with role='child' or linked to a Child instance.
    """
    def has_permission(self, request, view):
        user = request.user

        if not user or not user.is_authenticated:
            return False

        # Option 1: Child is linked to the user (assuming OneToOne or FK)
        if hasattr(user, 'role') and user.role == User.ROLE_CHILD:
            return True

        # Option 2: Authenticated as a User but has a linked Child record
        try:
            return Child.objects.filter(parent=user).exists()
        except:
            return False

class ManageChildrenView(APIView):
    permission_classes = [IsParentUser]

    def get(self, request):
        # Only parents reach here
        children = request.user.children.all()
        return Response({"children": [child.username for child in children]})
