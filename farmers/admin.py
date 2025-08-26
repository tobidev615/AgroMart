from django.contrib import admin
from .models import FarmerProfile, FarmCluster, Produce, FarmerEarnings


@admin.register(FarmerProfile)
class FarmerProfileAdmin(admin.ModelAdmin):
    list_display = ['name', 'user', 'location', 'total_earnings', 'total_orders', 'created_at']
    list_filter = ['created_at', 'updated_at']
    search_fields = ['name', 'user__username', 'user__email', 'location']
    readonly_fields = ['total_earnings', 'total_orders', 'created_at', 'updated_at']
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('user', 'name', 'location', 'crops', 'estimated_harvest')
        }),
        ('Earnings', {
            'fields': ('total_earnings', 'total_orders'),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(FarmCluster)
class FarmClusterAdmin(admin.ModelAdmin):
    list_display = ['name', 'location', 'member_count', 'created_at']
    list_filter = ['created_at', 'updated_at']
    search_fields = ['name', 'description', 'location']
    filter_horizontal = ['members']
    
    def member_count(self, obj):
        return obj.members.count()
    member_count.short_description = 'Members'


@admin.register(Produce)
class ProduceAdmin(admin.ModelAdmin):
    list_display = ['name', 'farmer', 'variety', 'quantity_available', 'price_per_unit', 'available', 'total_sold', 'total_revenue']
    list_filter = ['available', 'created_at', 'updated_at', 'farmer']
    search_fields = ['name', 'variety', 'description', 'farmer__name']
    readonly_fields = ['total_sold', 'total_revenue', 'created_at', 'updated_at']
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('farmer', 'name', 'variety', 'description', 'image')
        }),
        ('Pricing & Stock', {
            'fields': ('quantity_available', 'unit', 'price_per_unit', 'available')
        }),
        ('Sales Statistics', {
            'fields': ('total_sold', 'total_revenue'),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(FarmerEarnings)
class FarmerEarningsAdmin(admin.ModelAdmin):
    list_display = ['farmer', 'produce', 'order', 'quantity', 'total_amount', 'status', 'created_at']
    list_filter = ['status', 'created_at', 'updated_at', 'farmer']
    search_fields = ['farmer__name', 'produce__name', 'order__id']
    readonly_fields = ['created_at', 'updated_at']
    
    fieldsets = (
        ('Transaction Details', {
            'fields': ('farmer', 'order', 'produce', 'quantity', 'unit_price', 'total_amount')
        }),
        ('Status', {
            'fields': ('status',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('farmer', 'order', 'produce')

# Register your models here.
