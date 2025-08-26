from rest_framework import serializers

from farmers.models import Produce
from farmers.serializers import ProduceSerializer
from .models import Cart, CartItem, Order, OrderItem, OrderStatus
from farmers.serializers import FarmerProfileSerializer


class CartItemSerializer(serializers.ModelSerializer):
    produce = ProduceSerializer(read_only=True)
    produce_id = serializers.PrimaryKeyRelatedField(
        queryset=Produce.objects.all(), source="produce", write_only=True
    )

    class Meta:
        model = CartItem
        fields = ["id", "produce", "produce_id", "quantity", "added_at"]

    def validate_quantity(self, value):
        if value <= 0:
            raise serializers.ValidationError("Quantity must be greater than zero.")
        return value

    def validate(self, attrs):
        produce = attrs.get("produce") or getattr(self.instance, "produce", None)
        quantity = attrs.get("quantity") or getattr(self.instance, "quantity", None)
        if produce and quantity is not None:
            if produce.quantity_available < quantity:
                raise serializers.ValidationError({
                    "quantity": f"Only {produce.quantity_available} available"
                })
        return attrs


class CartSerializer(serializers.ModelSerializer):
    items = CartItemSerializer(many=True, read_only=True)

    class Meta:
        model = Cart
        fields = ["id", "items", "created_at", "updated_at"]


class OrderItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrderItem
        fields = [
            "id",
            "produce",
            "product_name",
            "unit",
            "price_per_unit",
            "quantity",
            "subtotal",
        ]


class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True, read_only=True)
    status = serializers.ChoiceField(choices=OrderStatus.choices)
    farmer_items = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Order
        fields = [
            "id",
            "status",
            "total_amount",
            "items",
            "farmer_items",
            "created_at",
            "updated_at",
        ]

    def get_farmer_items(self, obj):
        user = self.context.get("request").user if self.context.get("request") else None
        if not user or not hasattr(user, "farmer_profile"):
            return []
        farmer_profile = user.farmer_profile
        items = obj.items.filter(produce__farmer=farmer_profile)
        return OrderItemSerializer(items, many=True).data

