from decimal import Decimal
from django.db import transaction
from typing import Optional
from django.core.exceptions import ValidationError
from .models import Wallet, WalletTransaction, WalletTransactionType, Payment, PaymentStatus
from orders.models import Order


@transaction.atomic
def ensure_wallet(user) -> Wallet:
    wallet, _ = Wallet.objects.select_for_update().get_or_create(user=user)
    return wallet


@transaction.atomic
def wallet_deposit(user, amount: Decimal, reference: str = "", metadata: Optional[dict] = None) -> WalletTransaction:
    if amount <= 0:
        raise ValidationError("Amount must be positive")
    wallet = ensure_wallet(user)
    wallet.balance = (wallet.balance or Decimal("0.00")) + amount
    wallet.save(update_fields=["balance", "updated_at"])
    tx = WalletTransaction.objects.create(
        wallet=wallet,
        amount=amount,
        type=WalletTransactionType.DEPOSIT,
        reference=reference,
        metadata=metadata or {},
    )
    return tx


@transaction.atomic
def pay_order_from_wallet(user, order: Order, amount: Optional[Decimal] = None) -> Payment:
    if order.user_id != user.id:
        raise ValidationError("Cannot pay someone else's order")
    if order.payment_status == "PAID":
        return Payment.objects.get(order=order)
    amount_to_charge = amount if amount is not None else order.total_amount
    wallet = ensure_wallet(user)
    if wallet.balance < amount_to_charge:
        raise ValidationError("Insufficient wallet balance")
    wallet.balance -= amount_to_charge
    wallet.save(update_fields=["balance", "updated_at"])
    WalletTransaction.objects.create(
        wallet=wallet,
        amount=amount_to_charge,
        type=WalletTransactionType.PAYMENT,
        reference=f"ORDER:{order.id}",
        metadata={"order_id": order.id},
    )
    payment, _ = Payment.objects.update_or_create(
        order=order,
        defaults={
            "user": user,
            "provider": "wallet",
            "amount": amount_to_charge,
            "currency": "usd",
            "status": PaymentStatus.SUCCEEDED,
        },
    )
    order.payment_status = "PAID"
    order.save(update_fields=["payment_status", "updated_at"])
    return payment


@transaction.atomic
def refund_to_wallet(order: Order, amount: Decimal, reason: str = "") -> WalletTransaction:
    if amount <= 0:
        raise ValidationError("Refund amount must be positive")
    payment = Payment.objects.filter(order=order).first()
    user = order.user
    wallet = ensure_wallet(user)
    wallet.balance += amount
    wallet.save(update_fields=["balance", "updated_at"])
    tx = WalletTransaction.objects.create(
        wallet=wallet,
        amount=amount,
        type=WalletTransactionType.REFUND,
        reference=f"REFUND:ORDER:{order.id}",
        metadata={"order_id": order.id, "reason": reason},
    )
    if payment:
        payment.refunded_amount = (payment.refunded_amount or Decimal("0.00")) + amount
        if payment.refunded_amount >= payment.amount:
            payment.status = PaymentStatus.FAILED if payment.amount == 0 else PaymentStatus.SUCCEEDED
        payment.save(update_fields=["refunded_amount", "status", "updated_at"])
    # Update order.payment_status when full refund achieved
    from decimal import Decimal as D
    if payment and (payment.refunded_amount or D("0")) >= (payment.amount or D("0")):
        order.payment_status = "REFUNDED"
        order.save(update_fields=["payment_status", "updated_at"])
    else:
        order.payment_status = "PARTIALLY_REFUNDED"
        order.save(update_fields=["payment_status", "updated_at"])
    return tx