from django.contrib import admin
from .models import SubscriptionPlan, Subscription, SubscriptionItem


@admin.register(SubscriptionPlan)
class SubscriptionPlanAdmin(admin.ModelAdmin):
    list_display = ("name", "period", "price", "is_active")
    list_filter = ("period", "is_active")


class SubscriptionItemInline(admin.TabularInline):
    model = SubscriptionItem
    extra = 0


@admin.register(Subscription)
class SubscriptionAdmin(admin.ModelAdmin):
    list_display = ("user", "plan", "start_date", "next_delivery_date", "is_active")
    list_filter = ("plan__period", "is_active")
    inlines = [SubscriptionItemInline]

# Register your models here.
