from django.contrib import admin
from .models import Payment, Invoice, Wallet, WalletTransaction


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "order", "amount", "status", "provider", "created_at")
    search_fields = ("id", "order__id", "user__username", "provider_payment_id")
    list_filter = ("status", "provider", "created_at")


@admin.register(Invoice)
class InvoiceAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "order", "created_at")
    search_fields = ("id", "order__id", "user__username")
    list_filter = ("created_at",)


@admin.register(Wallet)
class WalletAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "balance", "updated_at")
    search_fields = ("id", "user__username")


@admin.register(WalletTransaction)
class WalletTransactionAdmin(admin.ModelAdmin):
    list_display = ("id", "wallet", "type", "amount", "created_at")
    search_fields = ("id", "wallet__user__username", "reference")
    list_filter = ("type", "created_at")