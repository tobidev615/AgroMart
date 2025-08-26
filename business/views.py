from datetime import date, timedelta
from decimal import Decimal

from django.db import transaction
from django.db.models import Sum, Count
from rest_framework import generics, permissions, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response

from userprofiles.models import UserType
from .models import (
    BusinessProfile,
    BusinessPricingTier,
    ContractOrder,
    ContractOrderItem,
    BusinessInvoice,
)
from .serializers import (
    BusinessProfileSerializer,
    BusinessPricingTierSerializer,
    ContractOrderSerializer,
    BusinessInvoiceSerializer,
    BulkOrderCreateSerializer,
)
from orders.models import Order, OrderItem, OrderStatus
from orders.serializers import OrderSerializer
from farmers.models import Produce
from farmers.models import FarmerEarnings
from notifications.utils import notify_user
from deliveries.models import Delivery


class IsBusinessOrStaff(permissions.BasePermission):
    def has_permission(self, request, view):
        user = request.user
        if not (user and user.is_authenticated):
            return False
        if user.is_staff:
            return True
        return hasattr(user, "profile") and user.profile.role == UserType.BUSINESS


class MyBusinessProfileView(generics.RetrieveUpdateAPIView):
    serializer_class = BusinessProfileSerializer
    permission_classes = [IsBusinessOrStaff]

    def get_object(self):
        user = self.request.user
        profile, _ = BusinessProfile.objects.get_or_create(
            user=user, defaults={"name": user.get_full_name() or user.username}
        )
        return profile


class MyBusinessOrdersView(generics.ListAPIView):
    serializer_class = OrderSerializer
    permission_classes = [IsBusinessOrStaff]

    def get_queryset(self):
        return Order.objects.filter(user=self.request.user).prefetch_related("items")


class PricingTierListCreateView(generics.ListCreateAPIView):
    serializer_class = BusinessPricingTierSerializer
    permission_classes = [permissions.IsAdminUser]

    def get_queryset(self):
        return BusinessPricingTier.objects.all().select_related("business", "produce")


class PricingTierDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = BusinessPricingTierSerializer
    permission_classes = [permissions.IsAdminUser]
    queryset = BusinessPricingTier.objects.all()


class ContractOrderListCreateView(generics.ListCreateAPIView):
    serializer_class = ContractOrderSerializer
    permission_classes = [IsBusinessOrStaff]

    def get_queryset(self):
        return ContractOrder.objects.filter(business__user=self.request.user).prefetch_related("items", "items__produce")

    def perform_create(self, serializer):
        business = BusinessProfile.objects.get(user=self.request.user)
        serializer.save(business=business)


class ContractOrderDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = ContractOrderSerializer
    permission_classes = [IsBusinessOrStaff]

    def get_queryset(self):
        return ContractOrder.objects.filter(business__user=self.request.user).prefetch_related("items", "items__produce")


class BusinessInvoiceListView(generics.ListAPIView):
    serializer_class = BusinessInvoiceSerializer
    permission_classes = [IsBusinessOrStaff]

    def get_queryset(self):
        return BusinessInvoice.objects.filter(business__user=self.request.user).select_related("order", "business")


class BusinessInvoiceDetailView(generics.RetrieveAPIView):
    serializer_class = BusinessInvoiceSerializer
    permission_classes = [IsBusinessOrStaff]

    def get_queryset(self):
        return BusinessInvoice.objects.filter(business__user=self.request.user).select_related("order", "business")


@api_view(["POST"])
@permission_classes([IsBusinessOrStaff])
def create_bulk_order(request):
    """Create an order with volume pricing and bulk units for business users."""
    serializer = BulkOrderCreateSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    items_data = serializer.validated_data["items"]

    with transaction.atomic():
        order = Order.objects.create(user=request.user, status=OrderStatus.PENDING)
        total = Decimal("0")

        for item in items_data:
            produce = Produce.objects.select_for_update().get(id=item["produce_id"])  # lock row
            quantity = int(item["quantity"])  # bulk quantity
            unit = item["unit"]

            if quantity <= 0:
                transaction.set_rollback(True)
                return Response({"detail": f"Invalid quantity for produce {produce.id}"}, status=status.HTTP_400_BAD_REQUEST)
            if produce.quantity_available < quantity:
                transaction.set_rollback(True)
                return Response({"detail": f"Insufficient stock for {produce.name}", "available": produce.quantity_available}, status=status.HTTP_400_BAD_REQUEST)

            # Determine unit price considering pricing tiers (business-specific first, then global)
            price = produce.price_per_unit
            tier = (
                BusinessPricingTier.objects.filter(business__user=request.user, produce=produce, min_quantity__lte=quantity, unit=unit, active=True)
                .order_by("-min_quantity")
                .first()
            ) or (
                BusinessPricingTier.objects.filter(business__isnull=True, produce=produce, min_quantity__lte=quantity, unit=unit, active=True)
                .order_by("-min_quantity")
                .first()
            )
            if tier:
                price = tier.unit_price

            subtotal = price * Decimal(quantity)

            # Create order item
            OrderItem.objects.create(
                order=order,
                produce=produce,
                product_name=produce.name,
                unit=unit,
                price_per_unit=price,
                quantity=quantity,
                subtotal=subtotal,
            )

            # Create farmer earnings
            FarmerEarnings.objects.create(
                farmer=produce.farmer,
                order=order,
                produce=produce,
                quantity=quantity,
                unit_price=price,
                total_amount=subtotal,
                status='PENDING'
            )

            # Decrement stock
            produce.quantity_available -= quantity
            if produce.quantity_available <= 0:
                produce.available = False
            produce.save(update_fields=["quantity_available", "available"]) 

            total += subtotal

        order.total_amount = total
        order.save(update_fields=["total_amount"]) 

        # Create delivery placeholder
        Delivery.objects.get_or_create(order=order)

    return Response(OrderSerializer(order).data, status=status.HTTP_201_CREATED)


@api_view(["POST"])  # admin-only run cycle
@permission_classes([permissions.IsAdminUser])
def run_contract_orders(request):
    """Process active contract orders due today and create Orders + Deliveries."""
    today = date.today()
    processed = 0
    for contract in ContractOrder.objects.select_related("business").prefetch_related("items").filter(is_active=True, next_delivery_date__lte=today):
        with transaction.atomic():
            order = Order.objects.create(user=contract.business.user, status=OrderStatus.PENDING)
            total = Decimal("0")
            for item in contract.items.select_related("produce"):
                produce = item.produce
                if produce.quantity_available < item.quantity:
                    continue
                subtotal = item.agreed_unit_price * Decimal(item.quantity)
                OrderItem.objects.create(
                    order=order,
                    produce=produce,
                    product_name=produce.name,
                    unit=item.unit,
                    price_per_unit=item.agreed_unit_price,
                    quantity=item.quantity,
                    subtotal=subtotal,
                )
                FarmerEarnings.objects.create(
                    farmer=produce.farmer,
                    order=order,
                    produce=produce,
                    quantity=item.quantity,
                    unit_price=item.agreed_unit_price,
                    total_amount=subtotal,
                    status='PENDING'
                )
                produce.quantity_available -= item.quantity
                if produce.quantity_available <= 0:
                    produce.available = False
                produce.save(update_fields=["quantity_available", "available"]) 
                total += subtotal

            order.total_amount = total
            order.save(update_fields=["total_amount"]) 
            Delivery.objects.get_or_create(order=order)

            # advance next date
            if contract.frequency == 'WEEKLY':
                contract.next_delivery_date = today + timedelta(days=7)
            elif contract.frequency == 'BIWEEKLY':
                contract.next_delivery_date = today + timedelta(days=14)
            else:
                contract.next_delivery_date = today + timedelta(days=30)
            contract.save(update_fields=["next_delivery_date"]) 
            processed += 1

    return Response({"processed": processed})


@api_view(["GET"])  # basic logistics dashboard
@permission_classes([IsBusinessOrStaff])
def logistics_dashboard(request):
    orders = Order.objects.filter(user=request.user).values("id", "status", "created_at")
    deliveries = Delivery.objects.filter(order__user=request.user).values("id", "order_id", "status", "scheduled_date", "notes")
    return Response({"orders": list(orders), "deliveries": list(deliveries)})


@api_view(["GET"])  # simple analytics
@permission_classes([IsBusinessOrStaff])
def business_analytics(request):
    totals = (
        Order.objects.filter(user=request.user)
        .aggregate(total_spent=Sum("total_amount"), total_orders=Count("id"))
    )
    top_items = (
        OrderItem.objects.filter(order__user=request.user)
        .values("product_name")
        .annotate(total_qty=Sum("quantity"))
        .order_by("-total_qty")[:10]
    )
    return Response({
        "total_spent": totals.get("total_spent") or Decimal("0.00"),
        "total_orders": totals.get("total_orders") or 0,
        "top_items": list(top_items),
    })
