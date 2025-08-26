from rest_framework import serializers

from .models import SubscriptionPlan, Subscription, SubscriptionItem, BillingPeriod
from farmers.serializers import ProduceSerializer


class SubscriptionPlanSerializer(serializers.ModelSerializer):
    period = serializers.ChoiceField(choices=BillingPeriod.choices)

    class Meta:
        model = SubscriptionPlan
        fields = ["id", "name", "period", "price", "description", "is_active"]


class SubscriptionItemSerializer(serializers.ModelSerializer):
    produce = ProduceSerializer(read_only=True)
    produce_id = serializers.IntegerField(write_only=True)

    class Meta:
        model = SubscriptionItem
        fields = ["id", "produce", "produce_id", "quantity"]


class SubscriptionSerializer(serializers.ModelSerializer):
    items = SubscriptionItemSerializer(many=True)

    class Meta:
        model = Subscription
        fields = [
            "id",
            "plan",
            "start_date",
            "next_delivery_date",
            "is_active",
            "items",
        ]

    def create(self, validated_data):
        items_data = validated_data.pop("items", [])
        user = self.context["request"].user
        subscription = Subscription.objects.create(user=user, **validated_data)
        for item in items_data:
            SubscriptionItem.objects.create(
                subscription=subscription,
                produce_id=item["produce_id"],
                quantity=item.get("quantity", 1),
            )
        return subscription





