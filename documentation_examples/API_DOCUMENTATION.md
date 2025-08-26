# FarmFresh API Documentation

## Overview

The FarmFresh API is a RESTful service for farm management, order processing, and delivery coordination. It supports both JWT and Token authentication, with comprehensive role-based access control.

## Base URL

- **Development**: `http://localhost:8000/api/v1/`
- **Production**: `https://api.farmfresh.com/api/v1/`

## Authentication

### JWT Authentication (Recommended)

**Login Flow:**
```http
POST /api/v1/accounts/jwt/login/
Content-Type: application/json

{
  "username": "farmer_jane",
  "password": "secure_password"
}
```

**Response:**
```json
{
  "access": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
  "refresh": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."
}
```

**Using JWT:**
```http
GET /api/v1/accounts/me/
Authorization: Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...
```

**Refresh Token:**
```http
POST /api/v1/accounts/jwt/refresh/
Content-Type: application/json

{
  "refresh": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."
}
```

### Token Authentication (Legacy)

**Login:**
```http
POST /api/v1/accounts/login/
Content-Type: application/json

{
  "username": "farmer_jane",
  "password": "secure_password"
}
```

**Using Token:**
```http
GET /api/v1/accounts/me/
Authorization: Token 9944b09199c62bcf9418ad846dd0e4bbdfc6ee4b
```

## User Roles & Permissions

| Role | Description | Access |
|------|-------------|--------|
| **FARMER** | Can manage produce and farm profiles | Own produce, farm profile |
| **CONSUMER** | Can place orders and manage subscriptions | Own orders, cart, subscriptions |
| **BUSINESS** | Business customers with bulk ordering | Own profile, business orders |
| **DISTRIBUTOR** | Delivery coordination | Assigned deliveries, delivery status |
| **STAFF** | Administrative access | All data, admin functions |

## Rate Limiting

| Endpoint | Anonymous | Authenticated |
|----------|-----------|---------------|
| `/register/` | 5/hour | 10/hour |
| `/login/` | 10/hour | 20/hour |
| `/checkout/` | N/A | 50/hour |
| `/public/produce/` | 1000/hour | 2000/hour |
| `/notifications/stream/` | N/A | 100/hour |

**Rate Limit Response:**
```json
{
  "detail": "Rate limit exceeded for this endpoint.",
  "code": "rate_limit_exceeded",
  "request_id": "abc123"
}
```

## Error Responses

### Standard Error Format
```json
{
  "detail": "Error message",
  "code": "error_code",
  "request_id": "abc123",
  "field_errors": {
    "field_name": ["Field-specific error"]
  }
}
```

### Common HTTP Status Codes

| Code | Description | Example |
|------|-------------|---------|
| `200` | Success | GET response |
| `201` | Created | POST response |
| `400` | Bad Request | Validation errors |
| `401` | Unauthorized | Missing/invalid token |
| `403` | Forbidden | Insufficient permissions |
| `404` | Not Found | Resource doesn't exist |
| `429` | Too Many Requests | Rate limit exceeded |
| `500` | Server Error | Internal error |

### Validation Error Example
```json
{
  "detail": "Validation error occurred.",
  "code": "validation_error",
  "field_errors": {
    "email": ["Enter a valid email address."],
    "password": ["This password is too short."]
  },
  "request_id": "abc123"
}
```

### Permission Error Example
```json
{
  "detail": "You don't have permission to perform this action.",
  "code": "permission_denied",
  "request_id": "abc123"
}
```

## Pagination

All list endpoints support pagination with the following format:

**Request:**
```http
GET /api/v1/farmers/public/produce/?page=2&page_size=10
```

**Response:**
```json
{
  "count": 150,
  "next": "http://localhost:8000/api/v1/farmers/public/produce/?page=3",
  "previous": "http://localhost:8000/api/v1/farmers/public/produce/?page=1",
  "results": [...]
}
```

**Parameters:**
- `page`: Page number (default: 1)
- `page_size`: Items per page (max: 100, default: 20)

## Filtering & Search

### Public Produce Filtering
```http
GET /api/v1/farmers/public/produce/?search=tomato&min_price=2.00&max_price=10.00&available=true
```

**Available Filters:**
- `search`: Search in name, variety, description
- `min_price`, `max_price`: Price range
- `available`: Boolean filter
- `farmer`: Filter by farmer ID
- `unit`: Filter by unit (kg, lb, etc.)

### Ordering
```http
GET /api/v1/farmers/public/produce/?ordering=-created_at,price
```

**Ordering Options:**
- `created_at`, `-created_at`: Date created
- `price`, `-price`: Price
- `name`, `-name`: Name
- `farmer__name`: Farmer name

## Real-time Notifications (SSE)

### Server-Sent Events Stream
```javascript
// For JWT authentication
const eventSource = new EventSource(
  '/api/v1/notifications/stream/?last_id=0&access=YOUR_JWT_TOKEN'
);

eventSource.onmessage = function(event) {
  const notification = JSON.parse(event.data);
  console.log('New notification:', notification);
};

eventSource.onerror = function(error) {
  console.error('SSE error:', error);
  eventSource.close();
};
```

**Notification Format:**
```json
{
  "id": 123,
  "title": "Order confirmed",
  "message": "Your order #456 has been confirmed.",
  "is_read": false,
  "created_at": "2024-01-15T10:30:00Z"
}
```

## File Uploads

### Produce Images
```http
POST /api/v1/farmers/produce/
Authorization: Bearer YOUR_JWT_TOKEN
Content-Type: multipart/form-data

{
  "name": "Fresh Tomatoes",
  "image": [binary file],
  "quantity_available": 50,
  "price_per_unit": 5.00
}
```

**Supported Formats:**
- JPEG, PNG, GIF
- Max size: 5MB
- Automatic resizing for thumbnails

## Webhooks (Future)

### Order Status Changes
```http
POST https://your-app.com/webhooks/order-status
Content-Type: application/json
X-FarmFresh-Signature: sha256=abc123

{
  "event": "order.status.changed",
  "data": {
    "order_id": 456,
    "old_status": "PENDING",
    "new_status": "CONFIRMED",
    "timestamp": "2024-01-15T10:30:00Z"
  }
}
```

## Security Headers

All responses include security headers:
- `X-Content-Type-Options: nosniff`
- `X-Frame-Options: DENY`
- `X-XSS-Protection: 1; mode=block`
- `Content-Security-Policy: default-src 'self'...`
- `Referrer-Policy: strict-origin-when-cross-origin`

## Request Tracing

Include `X-Request-ID` header for request tracing:
```http
GET /api/v1/accounts/me/
Authorization: Bearer YOUR_JWT_TOKEN
X-Request-ID: abc123-def456-ghi789
```

Response will echo the same request ID:
```json
{
  "user": {...},
  "request_id": "abc123-def456-ghi789"
}
```

## API Versioning

- **Current Version**: v1 (`/api/v1/`)
- **Legacy Support**: `/api/` (redirects to v1)
- **Future Versions**: `/api/v2/`, `/api/v3/`

## SDK Examples

### JavaScript/TypeScript
```typescript
import axios from 'axios';

class AgroMartAPI {
  private baseURL = 'http://localhost:8000/api/v1';
  private token: string | null = null;

  async login(username: string, password: string) {
    const response = await axios.post(`${this.baseURL}/accounts/jwt/login/`, {
      username,
      password
    });
    this.token = response.data.access;
    return response.data;
  }

  async getProfile() {
    const response = await axios.get(`${this.baseURL}/accounts/me/`, {
      headers: { Authorization: `Bearer ${this.token}` }
    });
    return response.data;
  }

  async getPublicProduce(filters = {}) {
    const response = await axios.get(`${this.baseURL}/farmers/public/produce/`, {
      params: filters
    });
    return response.data;
  }
}
```

### Python
```python
import requests

class AgroMartAPI:
    def __init__(self, base_url="http://localhost:8000/api/v1"):
        self.base_url = base_url
        self.token = None

    def login(self, username, password):
        response = requests.post(f"{self.base_url}/accounts/jwt/login/", {
            "username": username,
            "password": password
        })
        self.token = response.json()["access"]
        return response.json()

    def get_profile(self):
        headers = {"Authorization": f"Bearer {self.token}"}
        response = requests.get(f"{self.base_url}/accounts/me/", headers=headers)
        return response.json()

    def get_public_produce(self, **filters):
        response = requests.get(f"{self.base_url}/farmers/public/produce/", params=filters)
        return response.json()
```

## Testing

### Health Check
```bash
curl http://localhost:8000/api/v1/health/
```

### Readiness Check
```bash
curl http://localhost:8000/api/v1/readiness/
```

### Authentication Test
```bash
# Login
curl -X POST http://localhost:8000/api/v1/accounts/jwt/login/ \
  -H "Content-Type: application/json" \
  -d '{"username": "testuser", "password": "testpass"}'

# Use token
curl http://localhost:8000/api/v1/accounts/me/ \
  -H "Authorization: Bearer YOUR_TOKEN"
```

## Support

- **Documentation**: `/api/docs/` (Swagger UI)
- **Schema**: `/api/schema/` (OpenAPI JSON)
- **Redoc**: `/api/redoc/` (Alternative docs)
- **Health**: `/api/v1/health/`
- **Status**: `/api/v1/readiness/`


