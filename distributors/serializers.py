from rest_framework import serializers

from .models import DistributorProfile


class DistributorProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = DistributorProfile
        fields = [
            "id",
            "name",
            "hub_location",
            "vehicle_info",
            "created_at",
            "updated_at",
        ]





