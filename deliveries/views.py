from rest_framework import generics, permissions, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.request import Request
from django.shortcuts import get_object_or_404

from .models import Delivery, DeliveryStatus
from .serializers import DeliverySerializer
from userprofiles.models import UserType


class DeliveryListCreateView(generics.ListCreateAPIView):
    """List all deliveries (staff) or create a delivery (staff only)."""
    serializer_class = DeliverySerializer
    queryset = Delivery.objects.select_related("order", "distributor").all()

    def get_permissions(self):
        if self.request.method == "GET":
            return [permissions.IsAdminUser()]
        return [permissions.IsAdminUser()]


class DeliveryDetailView(generics.RetrieveUpdateAPIView):
    """Retrieve/update a delivery. Update restricted to staff or assigned distributor."""
    serializer_class = DeliverySerializer
    queryset = Delivery.objects.select_related("order", "distributor").all()


class DistributorAssignedDeliveriesList(generics.ListAPIView):
    """List deliveries assigned to the authenticated distributor."""
    serializer_class = DeliverySerializer

    def get_queryset(self):
        user = self.request.user
        return Delivery.objects.select_related("order", "distributor").filter(distributor__user=user)


@api_view(["POST"])
@permission_classes([permissions.IsAuthenticated])
def distributor_mark_delivered(request: Request, pk: int) -> Response:
    """Allow an assigned distributor to mark a delivery as delivered."""
    delivery = get_object_or_404(Delivery.objects.select_related("distributor"), pk=pk)
    if not delivery.distributor or delivery.distributor.user_id != request.user.id:
        return Response({"detail": "Not allowed"}, status=status.HTTP_403_FORBIDDEN)
    delivery.status = DeliveryStatus.DELIVERED
    delivery.save(update_fields=["status"])
    return Response({"detail": "Marked delivered"})
