from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework import status
from django.db import connection
from django.core.cache import cache
import redis
from django.conf import settings

@api_view(["GET"])
@permission_classes([AllowAny])
def health(request):
    return Response({"status": "ok"}, status=status.HTTP_200_OK)

@api_view(["GET"])
@permission_classes([AllowAny])
def readiness_probe(request):
    """Check if the application is ready to serve requests."""
    checks = {
        "database": False,
        "cache": False,
        "redis": False,
    }
    
    # Check database
    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
        checks["database"] = True
    except Exception:
        pass
    
    # Check cache
    try:
        cache.set("health_check", "ok", 1)
        if cache.get("health_check") == "ok":
            checks["cache"] = True
    except Exception:
        pass
    
    # Check Redis
    try:
        r = redis.Redis.from_url(settings.CELERY_BROKER_URL)
        r.ping()
        checks["redis"] = True
    except Exception:
        pass
    
    all_healthy = all(checks.values())
    status_code = status.HTTP_200_OK if all_healthy else status.HTTP_503_SERVICE_UNAVAILABLE
    
    return Response({
        "status": "healthy" if all_healthy else "unhealthy",
        "checks": checks
    }, status=status_code)

# Create your views here.
