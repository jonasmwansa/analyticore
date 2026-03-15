"""
Custom DRF Exception Handler

Returns generic error messages in production to avoid leaking internal details.
In DEBUG mode, includes the original error detail for development convenience.
"""
import logging
from rest_framework.views import exception_handler
from rest_framework.response import Response
from rest_framework import status
from django.conf import settings

logger = logging.getLogger(__name__)


def custom_exception_handler(exc, context):
    """
    Custom exception handler that:
    - Logs the full exception server-side
    - Returns generic error messages in production
    - Returns detailed errors only in DEBUG mode
    """
    # Call DRF's default exception handler first
    response = exception_handler(exc, context)

    if response is not None:
        # DRF handled it (validation errors, permission denied, etc.)
        return response

    # Unhandled exception — log it and return a safe response
    view = context.get('view', None)
    view_name = view.__class__.__name__ if view else 'Unknown'

    logger.exception(
        "Unhandled exception in %s: %s",
        view_name,
        str(exc),
    )

    if settings.DEBUG:
        detail = f"Internal error: {str(exc)}"
    else:
        detail = "An internal error occurred. Please try again later."

    return Response(
        {'detail': detail},
        status=status.HTTP_500_INTERNAL_SERVER_ERROR,
    )
