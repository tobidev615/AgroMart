# Consumers API Examples (v1)

## Me
```http
GET /api/v1/consumers/me/
Authorization: Bearer <access>
```

## Dashboard
```http
GET /api/v1/consumers/dashboard/
Authorization: Bearer <access>
```

## Wishlist
```http
GET /api/v1/consumers/wishlist/
Authorization: Bearer <access>
```

```http
POST /api/v1/consumers/wishlist/add/
Authorization: Bearer <access>
Content-Type: application/json

{ "produce_id": 1, "quantity": 2, "notes": "For salad" }
```

## Reviews
```http
GET /api/v1/consumers/reviews/
Authorization: Bearer <access>
```

```http
POST /api/v1/consumers/reviews/add/
Authorization: Bearer <access>
Content-Type: application/json

{ "produce_id": 1, "rating": 5, "review": "Excellent quality!" }
```

## Preferences
```http
GET /api/v1/consumers/preferences/
Authorization: Bearer <access>
```

```http
POST /api/v1/consumers/preferences/update/
Authorization: Bearer <access>
Content-Type: application/json

{ "preferred_produce_types": ["vegetables"], "notification_channels": ["in_app"] }
```

## Recommendations
```http
GET /api/v1/consumers/recommendations/
Authorization: Bearer <access>
```

## Order History
```http
GET /api/v1/consumers/order-history/
Authorization: Bearer <access>
```

## Spending Analytics
```http
GET /api/v1/consumers/spending-analytics/
Authorization: Bearer <access>
```
