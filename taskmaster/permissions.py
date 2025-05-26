from rest_framework import permissions


class IsParentOfTask(permissions.BasePermission):
    """
    Allow access only to the parent who owns the task.
    """

    def has_object_permission(self, request, view, obj):
        return obj.parent == request.user


class IsChildAssignedToTask(permissions.BasePermission):
    """
    Allow access only to the child assigned to the task.
    """

    def has_object_permission(self, request, view, obj):
        # Adjust this method based on your child authentication implementation
        return obj.assigned_to == request.user 
