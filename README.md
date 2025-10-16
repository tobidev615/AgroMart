# FarmFresh REST API

A Django REST API for catalog, orders, payments, deliveries, notifications, and more.

## Quick Start

```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
python manage.py migrate
python manage.py runserver
```

## Docs
- See `DOCs/README.md` (index)
- Endpoints overview: `DOCs/api-endpoints.md`
- Module docs: `DOCs/accounts.md`, `DOCs/inventory.md`, `DOCs/orders.md`, `DOCs/payments.md`, `DOCs/notifications.md`
- Additional: `DOCs/environment.md`, `DOCs/pagination.md`, `DOCs/errors.md`, `DOCs/notifications-sse.md`
- Postman: `DOCs/postman/`

Live schema/docs when running:
- `/api/schema/` (OpenAPI JSON)
- `/api/docs/` (Swagger UI)
- `/api/redoc/` (Redoc)

## Authentication
- JWT (preferred) and DRF Token. See `DOCs/accounts.md`.

## Notable Apps
- `inventory` (catalog)
- `orders` (cart/orders)
- `payments` (wallet + Stripe checkout)
- `deliveries` (status + distributor tools)
- `consumers`, `business`, `notifications`, `subscriptions`

## Testing
```bash
pip install -r requirements-dev.txt
pytest -q
```

## Env vars (see `.env.example`)
- `DEBUG`, `SECRET_KEY`, `ALLOWED_HOSTS`
- `DATABASE_URL` (prod)
- `CELERY_BROKER_URL` (Redis)
- `SENTRY_DSN` (optional)
- `STRIPE_API_KEY`, `STRIPE_WEBHOOK_SECRET` (payments)
