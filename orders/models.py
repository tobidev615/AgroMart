from django.db import models
from django.contrib.auth.models import User
from farmers.models import Produce
from django.core.validators import MinValueValidator
from django.db.models import Q


class OrderStatus(models.TextChoices):
    PENDING = "PENDING", "Pending"
    CONFIRMED = "CONFIRMED", "Confirmed"
    DELIVERED = "DELIVERED", "Delivered"


class Cart(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="cart")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self) -> str:
        return f"Cart({self.user.username})"


class CartItem(models.Model):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name="items")
    produce = models.ForeignKey(Produce, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    added_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("cart", "produce")

    def __str__(self) -> str:
        return f"{self.quantity} x {self.produce}"


class BoxSize(models.TextChoices):
    SMALL = "SMALL", "Small"
    MEDIUM = "MEDIUM", "Medium"
    LARGE = "LARGE", "Large"


class MixedBox(models.Model):
    """Predefined mixed produce box offered as the primary order unit."""
    name = models.CharField(max_length=150)
    size = models.CharField(max_length=20, choices=BoxSize.choices)
    description = models.TextField(blank=True)
    price = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(0)])
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        indexes = [
            models.Index(fields=["is_active"]),
            models.Index(fields=["size"]),
        ]

    def __str__(self) -> str:
        return f"{self.name} ({self.size})"


class MixedBoxItem(models.Model):
    """Composition of a mixed box in terms of produce and quantity."""
    box = models.ForeignKey(MixedBox, on_delete=models.CASCADE, related_name="items")
    produce = models.ForeignKey(Produce, on_delete=models.PROTECT, related_name="box_items")
    quantity = models.PositiveIntegerField(default=1, validators=[MinValueValidator(1)])

    class Meta:
        unique_together = ("box", "produce")
        indexes = [
            models.Index(fields=["box"]),
            models.Index(fields=["produce"]),
        ]

    def __str__(self) -> str:
        return f"{self.quantity} x {self.produce.name} in {self.box.name}"


class Order(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="orders")
    status = models.CharField(max_length=20, choices=OrderStatus.choices, default=OrderStatus.PENDING)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    payment_intent_id = models.CharField(max_length=255, blank=True)
    payment_status = models.CharField(max_length=24, choices=[
        ("UNPAID", "Unpaid"),
        ("PAID", "Paid"),
        ("PARTIALLY_REFUNDED", "Partially refunded"),
        ("REFUNDED", "Refunded"),
    ], default="UNPAID")
    delivery_window = models.ForeignKey('deliveries.DeliveryWindow', on_delete=models.SET_NULL, null=True, blank=True, related_name='orders')
    delivery_fee = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        indexes = [
            models.Index(fields=['status']),
            models.Index(fields=['created_at']),
            models.Index(fields=['user', 'status']),
        ]

    def __str__(self) -> str:
        return f"Order {self.id} by {self.user.username} - {self.status}"


class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name="items")
    produce = models.ForeignKey(Produce, on_delete=models.SET_NULL, null=True, blank=True)
    mixed_box = models.ForeignKey('orders.MixedBox', on_delete=models.PROTECT, null=True, blank=True, related_name='order_items')
    dry_variant = models.ForeignKey('inventory.ProductVariant', on_delete=models.PROTECT, null=True, blank=True, related_name='order_items')
    product_name = models.CharField(max_length=200)
    unit = models.CharField(max_length=50)
    price_per_unit = models.DecimalField(max_digits=10, decimal_places=2)
    quantity = models.PositiveIntegerField()
    subtotal = models.DecimalField(max_digits=12, decimal_places=2)
    # Shortage/substitution tracking
    is_substituted = models.BooleanField(default=False)
    substituted_product_name = models.CharField(max_length=200, blank=True)
    shortage_quantity = models.PositiveIntegerField(default=0)
    refunded_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0)

    def __str__(self) -> str:
        return f"{self.quantity} x {self.product_name}"

    class Meta:
        constraints = [
            models.CheckConstraint(
                check=(
                    Q(produce__isnull=False) |
                    Q(mixed_box__isnull=False) |
                    Q(dry_variant__isnull=False)
                ),
                name="order_item_requires_one_source",
            )
        ]

# Create your models here.
