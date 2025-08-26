from datetime import date, timedelta
from collections import Counter

from django.db.models import Sum
from rest_framework import generics, permissions, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response

from orders.models import OrderItem
from .models import SubscriptionPlan, Subscription, BillingPeriod
from .serializers import SubscriptionPlanSerializer, SubscriptionSerializer


class SubscriptionPlanListView(generics.ListAPIView):
    permission_classes = [permissions.AllowAny]
    serializer_class = SubscriptionPlanSerializer
    queryset = SubscriptionPlan.objects.filter(is_active=True)


class SubscriptionListCreateView(generics.ListCreateAPIView):
    serializer_class = SubscriptionSerializer

    def get_queryset(self):
        return Subscription.objects.filter(user=self.request.user, is_active=True)


class SubscriptionDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = SubscriptionSerializer
    queryset = Subscription.objects.all()

    def get_queryset(self):
        return Subscription.objects.filter(user=self.request.user)


@api_view(["POST"])
@permission_classes([permissions.IsAdminUser])
def run_subscription_cycle(request):
    today = date.today()
    subs = Subscription.objects.filter(is_active=True, next_delivery_date__lte=today)
    processed = 0
    for sub in subs:
        # naive next date calc
        delta = timedelta(days=7) if sub.plan.period == BillingPeriod.WEEKLY else timedelta(days=30)
        sub.next_delivery_date = today + delta
        sub.save(update_fields=["next_delivery_date"])
        processed += 1
    return Response({"processed": processed})


@api_view(["GET"])
@permission_classes([permissions.IsAuthenticated])
def suggest_bundles(request):
    # Simple suggestion: most frequently bought produce by the user in past orders
    items = (
        OrderItem.objects.filter(order__user=request.user)
        .values("product_name")
        .annotate(total_qty=Sum("quantity"))
        .order_by("-total_qty")[:10]
    )
    suggestions = [
        {"product_name": it["product_name"], "score": it["total_qty"]} for it in items
    ]
    return Response({"suggestions": suggestions})

# Create your views here.
