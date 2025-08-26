from django.db import models
from django.contrib.auth.models import User


class DistributorProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="distributor_profile")
    name = models.CharField(max_length=200)
    hub_location = models.CharField(max_length=255, blank=True)
    vehicle_info = models.CharField(max_length=255, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self) -> str:
        return self.name or self.user.username

# Create your models here.
