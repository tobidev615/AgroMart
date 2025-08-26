from rest_framework import generics, permissions

from userprofiles.models import UserType
from .models import DistributorProfile
from .serializers import DistributorProfileSerializer


class IsDistributorOrStaff(permissions.BasePermission):
    def has_permission(self, request, view):
        user = request.user
        if not (user and user.is_authenticated):
            return False
        if user.is_staff:
            return True
        return hasattr(user, "profile") and user.profile.role == UserType.DISTRIBUTOR


class MyDistributorProfileView(generics.RetrieveUpdateAPIView):
    serializer_class = DistributorProfileSerializer
    permission_classes = [IsDistributorOrStaff]

    def get_object(self):
        user = self.request.user
        profile, _ = DistributorProfile.objects.get_or_create(
            user=user, defaults={"name": user.get_full_name() or user.username}
        )
        return profile

# Create your views here.
