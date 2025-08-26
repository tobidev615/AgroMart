# Subscriptions API Examples

## Seeding Default Plans

Run one of the following to populate plans:

```bash
# Full demo dataset (users, produce, orders, deliveries, subscriptions, etc.)
python manage.py seed_all

# Only subscription plans
python manage.py seed_plans
```

## List Plans
```http
GET /api/plans/
```

Response 200
```json
[ { "id": 1, "name": "Weekly Box", "period": "WEEKLY", "price": "19.99" } ]
```

## Create Subscription
```http
POST /api/subscriptions/
Authorization: Bearer <access>
Content-Type: application/json

{ "plan": 1 }
```

Response 201
```json
{ "id": 5, "plan": 1, "status": "ACTIVE" }
```

