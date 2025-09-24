from django.db import models
from django.core.validators import MinValueValidator


class Category(models.Model):
    name = models.CharField(max_length=150)
    slug = models.SlugField(max_length=160, unique=True)
    parent = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, related_name='children')
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        indexes = [
            models.Index(fields=['slug']),
            models.Index(fields=['parent']),
            models.Index(fields=['is_active']),
        ]
        verbose_name_plural = 'Categories'

    def __str__(self) -> str:
        return self.name


class Product(models.Model):
    name = models.CharField(max_length=200)
    slug = models.SlugField(max_length=220, unique=True)
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, blank=True, related_name='products')
    description = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        indexes = [
            models.Index(fields=['slug']),
            models.Index(fields=['category']),
            models.Index(fields=['is_active']),
        ]

    def __str__(self) -> str:
        return self.name


class ProductVariant(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='variants')
    name = models.CharField(max_length=200, blank=True, help_text="Optional variant label, e.g., '500g' or 'Red'")
    sku = models.CharField(max_length=64, unique=True)
    option_values = models.JSONField(default=dict, blank=True, help_text="Structured variant options, e.g., size/color")
    price = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(0)])
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        indexes = [
            models.Index(fields=['sku']),
            models.Index(fields=['product']),
            models.Index(fields=['is_active']),
        ]

    def __str__(self) -> str:
        label = self.name or self.sku
        return f"{self.product.name} - {label}"


class InventoryItem(models.Model):
    variant = models.OneToOneField(ProductVariant, on_delete=models.CASCADE, related_name='inventory')
    on_hand = models.IntegerField(default=0)
    reserved = models.IntegerField(default=0)
    committed = models.IntegerField(default=0)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        indexes = [
            models.Index(fields=['variant']),
        ]

    def __str__(self) -> str:
        return f"Inventory({self.variant.sku}): {self.on_hand}/{self.reserved}/{self.committed}"


class StockMovementReason(models.TextChoices):
    PURCHASE = 'PURCHASE', 'Purchase'
    ORDER_RESERVED = 'ORDER_RESERVED', 'Order reserved'
    ORDER_COMMITTED = 'ORDER_COMMITTED', 'Order committed'
    RELEASED = 'RELEASED', 'Reserve released'
    RESTOCK = 'RESTOCK', 'Restock'
    ADJUSTMENT = 'ADJUSTMENT', 'Adjustment'


class StockMovement(models.Model):
    inventory = models.ForeignKey(InventoryItem, on_delete=models.CASCADE, related_name='movements')
    delta_on_hand = models.IntegerField(default=0)
    delta_reserved = models.IntegerField(default=0)
    delta_committed = models.IntegerField(default=0)
    reason = models.CharField(max_length=32, choices=StockMovementReason.choices)
    reference = models.CharField(max_length=255, blank=True)
    metadata = models.JSONField(default=dict, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        indexes = [
            models.Index(fields=['reason']),
            models.Index(fields=['created_at']),
        ]

    def __str__(self) -> str:
        return f"Movement {self.reason} for {self.inventory.variant.sku}"

