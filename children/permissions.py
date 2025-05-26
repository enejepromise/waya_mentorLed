from rest_framework import permissions


class IsParentOfChild(permissions.BasePermission):
    """
    Custom permission to only allow parents to access their own children.
    """

    def has_object_permission(self, request, view, obj):
        return obj.parent == request.user