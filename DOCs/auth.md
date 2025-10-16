## Authentication

### Options
- **JWT (preferred)** via SimpleJWT
- **DRF Token** via authtoken

### Headers
- `Authorization: Bearer <access>` (JWT)
- `Authorization: Token <token>` (DRF token)

### Endpoints (prefix: `/api/v1/accounts/`)
- `POST jwt/login/` → `{ access, refresh }`
- `POST jwt/refresh/` → `{ access }`
- `POST login/` → `{ token }` (DRF token)
- `POST register/` → `{ id, username, email, role, ... }`
- `GET/PATCH me/` → current profile
- `GET verify-email/?uid=...&token=...`
- `POST password-reset-request/` → `{ email }`
- `POST password-reset-confirm/` → `{ uid, token, new_password }`

### Examples
```bash
# JWT login
curl -X POST http://127.0.0.1:8000/api/v1/accounts/jwt/login/ \
  -H 'Content-Type: application/json' \
  -d '{"username":"alice","password":"password123"}'

# JWT refresh
curl -X POST http://127.0.0.1:8000/api/v1/accounts/jwt/refresh/ \
  -H 'Content-Type: application/json' \
  -d '{"refresh":"<REFRESH_TOKEN>"}'

# DRF token login (alternative)
curl -X POST http://127.0.0.1:8000/api/v1/accounts/login/ \
  -H 'Content-Type: application/json' \
  -d '{"username":"alice","password":"password123"}'

# Authenticated request (inventory)
curl http://127.0.0.1:8000/api/v1/inventory/products/?page=1 \
  -H 'Authorization: Bearer <ACCESS>' -H 'Accept: application/json'
```

### Roles
- `FARMER`, `CONSUMER`, `BUSINESS`, `DISTRIBUTOR`, `OTHERS`, plus staff

### Notes
- Most endpoints require authentication and will return `401` if missing/invalid.
- Use JWT for browser apps; keep `refresh` securely, rotate `access` via `jwt/refresh/`.
- For SSE, pass `access` or `token` as a query parameter; see `notifications-sse.md`.
