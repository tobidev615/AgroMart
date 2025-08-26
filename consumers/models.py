from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, MaxValueValidator
from decimal import Decimal
import json


class ConsumerProfile(models.Model):
    """Extended profile for consumers with preferences and analytics."""
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="consumer_profile")
    
    # Delivery preferences
    delivery_preferences = models.JSONField(default=dict, help_text="Delivery time preferences, address details")
    preferred_delivery_time = models.CharField(max_length=50, blank=True, help_text="Preferred delivery time slot")
    delivery_instructions = models.TextField(blank=True, help_text="Special delivery instructions")
    
    # Dietary preferences
    dietary_preferences = models.TextField(blank=True, help_text="Dietary restrictions, allergies, preferences")
    organic_preference = models.BooleanField(default=False, help_text="Prefer organic produce")
    local_preference = models.BooleanField(default=True, help_text="Prefer locally grown produce")
    
    # Analytics and tracking
    total_spent = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal('0.00'))
    total_orders = models.PositiveIntegerField(default=0)
    average_order_value = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'))
    last_order_date = models.DateTimeField(null=True, blank=True)
    
    # Preferences
    favorite_farmers = models.ManyToManyField('farmers.FarmerProfile', blank=True, related_name="favorite_consumers")
    favorite_produce_types = models.JSONField(default=list, help_text="List of favorite produce categories")
    
    # Communication preferences
    email_notifications = models.BooleanField(default=True)
    sms_notifications = models.BooleanField(default=False)
    marketing_emails = models.BooleanField(default=False)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'consumers_profile'
        indexes = [
            models.Index(fields=['user']),
            models.Index(fields=['total_spent']),
            models.Index(fields=['total_orders']),
        ]

    def __str__(self):
        return f"Consumer Profile for {self.user.username}"

    def update_spending_analytics(self, order_amount: Decimal) -> None:
        """Update spending analytics when a new order is placed."""
        self.total_spent += order_amount
        self.total_orders += 1
        self.average_order_value = self.total_spent / self.total_orders
        self.save(update_fields=['total_spent', 'total_orders', 'average_order_value'])

    def add_favorite_farmer(self, farmer_profile) -> None:
        """Add a farmer to favorites."""
        self.favorite_farmers.add(farmer_profile)

    def remove_favorite_farmer(self, farmer_profile) -> None:
        """Remove a farmer from favorites."""
        self.favorite_farmers.remove(farmer_profile)

    def add_favorite_produce_type(self, produce_type: str) -> None:
        """Add a produce type to favorites."""
        if produce_type not in self.favorite_produce_types:
            self.favorite_produce_types.append(produce_type)
            self.save(update_fields=['favorite_produce_types'])

    def get_delivery_preferences(self) -> dict:
        """Get delivery preferences as a dictionary."""
        return self.delivery_preferences or {}


class ConsumerWishlist(models.Model):
    """Wishlist items for consumers."""
    consumer = models.ForeignKey(ConsumerProfile, on_delete=models.CASCADE, related_name="wishlist_items")
    produce = models.ForeignKey('farmers.Produce', on_delete=models.CASCADE, related_name="wishlist_consumers")
    quantity = models.PositiveIntegerField(default=1, validators=[MinValueValidator(1)])
    notes = models.TextField(blank=True, help_text="Notes about this wishlist item")
    added_at = models.DateTimeField(auto_now_add=True)
    is_available = models.BooleanField(default=True, help_text="Whether the produce is currently available")

    class Meta:
        db_table = 'consumers_wishlist'
        unique_together = ['consumer', 'produce']
        indexes = [
            models.Index(fields=['consumer']),
            models.Index(fields=['produce']),
            models.Index(fields=['added_at']),
        ]

    def __str__(self):
        return f"{self.consumer.user.username}'s wishlist: {self.produce.name}"

    def update_availability(self) -> None:
        """Update availability status based on produce stock."""
        self.is_available = self.produce.available and self.produce.quantity_available > 0
        self.save(update_fields=['is_available'])


class ConsumerReview(models.Model):
    """Reviews and ratings for produce."""
    consumer = models.ForeignKey(ConsumerProfile, on_delete=models.CASCADE, related_name="reviews")
    produce = models.ForeignKey('farmers.Produce', on_delete=models.CASCADE, related_name="consumer_reviews")
    order = models.ForeignKey('orders.Order', on_delete=models.CASCADE, related_name="reviews", null=True, blank=True)
    
    rating = models.IntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)],
        help_text="Rating from 1 to 5 stars"
    )
    review = models.TextField(help_text="Detailed review of the produce")
    is_verified_purchase = models.BooleanField(default=False, help_text="Whether this review is from a verified purchase")
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'consumers_review'
        unique_together = ['consumer', 'produce']
        indexes = [
            models.Index(fields=['consumer']),
            models.Index(fields=['produce']),
            models.Index(fields=['rating']),
            models.Index(fields=['created_at']),
        ]

    def __str__(self):
        return f"{self.consumer.user.username}'s review of {self.produce.name}"

    def save(self, *args, **kwargs):
        """Override save to update produce average rating."""
        super().save(*args, **kwargs)
        self.update_produce_rating()

    def update_produce_rating(self) -> None:
        """Update the average rating for the produce."""
        reviews = ConsumerReview.objects.filter(produce=self.produce)
        if reviews.exists():
            avg_rating = reviews.aggregate(avg=models.Avg('rating'))['avg']
            self.produce.average_rating = round(avg_rating, 2)
            self.produce.save(update_fields=['average_rating'])


class ConsumerAnalytics(models.Model):
    """Analytics data for consumers."""
    consumer = models.OneToOneField(ConsumerProfile, on_delete=models.CASCADE, related_name="analytics")
    
    # Spending analytics
    monthly_spending = models.JSONField(default=dict, help_text="Monthly spending breakdown")
    yearly_spending = models.JSONField(default=dict, help_text="Yearly spending breakdown")
    
    # Order analytics
    order_frequency = models.DecimalField(max_digits=5, decimal_places=2, default=Decimal('0.00'), help_text="Orders per month")
    average_order_size = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'))
    
    # Produce preferences
    top_produce_categories = models.JSONField(default=list, help_text="Most ordered produce categories")
    seasonal_preferences = models.JSONField(default=dict, help_text="Seasonal produce preferences")
    
    # Delivery analytics
    preferred_delivery_days = models.JSONField(default=list, help_text="Most common delivery days")
    delivery_success_rate = models.DecimalField(max_digits=5, decimal_places=2, default=Decimal('100.00'))
    
    # Engagement metrics
    last_login = models.DateTimeField(null=True, blank=True)
    total_logins = models.PositiveIntegerField(default=0)
    days_since_last_order = models.PositiveIntegerField(default=0)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'consumers_analytics'
        verbose_name_plural = 'Consumer analytics'

    def __str__(self):
        return f"Analytics for {self.consumer.user.username}"

    def update_monthly_spending(self, month: str, amount: Decimal) -> None:
        """Update monthly spending data."""
        monthly_data = self.monthly_spending or {}
        monthly_data[month] = monthly_data.get(month, 0) + float(amount)
        self.monthly_spending = monthly_data
        self.save(update_fields=['monthly_spending'])

    def update_top_categories(self, category: str) -> None:
        """Update top produce categories."""
        categories = self.top_produce_categories or []
        if category not in categories:
            categories.append(category)
            # Keep only top 10 categories
            self.top_produce_categories = categories[:10]
            self.save(update_fields=['top_produce_categories'])


class ConsumerPreference(models.Model):
    """Detailed preferences for consumers."""
    consumer = models.OneToOneField(ConsumerProfile, on_delete=models.CASCADE, related_name="preferences")
    
    # Produce preferences
    preferred_produce_types = models.JSONField(default=list, help_text="Preferred produce types")
    excluded_produce_types = models.JSONField(default=list, help_text="Produce types to avoid")
    
    # Quantity preferences
    preferred_quantities = models.JSONField(default=dict, help_text="Preferred quantities for different produce")
    bulk_ordering_preference = models.BooleanField(default=False, help_text="Prefer bulk ordering")
    
    # Price preferences
    price_range_preference = models.CharField(max_length=50, blank=True, help_text="Preferred price range")
    discount_preference = models.BooleanField(default=True, help_text="Prefer discounted items")
    
    # Subscription preferences
    subscription_frequency = models.CharField(max_length=20, default="monthly", choices=[
        ('weekly', 'Weekly'),
        ('biweekly', 'Bi-weekly'),
        ('monthly', 'Monthly'),
        ('custom', 'Custom'),
    ])
    subscription_budget = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    
    # Notification preferences
    notification_channels = models.JSONField(default=list, help_text="Preferred notification channels")
    notification_frequency = models.CharField(max_length=20, default="immediate", choices=[
        ('immediate', 'Immediate'),
        ('daily', 'Daily digest'),
        ('weekly', 'Weekly digest'),
    ])
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'consumers_preference'

    def __str__(self):
        return f"Preferences for {self.consumer.user.username}"

    def add_preferred_produce_type(self, produce_type: str) -> None:
        """Add a preferred produce type."""
        if produce_type not in self.preferred_produce_types:
            self.preferred_produce_types.append(produce_type)
            self.save(update_fields=['preferred_produce_types'])

    def add_excluded_produce_type(self, produce_type: str) -> None:
        """Add an excluded produce type."""
        if produce_type not in self.excluded_produce_types:
            self.excluded_produce_types.append(produce_type)
            self.save(update_fields=['excluded_produce_types'])


