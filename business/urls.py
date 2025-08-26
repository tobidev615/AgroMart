from django.urls import path

from .views import (
    MyBusinessProfileView,
    MyBusinessOrdersView,
    PricingTierListCreateView,
    PricingTierDetailView,
    ContractOrderListCreateView,
    ContractOrderDetailView,
    BusinessInvoiceListView,
    BusinessInvoiceDetailView,
    create_bulk_order,
    run_contract_orders,
    logistics_dashboard,
    business_analytics,
)

urlpatterns = [
    path("me/", MyBusinessProfileView.as_view(), name="business-me"),
    path("orders/", MyBusinessOrdersView.as_view(), name="business-orders"),

    # Pricing tiers (admin-managed)
    path("pricing-tiers/", PricingTierListCreateView.as_view(), name="business-pricing-tiers"),
    path("pricing-tiers/<int:pk>/", PricingTierDetailView.as_view(), name="business-pricing-tier-detail"),

    # Contract orders
    path("contracts/", ContractOrderListCreateView.as_view(), name="business-contracts"),
    path("contracts/<int:pk>/", ContractOrderDetailView.as_view(), name="business-contract-detail"),
    path("contracts/run-cycle/", run_contract_orders, name="business-contracts-run"),

    # Invoices
    path("invoices/", BusinessInvoiceListView.as_view(), name="business-invoices"),
    path("invoices/<int:pk>/", BusinessInvoiceDetailView.as_view(), name="business-invoice-detail"),

    # Bulk orders
    path("bulk-orders/", create_bulk_order, name="business-bulk-order"),

    # Logistics dashboard & analytics
    path("logistics/", logistics_dashboard, name="business-logistics"),
    path("analytics/", business_analytics, name="business-analytics"),
]

