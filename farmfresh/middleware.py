import re
import html
from typing import Any, Callable
from django.http import HttpRequest, HttpResponse
from django.utils.deprecation import MiddlewareMixin
from rest_framework.throttling import UserRateThrottle, AnonRateThrottle
from rest_framework.response import Response
from rest_framework import status


class SecurityHeadersMiddleware(MiddlewareMixin):
    """Add security headers to all responses."""
    
    def process_response(self, request: HttpRequest, response: HttpResponse) -> HttpResponse:
        # Security headers
        response["X-Content-Type-Options"] = "nosniff"
        response["X-Frame-Options"] = "DENY"
        response["X-XSS-Protection"] = "1; mode=block"
        response["Referrer-Policy"] = "strict-origin-when-cross-origin"
        response["Permissions-Policy"] = "geolocation=(), microphone=(), camera=()"
        
        # Content Security Policy
        csp = (
            "default-src 'self'; "
            "script-src 'self' 'unsafe-inline'; "
            "style-src 'self' 'unsafe-inline'; "
            "img-src 'self' data: https:; "
            "font-src 'self'; "
            "connect-src 'self'; "
            "frame-ancestors 'none';"
        )
        response["Content-Security-Policy"] = csp
        
        return response


class InputSanitizationMiddleware(MiddlewareMixin):
    """Sanitize user input to prevent XSS and injection attacks."""
    
    def __init__(self, get_response: Callable) -> None:
        super().__init__(get_response)
        # Patterns for potentially dangerous content
        self.dangerous_patterns = [
            r'<script[^>]*>.*?</script>',
            r'javascript:',
            r'vbscript:',
            r'on\w+\s*=',
            r'<iframe[^>]*>',
            r'<object[^>]*>',
            r'<embed[^>]*>',
        ]
        self.compiled_patterns = [re.compile(pattern, re.IGNORECASE | re.DOTALL) 
                                for pattern in self.dangerous_patterns]
    
    def process_request(self, request: HttpRequest):
        """Sanitize GET and POST parameters."""
        if request.method in ['GET', 'POST']:
            # Sanitize GET parameters
            for key, value in request.GET.items():
                if isinstance(value, str):
                    sanitized = self._sanitize_input(value)
                    if sanitized != value:
                        request.GET._mutable = True
                        request.GET[key] = sanitized
                        request.GET._mutable = False
            
            # Sanitize POST parameters
            if hasattr(request, 'POST') and request.POST:
                for key, value in request.POST.items():
                    if isinstance(value, str):
                        sanitized = self._sanitize_input(value)
                        if sanitized != value:
                            request.POST._mutable = True
                            request.POST[key] = sanitized
                            request.POST._mutable = False
        
        return None
    
    def _sanitize_input(self, value: str) -> str:
        """Sanitize a single input value."""
        # Check for dangerous patterns
        for pattern in self.compiled_patterns:
            if pattern.search(value):
                return ""
        
        # HTML escape to prevent XSS
        return html.escape(value, quote=True)


class AdvancedRateLimitMiddleware(MiddlewareMixin):
    """Advanced rate limiting per endpoint with different limits."""
    
    def __init__(self, get_response: Callable) -> None:
        super().__init__(get_response)
        self.endpoint_limits = {
            '/api/accounts/register/': {'anon': '5/hour', 'user': '10/hour'},
            '/api/accounts/login/': {'anon': '10/hour', 'user': '20/hour'},
            '/api/checkout/': {'user': '50/hour'},
            '/api/farmers/public/produce/': {'anon': '1000/hour', 'user': '2000/hour'},
            '/api/notifications/stream/': {'user': '100/hour'},
        }
        self.throttle_classes = {
            'anon': AnonRateThrottle,
            'user': UserRateThrottle,
        }
    
    def process_view(self, request: HttpRequest, view_func, view_args, view_kwargs):
        """Apply rate limiting based on endpoint."""
        path = request.path_info
        
        # Find matching endpoint limits
        for endpoint, limits in self.endpoint_limits.items():
            if path.startswith(endpoint):
                response = self._apply_rate_limit(request, limits, view_func)
                if response:
                    return response
                break
        
        return None
    
    def _apply_rate_limit(self, request: HttpRequest, limits: dict, view):
        """Apply rate limiting for specific endpoint."""
        user_type = 'user' if request.user.is_authenticated else 'anon'
        
        if user_type in limits:
            throttle_class = self.throttle_classes[user_type]
            throttle = throttle_class()
            
            # Set custom rate limit
            throttle.rate = limits[user_type]
            
            # Check if throttled
            if not throttle.allow_request(request, view):
                return Response(
                    {"detail": "Rate limit exceeded for this endpoint."},
                    status=status.HTTP_429_TOO_MANY_REQUESTS
                )
        return None


class SQLInjectionProtectionMiddleware(MiddlewareMixin):
    """Additional SQL injection protection beyond Django ORM."""
    
    def __init__(self, get_response: Callable) -> None:
        super().__init__(get_response)
        # SQL injection patterns
        self.sql_patterns = [
            r'(\b(union|select|insert|update|delete|drop|create|alter)\b)',
            r'(\b(or|and)\b\s+\d+\s*=\s*\d+)',
            r'(\b(union|select)\b.*\bfrom\b)',
            r'(\b(union|select)\b.*\bwhere\b)',
            r'(\b(union|select)\b.*\bgroup\b\s+by\b)',
            r'(\b(union|select)\b.*\border\b\s+by\b)',
            r'(\b(union|select)\b.*\blimit\b)',
            r'(\b(union|select)\b.*\boffset\b)',
            r'(\b(union|select)\b.*\btop\b)',
            r'(\b(union|select)\b.*\brownum\b)',
            r'(\b(union|select)\b.*\brownumber\b)',
            r'(\b(union|select)\b.*\brownum\b)',
            r'(\b(union|select)\b.*\brownumber\b)',
            r'(\b(union|select)\b.*\brownum\b)',
            r'(\b(union|select)\b.*\brownumber\b)',
        ]
        self.compiled_sql_patterns = [re.compile(pattern, re.IGNORECASE) 
                                     for pattern in self.sql_patterns]
    
    def process_request(self, request: HttpRequest):
        """Check for SQL injection attempts in request parameters."""
        # Check GET parameters
        for key, value in request.GET.items():
            if isinstance(value, str) and self._contains_sql_injection(value):
                return Response(
                    {"detail": "Invalid input detected."},
                    status=status.HTTP_400_BAD_REQUEST
                )
        
        # Check POST parameters
        if hasattr(request, 'POST') and request.POST:
            for key, value in request.POST.items():
                if isinstance(value, str) and self._contains_sql_injection(value):
                    return Response(
                        {"detail": "Invalid input detected."},
                        status=status.HTTP_400_BAD_REQUEST
                    )
        
        return None
    
    def _contains_sql_injection(self, value: str) -> bool:
        """Check if value contains SQL injection patterns."""
        for pattern in self.compiled_sql_patterns:
            if pattern.search(value):
                return True
        return False

