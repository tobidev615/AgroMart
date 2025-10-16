"""
URL configuration for farmfresh project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from drf_spectacular.views import SpectacularAPIView, SpectacularRedocView, SpectacularSwaggerView
from django.conf import settings
from django.conf.urls.static import static
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt

@csrf_exempt
def debug_static(request):
    """Debug endpoint to check static file configuration"""
    return JsonResponse({
        'DEBUG': settings.DEBUG,
        'STATIC_URL': settings.STATIC_URL,
        'STATIC_ROOT': str(settings.STATIC_ROOT),
        'STATICFILES_DIRS': [str(p) for p in getattr(settings, 'STATICFILES_DIRS', [])],
        'INSTALLED_APPS': [app for app in settings.INSTALLED_APPS if 'static' in app.lower()],
        'request_path': request.path,
        'request_method': request.method,
    })

urlpatterns = [
    path('debug/static/', debug_static, name='debug_static'),
    path('admin/', admin.site.urls),
    # OpenAPI schema and docs
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    path('api/docs/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
    path('api/redoc/', SpectacularRedocView.as_view(url_name='schema'), name='redoc'),
    
    # API v1 endpoints
    path('api/v1/', include('api.urls')),
    path('api/v1/accounts/', include('userprofiles.urls')),
    path('api/v1/farmers/', include('farmers.urls')),
    path('api/v1/', include('orders.urls')),
    path('api/v1/', include('deliveries.urls')),
    path('api/v1/', include('notifications.urls')),
    path('api/v1/', include('subscriptions.urls')),
    path('api/v1/business/', include('business.urls')),
    path('api/v1/distributors/', include('distributors.urls')),
    path('api/v1/consumers/', include('consumers.urls')),
    path('api/v1/', include('payments.urls')),
    path('api/v1/', include('inventory.urls')),
    
    # Legacy endpoints (redirect to v1)
    path('api/', include('api.urls')),
    path('api/accounts/', include('userprofiles.urls')),
    path('api/farmers/', include('farmers.urls')),
    path('api/', include('orders.urls')),
    path('api/', include('deliveries.urls')),
    path('api/', include('notifications.urls')),
    path('api/', include('subscriptions.urls')),
    path('api/business/', include('business.urls')),
    path('api/distributors/', include('distributors.urls')),
    path('api/consumers/', include('consumers.urls')),
    path('api/', include('payments.urls')),
    path('api/', include('inventory.urls')),
]

# Serve static and media files
if settings.DEBUG:
    # In development, serve files directly
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
else:
    # In production, serve static files from collected directory
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    # Media files should be served by your web server or CDN in production
    # But for now, we'll serve them here too
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)