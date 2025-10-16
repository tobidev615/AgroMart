# Business (Corporate Buyers) API Examples (v1)

## Profile
```http
GET /api/v1/business/me/
Authorization: Bearer <access>
```

```http
PATCH /api/v1/business/me/
Authorization: Bearer <access>
Content-Type: application/json

{ "company": "Blue Harbor Hotel", "business_type": "HOTEL" }
```

## Orders
```http
GET /api/v1/business/orders/
Authorization: Bearer <access>
```

## Bulk Orders
```http
POST /api/v1/business/bulk-orders/
Authorization: Bearer <access>
Content-Type: application/json

{ "items": [{ "produce_id": 1, "quantity": 50, "unit": "crate" }] }
```

## Pricing Tiers (Admin)
```http
GET /api/v1/business/pricing-tiers/
Authorization: Bearer <staff-access>
```

## Contracts
```http
GET /api/v1/business/contracts/
Authorization: Bearer <access>
```

```http
POST /api/v1/business/contracts/
Authorization: Bearer <access>
Content-Type: application/json

{ "name": "Weekly tomatoes", "frequency": "WEEKLY", "items": [{ "produce": 1, "quantity": 50, "unit": "kg", "agreed_unit_price": "1200.00" }] }
```

## Invoices
```http
GET /api/v1/business/invoices/
Authorization: Bearer <access>
```

## Logistics & Analytics
```http
GET /api/v1/business/logistics/
Authorization: Bearer <access>
```

```http
GET /api/v1/business/analytics/
Authorization: Bearer <access>
```
