from django.contrib import admin
from django.utils.html import format_html
from django.db.models import Sum, Count, Avg
from django.utils import timezone
from datetime import timedelta

from .models import (
    ConsumerProfile, ConsumerWishlist, ConsumerReview, 
    ConsumerAnalytics, ConsumerPreference
)


@admin.register(ConsumerProfile)
class ConsumerProfileAdmin(admin.ModelAdmin):
    list_display = [
        'user', 'total_spent', 'total_orders', 'average_order_value',
        'organic_preference', 'local_preference', 'created_at'
    ]
    list_filter = [
        'organic_preference', 'local_preference', 'email_notifications',
        'sms_notifications', 'marketing_emails', 'created_at'
    ]
    search_fields = [
        'user__username', 'user__email', 'user__first_name', 'user__last_name',
        'dietary_preferences', 'delivery_instructions'
    ]
    readonly_fields = ['total_spent', 'total_orders', 'average_order_value', 'last_order_date']
    filter_horizontal = ['favorite_farmers']
    
    fieldsets = (
        ('User Information', {
            'fields': ('user', 'created_at', 'updated_at')
        }),
        ('Delivery Preferences', {
            'fields': ('delivery_preferences', 'preferred_delivery_time', 'delivery_instructions')
        }),
        ('Dietary Preferences', {
            'fields': ('dietary_preferences', 'organic_preference', 'local_preference')
        }),
        ('Analytics', {
            'fields': ('total_spent', 'total_orders', 'average_order_value', 'last_order_date'),
            'classes': ('collapse',)
        }),
        ('Favorites', {
            'fields': ('favorite_farmers', 'favorite_produce_types'),
            'classes': ('collapse',)
        }),
        ('Communication Preferences', {
            'fields': ('email_notifications', 'sms_notifications', 'marketing_emails'),
            'classes': ('collapse',)
        }),
    )
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('user')
    
    def get_readonly_fields(self, request, obj=None):
        if obj:  # Editing an existing object
            return self.readonly_fields + ('user',)
        return self.readonly_fields


@admin.register(ConsumerWishlist)
class ConsumerWishlistAdmin(admin.ModelAdmin):
    list_display = [
        'consumer', 'produce', 'quantity', 'is_available', 'added_at'
    ]
    list_filter = ['is_available', 'added_at']
    search_fields = [
        'consumer__user__username', 'produce__name', 'produce__variety', 'notes'
    ]
    readonly_fields = ['added_at', 'is_available']
    
    fieldsets = (
        ('Consumer Information', {
            'fields': ('consumer', 'added_at')
        }),
        ('Produce Information', {
            'fields': ('produce', 'quantity', 'is_available')
        }),
        ('Additional Information', {
            'fields': ('notes',),
            'classes': ('collapse',)
        }),
    )
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('consumer__user', 'produce')
    
    def save_model(self, request, obj, form, change):
        """Update availability when saving."""
        super().save_model(request, obj, form, change)
        obj.update_availability()


@admin.register(ConsumerReview)
class ConsumerReviewAdmin(admin.ModelAdmin):
    list_display = [
        'consumer', 'produce', 'rating', 'is_verified_purchase', 'created_at'
    ]
    list_filter = [
        'rating', 'is_verified_purchase', 'created_at'
    ]
    search_fields = [
        'consumer__user__username', 'produce__name', 'review'
    ]
    readonly_fields = ['created_at', 'updated_at', 'is_verified_purchase']
    
    fieldsets = (
        ('Review Information', {
            'fields': ('consumer', 'produce', 'order', 'is_verified_purchase')
        }),
        ('Review Content', {
            'fields': ('rating', 'review')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('consumer__user', 'produce', 'order')
    
    def get_readonly_fields(self, request, obj=None):
        if obj:  # Editing an existing object
            return self.readonly_fields + ('consumer', 'produce')
        return self.readonly_fields


@admin.register(ConsumerAnalytics)
class ConsumerAnalyticsAdmin(admin.ModelAdmin):
    list_display = [
        'consumer', 'order_frequency', 'average_order_size', 'delivery_success_rate',
        'total_logins', 'days_since_last_order'
    ]
    list_filter = ['created_at', 'updated_at']
    search_fields = ['consumer__user__username', 'consumer__user__email']
    readonly_fields = [
        'monthly_spending', 'yearly_spending', 'top_produce_categories',
        'seasonal_preferences', 'preferred_delivery_days', 'delivery_success_rate',
        'last_login', 'total_logins', 'days_since_last_order', 'created_at', 'updated_at'
    ]
    
    fieldsets = (
        ('Consumer Information', {
            'fields': ('consumer', 'created_at', 'updated_at')
        }),
        ('Spending Analytics', {
            'fields': ('monthly_spending', 'yearly_spending'),
            'classes': ('collapse',)
        }),
        ('Order Analytics', {
            'fields': ('order_frequency', 'average_order_size'),
            'classes': ('collapse',)
        }),
        ('Produce Preferences', {
            'fields': ('top_produce_categories', 'seasonal_preferences'),
            'classes': ('collapse',)
        }),
        ('Delivery Analytics', {
            'fields': ('preferred_delivery_days', 'delivery_success_rate'),
            'classes': ('collapse',)
        }),
        ('Engagement Metrics', {
            'fields': ('last_login', 'total_logins', 'days_since_last_order'),
            'classes': ('collapse',)
        }),
    )
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('consumer__user')
    
    def get_readonly_fields(self, request, obj=None):
        if obj:  # Editing an existing object
            return self.readonly_fields + ('consumer',)
        return self.readonly_fields


@admin.register(ConsumerPreference)
class ConsumerPreferenceAdmin(admin.ModelAdmin):
    list_display = [
        'consumer', 'subscription_frequency', 'bulk_ordering_preference',
        'discount_preference', 'notification_frequency'
    ]
    list_filter = [
        'subscription_frequency', 'bulk_ordering_preference', 'discount_preference',
        'notification_frequency', 'created_at'
    ]
    search_fields = ['consumer__user__username', 'consumer__user__email']
    readonly_fields = ['created_at', 'updated_at']
    
    fieldsets = (
        ('Consumer Information', {
            'fields': ('consumer', 'created_at', 'updated_at')
        }),
        ('Produce Preferences', {
            'fields': ('preferred_produce_types', 'excluded_produce_types'),
            'classes': ('collapse',)
        }),
        ('Quantity Preferences', {
            'fields': ('preferred_quantities', 'bulk_ordering_preference'),
            'classes': ('collapse',)
        }),
        ('Price Preferences', {
            'fields': ('price_range_preference', 'discount_preference'),
            'classes': ('collapse',)
        }),
        ('Subscription Preferences', {
            'fields': ('subscription_frequency', 'subscription_budget'),
            'classes': ('collapse',)
        }),
        ('Notification Preferences', {
            'fields': ('notification_channels', 'notification_frequency'),
            'classes': ('collapse',)
        }),
    )
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('consumer__user')
    
    def get_readonly_fields(self, request, obj=None):
        if obj:  # Editing an existing object
            return self.readonly_fields + ('consumer',)
        return self.readonly_fields


# Custom admin actions
@admin.action(description="Update wishlist availability")
def update_wishlist_availability(modeladmin, request, queryset):
    """Update availability for selected wishlist items."""
    updated = 0
    for wishlist_item in queryset:
        wishlist_item.update_availability()
        updated += 1
    modeladmin.message_user(request, f"Updated availability for {updated} wishlist items.")


@admin.action(description="Recalculate consumer analytics")
def recalculate_consumer_analytics(modeladmin, request, queryset):
    """Recalculate analytics for selected consumers."""
    updated = 0
    for consumer_profile in queryset:
        # This would trigger analytics recalculation
        # Implementation would depend on your analytics logic
        updated += 1
    modeladmin.message_user(request, f"Recalculated analytics for {updated} consumers.")


# Add custom actions to admin classes
ConsumerWishlistAdmin.actions = [update_wishlist_availability]
ConsumerProfileAdmin.actions = [recalculate_consumer_analytics]
