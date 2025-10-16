# FarmFresh Postman Collection

This folder contains:
- `FarmFresh.postman_collection.json` — the API collection with folders per module
- `FarmFresh.postman_environment.json` — a local environment with variables

## Import
1. Open Postman → Import → Select both JSON files from `DOCs/postman/`.
2. Choose the environment "FarmFresh Local" in the top-right.

## Variables
- `baseUrl`: e.g., `http://127.0.0.1:8000`
- `apiPrefix`: `/api/v1`
- `accessToken`: set automatically after JWT Login
- `refreshToken`: set automatically after JWT Login
- `drfToken`: set after DRF Token Login (alternative auth)
- `stripeSignature`: for webhook testing (optional)

## Auth flows
- Use "Auth → JWT Login" to obtain `access`/`refresh`. Collection-level Bearer auth uses `{{accessToken}}`.
- Alternatively, "Auth → DRF Token Login" stores `{{drfToken}}`; for any request, override auth to Header: `Authorization: Token {{drfToken}}`.
- SSE uses query `?access={{accessToken}}` as configured.

## Common flows for FE devs
- Accounts: register → jwt/login → me
- Browse catalog: inventory/categories → inventory/products → farmers/public/produce
- Cart/Checkout: cart/items (POST) → checkout → payments/checkout-session
- Consumers: dashboard, wishlist add, reviews add, preferences update
- Business: bulk orders, logistics, analytics
- Deliveries: mark delivered (distributor)

## Notes
- Most endpoints require auth; unauthenticated ones are marked with "noauth" in the collection.
- Query parameters: `page`, `page_size`, `search`, `ordering` are commonly supported.
- See live docs at `/api/docs/` or `/api/redoc/` when running the server.
