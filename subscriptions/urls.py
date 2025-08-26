from django.urls import path

from .views import (
    SubscriptionPlanListView,
    SubscriptionListCreateView,
    SubscriptionDetailView,
    run_subscription_cycle,
    suggest_bundles,
)

urlpatterns = [
    path("plans/", SubscriptionPlanListView.as_view(), name="subscription-plans"),
    path("subscriptions/", SubscriptionListCreateView.as_view(), name="subscriptions"),
    path("subscriptions/<int:pk>/", SubscriptionDetailView.as_view(), name="subscription-detail"),
    path("subscriptions/run-cycle/", run_subscription_cycle, name="subscription-run-cycle"),
    path("subscriptions/suggest/", suggest_bundles, name="subscription-suggest"),
]





