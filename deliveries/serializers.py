from rest_framework import serializers

from .models import Delivery, DeliveryStatus, DeliveryBatch, DeliveryWindow


class DeliverySerializer(serializers.ModelSerializer):
    status = serializers.ChoiceField(choices=DeliveryStatus.choices)

    class Meta:
        model = Delivery
        fields = [
            "id",
            "order",
            "scheduled_date",
            "status",
            "distributor",
            "notes",
            "batch",
            "payout_amount",
            "payout_status",
            "payout_reference",
            "created_at",
            "updated_at",
        ]


class DeliveryWindowSerializer(serializers.ModelSerializer):
    class Meta:
        model = DeliveryWindow
        fields = [
            "id",
            "name",
            "days_of_week",
            "start_time",
            "end_time",
            "cutoff_time",
            "zone",
            "active",
        ]


class DeliveryBatchSerializer(serializers.ModelSerializer):
    class Meta:
        model = DeliveryBatch
        fields = [
            "id",
            "name",
            "batch_date",
            "status",
            "cutoff_at",
            "window",
            "created_at",
            "updated_at",
        ]