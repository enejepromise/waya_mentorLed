from rest_framework import permissions
from users.models import User

class IsParent(permissions.BasePermission):
    """
    Allows access only to authenticated parent users.
    """
    message = "You must be a parent user to perform this action."

    def has_permission(self, request, view):
        user = request.user
        return (
            user 
            and user.is_authenticated 
            and user.role == User.ROLE_PARENT
        )

class IsChild(permissions.BasePermission):
    """
    Allows access only to authenticated child users.
    This assumes your custom authentication/middleware sets request.child for authenticated children.
    """
    message = "You must be a child user to perform this action."

    def has_permission(self, request, view):
        return hasattr(request, 'child') and request.child is not None

class IsParentOrChild(permissions.BasePermission):
    """
    Allows access if the requester is either the parent user or the authenticated child.
    """
    message = "You must be a parent or an authenticated child to perform this action."

    def has_permission(self, request, view):
        user = request.user
        is_parent = user and user.is_authenticated and user.role == User.ROLE_PARENT
        is_child = hasattr(request, 'child') and request.child is not None
        return is_parent or is_child

class IsOwnerParentOrAssignedChild(permissions.BasePermission):
    """
    Object-level permission to allow parents who own an object or the assigned child to access it.
    Assumes view is used on objects with 'parent' and 'assigned_to' (child) attributes.
    """

    message = "You do not have permission to access this object's data."

    def has_object_permission(self, request, view, obj):
        # Parent owns the object
        if request.user and request.user.is_authenticated and request.user.role == User.ROLE_PARENT:
            return obj.parent == request.user
        # Child assigned to the object matches authenticated child
        if hasattr(request, 'child') and request.child is not None:
            return obj.assigned_to == request.child
        return False
