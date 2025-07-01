from rest_framework import permissions


class IsParentOfChore(permissions.BasePermission):
    """
    Allow access only to the parent who owns the chore.
    """

    def has_object_permission(self, request, view, obj):
        return obj.parent == request.user


class IsChildAssignedToChore(permissions.BasePermission):
    """
    Allow access only to the child assigned to the chore.
    """

    def has_object_permission(self, request, view, obj):
        # Adjust this based on how child users are authenticated
        return obj.assigned_to == request.user
