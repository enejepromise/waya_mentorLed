from rest_framework import permissions
from children.models import Child


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

class IsParentOrChildViewingOwnChores(permissions.BasePermission):
    """
    Allow access if the user is the parent of the child,
    or if the middleware has attached the child and it's the correct one.
    """

    def has_permission(self, request, view):
        child_id = request.query_params.get("childId")
        if not child_id:
            return False

        try:
            child = Child.objects.get(id=child_id)
        except Child.DoesNotExist:
            return False

        # Parent access
        if child.parent == request.user:
            return True

        # Middleware should have attached the correct child if child is logged in
        if hasattr(request, "child") and str(request.child.id) == str(child_id):
            return True

        return False
