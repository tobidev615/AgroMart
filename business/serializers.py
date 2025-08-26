from rest_framework import serializers
from decimal import Decimal

from .models import (
    BusinessProfile,
    BusinessPricingTier,
    ContractOrder,
    ContractOrderItem,
    BusinessInvoice,
)


class BusinessPricingTierSerializer(serializers.ModelSerializer):
    class Meta:
        model = BusinessPricingTier
        fields = [
            "id",
            "business",
            "produce",
            "min_quantity",
            "unit",
            "unit_price",
            "active",
        ]
        read_only_fields = ["id"]


class ContractOrderItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = ContractOrderItem
        fields = ["id", "produce", "quantity", "unit", "agreed_unit_price"]
        read_only_fields = ["id"]


class ContractOrderSerializer(serializers.ModelSerializer):
    items = ContractOrderItemSerializer(many=True)

    class Meta:
        model = ContractOrder
        fields = [
            "id",
            "business",
            "name",
            "frequency",
            "next_delivery_date",
            "priority",
            "is_active",
            "notes",
            "items",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]

    def create(self, validated_data):
        items_data = validated_data.pop("items", [])
        contract = ContractOrder.objects.create(**validated_data)
        for item in items_data:
            ContractOrderItem.objects.create(contract=contract, **item)
        return contract

    def update(self, instance, validated_data):
        items_data = validated_data.pop("items", None)
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        if items_data is not None:
            instance.items.all().delete()
            for item in items_data:
                ContractOrderItem.objects.create(contract=instance, **item)
        return instance


class BusinessInvoiceSerializer(serializers.ModelSerializer):
    class Meta:
        model = BusinessInvoice
        fields = [
            "id",
            "business",
            "order",
            "payment_terms_days",
            "issued_at",
            "due_date",
            "status",
            "total_amount",
            "pdf_path",
        ]
        read_only_fields = ["id", "issued_at", "pdf_path", "total_amount"]


class BusinessProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = BusinessProfile
        fields = [
            "id",
            "user",
            "name",
            "company",
            "business_type",
            "tax_id",
            "address",
            "city",
            "country",
            "account_manager_name",
            "account_manager_email",
            "account_manager_phone",
            "support_whatsapp",
            "support_phone",
            "credit_terms_days",
            "credit_limit",
            "branding_enabled",
            "brand_name",
            "packaging_preferences",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "user", "created_at", "updated_at"]


class BulkOrderItemInputSerializer(serializers.Serializer):
    produce_id = serializers.IntegerField()
    quantity = serializers.IntegerField(min_value=1)
    unit = serializers.CharField(max_length=50)


class BulkOrderCreateSerializer(serializers.Serializer):
    items = BulkOrderItemInputSerializer(many=True)

    def validate(self, attrs):
        if not attrs.get("items"):
            raise serializers.ValidationError("At least one item is required")
        return attrs



