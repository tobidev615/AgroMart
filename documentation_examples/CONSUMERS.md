# Consumers API Documentation

## Overview

The Consumers app provides comprehensive functionality for consumer users, including profile management, wishlist, reviews, analytics, preferences, and personalized recommendations.

## Authentication

All consumer endpoints require authentication. Use either:
- **JWT**: `Authorization: Bearer <access_token>`
- **Token**: `Authorization: Token <token>`

## Consumer Profile Management

### Get Consumer Profile
```http
GET /api/v1/consumers/me/
Authorization: Bearer <access_token>
```

**Response 200:**
```json
{
  "id": 1,
  "user": {
    "id": 1,
    "username": "alice",
    "email": "alice@example.com",
    "first_name": "Alice",
    "last_name": "Smith"
  },
  "delivery_preferences": {
    "preferred_time": "morning",
    "address": "123 Main St"
  },
  "preferred_delivery_time": "09:00-12:00",
  "delivery_instructions": "Leave at front door",
  "dietary_preferences": "Vegetarian, no nuts",
  "organic_preference": true,
  "local_preference": true,
  "total_spent": "150.00",
  "total_orders": 5,
  "average_order_value": "30.00",
  "last_order_date": "2024-01-15T10:30:00Z",
  "favorite_farmers": [],
  "favorite_produce_types": ["vegetables", "fruits"],
  "email_notifications": true,
  "sms_notifications": false,
  "marketing_emails": false,
  "created_at": "2024-01-01T00:00:00Z",
  "updated_at": "2024-01-15T10:30:00Z"
}
```

### Update Consumer Profile
```http
PATCH /api/v1/consumers/me/
Authorization: Bearer <access_token>
Content-Type: application/json

{
  "delivery_preferences": {
    "preferred_time": "afternoon",
    "address": "456 Oak Ave"
  },
  "dietary_preferences": "Vegan, gluten-free",
  "organic_preference": true,
  "local_preference": false
}
```

## Consumer Dashboard

### Get Dashboard Data
```http
GET /api/v1/consumers/dashboard/
Authorization: Bearer <access_token>
```

**Response 200:**
```json
{
  "profile": {
    "id": 1,
    "user": {...},
    "total_spent": "150.00",
    "total_orders": 5,
    "average_order_value": "30.00"
  },
  "analytics": {
    "order_frequency": "2.5",
    "average_order_size": "30.00",
    "delivery_success_rate": "100.00"
  },
  "preferences": {
    "subscription_frequency": "monthly",
    "bulk_ordering_preference": false,
    "discount_preference": true
  },
  "recent_orders": [
    {
      "id": 1,
      "total_amount": "45.00",
      "status": "DELIVERED",
      "created_at": "2024-01-15T10:30:00Z"
    }
  ],
  "wishlist_items": [
    {
      "id": 1,
      "produce": {
        "id": 1,
        "name": "Organic Tomatoes",
        "price_per_unit": "3.50"
      },
      "quantity": 2,
      "is_available": true
    }
  ],
  "favorite_farmers": [
    {
      "id": 1,
      "farm_name": "Green Valley Farm",
      "location": "Springfield"
    }
  ],
  "top_produce_categories": ["vegetables", "fruits", "herbs"],
  "monthly_spending_chart": {
    "2024-01": 150.00,
    "2023-12": 120.00,
    "2023-11": 90.00
  },
  "order_frequency_trend": {
    "2024-W03": 2,
    "2024-W02": 1,
    "2024-W01": 1
  }
}
```

## Wishlist Management

### List Wishlist Items
```http
GET /api/v1/consumers/wishlist/
Authorization: Bearer <access_token>
```

**Response 200:**
```json
{
  "count": 3,
  "next": null,
  "previous": null,
  "results": [
    {
      "id": 1,
      "consumer": 1,
      "produce": {
        "id": 1,
        "name": "Organic Tomatoes",
        "variety": "Cherry",
        "price_per_unit": "3.50",
        "unit": "kg"
      },
      "quantity": 2,
      "notes": "For salads",
      "added_at": "2024-01-15T10:30:00Z",
      "is_available": true
    }
  ]
}
```

### Add to Wishlist
```http
POST /api/v1/consumers/wishlist/add/
Authorization: Bearer <access_token>
Content-Type: application/json

{
  "produce_id": 1,
  "quantity": 2,
  "notes": "For salads"
}
```

**Response 201:**
```json
{
  "id": 1,
  "consumer": 1,
  "produce": {
    "id": 1,
    "name": "Organic Tomatoes",
    "price_per_unit": "3.50"
  },
  "quantity": 2,
  "notes": "For salads",
  "added_at": "2024-01-15T10:30:00Z",
  "is_available": true
}
```

### Update Wishlist Item
```http
PATCH /api/v1/consumers/wishlist/1/
Authorization: Bearer <access_token>
Content-Type: application/json

{
  "quantity": 3,
  "notes": "For salads and cooking"
}
```

### Delete Wishlist Item
```http
DELETE /api/v1/consumers/wishlist/1/
Authorization: Bearer <access_token>
```

## Reviews and Ratings

### List Reviews
```http
GET /api/v1/consumers/reviews/
Authorization: Bearer <access_token>
```

**Response 200:**
```json
{
  "count": 2,
  "next": null,
  "previous": null,
  "results": [
    {
      "id": 1,
      "consumer": 1,
      "produce": {
        "id": 1,
        "name": "Organic Tomatoes"
      },
      "rating": 5,
      "review": "Excellent quality tomatoes! Very fresh and flavorful.",
      "is_verified_purchase": true,
      "user_info": {
        "username": "alice",
        "first_name": "Alice",
        "last_name": "Smith"
      },
      "created_at": "2024-01-15T10:30:00Z"
    }
  ]
}
```

### Add Review
```http
POST /api/v1/consumers/reviews/add/
Authorization: Bearer <access_token>
Content-Type: application/json

{
  "produce_id": 1,
  "order_id": 1,
  "rating": 5,
  "review": "Excellent quality tomatoes! Very fresh and flavorful."
}
```

**Response 201:**
```json
{
  "id": 1,
  "consumer": 1,
  "produce": {
    "id": 1,
    "name": "Organic Tomatoes"
  },
  "order": {
    "id": 1,
    "total_amount": "45.00"
  },
  "rating": 5,
  "review": "Excellent quality tomatoes! Very fresh and flavorful.",
  "is_verified_purchase": true,
  "user_info": {
    "username": "alice",
    "first_name": "Alice",
    "last_name": "Smith"
  },
  "created_at": "2024-01-15T10:30:00Z"
}
```

### Update Review
```http
PATCH /api/v1/consumers/reviews/1/
Authorization: Bearer <access_token>
Content-Type: application/json

{
  "rating": 4,
  "review": "Good quality tomatoes, but could be fresher."
}
```

## Analytics

### Get Consumer Analytics
```http
GET /api/v1/consumers/analytics/
Authorization: Bearer <access_token>
```

**Response 200:**
```json
{
  "id": 1,
  "consumer": 1,
  "monthly_spending": {
    "2024-01": 150.00,
    "2023-12": 120.00
  },
  "yearly_spending": {
    "2024": 150.00,
    "2023": 450.00
  },
  "order_frequency": "2.5",
  "average_order_size": "30.00",
  "top_produce_categories": ["vegetables", "fruits"],
  "seasonal_preferences": {
    "summer": ["tomatoes", "cucumbers"],
    "winter": ["carrots", "potatoes"]
  },
  "preferred_delivery_days": ["Monday", "Wednesday"],
  "delivery_success_rate": "100.00",
  "last_login": "2024-01-15T10:30:00Z",
  "total_logins": 25,
  "days_since_last_order": 2
}
```

### Get Spending Analytics
```http
GET /api/v1/consumers/spending-analytics/
Authorization: Bearer <access_token>
```

**Response 200:**
```json
{
  "monthly_spending": {
    "2024-01": 150.00,
    "2023-12": 120.00,
    "2023-11": 90.00
  },
  "category_spending": [
    {
      "items__produce__category": "vegetables",
      "total": 80.00
    },
    {
      "items__produce__category": "fruits",
      "total": 70.00
    }
  ],
  "average_order_trend": [
    {
      "month": "2024-01",
      "average_order_value": 30.00,
      "order_count": 5
    }
  ],
  "total_spent": 150.00,
  "total_orders": 5
}
```

## Preferences

### Get Consumer Preferences
```http
GET /api/v1/consumers/preferences/
Authorization: Bearer <access_token>
```

**Response 200:**
```json
{
  "id": 1,
  "consumer": 1,
  "preferred_produce_types": ["vegetables", "fruits"],
  "excluded_produce_types": ["dairy", "meat"],
  "preferred_quantities": {
    "tomatoes": 2,
    "apples": 1
  },
  "bulk_ordering_preference": false,
  "price_range_preference": "10-50",
  "discount_preference": true,
  "subscription_frequency": "monthly",
  "subscription_budget": 100.00,
  "notification_channels": ["email", "in_app"],
  "notification_frequency": "immediate",
  "created_at": "2024-01-01T00:00:00Z",
  "updated_at": "2024-01-15T10:30:00Z"
}
```

### Update Preferences
```http
PATCH /api/v1/consumers/preferences/
Authorization: Bearer <access_token>
Content-Type: application/json

{
  "preferred_produce_types": ["vegetables", "fruits", "herbs"],
  "excluded_produce_types": ["dairy"],
  "subscription_frequency": "weekly",
  "notification_channels": ["email", "sms"]
}
```

### Update Specific Preferences
```http
POST /api/v1/consumers/preferences/update/
Authorization: Bearer <access_token>
Content-Type: application/json

{
  "preferred_produce_types": ["vegetables", "fruits"],
  "subscription_budget": 150.00,
  "notification_frequency": "daily"
}
```

## Favorites

### Toggle Favorite Farmer
```http
POST /api/v1/consumers/favorites/toggle-farmer/
Authorization: Bearer <access_token>
Content-Type: application/json

{
  "farmer_id": 1
}
```

**Response 200:**
```json
{
  "message": "Farmer added to favorites",
  "action": "added",
  "farmer_id": 1
}
```

## Recommendations

### Get Personalized Recommendations
```http
GET /api/v1/consumers/recommendations/
Authorization: Bearer <access_token>
```

**Response 200:**
```json
{
  "recommendations": [
    {
      "id": 1,
      "name": "Organic Tomatoes",
      "variety": "Cherry",
      "price_per_unit": "3.50",
      "quantity_available": 10,
      "farmer": {
        "id": 1,
        "farm_name": "Green Valley Farm"
      }
    }
  ],
  "based_on": {
    "order_history": ["vegetables", "fruits"],
    "preferences": ["vegetables", "fruits"],
    "excluded": ["dairy"]
  }
}
```

## Order History

### Get Order History
```http
GET /api/v1/consumers/order-history/
Authorization: Bearer <access_token>
```

**Response 200:**
```json
{
  "orders": [
    {
      "id": 1,
      "total_amount": "45.00",
      "status": "DELIVERED",
      "created_at": "2024-01-15T10:30:00Z",
      "items": [
        {
          "product_name": "Organic Tomatoes",
          "quantity": 2,
          "price_per_unit": "3.50",
          "subtotal": "7.00"
        }
      ]
    }
  ],
  "statistics": {
    "total_orders": 5,
    "total_spent": 150.00,
    "average_order_value": 30.00,
    "top_produce": [
      {
        "items__produce__name": "Organic Tomatoes",
        "total_quantity": 10
      }
    ]
  }
}
```

## Error Responses

### Validation Error (400)
```json
{
  "error": "Validation failed",
  "details": {
    "rating": ["Rating must be between 1 and 5."],
    "review": ["Review must be at least 10 characters long."]
  }
}
```

### Not Found (404)
```json
{
  "error": "Consumer profile not found"
}
```

### Permission Denied (403)
```json
{
  "error": "You do not have permission to access this resource"
}
```

## Features Summary

### ✅ **Consumer Profile Management**
- Extended profile with delivery preferences
- Dietary preferences and restrictions
- Spending analytics tracking
- Favorite farmers and produce types
- Communication preferences

### ✅ **Wishlist Functionality**
- Add/remove produce to wishlist
- Quantity and notes for wishlist items
- Availability tracking
- Search and filter wishlist items

### ✅ **Review & Rating System**
- Rate produce from 1-5 stars
- Write detailed reviews
- Verified purchase badges
- Review history and management

### ✅ **Consumer Analytics**
- Spending patterns and trends
- Order frequency analysis
- Produce category preferences
- Delivery success tracking
- Engagement metrics

### ✅ **Preference Management**
- Preferred produce types
- Excluded produce types
- Quantity preferences
- Price range preferences
- Subscription preferences
- Notification preferences

### ✅ **Personalized Features**
- Favorite farmers management
- Personalized recommendations
- Order history with statistics
- Spending analytics
- Dashboard with comprehensive data

### ✅ **Integration with Other Apps**
- Automatic profile creation for CONSUMER users
- Analytics updates on order placement
- Integration with orders, farmers, and subscriptions
- Real-time availability updates

## Database Schema

### ConsumerProfile
- User relationship and basic info
- Delivery preferences (JSON)
- Dietary preferences
- Spending analytics
- Favorite farmers (ManyToMany)
- Communication preferences

### ConsumerWishlist
- Consumer and produce relationships
- Quantity and notes
- Availability tracking
- Timestamps

### ConsumerReview
- Consumer and produce relationships
- Rating (1-5) and review text
- Verified purchase flag
- Order relationship (optional)

### ConsumerAnalytics
- Spending breakdowns (monthly/yearly)
- Order frequency and size
- Produce preferences
- Delivery analytics
- Engagement metrics

### ConsumerPreference
- Produce type preferences
- Quantity preferences
- Price and subscription preferences
- Notification preferences

## Permissions

- **IsConsumerOrStaff**: Only consumers and staff can access consumer endpoints
- **Profile Management**: Consumers can only manage their own profiles
- **Reviews**: Consumers can only review produce they've purchased
- **Wishlist**: Consumers can only manage their own wishlist
- **Analytics**: Consumers can only view their own analytics

## Rate Limiting

- **Anonymous**: 100 requests/hour
- **Authenticated**: 1000 requests/hour
- **Consumer-specific endpoints**: 500 requests/hour per user

## Integration Points

1. **User Registration**: Automatic consumer profile creation
2. **Order Placement**: Analytics updates and spending tracking
3. **Produce Reviews**: Rating system integration
4. **Farmer Favorites**: Cross-app relationships
5. **Subscription Management**: Preference integration
6. **Notifications**: Communication preference respect


