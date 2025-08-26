from django.contrib.auth.models import User
from rest_framework import serializers

from .models import UserProfile, UserType


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["id", "username", "email", "first_name", "last_name"]


class UserProfileSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)

    class Meta:
        model = UserProfile
        fields = [
            "id",
            "user",
            "role",
            "email_verified",
            "phone_number",
            "address",
            "city",
            "country",
            "created_at",
            "updated_at",
        ]


class RegistrationSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=8)
    role = serializers.ChoiceField(choices=UserType.choices, required=False, default=UserType.OTHERS)

    class Meta:
        model = User
        fields = ["username", "email", "first_name", "last_name", "password", "role"]

    def create(self, validated_data):
        role = validated_data.pop("role", UserType.OTHERS)
        password = validated_data.pop("password")
        user = User(**validated_data)
        user.set_password(password)
        user.save()
        # set role on auto-created profile
        if hasattr(user, "profile"):
            user.profile.role = role
            user.profile.save(update_fields=["role"])
        return user

