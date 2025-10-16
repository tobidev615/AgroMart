from rest_framework import generics, permissions, status, viewsets
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.request import Request
from django.shortcuts import get_object_or_404
from django.db.models import Sum, Count

from .models import Delivery, DeliveryStatus, DeliveryBatch, DeliveryWindow
from .serializers import DeliverySerializer, DeliveryBatchSerializer, DeliveryWindowSerializer
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


@api_view(["GET"]) 
@permission_classes([permissions.IsAuthenticated])
def distributor_payout_summary(request):
    """Summary of payout amounts for the authenticated distributor."""
    qs = Delivery.objects.filter(distributor__user=request.user)
    totals = qs.aggregate(
        total_jobs=Count("id"),
        total_delivered=Count("id", filter=Delivery.objects.filter(distributor__user=request.user, status=DeliveryStatus.DELIVERED).values("id")),
        payout_unpaid=Sum("payout_amount", filter=Delivery.objects.filter(distributor__user=request.user, payout_status="UNPAID").values("id")),
        payout_pending=Sum("payout_amount", filter=Delivery.objects.filter(distributor__user=request.user, payout_status="PENDING").values("id")),
        payout_paid=Sum("payout_amount", filter=Delivery.objects.filter(distributor__user=request.user, payout_status="PAID").values("id")),
    )
    # Normalize None to 0
    for key in list(totals.keys()):
        totals[key] = totals[key] or 0
    return Response(totals)


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


class DeliveryWindowViewSet(viewsets.ModelViewSet):
    serializer_class = DeliveryWindowSerializer
    queryset = DeliveryWindow.objects.all()

    def get_permissions(self):
        if self.action in ["list", "retrieve"]:
            return [permissions.AllowAny()]
        return [permissions.IsAdminUser()]


class DeliveryBatchViewSet(viewsets.ModelViewSet):
    serializer_class = DeliveryBatchSerializer
    queryset = DeliveryBatch.objects.select_related("window").all()

    def get_permissions(self):
        if self.action in ["list", "retrieve"]:
            return [permissions.AllowAny()]
        return [permissions.IsAdminUser()]