from rest_framework import serializers

from .models import Delivery, DeliveryStatus


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
            "created_at",
            "updated_at",
        ]





