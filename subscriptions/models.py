from django.db import models
from django.contrib.auth.models import User
from farmers.models import Produce


class BillingPeriod(models.TextChoices):
    WEEKLY = "WEEKLY", "Weekly"
    MONTHLY = "MONTHLY", "Monthly"


class SubscriptionPlan(models.Model):
    name = models.CharField(max_length=100)
    period = models.CharField(max_length=20, choices=BillingPeriod.choices, default=BillingPeriod.WEEKLY)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    description = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)

    def __str__(self) -> str:
        return f"{self.name} ({self.period})"


class Subscription(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="subscriptions")
    plan = models.ForeignKey(SubscriptionPlan, on_delete=models.PROTECT)
    start_date = models.DateField()
    next_delivery_date = models.DateField()
    is_active = models.BooleanField(default=True)
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
