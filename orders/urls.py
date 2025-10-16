from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import (
    cart_view,
    CartItemListCreateView,
    CartItemDetailView,
    checkout,
    OrderListView,
    OrderDetailUpdateStatusView,
    FarmerOrderHistoryView,
    MixedBoxViewSet,
)

router = DefaultRouter()
router.register(r"mixed-boxes", MixedBoxViewSet, basename="mixed-box")

urlpatterns = [
    path("cart/", cart_view, name="cart"),
    path("cart/items/", CartItemListCreateView.as_view(), name="cart-items"),
    path("cart/items/<int:pk>/", CartItemDetailView.as_view(), name="cart-item-detail"),
    path("checkout/", checkout, name="checkout"),
    path("orders/", OrderListView.as_view(), name="orders"),
    path("orders/<int:pk>/", OrderDetailUpdateStatusView.as_view(), name="order-detail"),
    path("farmer/orders/", FarmerOrderHistoryView.as_view(), name="farmer-orders"),
    path("", include(router.urls)),
]