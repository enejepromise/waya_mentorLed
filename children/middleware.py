from children.models import Child
from django.core.exceptions import PermissionDenied

class AttachChildFromHeaderMiddleware:
    """
    Middleware to attach a `request.child` based on 'X-Child-ID' header.
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        child_id = request.headers.get('X-Child-ID')

        if request.user.is_authenticated and child_id:
            try:
                child = Child.objects.get(id=child_id, parent=request.user)
                request.child = child
            except Child.DoesNotExist:
                raise PermissionDenied("Invalid child ID or unauthorized access.")

        return self.get_response(request)
