# Orders API Examples (v1)

## Add To Cart
```http
POST /api/v1/cart/items/
Authorization: Bearer <access>
Content-Type: application/json

{ "produce_id": 10, "quantity": 2 }
```

Response 201
```json
{ "id": 5, "produce": {"id": 10, "name": "Tomato"}, "quantity": 2 }
```

## Checkout
```http
POST /api/v1/checkout/
Authorization: Bearer <access>
```

Response 201
```json
{
  "id": 42,
  "status": "PENDING",
  "total_amount": "9.00",
  "items": [
    { "produce": {"id": 10, "name": "Tomato"}, "quantity": 2, "subtotal": "9.00" }
  ]
}
```

## Update Order Status (Staff)
```http
PATCH /api/v1/orders/42/
Authorization: Bearer <staff-access>
Content-Type: application/json

{ "status": "CONFIRMED" }
```

Response 200
```json
{ "id": 42, "status": "CONFIRMED", "total_amount": "9.00" }
```
