from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import (
    DeliveryListCreateView,
    DeliveryDetailView,
    DistributorAssignedDeliveriesList,
    distributor_mark_delivered,
    DeliveryBatchViewSet,
    DeliveryWindowViewSet,
)

router = DefaultRouter()
router.register(r"delivery-windows", DeliveryWindowViewSet, basename="delivery-window")
router.register(r"delivery-batches", DeliveryBatchViewSet, basename="delivery-batch")

urlpatterns = [
    path("deliveries/", DeliveryListCreateView.as_view(), name="deliveries"),
    path("deliveries/<int:pk>/", DeliveryDetailView.as_view(), name="delivery-detail"),
    path("deliveries/assigned/", DistributorAssignedDeliveriesList.as_view(), name="deliveries-assigned"),
    path("deliveries/<int:pk>/mark-delivered/", distributor_mark_delivered, name="delivery-mark-delivered"),
    path("", include(router.urls)),
]

