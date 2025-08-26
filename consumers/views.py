from rest_framework import generics, permissions, status, filters
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.request import Request
from django.shortcuts import get_object_or_404
from django.db.models import Q, Sum, Count, Avg
from django.utils import timezone
from django.contrib.auth.models import User
from datetime import timedelta, datetime
from decimal import Decimal
from typing import Any, Dict, List

from .models import (
    ConsumerProfile, ConsumerWishlist, ConsumerReview, 
    ConsumerAnalytics, ConsumerPreference
)
from .serializers import (
    ConsumerProfileSerializer, ConsumerWishlistSerializer, ConsumerReviewSerializer,
    ConsumerAnalyticsSerializer, ConsumerPreferenceSerializer, ConsumerDashboardSerializer,
    ConsumerWishlistCreateSerializer, ConsumerReviewCreateSerializer
)
from userprofiles.models import UserType
from orders.models import Order
from farmers.models import Produce, FarmerProfile
from farmers.serializers import ProduceSerializer
from orders.serializers import OrderSerializer


class IsConsumerOrStaff(permissions.BasePermission):
    """Allow access to staff or users whose profile role is CONSUMER."""
    def has_permission(self, request, view) -> bool:
        user = request.user
        if not (user and user.is_authenticated):
            return False
        if getattr(user, "is_staff", False):
            return True
        return bool(hasattr(user, "profile") and user.profile.role == UserType.CONSUMER)


class ConsumerProfileView(generics.RetrieveUpdateAPIView):
    """Get and update consumer profile."""
    serializer_class = ConsumerProfileSerializer
    permission_classes = [IsConsumerOrStaff]

    def get_object(self):
        """Get consumer profile for the current user."""
        user = self.request.user
        if user.is_staff and 'pk' in self.kwargs:
            return get_object_or_404(ConsumerProfile, pk=self.kwargs['pk'])
        return get_object_or_404(ConsumerProfile, user=user)

    def perform_update(self, serializer):
        """Update consumer profile."""
        serializer.save()


class ConsumerWishlistViewSet(generics.ListCreateAPIView):
    """List and create wishlist items for the current consumer."""
    serializer_class = ConsumerWishlistSerializer
    permission_classes = [IsConsumerOrStaff]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['produce__name', 'produce__variety', 'notes']
    ordering_fields = ['added_at', 'produce__name', 'produce__price_per_unit']
    ordering = ['-added_at']

    def get_queryset(self):
        """Get wishlist items for the current consumer."""
        return ConsumerWishlist.objects.filter(
            consumer=self.request.user.consumer_profile
        ).select_related('produce', 'produce__farmer')

    def perform_create(self, serializer):
        """Create wishlist item."""
        serializer.save(consumer=self.request.user.consumer_profile)


class ConsumerWishlistDetailView(generics.RetrieveUpdateDestroyAPIView):
    """Retrieve, update, or delete a wishlist item."""
    serializer_class = ConsumerWishlistSerializer
    permission_classes = [IsConsumerOrStaff]

    def get_queryset(self):
        """Get wishlist items for the current consumer."""
        return ConsumerWishlist.objects.filter(
            consumer=self.request.user.consumer_profile
        ).select_related('produce', 'produce__farmer')


class ConsumerReviewViewSet(generics.ListCreateAPIView):
    """List and create reviews for the current consumer."""
    serializer_class = ConsumerReviewSerializer
    permission_classes = [IsConsumerOrStaff]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['produce__name', 'review']
    ordering_fields = ['created_at', 'rating', 'produce__name']
    ordering = ['-created_at']

    def get_queryset(self):
        """Get reviews for the current consumer."""
        return ConsumerReview.objects.filter(
            consumer=self.request.user.consumer_profile
        ).select_related('produce', 'produce__farmer', 'order')

    def perform_create(self, serializer):
        """Create review."""
        serializer.save(consumer=self.request.user.consumer_profile)


class ConsumerReviewDetailView(generics.RetrieveUpdateDestroyAPIView):
    """Retrieve, update, or delete a review."""
    serializer_class = ConsumerReviewSerializer
    permission_classes = [IsConsumerOrStaff]

    def get_queryset(self):
        """Get reviews for the current consumer."""
        return ConsumerReview.objects.filter(
            consumer=self.request.user.consumer_profile
        ).select_related('produce', 'produce__farmer', 'order')


class ConsumerAnalyticsView(generics.RetrieveAPIView):
    """Get analytics for the current consumer."""
    serializer_class = ConsumerAnalyticsSerializer
    permission_classes = [IsConsumerOrStaff]

    def get_object(self):
        """Get analytics for the current consumer."""
        return get_object_or_404(ConsumerAnalytics, consumer=self.request.user.consumer_profile)


class ConsumerPreferenceView(generics.RetrieveUpdateAPIView):
    """Get and update consumer preferences."""
    serializer_class = ConsumerPreferenceSerializer
    permission_classes = [IsConsumerOrStaff]

    def get_object(self):
        """Get preferences for the current consumer."""
        return get_object_or_404(ConsumerPreference, consumer=self.request.user.consumer_profile)

    def perform_update(self, serializer):
        """Update preferences."""
        serializer.save()


@api_view(['GET'])
@permission_classes([IsConsumerOrStaff])
def consumer_dashboard(request: Request) -> Response:
    """Get comprehensive consumer dashboard data."""
    user = request.user
    consumer_profile = get_object_or_404(ConsumerProfile, user=user)
    
    # Get recent orders
    recent_orders = Order.objects.filter(user=user).order_by('-created_at')[:5]
    
    # Get wishlist items
    wishlist_items = ConsumerWishlist.objects.filter(consumer=consumer_profile).select_related('produce')[:10]
    
    # Get favorite farmers
    favorite_farmers = consumer_profile.favorite_farmers.all()[:5]
    
    # Get analytics
    analytics = ConsumerAnalytics.objects.filter(consumer=consumer_profile).first()
    
    # Get preferences
    preferences = ConsumerPreference.objects.filter(consumer=consumer_profile).first()
    
    # Calculate top produce categories from order history
    top_categories = (
        Order.objects.filter(user=user)
        .values('items__produce__category')
        .annotate(count=Count('items'))
        .order_by('-count')[:5]
        .values_list('items__produce__category', flat=True)
    )
    
    # Calculate monthly spending chart (last 6 months)
    monthly_spending = {}
    for i in range(6):
        month = timezone.now() - timedelta(days=30*i)
        month_key = month.strftime('%Y-%m')
        monthly_total = Order.objects.filter(
            user=user,
            created_at__year=month.year,
            created_at__month=month.month
        ).aggregate(total=Sum('total_amount'))['total'] or Decimal('0.00')
        monthly_spending[month_key] = float(monthly_total)
    
    # Calculate order frequency trend
    order_frequency = {}
    for i in range(4):
        week = timezone.now() - timedelta(weeks=i)
        week_key = week.strftime('%Y-W%W')
        week_count = Order.objects.filter(
            user=user,
            created_at__gte=week,
            created_at__lt=week + timedelta(weeks=1)
        ).count()
        order_frequency[week_key] = week_count
    
    dashboard_data = {
        'profile': consumer_profile,
        'analytics': analytics,
        'preferences': preferences,
        'recent_orders': recent_orders,
        'wishlist_items': wishlist_items,
        'favorite_farmers': favorite_farmers,
        'top_produce_categories': list(top_categories),
        'monthly_spending_chart': monthly_spending,
        'order_frequency_trend': order_frequency,
    }
    
    serializer = ConsumerDashboardSerializer(dashboard_data)
    return Response(serializer.data)


@api_view(['POST'])
@permission_classes([IsConsumerOrStaff])
def add_to_wishlist(request: Request) -> Response:
    """Add produce to consumer wishlist."""
    serializer = ConsumerWishlistCreateSerializer(data=request.data, context={'request': request})
    if serializer.is_valid():
        wishlist_item = serializer.save()
        return Response(ConsumerWishlistSerializer(wishlist_item).data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([IsConsumerOrStaff])
def add_review(request: Request) -> Response:
    """Add review for produce."""
    serializer = ConsumerReviewCreateSerializer(data=request.data, context={'request': request})
    if serializer.is_valid():
        review = serializer.save()
        return Response(ConsumerReviewSerializer(review).data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([IsConsumerOrStaff])
def toggle_favorite_farmer(request: Request) -> Response:
    """Add or remove farmer from favorites."""
    farmer_id = request.data.get('farmer_id')
    if not farmer_id:
        return Response({'error': 'farmer_id is required'}, status=status.HTTP_400_BAD_REQUEST)
    
    try:
        farmer = FarmerProfile.objects.get(id=farmer_id)
        consumer_profile = request.user.consumer_profile
        
        if farmer in consumer_profile.favorite_farmers.all():
            consumer_profile.remove_favorite_farmer(farmer)
            action = 'removed'
        else:
            consumer_profile.add_favorite_farmer(farmer)
            action = 'added'
        
        return Response({
            'message': f'Farmer {action} from favorites',
            'action': action,
            'farmer_id': farmer_id
        })
    except FarmerProfile.DoesNotExist:
        return Response({'error': 'Farmer not found'}, status=status.HTTP_404_NOT_FOUND)


@api_view(['GET'])
@permission_classes([IsConsumerOrStaff])
def consumer_recommendations(request: Request) -> Response:
    """Get personalized recommendations for consumer."""
    user = request.user
    consumer_profile = get_object_or_404(ConsumerProfile, user=user)
    
    # Get user's order history
    ordered_produce = Order.objects.filter(user=user).values_list('items__produce__category', flat=True).distinct()
    
    # Get preferences
    preferences = ConsumerPreference.objects.filter(consumer=consumer_profile).first()
    preferred_types = preferences.preferred_produce_types if preferences else []
    excluded_types = preferences.excluded_produce_types if preferences else []
    
    # Build recommendation query
    recommended_produce = Produce.objects.filter(available=True).exclude(
        category__in=excluded_types
    )
    
    # Prioritize preferred types
    if preferred_types:
        recommended_produce = recommended_produce.filter(category__in=preferred_types)
    
    # Add organic preference
    if consumer_profile.organic_preference:
        recommended_produce = recommended_produce.filter(is_organic=True)
    
    # Add local preference
    if consumer_profile.local_preference:
        # This would need to be implemented based on location logic
        pass
    
    # Order by rating and availability
    recommended_produce = recommended_produce.order_by('-average_rating', '-quantity_available')[:10]
    
    return Response({
        'recommendations': ProduceSerializer(recommended_produce, many=True).data,
        'based_on': {
            'order_history': list(ordered_produce),
            'preferences': preferred_types,
            'excluded': excluded_types
        }
    })


@api_view(['GET'])
@permission_classes([IsConsumerOrStaff])
def consumer_order_history(request: Request) -> Response:
    """Get detailed order history for consumer."""
    user = request.user
    
    # Get all orders with items
    orders = Order.objects.filter(user=user).prefetch_related('items', 'items__produce').order_by('-created_at')
    
    # Calculate statistics
    total_orders = orders.count()
    total_spent = orders.aggregate(total=Sum('total_amount'))['total'] or Decimal('0.00')
    average_order_value = total_spent / total_orders if total_orders > 0 else Decimal('0.00')
    
    # Get most ordered produce
    top_produce = (
        Order.objects.filter(user=user)
        .values('items__produce__name')
        .annotate(total_quantity=Sum('items__quantity'))
        .order_by('-total_quantity')[:5]
    )
    
    return Response({
        'orders': OrderSerializer(orders, many=True).data,
        'statistics': {
            'total_orders': total_orders,
            'total_spent': float(total_spent),
            'average_order_value': float(average_order_value),
            'top_produce': list(top_produce)
        }
    })


@api_view(['POST'])
@permission_classes([IsConsumerOrStaff])
def update_consumer_preferences(request: Request) -> Response:
    """Update specific consumer preferences."""
    consumer_profile = get_object_or_404(ConsumerProfile, user=request.user)
    preference, created = ConsumerPreference.objects.get_or_create(consumer=consumer_profile)
    
    # Update specific fields
    fields_to_update = [
        'preferred_produce_types', 'excluded_produce_types', 'preferred_quantities',
        'bulk_ordering_preference', 'price_range_preference', 'discount_preference',
        'subscription_frequency', 'subscription_budget', 'notification_channels',
        'notification_frequency'
    ]
    
    for field in fields_to_update:
        if field in request.data:
            setattr(preference, field, request.data[field])
    
    preference.save()
    
    return Response(ConsumerPreferenceSerializer(preference).data)


@api_view(['GET'])
@permission_classes([IsConsumerOrStaff])
def consumer_spending_analytics(request: Request) -> Response:
    """Get detailed spending analytics for consumer."""
    user = request.user
    
    # Get spending by month (last 12 months)
    monthly_spending = {}
    for i in range(12):
        month = timezone.now() - timedelta(days=30*i)
        month_key = month.strftime('%Y-%m')
        monthly_total = Order.objects.filter(
            user=user,
            created_at__year=month.year,
            created_at__month=month.month
        ).aggregate(total=Sum('total_amount'))['total'] or Decimal('0.00')
        monthly_spending[month_key] = float(monthly_total)
    
    # Get spending by produce category
    category_spending = (
        Order.objects.filter(user=user)
        .values('items__produce__category')
        .annotate(total=Sum('items__subtotal'))
        .order_by('-total')
    )
    
    # Get average order value trend
    avg_order_trend = []
    for i in range(6):
        month = timezone.now() - timedelta(days=30*i)
        month_orders = Order.objects.filter(
            user=user,
            created_at__year=month.year,
            created_at__month=month.month
        )
        avg_value = month_orders.aggregate(avg=Avg('total_amount'))['avg'] or Decimal('0.00')
        avg_order_trend.append({
            'month': month.strftime('%Y-%m'),
            'average_order_value': float(avg_value),
            'order_count': month_orders.count()
        })
    
    return Response({
        'monthly_spending': monthly_spending,
        'category_spending': list(category_spending),
        'average_order_trend': avg_order_trend,
        'total_spent': float(Order.objects.filter(user=user).aggregate(total=Sum('total_amount'))['total'] or Decimal('0.00')),
        'total_orders': Order.objects.filter(user=user).count()
    })


