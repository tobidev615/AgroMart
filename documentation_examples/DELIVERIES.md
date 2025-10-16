# Deliveries API Examples (v1)

## Create Delivery (Staff)
```http
POST /api/v1/deliveries/
Authorization: Bearer <staff-access>
Content-Type: application/json

{ "order": 42, "scheduled_date": "2025-08-10T09:00:00Z" }
```

Response 201
```json
{ "id": 7, "order": 42, "status": "PENDING" }
```

## Mark Delivered (Distributor)
```http
POST /api/v1/deliveries/7/mark-delivered/
Authorization: Bearer <distributor-access>
```

Response 200
```json
{ "detail": "Marked delivered" }
```

## Payout Summary (Distributor)
```http
GET /api/v1/deliveries/payout-summary/
Authorization: Bearer <distributor-access>
```
