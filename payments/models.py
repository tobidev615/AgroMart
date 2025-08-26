from django.db import models
from django.contrib.auth.models import User
from orders.models import Order


class PaymentStatus(models.TextChoices):
    PENDING = 'PENDING', 'Pending'
    SUCCEEDED = 'SUCCEEDED', 'Succeeded'
    FAILED = 'FAILED', 'Failed'


class Payment(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='payments')
    order = models.OneToOneField(Order, on_delete=models.CASCADE, related_name='payment')
    provider = models.CharField(max_length=32, default='stripe')
    provider_payment_id = models.CharField(max_length=255, blank=True)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    currency = models.CharField(max_length=8, default='usd')
    status = models.CharField(max_length=16, choices=PaymentStatus.choices, default=PaymentStatus.PENDING)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


class Invoice(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='invoices')
    order = models.OneToOneField(Order, on_delete=models.CASCADE, related_name='invoice')
    file = models.FileField(upload_to='invoices/')
    created_at = models.DateTimeField(auto_now_add=True)
