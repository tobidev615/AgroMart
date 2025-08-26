from django.contrib import admin
from .models import Delivery


@admin.register(Delivery)
class DeliveryAdmin(admin.ModelAdmin):
    list_display = ("order", "scheduled_date", "status", "distributor", "created_at")
    list_filter = ("status",)

# Register your models here.
