# Notifications API Examples (v1)

## List Notifications
```http
GET /api/v1/notifications/
Authorization: Bearer <access>
```

Response 200
```json
{ "count": 0, "results": [] }
```

## SSE Stream
When using JWT in browsers, pass the access token as a query param.
```http
GET /api/v1/notifications/stream/?last_id=0&access=<JWT>
```

Message format (onmessage):
```json
{ "id": 1, "title": "Order confirmed", "message": "Your order #42...", "is_read": false }
```
