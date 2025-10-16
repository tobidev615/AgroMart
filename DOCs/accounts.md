## Accounts & Authentication

Use JWT (preferred) or DRF Token.

### Endpoints (prefix: `/api/v1/accounts/`)
- `POST jwt/login/` → `{ access, refresh }`
- `POST jwt/refresh/` → `{ access }`
- `POST login/` → `{ token }` (DRF token)
- `POST register/` → creates user and profile
- `GET|PATCH me/` → current profile
- `GET verify-email/?uid=...&token=...`
- `POST password-reset-request/`
- `POST password-reset-confirm/`

### Headers
- `Authorization: Bearer <access>` (JWT)
- `Authorization: Token <token>` (DRF token)

### Notes
- Most endpoints require auth
- Prefer JWT for browser apps; refresh short‑lived access tokens
