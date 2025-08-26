from django.urls import path

from .views import (
    MyFarmerProfileView,
    ProduceListCreateView,
    ProduceRetrieveUpdateDestroyView,
    FarmClusterListCreateView,
    FarmClusterRetrieveUpdateDestroyView,
    FarmerProfileListView,
    FarmerProfileAdminDetailView,
    PublicProduceListView,
    PublicProduceDetailView,
    FarmerEarningsListView,
    farmer_dashboard,
    farmer_analytics,
)

urlpatterns = [
    path("me/", MyFarmerProfileView.as_view(), name="farmer-me"),
    path("produce/", ProduceListCreateView.as_view(), name="produce-list-create"),
    path("produce/<int:pk>/", ProduceRetrieveUpdateDestroyView.as_view(), name="produce-detail"),
    path("clusters/", FarmClusterListCreateView.as_view(), name="cluster-list-create"),
    path("clusters/<int:pk>/", FarmClusterRetrieveUpdateDestroyView.as_view(), name="cluster-detail"),
    # Admin/staff endpoints
    path("admin/farmers/", FarmerProfileListView.as_view(), name="admin-farmers-list"),
    path("admin/farmers/<int:pk>/", FarmerProfileAdminDetailView.as_view(), name="admin-farmer-detail"),
    # Public endpoints
    path("public/produce/", PublicProduceListView.as_view(), name="public-produce-list"),
    path("public/produce/<int:pk>/", PublicProduceDetailView.as_view(), name="public-produce-detail"),
    # Earnings dashboard endpoints
    path("earnings/", FarmerEarningsListView.as_view(), name="farmer-earnings"),
    path("dashboard/", farmer_dashboard, name="farmer-dashboard"),
    path("analytics/", farmer_analytics, name="farmer-analytics"),
]

