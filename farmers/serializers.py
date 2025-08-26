from django.contrib.auth.models import User
from rest_framework import serializers

from .models import FarmerProfile, FarmCluster, Produce, FarmerEarnings


class UserMiniSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["id", "username"]


class FarmerProfileSerializer(serializers.ModelSerializer):
    user = serializers.StringRelatedField()
    total_earnings = serializers.DecimalField(max_digits=12, decimal_places=2, read_only=True)
    total_orders = serializers.IntegerField(read_only=True)

    class Meta:
        model = FarmerProfile
        fields = [
            "id",
            "user",
            "name",
            "location",
            "crops",
            "estimated_harvest",
            "total_earnings",
            "total_orders",
            "created_at",
            "updated_at",
        ]


class FarmClusterSerializer(serializers.ModelSerializer):
    members = serializers.StringRelatedField(many=True)

    class Meta:
        model = FarmCluster
        fields = [
            "id",
            "name",
            "description",
            "location",
            "members",
            "created_at",
            "updated_at",
        ]


class ProduceSerializer(serializers.ModelSerializer):
    farmer = serializers.StringRelatedField()
    total_sold = serializers.IntegerField(read_only=True)
    total_revenue = serializers.DecimalField(max_digits=12, decimal_places=2, read_only=True)

    class Meta:
        model = Produce
        fields = [
            "id",
            "farmer",
            "name",
            "variety",
            "description",
            "image",
            "quantity_available",
            "unit",
            "price_per_unit",
            "available",
            "total_sold",
            "total_revenue",
            "created_at",
            "updated_at",
        ]


class ProducePublicSerializer(serializers.ModelSerializer):
    """Serializer for public produce browsing with farmer info."""
    farmer_name = serializers.CharField(source="farmer.name", read_only=True)
    farmer_location = serializers.CharField(source="farmer.location", read_only=True)

    class Meta:
        model = Produce
        fields = [
            "id",
            "farmer_name",
            "farmer_location",
            "name",
            "variety",
            "description",
            "image",
            "quantity_available",
            "unit",
            "price_per_unit",
            "available",
            "created_at",
        ]


class FarmerEarningsSerializer(serializers.ModelSerializer):
    """Serializer for farmer earnings tracking."""
    produce_name = serializers.CharField(source="produce.name", read_only=True)
    order_id = serializers.IntegerField(source="order.id", read_only=True)
    customer_name = serializers.CharField(source="order.user.get_full_name", read_only=True)

    class Meta:
        model = FarmerEarnings
        fields = [
            "id",
            "produce_name",
            "order_id",
            "customer_name",
            "quantity",
            "unit_price",
            "total_amount",
            "status",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["farmer", "order", "produce"]


class FarmerDashboardSerializer(serializers.Serializer):
    """Serializer for farmer dashboard summary."""
    total_earnings = serializers.DecimalField(max_digits=12, decimal_places=2)
    total_orders = serializers.IntegerField()
    pending_earnings = serializers.DecimalField(max_digits=12, decimal_places=2)
    confirmed_earnings = serializers.DecimalField(max_digits=12, decimal_places=2)
    paid_earnings = serializers.DecimalField(max_digits=12, decimal_places=2)
    active_produce_count = serializers.IntegerField()
    total_produce_count = serializers.IntegerField()
    recent_orders = serializers.ListField(child=serializers.DictField())
    top_selling_produce = serializers.ListField(child=serializers.DictField())
    monthly_earnings = serializers.ListField(child=serializers.DictField())

