from django.contrib import admin
from .models import DistributorProfile


@admin.register(DistributorProfile)
class DistributorProfileAdmin(admin.ModelAdmin):
    list_display = ("user", "name", "hub_location", "created_at")
    search_fields = ("user__username", "name", "hub_location")

# Register your models here.
