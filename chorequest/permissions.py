# chorequest/permissions.py

from rest_framework.permissions import BasePermission

class IsChild(BasePermission):
    """
    Allows access only to requests authenticated as a Child.
    """
    def has_permission(self, request, view):
        return hasattr(request, 'child')
