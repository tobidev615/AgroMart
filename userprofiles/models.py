from django.db import models
from django.contrib.auth.models import User


class UserType(models.TextChoices):
    FARMER = "FARMER", "Farmer"
    CONSUMER = "CONSUMER", "Consumer"
    OTHERS = "OTHERS", "Others"
    BUSINESS = "BUSINESS", "Business"
    DISTRIBUTOR = "DISTRIBUTOR", "Distributor"
    STAFF = "STAFF", "Staff"


class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="profile")
    role = models.CharField(max_length=20, choices=UserType.choices, default=UserType.OTHERS)
    email_verified = models.BooleanField(default=False)
    phone_number = models.CharField(max_length=20, blank=True)
    address = models.CharField(max_length=255, blank=True)
    city = models.CharField(max_length=100, blank=True)
    country = models.CharField(max_length=100, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self) -> str:
        return f"Profile for {self.user.username}"

# Create your models here.
