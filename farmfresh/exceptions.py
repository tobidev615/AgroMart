from typing import Any, Dict, Optional
from django.http import HttpRequest
from rest_framework.views import exception_handler
from rest_framework.response import Response
from rest_framework import status
from rest_framework.exceptions import APIException
import logging

logger = logging.getLogger(__name__)


class FarmFreshException(APIException):
    """Base exception for FarmFresh API."""
    status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
    default_detail = "An unexpected error occurred."
    default_code = "server_error"


class ValidationError(FarmFreshException):
    """Custom validation error."""
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = "Validation error."
    default_code = "validation_error"


class ResourceNotFoundError(FarmFreshException):
    """Resource not found error."""
    status_code = status.HTTP_404_NOT_FOUND
    default_detail = "Resource not found."
    default_code = "not_found"


class PermissionDeniedError(FarmFreshException):
    """Permission denied error."""
    status_code = status.HTTP_403_FORBIDDEN
    default_detail = "Permission denied."
    default_code = "permission_denied"


class RateLimitExceededError(FarmFreshException):
    """Rate limit exceeded error."""
    status_code = status.HTTP_429_TOO_MANY_REQUESTS
    default_detail = "Rate limit exceeded."
    default_code = "rate_limit_exceeded"


class ExternalServiceError(FarmFreshException):
    """External service error."""
    status_code = status.HTTP_502_BAD_GATEWAY
    default_detail = "External service unavailable."
    default_code = "external_service_error"


def custom_exception_handler(exc: Exception, context: Dict[str, Any]) -> Optional[Response]:
    """Custom exception handler for better error responses."""
    # Call REST framework's default exception handler first
    response = exception_handler(exc, context)
    
    if response is None:
        # Handle unexpected exceptions
        logger.error(f"Unexpected error: {exc}", exc_info=True)
        response = Response(
            {
                "detail": "An unexpected error occurred.",
                "code": "server_error",
                "request_id": getattr(context.get('request'), 'request_id', None)
            },
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )
    else:
        # Add request ID to response
        request = context.get('request')
        if request and hasattr(request, 'request_id'):
            response.data['request_id'] = request.request_id
        
        # Add error code if not present
        if 'code' not in response.data:
            response.data['code'] = getattr(exc, 'default_code', 'error')
        
        # Log the error
        logger.error(
            f"API Error: {response.status_code} - {response.data.get('detail', 'Unknown error')}",
            extra={
                'request_id': getattr(request, 'request_id', None),
                'user': getattr(request, 'user', None),
                'path': getattr(request, 'path', None),
                'method': getattr(request, 'method', None),
            }
        )
    
    return response


def handle_validation_error(exc: Exception, context: Dict[str, Any]) -> Response:
    """Handle validation errors with detailed field information."""
    request = context.get('request')
    
    # Extract field errors
    field_errors = {}
    if hasattr(exc, 'detail'):
        if isinstance(exc.detail, dict):
            field_errors = exc.detail
        else:
            field_errors = {'non_field_errors': [str(exc.detail)]}
    
    response_data = {
        "detail": "Validation error occurred.",
        "code": "validation_error",
        "field_errors": field_errors,
        "request_id": getattr(request, 'request_id', None) if request else None
    }
    
    logger.warning(
        f"Validation Error: {field_errors}",
        extra={
            'request_id': getattr(request, 'request_id', None),
            'user': getattr(request, 'user', None),
            'path': getattr(request, 'path', None),
        }
    )
    
    return Response(response_data, status=status.HTTP_400_BAD_REQUEST)


def handle_permission_error(exc: Exception, context: Dict[str, Any]) -> Response:
    """Handle permission denied errors."""
    request = context.get('request')
    
    response_data = {
        "detail": "You don't have permission to perform this action.",
        "code": "permission_denied",
        "request_id": getattr(request, 'request_id', None) if request else None
    }
    
    logger.warning(
        f"Permission Denied: {getattr(request, 'user', 'Anonymous')} tried to access {getattr(request, 'path', 'Unknown')}",
        extra={
            'request_id': getattr(request, 'request_id', None),
            'user': getattr(request, 'user', None),
            'path': getattr(request, 'path', None),
            'method': getattr(request, 'method', None),
        }
    )
    
    return Response(response_data, status=status.HTTP_403_FORBIDDEN)


def handle_rate_limit_error(exc: Exception, context: Dict[str, Any]) -> Response:
    """Handle rate limit exceeded errors."""
    request = context.get('request')
    
    response_data = {
        "detail": "Rate limit exceeded. Please try again later.",
        "code": "rate_limit_exceeded",
        "retry_after": getattr(exc, 'wait', 60),
        "request_id": getattr(request, 'request_id', None) if request else None
    }
    
    logger.warning(
        f"Rate Limit Exceeded: {getattr(request, 'user', 'Anonymous')} on {getattr(request, 'path', 'Unknown')}",
        extra={
            'request_id': getattr(request, 'request_id', None),
            'user': getattr(request, 'user', None),
            'path': getattr(request, 'path', None),
            'ip': getattr(request, 'META', {}).get('REMOTE_ADDR', None),
        }
    )
    
    return Response(response_data, status=status.HTTP_429_TOO_MANY_REQUESTS)


