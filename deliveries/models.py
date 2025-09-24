from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from django.utils import timezone as dj_timezone

from orders.models import Order


class DeliveryStatus(models.TextChoices):
    PENDING = "PENDING", "Pending"
    SCHEDULED = "SCHEDULED", "Scheduled"
    OUT_FOR_DELIVERY = "OUT_FOR_DELIVERY", "Out for delivery"
    DELIVERED = "DELIVERED", "Delivered"


class DeliveryBatchStatus(models.TextChoices):
    DRAFT = "DRAFT", "Draft"
    LOCKED = "LOCKED", "Locked"
    COMPLETED = "COMPLETED", "Completed"


class DeliveryBatch(models.Model):
    """Grouping of deliveries for fixed delivery days (e.g., twice weekly)."""
    name = models.CharField(max_length=120, blank=True)
    batch_date = models.DateField()
    status = models.CharField(max_length=20, choices=DeliveryBatchStatus.choices, default=DeliveryBatchStatus.DRAFT)
    cutoff_at = models.DateTimeField(null=True, blank=True, help_text="After this time, orders fall into the next batch")
    window = models.ForeignKey('deliveries.DeliveryWindow', on_delete=models.PROTECT, null=True, blank=True, related_name='batches')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        indexes = [
            models.Index(fields=["batch_date"]),
            models.Index(fields=["status"]),
        ]

    def __str__(self) -> str:
        label = self.name or self.batch_date.isoformat()
        return f"Batch {label} ({self.status})"


class DeliveryWindow(models.Model):
    """Configurable delivery windows with cutoff rules and days-of-week constraints."""
    name = models.CharField(max_length=120)
    days_of_week = models.JSONField(default=list, help_text="List of integers 0-6 (Mon-Sun)")
    start_time = models.TimeField()
    end_time = models.TimeField()
    cutoff_time = models.TimeField(help_text="Time of day cutoff to lock batches")
    zone = models.CharField(max_length=120, blank=True)
    active = models.BooleanField(default=True)

    class Meta:
        indexes = [
            models.Index(fields=['active']),
            models.Index(fields=['zone']),
        ]

    def __str__(self) -> str:
        return self.name

class Delivery(models.Model):
    order = models.OneToOneField('orders.Order', on_delete=models.CASCADE, related_name='delivery')
    distributor = models.ForeignKey('distributors.DistributorProfile', on_delete=models.SET_NULL, null=True, blank=True, related_name='deliveries')
    status = models.CharField(max_length=20, choices=DeliveryStatus.choices, default=DeliveryStatus.PENDING)
    scheduled_date = models.DateTimeField(default=timezone.now)
    delivered_at = models.DateTimeField(null=True, blank=True)
    notes = models.TextField(blank=True)
    batch = models.ForeignKey('deliveries.DeliveryBatch', on_delete=models.SET_NULL, null=True, blank=True, related_name='deliveries')
    payout_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    payout_status = models.CharField(max_length=20, choices=[
        ("UNPAID", "Unpaid"),
        ("PENDING", "Pending"),
        ("PAID", "Paid"),
    ], default="UNPAID")
    payout_reference = models.CharField(max_length=120, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        indexes = [
            models.Index(fields=['status']),
            models.Index(fields=['distributor']),
            models.Index(fields=['scheduled_date']),
            models.Index(fields=['distributor', 'status']),
            models.Index(fields=['batch']),
            models.Index(fields=['payout_status']),
        ]

    def __str__(self) -> str:
        return f"Delivery {self.id} for Order {self.order.id} - {self.status}"

# Create your models here.
