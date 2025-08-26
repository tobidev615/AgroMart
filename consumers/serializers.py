from rest_framework import serializers
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, MaxValueValidator
from decimal import Decimal

from .models import (
    ConsumerProfile, ConsumerWishlist, ConsumerReview, 
    ConsumerAnalytics, ConsumerPreference
)
from farmers.serializers import ProduceSerializer, FarmerProfileSerializer
from orders.serializers import OrderSerializer


class ConsumerProfileSerializer(serializers.ModelSerializer):
    """Serializer for consumer profile with nested user data."""
    user = serializers.SerializerMethodField()
    favorite_farmers = FarmerProfileSerializer(many=True, read_only=True)
    total_spent = serializers.DecimalField(max_digits=12, decimal_places=2, read_only=True)
    total_orders = serializers.IntegerField(read_only=True)
    average_order_value = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)

    class Meta:
        model = ConsumerProfile
        fields = [
            'id', 'user', 'delivery_preferences', 'preferred_delivery_time',
            'delivery_instructions', 'dietary_preferences', 'organic_preference',
            'local_preference', 'total_spent', 'total_orders', 'average_order_value',
            'last_order_date', 'favorite_farmers', 'favorite_produce_types',
            'email_notifications', 'sms_notifications', 'marketing_emails',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at', 'total_spent', 'total_orders', 'average_order_value']

    def get_user(self, obj):
        """Get user information."""
        return {
            'id': obj.user.id,
            'username': obj.user.username,
            'email': obj.user.email,
            'first_name': obj.user.first_name,
            'last_name': obj.user.last_name,
        }

    def validate_delivery_preferences(self, value):
        """Validate delivery preferences JSON."""
        if not isinstance(value, dict):
            raise serializers.ValidationError("Delivery preferences must be a dictionary.")
        return value

    def validate_favorite_produce_types(self, value):
        """Validate favorite produce types list."""
        if not isinstance(value, list):
            raise serializers.ValidationError("Favorite produce types must be a list.")
        return value


class ConsumerProfileCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating consumer profile."""
    user_id = serializers.IntegerField(write_only=True)

    class Meta:
        model = ConsumerProfile
        fields = [
            'user_id', 'delivery_preferences', 'preferred_delivery_time',
            'delivery_instructions', 'dietary_preferences', 'organic_preference',
            'local_preference', 'favorite_produce_types', 'email_notifications',
            'sms_notifications', 'marketing_emails'
        ]

    def create(self, validated_data):
        user_id = validated_data.pop('user_id')
        user = User.objects.get(id=user_id)
        return ConsumerProfile.objects.create(user=user, **validated_data)


class ConsumerWishlistSerializer(serializers.ModelSerializer):
    """Serializer for consumer wishlist items."""
    produce = ProduceSerializer(read_only=True)
    produce_id = serializers.IntegerField(write_only=True)
    consumer = serializers.PrimaryKeyRelatedField(read_only=True)

    class Meta:
        model = ConsumerWishlist
        fields = [
            'id', 'consumer', 'produce', 'produce_id', 'quantity', 'notes',
            'added_at', 'is_available'
        ]
        read_only_fields = ['id', 'consumer', 'added_at', 'is_available']

    def validate_quantity(self, value):
        """Validate quantity is positive."""
        if value <= 0:
            raise serializers.ValidationError("Quantity must be greater than 0.")
        return value

    def create(self, validated_data):
        """Create wishlist item with consumer from request."""
        produce_id = validated_data.pop('produce_id')
        consumer = self.context['request'].user.consumer_profile
        produce = Produce.objects.get(id=produce_id)
        
        # Check if already in wishlist
        if ConsumerWishlist.objects.filter(consumer=consumer, produce=produce).exists():
            raise serializers.ValidationError("This produce is already in your wishlist.")
        
        return ConsumerWishlist.objects.create(
            consumer=consumer,
            produce=produce,
            **validated_data
        )


class ConsumerReviewSerializer(serializers.ModelSerializer):
    """Serializer for consumer reviews."""
    consumer = serializers.PrimaryKeyRelatedField(read_only=True)
    produce = ProduceSerializer(read_only=True)
    produce_id = serializers.IntegerField(write_only=True)
    order = OrderSerializer(read_only=True)
    order_id = serializers.IntegerField(write_only=True, required=False)
    user_info = serializers.SerializerMethodField()

    class Meta:
        model = ConsumerReview
        fields = [
            'id', 'consumer', 'produce', 'produce_id', 'order', 'order_id',
            'rating', 'review', 'is_verified_purchase', 'user_info',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'consumer', 'created_at', 'updated_at', 'is_verified_purchase']

    def get_user_info(self, obj):
        """Get user information for the review."""
        return {
            'username': obj.consumer.user.username,
            'first_name': obj.consumer.user.first_name,
            'last_name': obj.consumer.user.last_name,
        }

    def validate_rating(self, value):
        """Validate rating is between 1 and 5."""
        if not 1 <= value <= 5:
            raise serializers.ValidationError("Rating must be between 1 and 5.")
        return value

    def validate_review(self, value):
        """Validate review text."""
        if len(value.strip()) < 10:
            raise serializers.ValidationError("Review must be at least 10 characters long.")
        return value

    def create(self, validated_data):
        """Create review with consumer from request."""
        produce_id = validated_data.pop('produce_id')
        order_id = validated_data.pop('order_id', None)
        consumer = self.context['request'].user.consumer_profile
        produce = Produce.objects.get(id=produce_id)
        
        # Check if already reviewed this produce
        if ConsumerReview.objects.filter(consumer=consumer, produce=produce).exists():
            raise serializers.ValidationError("You have already reviewed this produce.")
        
        # Set verified purchase if order is provided
        is_verified = False
        order = None
        if order_id:
            try:
                order = Order.objects.get(id=order_id, user=consumer.user)
                is_verified = True
            except Order.DoesNotExist:
                pass
        
        return ConsumerReview.objects.create(
            consumer=consumer,
            produce=produce,
            order=order,
            is_verified_purchase=is_verified,
            **validated_data
        )


class ConsumerAnalyticsSerializer(serializers.ModelSerializer):
    """Serializer for consumer analytics."""
    consumer = serializers.PrimaryKeyRelatedField(read_only=True)
    monthly_spending = serializers.JSONField(read_only=True)
    yearly_spending = serializers.JSONField(read_only=True)
    top_produce_categories = serializers.JSONField(read_only=True)
    seasonal_preferences = serializers.JSONField(read_only=True)
    preferred_delivery_days = serializers.JSONField(read_only=True)

    class Meta:
        model = ConsumerAnalytics
        fields = [
            'id', 'consumer', 'monthly_spending', 'yearly_spending',
            'order_frequency', 'average_order_size', 'top_produce_categories',
            'seasonal_preferences', 'preferred_delivery_days', 'delivery_success_rate',
            'last_login', 'total_logins', 'days_since_last_order',
            'created_at', 'updated_at'
        ]
        read_only_fields = [
            'id', 'consumer', 'monthly_spending', 'yearly_spending',
            'order_frequency', 'average_order_size', 'top_produce_categories',
            'seasonal_preferences', 'preferred_delivery_days', 'delivery_success_rate',
            'last_login', 'total_logins', 'days_since_last_order',
            'created_at', 'updated_at'
        ]


class ConsumerPreferenceSerializer(serializers.ModelSerializer):
    """Serializer for consumer preferences."""
    consumer = serializers.PrimaryKeyRelatedField(read_only=True)
    preferred_produce_types = serializers.JSONField()
    excluded_produce_types = serializers.JSONField()
    preferred_quantities = serializers.JSONField()
    notification_channels = serializers.JSONField()

    class Meta:
        model = ConsumerPreference
        fields = [
            'id', 'consumer', 'preferred_produce_types', 'excluded_produce_types',
            'preferred_quantities', 'bulk_ordering_preference', 'price_range_preference',
            'discount_preference', 'subscription_frequency', 'subscription_budget',
            'notification_channels', 'notification_frequency', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'consumer', 'created_at', 'updated_at']

    def validate_preferred_produce_types(self, value):
        """Validate preferred produce types list."""
        if not isinstance(value, list):
            raise serializers.ValidationError("Preferred produce types must be a list.")
        return value

    def validate_excluded_produce_types(self, value):
        """Validate excluded produce types list."""
        if not isinstance(value, list):
            raise serializers.ValidationError("Excluded produce types must be a list.")
        return value

    def validate_preferred_quantities(self, value):
        """Validate preferred quantities dictionary."""
        if not isinstance(value, dict):
            raise serializers.ValidationError("Preferred quantities must be a dictionary.")
        return value

    def validate_notification_channels(self, value):
        """Validate notification channels list."""
        if not isinstance(value, list):
            raise serializers.ValidationError("Notification channels must be a list.")
        valid_channels = ['email', 'sms', 'push', 'in_app']
        for channel in value:
            if channel not in valid_channels:
                raise serializers.ValidationError(f"Invalid notification channel: {channel}")
        return value


class ConsumerDashboardSerializer(serializers.Serializer):
    """Serializer for consumer dashboard data."""
    profile = ConsumerProfileSerializer()
    analytics = ConsumerAnalyticsSerializer()
    preferences = ConsumerPreferenceSerializer()
    recent_orders = OrderSerializer(many=True)
    wishlist_items = ConsumerWishlistSerializer(many=True)
    favorite_farmers = FarmerProfileSerializer(many=True)
    top_produce_categories = serializers.ListField(child=serializers.CharField())
    monthly_spending_chart = serializers.DictField()
    order_frequency_trend = serializers.DictField()


class ConsumerWishlistCreateSerializer(serializers.ModelSerializer):
    """Simplified serializer for creating wishlist items."""
    produce_id = serializers.IntegerField()

    class Meta:
        model = ConsumerWishlist
        fields = ['produce_id', 'quantity', 'notes']

    def validate_produce_id(self, value):
        """Validate produce exists and is available."""
        try:
            produce = Produce.objects.get(id=value)
            if not produce.available:
                raise serializers.ValidationError("This produce is not available.")
        except Produce.DoesNotExist:
            raise serializers.ValidationError("Produce not found.")
        return value


class ConsumerReviewCreateSerializer(serializers.ModelSerializer):
    """Simplified serializer for creating reviews."""
    produce_id = serializers.IntegerField()
    order_id = serializers.IntegerField(required=False)

    class Meta:
        model = ConsumerReview
        fields = ['produce_id', 'order_id', 'rating', 'review']

    def validate_produce_id(self, value):
        """Validate produce exists."""
        try:
            Produce.objects.get(id=value)
        except Produce.DoesNotExist:
            raise serializers.ValidationError("Produce not found.")
        return value

    def validate_order_id(self, value):
        """Validate order exists and belongs to user."""
        if value:
            try:
                Order.objects.get(id=value, user=self.context['request'].user)
            except Order.DoesNotExist:
                raise serializers.ValidationError("Order not found or doesn't belong to you.")
        return value


# Import statements for the models used in serializers
from farmers.models import Produce
from orders.models import Order


