## API Endpoints Overview

Prefer `/api/v1/` routes. Explore live docs at `/api/docs/` or `/api/redoc/`.

### Health
- `GET /api/v1/health/` – basic health
- `GET /api/v1/readiness/` – checks DB/cache/Redis

### Accounts
- `POST /api/v1/accounts/register/`
- `POST /api/v1/accounts/login/` (token)
- `POST /api/v1/accounts/jwt/login/`, `POST /api/v1/accounts/jwt/refresh/`
- `GET|PATCH /api/v1/accounts/me/`

### Farmers
- `GET|POST|PUT|PATCH|DELETE /api/v1/farmers/me/`
- `GET|POST|PUT|PATCH|DELETE /api/v1/farmers/produce/`
- `GET /api/v1/farmers/public/produce/` (public list)
- `GET /api/v1/farmers/public/produce/<id>/`

### Consumers
- `GET|PATCH /api/v1/consumers/me/`
- `GET /api/v1/consumers/dashboard/`
- `GET|POST|PUT|PATCH|DELETE /api/v1/consumers/wishlist/`
- `GET|POST|PUT|PATCH|DELETE /api/v1/consumers/reviews/`
- `GET /api/v1/consumers/analytics/`
- `GET|PATCH /api/v1/consumers/preferences/`
- `POST /api/v1/consumers/favorites/toggle-farmer/`
- `GET /api/v1/consumers/recommendations/`
- `GET /api/v1/consumers/order-history/`

### Orders
- `GET|POST|PUT|PATCH|DELETE /api/v1/cart/`
- `GET|POST|PUT|PATCH|DELETE /api/v1/cart/items/`
- `POST /api/v1/checkout/`
- `GET|PUT|PATCH /api/v1/orders/`
- `GET /api/v1/farmers/orders/`

### Subscriptions
- `GET /api/v1/subscriptions/plans/`
- `GET|POST /api/v1/subscriptions/`
- `GET /api/v1/subscriptions/suggestions/`
- `POST /api/v1/subscriptions/run-cycle/` (staff)

### Notifications
- `GET /api/v1/notifications/`
- `PATCH /api/v1/notifications/<id>/`
- `GET /api/v1/notifications/stream/` (SSE)

### Business, Distributors, Deliveries, Payments
- See live docs and `../documentation_examples/BUSINESS.md` for the Business module.
- Distributors: profile endpoints under `/api/v1/distributors/…`
- Deliveries: `/api/v1/deliveries/…` plus `/api/v1/deliveries/assigned/`, `/api/v1/deliveries/<id>/mark-delivered/`
- Payments: `/api/v1/payments/…` (see live docs)

### Query parameters (common)
- `page`, `page_size` – pagination
- `search` – full-text search for supported lists
- `ordering` – e.g. `name`, `-created_at`
- Additional filters vary by resource; see OpenAPI.