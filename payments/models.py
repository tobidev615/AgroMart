from django.db import models
from django.contrib.auth.models import User
from orders.models import Order
from decimal import Decimal


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


class Wallet(models.Model):
    """Prepaid balance for users to fund subscriptions and orders."""
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='wallet')
    balance = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal('0.00'))
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self) -> str:
        return f"Wallet({self.user.username}): {self.balance}"


class WalletTransactionType(models.TextChoices):
    DEPOSIT = 'DEPOSIT', 'Deposit'
    PAYMENT = 'PAYMENT', 'Payment'
    REFUND = 'REFUND', 'Refund'
    WITHDRAWAL = 'WITHDRAWAL', 'Withdrawal'
    ADJUSTMENT = 'ADJUSTMENT', 'Adjustment'


class WalletTransaction(models.Model):
    wallet = models.ForeignKey(Wallet, on_delete=models.CASCADE, related_name='transactions')
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    type = models.CharField(max_length=20, choices=WalletTransactionType.choices)
    reference = models.CharField(max_length=255, blank=True)
    metadata = models.JSONField(default=dict, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        indexes = [
            models.Index(fields=['type']),
            models.Index(fields=['created_at']),
        ]

    def __str__(self) -> str:
        sign = '+' if self.type in {WalletTransactionType.DEPOSIT, WalletTransactionType.REFUND, WalletTransactionType.ADJUSTMENT} else '-'
        return f"{sign}{self.amount} {self.type} for {self.wallet.user.username}"
