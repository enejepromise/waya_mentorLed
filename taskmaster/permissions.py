from rest_framework import permissions
from children.models import Child

class IsParentOrChildViewingOwnChores(permissions.BasePermission):
    """
    Allows:
    - A parent to view their own child's chores (via `childId` query param)
    - A child to view their own chores (uses `request.child`)
    """

    def has_permission(self, request, view):
        child_id = request.query_params.get("childId")

        # Case: child is logged in
        if hasattr(request, "child"):
            # If no childId is given, assume self-view
            if not child_id or str(request.child.id) == str(child_id):
                return True
            return False

        # Case: parent is logged in
        if request.user.is_authenticated:
            if not child_id:
                return False  # Parent must supply childId
            try:
                child = Child.objects.get(id=child_id)
                if child.parent == request.user:
                    request._view_child = child  # cache if needed
                    return True
            except Child.DoesNotExist:
                return False

        return False
from rest_framework import permissions

class IsParentOfChore(permissions.BasePermission):
    """
    Allows only the parent who owns the chore to access it.
    """
    def has_object_permission(self, request, view, obj):
        return obj.parent == request.user
# taskmaster/permissions.py
from rest_framework.permissions import BasePermission

class IsChildAssignedToChore(BasePermission):
    """
    Allows access only if the authenticated child is assigned to the chore.
    Assumes child authentication sets request.child.
    """

    def has_object_permission(self, request, view, obj):
        # obj is a Chore instance
        # Check if request.child exists and is assigned to this chore
        child = getattr(request, 'child', None)
        if child is None:
            return False

        return obj.assigned_to == child
