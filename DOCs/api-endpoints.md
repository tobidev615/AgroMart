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
- `GET /api/v1/accounts/verify-email/?uid=...&token=...`
- `POST /api/v1/accounts/password-reset-request/`
- `POST /api/v1/accounts/password-reset-confirm/`

### Inventory (Catalog)
- `GET /api/v1/inventory/categories/`
- `GET /api/v1/inventory/products/`
- `GET /api/v1/inventory/variants/`

### Consumers
- `GET|PATCH /api/v1/consumers/me/`
- `GET /api/v1/consumers/dashboard/`
- `GET|POST|PATCH|DELETE /api/v1/consumers/wishlist/`
- `POST /api/v1/consumers/wishlist/add/`
- `GET|POST|PATCH|DELETE /api/v1/consumers/reviews/`
- `POST /api/v1/consumers/reviews/add/`
- `GET /api/v1/consumers/analytics/`
- `GET|PATCH /api/v1/consumers/preferences/`
- `POST /api/v1/consumers/preferences/update/`
- `POST /api/v1/consumers/favorites/toggle-farmer/`
- `GET /api/v1/consumers/recommendations/`
- `GET /api/v1/consumers/order-history/`
- `GET /api/v1/consumers/spending-analytics/`

### Orders
- `GET|POST|PUT|DELETE /api/v1/cart/`
- `GET|POST|PATCH|DELETE /api/v1/cart/items/`
- `GET|PATCH|DELETE /api/v1/cart/items/<id>/`
- `POST /api/v1/checkout/`
- `GET /api/v1/orders/`
- `GET /api/v1/orders/<id>/`
- `GET /api/v1/farmer/orders/` – farmer’s orders history

### Payments
- `GET /api/v1/payments/wallet/`
- `POST /api/v1/payments/wallet/deposit/`
- `POST /api/v1/payments/wallet/pay/`
- `POST /api/v1/payments/checkout-session/`
- `POST /api/v1/payments/stripe/webhook/` (no auth)

### Deliveries
- `GET|POST /api/v1/deliveries/` (admin)
- `GET|PATCH /api/v1/deliveries/<id>/`
- `GET /api/v1/deliveries/assigned/` (distributor)
- `POST /api/v1/deliveries/<id>/mark-delivered/` (distributor)
- `GET /api/v1/deliveries/payout-summary/` (distributor)
- Delivery windows (RO): via inventory router
- Delivery batches (RO): via inventory router

### Business
- `GET|PATCH /api/v1/business/me/`
- `GET /api/v1/business/orders/`
- `POST /api/v1/business/bulk-orders/`
- `GET|POST /api/v1/business/pricing-tiers/` (admin)
- `GET|PATCH|DELETE /api/v1/business/pricing-tiers/<id>/` (admin)
- `GET|POST /api/v1/business/contracts/`
- `GET|PATCH|DELETE /api/v1/business/contracts/<id>/`
- `POST /api/v1/business/contracts/run-cycle/` (admin)
- `GET /api/v1/business/invoices/`
- `GET /api/v1/business/invoices/<id>/`
- `GET /api/v1/business/logistics/`
- `GET /api/v1/business/analytics/`

### Subscriptions
- `GET /api/v1/subscriptions/plans/`
- `GET|POST /api/v1/subscriptions/subscriptions/`
- `GET|PATCH|DELETE /api/v1/subscriptions/subscriptions/<id>/`
- `GET /api/v1/subscriptions/suggest/`
- `POST /api/v1/subscriptions/run-cycle/` (admin)

### Notifications
- `GET /api/v1/notifications/`
- `PATCH /api/v1/notifications/<id>/`
- `GET /api/v1/notifications/stream/` (SSE; query `access` or `token`)

### Notes
- Pagination: `page`, `page_size`
- Filtering/search: `search`, `ordering`, per-app filters
- Auth: JWT preferred; DRF Token supported
