## Environment, CORS, and Local Run

### Local dev API
- Base URL: `http://127.0.0.1:8000`
- Start: `python manage.py runserver`
- Health: `GET /api/health/`

### CORS & CSRF
- Dev default: `CORS_ALLOW_ALL_ORIGINS=true` (open CORS)
- Production: configure `CORS_ALLOWED_ORIGINS=[...]` and `CSRF_TRUSTED_ORIGINS=[...]`
- For browser apps using JWT, CSRF is not enforced on pure token auth; still use HTTPS and secure storage.

### Headers to send
- `Authorization: Bearer <access>`
- `Accept: application/json`
- `Content-Type: application/json`
- Optional: `X-Request-ID: <uuid>` for traceability

### Rate limits
- Anonymous: 100/hour
- Authenticated: 1000/hour

### Pagination defaults
- `page_size`: 20 (max 100) via `?page_size=`

### Useful endpoints
- OpenAPI JSON: `/api/schema/`
- Swagger UI: `/api/docs/`
- Redoc: `/api/redoc/`
