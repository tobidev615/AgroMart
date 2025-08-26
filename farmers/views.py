from rest_framework import generics, permissions, filters
from django.db.models import Q, Sum, Count
from django.shortcuts import get_object_or_404
from rest_framework import viewsets
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from django.utils import timezone
from datetime import timedelta
from decimal import Decimal
from typing import Any

from .models import FarmerProfile, FarmCluster, Produce, FarmerEarnings
from .serializers import (
    FarmerProfileSerializer,
    FarmClusterSerializer,
    ProduceSerializer,
    ProducePublicSerializer,
    FarmerEarningsSerializer,
    FarmerDashboardSerializer,
)


class IsFarmerOrStaff(permissions.BasePermission):
    """Allow access to staff or users whose profile role is FARMER."""
    def has_permission(self, request, view) -> bool:  # type: ignore[override]
        user = request.user
        if not (user and user.is_authenticated):
            return False
        if getattr(user, "is_staff", False):
            return True
        return bool(hasattr(user, "profile") and user.profile.role == "FARMER")


class MyFarmerProfileView(generics.RetrieveUpdateAPIView):
    serializer_class = FarmerProfileSerializer
    permission_classes = [IsFarmerOrStaff]

    def get_object(self):
        user = self.request.user
        farmer_profile, _ = FarmerProfile.objects.get_or_create(user=user, defaults={
            "name": user.get_full_name() or user.username,
        })
        return farmer_profile


class ProduceListCreateView(generics.ListCreateAPIView):
    serializer_class = ProduceSerializer
    permission_classes = [IsFarmerOrStaff]

    def get_queryset(self):
        user = self.request.user
        if not user.is_authenticated:
            return Produce.objects.none()
        if user.is_staff:
            return Produce.objects.all()
        return Produce.objects.filter(farmer__user=user)

    def perform_create(self, serializer):
        farmer_profile, _ = FarmerProfile.objects.get_or_create(user=self.request.user, defaults={
            "name": self.request.user.get_full_name() or self.request.user.username,
        })
        serializer.save(farmer=farmer_profile)


class ProduceRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = ProduceSerializer
    queryset = Produce.objects.all()
    permission_classes = [IsFarmerOrStaff]

    def get_queryset(self):
        user = self.request.user
        if user.is_staff:
            return Produce.objects.all()
        return Produce.objects.filter(farmer__user=user)


class FarmClusterListCreateView(generics.ListCreateAPIView):
    serializer_class = FarmClusterSerializer
    queryset = FarmCluster.objects.all()
    permission_classes = [permissions.IsAuthenticated]


class FarmClusterRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = FarmClusterSerializer
    queryset = FarmCluster.objects.all()
    permission_classes = [permissions.IsAuthenticated]


class FarmerProfileListView(generics.ListAPIView):
    serializer_class = FarmerProfileSerializer
    permission_classes = [permissions.IsAdminUser]
    queryset = FarmerProfile.objects.all()


class FarmerProfileAdminDetailView(generics.RetrieveUpdateAPIView):
    serializer_class = FarmerProfileSerializer
    permission_classes = [permissions.IsAdminUser]
    queryset = FarmerProfile.objects.all()


class PublicProduceListView(generics.ListAPIView):
    permission_classes = [permissions.AllowAny]
    serializer_class = ProduceSerializer
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ["name", "variety", "description", "farmer__name", "farmer__user__username"]
    ordering_fields = ["price_per_unit", "created_at", "quantity_available"]

    def get_queryset(self):
        queryset = Produce.objects.select_related("farmer", "farmer__user").filter(available=True)
        # optional manual filters
        params = self.request.query_params
        min_price = params.get("min_price")
        max_price = params.get("max_price")
        farmer_id = params.get("farmer_id")
        location = params.get("location")
        crops = params.get("crops")
        if min_price:
            queryset = queryset.filter(price_per_unit__gte=min_price)
        if max_price:
            queryset = queryset.filter(price_per_unit__lte=max_price)
        if farmer_id:
            queryset = queryset.filter(farmer_id=farmer_id)
        if location:
            queryset = queryset.filter(farmer__location__icontains=location)
        if crops:
            queryset = queryset.filter(
                Q(farmer__crops__icontains=crops)
                | Q(name__icontains=crops)
                | Q(variety__icontains=crops)
            )
        return queryset


class PublicProduceDetailView(generics.RetrieveAPIView):
    permission_classes = [permissions.AllowAny]
    serializer_class = ProduceSerializer
    queryset = Produce.objects.select_related("farmer", "farmer__user").filter(available=True)


class FarmerProfileViewSet(viewsets.ModelViewSet):
    serializer_class = FarmerProfileSerializer
    permission_classes = [IsFarmerOrStaff]

    def get_queryset(self):
        if self.request.user.is_staff:
            return FarmerProfile.objects.select_related('user').all()
        return FarmerProfile.objects.select_related('user').filter(user=self.request.user)


class ProduceViewSet(viewsets.ModelViewSet):
    serializer_class = ProduceSerializer
    permission_classes = [IsFarmerOrStaff]

    def get_queryset(self):
        if self.request.user.is_staff:
            return Produce.objects.select_related('farmer', 'farmer__user').all()
        return Produce.objects.select_related('farmer', 'farmer__user').filter(farmer__user=self.request.user)


class ProducePublicViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = ProducePublicSerializer
    permission_classes = [permissions.AllowAny]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['farmer', 'available', 'unit']
    search_fields = ['name', 'variety', 'description', 'farmer__name']
    ordering_fields = ['price_per_unit', 'created_at', 'name']
    ordering = ['-created_at']

    def get_queryset(self):
        return Produce.objects.select_related('farmer', 'farmer__user').filter(available=True)


# New Earnings Dashboard Views
class FarmerEarningsListView(generics.ListAPIView):
    """List farmer's earnings transactions."""
    serializer_class = FarmerEarningsSerializer
    permission_classes = [IsFarmerOrStaff]
    filter_backends = [filters.OrderingFilter]
    ordering_fields = ['created_at', 'total_amount', 'status']
    ordering = ['-created_at']

    def get_queryset(self):
        user = self.request.user
        if user.is_staff:
            return FarmerEarnings.objects.select_related('farmer', 'order', 'produce').all()
        return FarmerEarnings.objects.select_related('farmer', 'order', 'produce').filter(farmer__user=user)


@api_view(['GET'])
@permission_classes([IsFarmerOrStaff])
def farmer_dashboard(request):
    """Get farmer dashboard summary with earnings, orders, and analytics."""
    user = request.user
    farmer_profile = get_object_or_404(FarmerProfile, user=user)
    
    # Get earnings summary
    earnings_summary = FarmerEarnings.objects.filter(farmer=farmer_profile).aggregate(
        total_earnings=Sum('total_amount'),
        pending_earnings=Sum('total_amount', filter=Q(status='PENDING')),
        confirmed_earnings=Sum('total_amount', filter=Q(status='CONFIRMED')),
        paid_earnings=Sum('total_amount', filter=Q(status='PAID')),
    )
    
    # Get produce counts
    produce_counts = Produce.objects.filter(farmer=farmer_profile).aggregate(
        active_count=Count('id', filter=Q(available=True)),
        total_count=Count('id'),
    )
    
    # Get recent orders (last 10)
    recent_orders = FarmerEarnings.objects.filter(farmer=farmer_profile).select_related(
        'order', 'produce'
    ).order_by('-created_at')[:10]
    
    recent_orders_data = []
    for earning in recent_orders:
        recent_orders_data.append({
            'id': earning.id,
            'order_id': earning.order.id,
            'produce_name': earning.produce.name,
            'quantity': earning.quantity,
            'total_amount': str(earning.total_amount),
            'status': earning.status,
            'created_at': earning.created_at.isoformat(),
        })
    
    # Get top selling produce
    top_produce = Produce.objects.filter(farmer=farmer_profile).annotate(
        total_revenue=Sum('earnings__total_amount')
    ).order_by('-total_revenue')[:5]
    
    top_produce_data = []
    for produce in top_produce:
        top_produce_data.append({
            'id': produce.id,
            'name': produce.name,
            'total_sold': produce.total_sold,
            'total_revenue': str(produce.total_revenue),
        })
    
    # Get monthly earnings (last 6 months)
    monthly_earnings = []
    for i in range(6):
        month_start = timezone.now() - timedelta(days=30*i)
        month_end = month_start + timedelta(days=30)
        month_earnings = FarmerEarnings.objects.filter(
            farmer=farmer_profile,
            created_at__gte=month_start,
            created_at__lt=month_end
        ).aggregate(total=Sum('total_amount'))['total'] or Decimal('0.00')
        
        monthly_earnings.append({
            'month': month_start.strftime('%Y-%m'),
            'earnings': str(month_earnings),
        })
    
    dashboard_data = {
        'total_earnings': earnings_summary['total_earnings'] or Decimal('0.00'),
        'total_orders': farmer_profile.total_orders,
        'pending_earnings': earnings_summary['pending_earnings'] or Decimal('0.00'),
        'confirmed_earnings': earnings_summary['confirmed_earnings'] or Decimal('0.00'),
        'paid_earnings': earnings_summary['paid_earnings'] or Decimal('0.00'),
        'active_produce_count': produce_counts['active_count'],
        'total_produce_count': produce_counts['total_count'],
        'recent_orders': recent_orders_data,
        'top_selling_produce': top_produce_data,
        'monthly_earnings': monthly_earnings,
    }
    
    serializer = FarmerDashboardSerializer(dashboard_data)
    return Response(serializer.data)


@api_view(['GET'])
@permission_classes([IsFarmerOrStaff])
def farmer_analytics(request):
    """Get detailed analytics for farmer."""
    user = request.user
    farmer_profile = get_object_or_404(FarmerProfile, user=user)
    
    # Get date range from query params
    days = int(request.GET.get('days', 30))
    start_date = timezone.now() - timedelta(days=days)
    
    # Earnings over time
    earnings_over_time = FarmerEarnings.objects.filter(
        farmer=farmer_profile,
        created_at__gte=start_date
    ).values('created_at__date').annotate(
        daily_earnings=Sum('total_amount')
    ).order_by('created_at__date')
    
    # Produce performance
    produce_performance = Produce.objects.filter(farmer=farmer_profile).annotate(
        total_orders=Count('earnings'),
        total_revenue=Sum('earnings__total_amount')
    ).order_by('-total_revenue')
    
    analytics_data = {
        'earnings_over_time': [
            {
                'date': item['created_at__date'].isoformat(),
                'earnings': str(item['daily_earnings']),
            }
            for item in earnings_over_time
        ],
        'produce_performance': [
            {
                'id': produce.id,
                'name': produce.name,
                'total_orders': produce.total_orders,
                'total_revenue': str(produce.total_revenue or Decimal('0.00')),
                'total_sold': produce.total_sold,
            }
            for produce in produce_performance
        ],
        'summary': {
            'total_earnings': str(farmer_profile.total_earnings),
            'total_orders': farmer_profile.total_orders,
            'active_produce': Produce.objects.filter(farmer=farmer_profile, available=True).count(),
        }
    }
    
    return Response(analytics_data)
