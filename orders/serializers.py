from rest_framework import serializers

from farmers.models import Produce
from farmers.serializers import ProduceSerializer
from .models import Cart, CartItem, Order, OrderItem, OrderStatus, MixedBox, MixedBoxItem
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
            "mixed_box",
            "dry_variant",
            "product_name",
            "unit",
            "price_per_unit",
            "quantity",
            "subtotal",
            "is_substituted",
            "substituted_product_name",
            "shortage_quantity",
            "refunded_amount",
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
            "payment_status",
            "payment_intent_id",
            "total_amount",
            "items",
            "farmer_items",
            "delivery_window",
            "delivery_fee",
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


class MixedBoxItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = MixedBoxItem
        fields = ["id", "produce", "quantity"]


class MixedBoxSerializer(serializers.ModelSerializer):
    items = MixedBoxItemSerializer(many=True)

    class Meta:
        model = MixedBox
        fields = [
            "id",
            "name",
            "size",
            "description",
            "price",
            "is_active",
            "items",
            "created_at",
            "updated_at",
        ]

    def create(self, validated_data):
        items_data = validated_data.pop("items", [])
        box = MixedBox.objects.create(**validated_data)
        for item in items_data:
            MixedBoxItem.objects.create(box=box, **item)
        return box

    def update(self, instance, validated_data):
        items_data = validated_data.pop("items", None)
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        if items_data is not None:
            instance.items.all().delete()
            for item in items_data:
                MixedBoxItem.objects.create(box=instance, **item)
        return instance