from rest_framework.permissions import BasePermission

class IsParentUser(BasePermission):
    """
    Allows access only to parent users.
    """
    def has_permission(self, request, view):
        return request.user.is_authenticated and not hasattr(request.user, 'child')

class IsChildUser(BasePermission):
    """
    Allows access only to child users.
    """
    def has_permission(self, request, view):
        return hasattr(request.user, 'child') and not request.user.is_superuser
