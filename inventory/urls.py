from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import CategoryViewSet, ProductViewSet, ProductVariantViewSet

router = DefaultRouter()
router.register(r"categories", CategoryViewSet, basename="inventory-category")
router.register(r"products", ProductViewSet, basename="inventory-product")
router.register(r"variants", ProductVariantViewSet, basename="inventory-variant")

urlpatterns = [
    path("inventory/", include(router.urls)),
]