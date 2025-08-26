# Farmers API Documentation

## Overview

The Farmers API provides comprehensive functionality for farmer profiles, produce management, cluster membership, and earnings tracking.

## Authentication

All farmer endpoints require authentication. Use either JWT or Token authentication:

```http
Authorization: Bearer <jwt_token>
# or
Authorization: Token <api_token>
```

## Endpoints

### Farmer Profile

#### Get/Update My Profile
```http
GET /api/v1/farmers/me/
PUT /api/v1/farmers/me/
PATCH /api/v1/farmers/me/
```

**Response:**
```json
{
  "id": 1,
  "user": "farmer_jane",
  "name": "Jane Smith",
  "location": "Springfield, IL",
  "crops": "tomatoes, corn, wheat",
  "estimated_harvest": "500kg tomatoes",
  "total_earnings": "1250.00",
  "total_orders": 15,
  "created_at": "2024-01-15T10:30:00Z",
  "updated_at": "2024-01-15T10:30:00Z"
}
```

### Produce Management

#### List My Produce
```http
GET /api/v1/farmers/produce/
```

**Response:**
```json
{
  "count": 5,
  "next": null,
  "previous": null,
  "results": [
    {
      "id": 1,
      "farmer": "Jane Smith",
      "name": "Cherry Tomatoes",
      "variety": "Sweet 100",
      "description": "Sweet cherry tomatoes",
      "image": "/media/produce/tomatoes.jpg",
      "quantity_available": 50,
      "unit": "kg",
      "price_per_unit": "5.00",
      "available": true,
      "total_sold": 25,
      "total_revenue": "125.00",
      "created_at": "2024-01-15T10:30:00Z",
      "updated_at": "2024-01-15T10:30:00Z"
    }
  ]
}
```

#### Create New Produce
```http
POST /api/v1/farmers/produce/
Content-Type: application/json

{
  "name": "Fresh Corn",
  "variety": "Sweet Yellow",
  "description": "Sweet yellow corn",
  "quantity_available": 100,
  "unit": "kg",
  "price_per_unit": "3.50"
}
```

#### Update Produce
```http
PUT /api/v1/farmers/produce/1/
Content-Type: application/json

{
  "name": "Cherry Tomatoes",
  "variety": "Sweet 100",
  "description": "Sweet cherry tomatoes",
  "quantity_available": 75,
  "unit": "kg",
  "price_per_unit": "5.50",
  "available": true
}
```

#### Delete Produce
```http
DELETE /api/v1/farmers/produce/1/
```

### Earnings Dashboard

#### Get Dashboard Summary
```http
GET /api/v1/farmers/dashboard/
```

**Response:**
```json
{
  "total_earnings": "1250.00",
  "total_orders": 15,
  "pending_earnings": "150.00",
  "confirmed_earnings": "800.00",
  "paid_earnings": "300.00",
  "active_produce_count": 3,
  "total_produce_count": 5,
  "recent_orders": [
    {
      "id": 1,
      "order_id": 123,
      "produce_name": "Cherry Tomatoes",
      "quantity": 5,
      "total_amount": "25.00",
      "status": "CONFIRMED",
      "created_at": "2024-01-15T10:30:00Z"
    }
  ],
  "top_selling_produce": [
    {
      "id": 1,
      "name": "Cherry Tomatoes",
      "total_sold": 25,
      "total_revenue": "125.00"
    }
  ],
  "monthly_earnings": [
    {
      "month": "2024-01",
      "earnings": "450.00"
    },
    {
      "month": "2023-12",
      "earnings": "800.00"
    }
  ]
}
```

#### Get Earnings History
```http
GET /api/v1/farmers/earnings/
```

**Response:**
```json
{
  "count": 15,
  "next": null,
  "previous": null,
  "results": [
    {
      "id": 1,
      "produce_name": "Cherry Tomatoes",
      "order_id": 123,
      "customer_name": "John Doe",
      "quantity": 5,
      "unit_price": "5.00",
      "total_amount": "25.00",
      "status": "CONFIRMED",
      "created_at": "2024-01-15T10:30:00Z",
      "updated_at": "2024-01-15T10:30:00Z"
    }
  ]
}
```

#### Get Analytics
```http
GET /api/v1/farmers/analytics/?days=30
```

**Response:**
```json
{
  "earnings_over_time": [
    {
      "date": "2024-01-15",
      "earnings": "25.00"
    },
    {
      "date": "2024-01-14",
      "earnings": "50.00"
    }
  ],
  "produce_performance": [
    {
      "id": 1,
      "name": "Cherry Tomatoes",
      "total_orders": 5,
      "total_revenue": "125.00",
      "total_sold": 25
    }
  ],
  "summary": {
    "total_earnings": "1250.00",
    "total_orders": 15,
    "active_produce": 3
  }
}
```

### Farm Clusters

#### List Clusters
```http
GET /api/v1/farmers/clusters/
```

#### Create Cluster
```http
POST /api/v1/farmers/clusters/
Content-Type: application/json

{
  "name": "Springfield Farmers Co-op",
  "description": "Local farmers cooperative",
  "location": "Springfield, IL"
}
```

### Public Produce Browsing

#### List All Available Produce
```http
GET /api/v1/farmers/public/produce/
```

**Query Parameters:**
- `search`: Search in name, variety, description
- `min_price`, `max_price`: Price range
- `farmer_id`: Filter by specific farmer
- `location`: Filter by location
- `crops`: Filter by crop type
- `ordering`: Sort by field (e.g., `price_per_unit`, `-created_at`)

**Example:**
```http
GET /api/v1/farmers/public/produce/?search=tomato&min_price=2.00&max_price=10.00&ordering=-created_at
```

## Error Responses

### Validation Error
```json
{
  "detail": "Validation error occurred.",
  "code": "validation_error",
  "field_errors": {
    "price_per_unit": ["This field must be greater than 0."],
    "quantity_available": ["This field must be greater than or equal to 0."]
  },
  "request_id": "abc123"
}
```

### Permission Error
```json
{
  "detail": "You don't have permission to perform this action.",
  "code": "permission_denied",
  "request_id": "abc123"
}
```

## File Uploads

### Upload Produce Image
```http
POST /api/v1/farmers/produce/
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

## Earnings Tracking

### How Earnings Work

1. **Order Placement**: When a customer places an order, `FarmerEarnings` records are created with status `PENDING`
2. **Order Confirmation**: When staff confirms an order, earnings status changes to `CONFIRMED` and farmer's total earnings are updated
3. **Payment**: When payment is processed, earnings status changes to `PAID`

### Earnings Status Flow
```
PENDING → CONFIRMED → PAID
```

### Automatic Updates

- **Farmer Profile**: `total_earnings` and `total_orders` are automatically updated
- **Produce Stats**: `total_sold` and `total_revenue` are updated per produce
- **Notifications**: Farmers are notified of new orders and status changes

## Usage Examples

### JavaScript/TypeScript
```typescript
class FarmerAPI {
  private baseURL = 'http://localhost:8000/api/v1/farmers';
  private token: string;

  constructor(token: string) {
    this.token = token;
  }

  async getDashboard() {
    const response = await fetch(`${this.baseURL}/dashboard/`, {
      headers: { Authorization: `Bearer ${this.token}` }
    });
    return response.json();
  }

  async createProduce(data: any) {
    const response = await fetch(`${this.baseURL}/produce/`, {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${this.token}`,
        'Content-Type': 'application/json'
      },
      body: JSON.stringify(data)
    });
    return response.json();
  }

  async getEarnings() {
    const response = await fetch(`${this.baseURL}/earnings/`, {
      headers: { Authorization: `Bearer ${this.token}` }
    });
    return response.json();
  }
}
```

### Python
```python
import requests

class FarmerAPI:
    def __init__(self, base_url="http://localhost:8000/api/v1/farmers", token=None):
        self.base_url = base_url
        self.token = token
        self.headers = {"Authorization": f"Bearer {token}"} if token else {}

    def get_dashboard(self):
        response = requests.get(f"{self.base_url}/dashboard/", headers=self.headers)
        return response.json()

    def create_produce(self, data):
        response = requests.post(
            f"{self.base_url}/produce/",
            json=data,
            headers=self.headers
        )
        return response.json()

    def get_earnings(self):
        response = requests.get(f"{self.base_url}/earnings/", headers=self.headers)
        return response.json()
```

## Testing

### Test Dashboard
```bash
curl -H "Authorization: Bearer YOUR_TOKEN" \
  http://localhost:8000/api/v1/farmers/dashboard/
```

### Test Produce Creation
```bash
curl -X POST \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"name": "Fresh Corn", "quantity_available": 100, "unit": "kg", "price_per_unit": "3.50"}' \
  http://localhost:8000/api/v1/farmers/produce/
```

### Test Earnings
```bash
curl -H "Authorization: Bearer YOUR_TOKEN" \
  http://localhost:8000/api/v1/farmers/earnings/
```
