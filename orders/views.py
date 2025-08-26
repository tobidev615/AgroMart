from decimal import Decimal
from typing import Any

from django.db import transaction
from django.db.models import F
from django.contrib.auth.models import User
from django.utils import timezone
from rest_framework import generics, permissions, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework import viewsets

from .models import Cart, CartItem, Order, OrderItem, OrderStatus
from .serializers import CartSerializer, CartItemSerializer, OrderSerializer
from notifications.utils import notify_user
from deliveries.models import Delivery, DeliveryStatus
from farmers.models import FarmerEarnings


def get_or_create_cart(user: User) -> Cart:
    """Return the user's cart, creating it if missing."""
    cart, _ = Cart.objects.get_or_create(user=user)
    return cart


@api_view(["GET", "POST", "PUT", "DELETE"])
@permission_classes([permissions.IsAuthenticated])
def cart_view(request: Request) -> Response:
    """Manage user's shopping cart."""
    cart = get_or_create_cart(request.user)  # type: ignore[arg-type]
    
    if request.method == "GET":
        serializer = CartSerializer(cart)
        return Response(serializer.data)
    
    elif request.method == "POST":
        # Add item to cart
        serializer = CartItemSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(cart=cart)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    elif request.method == "PUT":
        # Update cart
        serializer = CartSerializer(cart, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    elif request.method == "DELETE":
        # Clear cart
        cart.items.all().delete()
        return Response({"detail": "Cart cleared."}, status=status.HTTP_204_NO_CONTENT)


class CartItemListCreateView(generics.ListCreateAPIView):
    """List and add items in the current user's cart."""
    serializer_class = CartItemSerializer

    def get_queryset(self):
        return get_or_create_cart(self.request.user).items.select_related("produce")  # type: ignore[arg-type]

    def perform_create(self, serializer: CartItemSerializer) -> None:
        cart = get_or_create_cart(self.request.user)  # type: ignore[arg-type]
        serializer.save(cart=cart)


class CartItemDetailView(generics.RetrieveUpdateDestroyAPIView):
    """Retrieve, update, or remove a cart item from the current user's cart."""
    serializer_class = CartItemSerializer

    def get_queryset(self):
        return get_or_create_cart(self.request.user).items.select_related("produce")  # type: ignore[arg-type]


@api_view(["POST"])
@permission_classes([permissions.IsAuthenticated])
@transaction.atomic
def checkout(request: Request) -> Response:
    """Create an order from the user's cart.

    Steps:
    - Validate cart has items and quantities are in stock
    - Create order and order items
    - Decrement stock atomically; mark produce unavailable at zero
    - Create FarmerEarnings records for each produce
    - Notify farmers per order
    - Clear cart and create a delivery placeholder
    """
    cart = get_or_create_cart(request.user)  # type: ignore[arg-type]
    items = list(cart.items.select_related("produce"))
    if not items:
        return Response({"detail": "Cart is empty."}, status=status.HTTP_400_BAD_REQUEST)

    # Validate stock
    stock_errors = []
    for item in items:
        available_qty = item.produce.quantity_available
        if item.quantity <= 0:
            stock_errors.append({
                "produce_id": item.produce_id,
                "name": item.produce.name,
                "detail": "Quantity must be greater than zero."
            })
        elif available_qty < item.quantity:
            stock_errors.append({
                "produce_id": item.produce_id,
                "name": item.produce.name,
                "available": available_qty,
                "requested": item.quantity,
                "detail": "Insufficient stock",
            })
    if stock_errors:
        return Response({"errors": stock_errors}, status=status.HTTP_400_BAD_REQUEST)

    # Create order and reserve stock
    order = Order.objects.create(user=request.user, status=OrderStatus.PENDING)
    total = Decimal("0")

    for item in items:
        produce = item.produce
        price = produce.price_per_unit
        subtotal = price * item.quantity
        
        # Create order item
        OrderItem.objects.create(
            order=order,
            produce=produce,
            product_name=produce.name,
            unit=produce.unit,
            price_per_unit=price,
            quantity=item.quantity,
            subtotal=subtotal,
        )
        
        # Create FarmerEarnings record
        FarmerEarnings.objects.create(
            farmer=produce.farmer,
            order=order,
            produce=produce,
            quantity=item.quantity,
            unit_price=price,
            total_amount=subtotal,
            status='PENDING'
        )
        
        # decrement stock
        produce.quantity_available = F("quantity_available") - item.quantity
        produce.save(update_fields=["quantity_available"]) 
        # if stock reaches 0, mark unavailable
        produce.refresh_from_db(fields=["quantity_available", "available"])
        if produce.quantity_available <= 0 and produce.available:
            produce.available = False
            produce.save(update_fields=["available"])
        total += subtotal

    order.total_amount = total
    order.save(update_fields=["total_amount"])
    cart.items.all().delete()

    # Update consumer analytics if user is a consumer
    if hasattr(request.user, 'consumer_profile'):
        consumer_profile = request.user.consumer_profile
        consumer_profile.update_spending_analytics(total)
        consumer_profile.last_order_date = timezone.now()
        consumer_profile.save(update_fields=['last_order_date'])

    # notify farmers per order item
    notified_farmers = set()
    for order_item in order.items.select_related("produce__farmer__user"):
        farmer_user = order_item.produce.farmer.user if order_item.produce and order_item.produce.farmer else None
        if farmer_user and farmer_user.id not in notified_farmers:
            notify_user(
                farmer_user,
                title="New order placed",
                message=f"An order containing your produce has been placed. Order #{order.id}.",
            )
            notified_farmers.add(farmer_user.id)

    # create delivery placeholder (scheduled date optional; set when staff confirms)
    Delivery.objects.get_or_create(order=order)

    return Response(OrderSerializer(order).data, status=status.HTTP_201_CREATED)


class OrderListView(generics.ListAPIView):
    """List the current user's orders with eager-loaded order items."""
    serializer_class = OrderSerializer

    def get_queryset(self):
        return Order.objects.filter(user=self.request.user).prefetch_related("items")


class OrderViewSet(viewsets.ModelViewSet):
    """CRUD for orders scoped to the authenticated user."""
    serializer_class = OrderSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Order.objects.select_related('user').prefetch_related('items', 'items__produce', 'items__produce__farmer').filter(user=self.request.user)


class OrderDetailUpdateStatusView(generics.RetrieveUpdateAPIView):
    """Retrieve and update order status (staff only for status updates)."""
    serializer_class = OrderSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Order.objects.select_related('user').prefetch_related('items').filter(user=self.request.user)

    def perform_update(self, serializer):
        """Update order status and notify user of changes."""
        old_status = self.get_object().status
        new_status = serializer.validated_data.get('status', old_status)
        
        # Save the order
        order = serializer.save()
        
        # If status changed, notify user and update earnings
        if old_status != new_status:
            # Notify user of status change
            notify_user(
                order.user,
                title=f"Order #{order.id} status updated",
                message=f"Your order status has been updated to {new_status}.",
            )
            
            # If order is confirmed, update farmer earnings
            if new_status == OrderStatus.CONFIRMED:
                from farmers.models import FarmerEarnings
                earnings_records = FarmerEarnings.objects.filter(order=order)
                for earning in earnings_records:
                    earning.status = 'CONFIRMED'
                    earning.save()
                    
                    # Update farmer profile earnings
                    earning.farmer.update_earnings(earning.total_amount)
                    
                    # Update produce sales stats
                    earning.produce.update_sales_stats(earning.quantity, earning.total_amount)


class FarmerOrderHistoryView(generics.ListAPIView):
    """List orders that include items from the requesting farmer."""
    serializer_class = OrderSerializer

    def get_queryset(self):
        user = self.request.user
        if not user.is_authenticated or not hasattr(user, "farmer_profile"):
            return Order.objects.none()
        farmer_profile = user.farmer_profile
        return (
            Order.objects.filter(items__produce__farmer=farmer_profile)
            .distinct()
            .prefetch_related("items")
        )

# Create your views here.
