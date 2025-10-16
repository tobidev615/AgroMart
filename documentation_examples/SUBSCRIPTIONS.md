# Subscriptions API Examples (v1)

## List Plans
```http
GET /api/v1/subscriptions/plans/
```

## My Subscriptions
```http
GET /api/v1/subscriptions/subscriptions/
Authorization: Bearer <access>
```

## Create Subscription
```http
POST /api/v1/subscriptions/subscriptions/
Authorization: Bearer <access>
Content-Type: application/json

{ "plan": 1, "items": [{ "produce_id": 1, "quantity": 2 }] }
```

## Suggest Bundles
```http
GET /api/v1/subscriptions/suggest/
Authorization: Bearer <access>
```

## Run Cycle (Admin)
```http
POST /api/v1/subscriptions/run-cycle/
Authorization: Bearer <staff-access>
```
