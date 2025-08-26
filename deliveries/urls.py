from django.urls import path

from .views import (
    DeliveryListCreateView,
    DeliveryDetailView,
    DistributorAssignedDeliveriesList,
    distributor_mark_delivered,
)

urlpatterns = [
    path("deliveries/", DeliveryListCreateView.as_view(), name="deliveries"),
    path("deliveries/<int:pk>/", DeliveryDetailView.as_view(), name="delivery-detail"),
    path("deliveries/assigned/", DistributorAssignedDeliveriesList.as_view(), name="deliveries-assigned"),
    path("deliveries/<int:pk>/mark-delivered/", distributor_mark_delivered, name="delivery-mark-delivered"),
]

