from django.urls import path
from . import views

# app_name = 'consumers'  # Commented out to avoid namespace conflict

urlpatterns = [
    # Consumer Profile
    path('me/', views.ConsumerProfileView.as_view(), name='consumer-profile'),
    path('me/<int:pk>/', views.ConsumerProfileView.as_view(), name='consumer-profile-detail'),
    
    # Consumer Dashboard
    path('dashboard/', views.consumer_dashboard, name='consumer-dashboard'),
    
    # Wishlist
    path('wishlist/', views.ConsumerWishlistViewSet.as_view(), name='consumer-wishlist'),
    path('wishlist/<int:pk>/', views.ConsumerWishlistDetailView.as_view(), name='consumer-wishlist-detail'),
    path('wishlist/add/', views.add_to_wishlist, name='add-to-wishlist'),
    
    # Reviews
    path('reviews/', views.ConsumerReviewViewSet.as_view(), name='consumer-reviews'),
    path('reviews/<int:pk>/', views.ConsumerReviewDetailView.as_view(), name='consumer-review-detail'),
    path('reviews/add/', views.add_review, name='add-review'),
    
    # Analytics
    path('analytics/', views.ConsumerAnalyticsView.as_view(), name='consumer-analytics'),
    path('spending-analytics/', views.consumer_spending_analytics, name='consumer-spending-analytics'),
    
    # Preferences
    path('preferences/', views.ConsumerPreferenceView.as_view(), name='consumer-preferences'),
    path('preferences/update/', views.update_consumer_preferences, name='update-consumer-preferences'),
    
    # Favorites
    path('favorites/toggle-farmer/', views.toggle_favorite_farmer, name='toggle-favorite-farmer'),
    
    # Recommendations
    path('recommendations/', views.consumer_recommendations, name='consumer-recommendations'),
    
    # Order History
    path('order-history/', views.consumer_order_history, name='consumer-order-history'),
]
