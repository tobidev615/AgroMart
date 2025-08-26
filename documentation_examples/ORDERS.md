# Orders API Examples

## Add To Cart
```http
POST /api/cart/items/
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
POST /api/checkout/
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
PATCH /api/orders/42/
Authorization: Bearer <staff-access>
Content-Type: application/json

{ "status": "CONFIRMED" }
```

Response 200
```json
{ "id": 42, "status": "CONFIRMED", "total_amount": "9.00" }
```
