from rest_framework import permissions
from children.models import Child


class IsParentOfChore(permissions.BasePermission):
    """
    Allows access only to the parent who owns the chore.
    """

    def has_object_permission(self, request, view, obj):
        return obj.parent == request.user


class IsChildAssignedToChore(permissions.BasePermission):
    """
    Allows access only to the child assigned to the chore.
    Requires `request.child` to be set by authentication logic.
    """

    def has_object_permission(self, request, view, obj):
        return hasattr(request, "child") and obj.assigned_to == request.child


class IsParentOrChildViewingOwnChores(permissions.BasePermission):
    """
    Allows:
    - A parent to view their own child's chores (using query param `childId`)
    - A child to view their own chores (matched against `request.child.id`)
    """

    def has_permission(self, request, view):
        child_id = request.query_params.get("childId")
        if not child_id:
            return False

        try:
            child = Child.objects.get(id=child_id)
        except Child.DoesNotExist:
            return False

        # Parent is logged in
        if request.user.is_authenticated and child.parent == request.user:
            request._view_child = child  # Optional: cache for view use
            return True

        # Child is logged in (attached to request manually)
        if hasattr(request, "child") and str(request.child.id) == str(child_id):
            return True

        return False
