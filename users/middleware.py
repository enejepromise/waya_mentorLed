# users/middleware.py
import json
import logging
import traceback
from django.http import JsonResponse
from django.conf import settings
from django.core.exceptions import PermissionDenied
from django.http import Http404
from rest_framework.exceptions import ValidationError, APIException

logger = logging.getLogger(__name__)

class CustomErrorHandlingMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        try:
            response = self.get_response(request)
            return response
        except Exception as exc:
            # Log full traceback
            logger.error("Unhandled exception:", exc_info=True)

            # Default response data
            data = {
                "detail": "An unexpected error occurred."
            }
            status_code = 500

            # Handle specific exceptions
            if isinstance(exc, Http404):
                data["detail"] = "Not found."
                status_code = 404
            elif isinstance(exc, PermissionDenied):
                data["detail"] = "Permission denied."
                status_code = 403
            elif isinstance(exc, ValidationError):
                # Validation errors from DRF serializers
                data = exc.detail
                status_code = 400
            elif isinstance(exc, APIException):
                data = exc.detail
                status_code = exc.status_code

            # Show detailed error info in debug mode
            if settings.DEBUG:
                data["error_type"] = exc.__class__.__name__
                data["traceback"] = traceback.format_exc()

            return JsonResponse(data, status=status_code)
