from django.db import models
from django.contrib.auth.models import User
from farmers.models import Produce


class BillingPeriod(models.TextChoices):
    WEEKLY = "WEEKLY", "Weekly"
    BIWEEKLY = "BIWEEKLY", "Bi-weekly"
    MONTHLY = "MONTHLY", "Monthly"


class SubscriptionPlan(models.Model):
    name = models.CharField(max_length=100)
    period = models.CharField(max_length=20, choices=BillingPeriod.choices, default=BillingPeriod.WEEKLY)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    description = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)
    discount_percent = models.DecimalField(max_digits=5, decimal_places=2, default=0, help_text="Optional discount when used for subscriptions")

    def __str__(self) -> str:
        return f"{self.name} ({self.period})"


class Subscription(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="subscriptions")
    plan = models.ForeignKey(SubscriptionPlan, on_delete=models.PROTECT)
    mixed_box = models.ForeignKey('orders.MixedBox', on_delete=models.PROTECT, null=True, blank=True, help_text="Box subscribed to, if box-based")
    start_date = models.DateField()
    next_delivery_date = models.DateField()
    is_active = models.BooleanField(default=True)
    skip_next = models.BooleanField(default=False)
    paused_at = models.DateTimeField(null=True, blank=True)
    last_renewal_at = models.DateTimeField(null=True, blank=True)
    last_renewal_result = models.CharField(max_length=255, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self) -> str:
        return f"Subscription({self.user.username}, {self.plan.name})"


class SubscriptionItem(models.Model):
    subscription = models.ForeignKey(Subscription, on_delete=models.CASCADE, related_name="items")
    produce = models.ForeignKey(Produce, on_delete=models.PROTECT)
    quantity = models.PositiveIntegerField(default=1)

    def __str__(self) -> str:
        return f"{self.quantity} x {self.produce.name}"

# Create your models here.
