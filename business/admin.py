from django.contrib import admin

from .models import (
    BusinessProfile,
    BusinessPricingTier,
    ContractOrder,
    ContractOrderItem,
    BusinessInvoice,
)


@admin.register(BusinessProfile)
class BusinessProfileAdmin(admin.ModelAdmin):
    list_display = ("user", "company", "business_type", "credit_terms_days", "credit_limit", "created_at")
    list_filter = ("business_type", "created_at")
    search_fields = ("user__username", "company", "name", "tax_id")


@admin.register(BusinessPricingTier)
class BusinessPricingTierAdmin(admin.ModelAdmin):
    list_display = ("business", "produce", "min_quantity", "unit", "unit_price", "active")
    list_filter = ("active", "unit")
    search_fields = ("produce__name",)


class ContractOrderItemInline(admin.TabularInline):
    model = ContractOrderItem
    extra = 0


@admin.register(ContractOrder)
class ContractOrderAdmin(admin.ModelAdmin):
    list_display = ("business", "name", "frequency", "next_delivery_date", "priority", "is_active")
    list_filter = ("frequency", "is_active", "priority")
    search_fields = ("name", "business__company")
    inlines = [ContractOrderItemInline]


@admin.register(BusinessInvoice)
class BusinessInvoiceAdmin(admin.ModelAdmin):
    list_display = ("business", "order", "status", "due_date", "total_amount")
    list_filter = ("status",)
    search_fields = ("business__company", "order__id")
