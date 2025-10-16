## FarmFresh API – Frontend Documentation

This guide is for frontend developers integrating with the FarmFresh Django REST API.

- **Base URL (dev)**: `http://127.0.0.1:8000`
- **API version prefix**: Prefer `'/api/v1/'`. Legacy `'/api/'` routes are deprecated; use v1.
- **OpenAPI**: `GET /api/schema/` (JSON), `GET /api/docs/` (Swagger UI), `GET /api/redoc/` (Redoc)
- **Auth**: JWT or DRF Token. Prefer JWT. See `auth.md`.
- **Headers**: `Authorization: Bearer <access>` or `Token <token>`, `Content-Type: application/json`, `Accept: application/json`, optional `X-Request-ID: <uuid>`.
- **Pagination**: Page-number pagination with `page` and `page_size`. See `pagination.md`.
- **Errors**: Consistent error shape with `detail`, `code`, and `request_id`. See `errors.md`.
- **Notifications**: Server-Sent Events stream. See `notifications-sse.md`.
- **Rate limits**: 100/hour (anonymous), 1000/hour (authenticated).

### Navigation
- Auth: `auth.md`
- Endpoints overview: `api-endpoints.md`
- Error handling: `errors.md`
- Pagination: `pagination.md`
- Notifications (SSE): `notifications-sse.md`
- Environment, CORS and CSRF: `environment.md`
- Postman collection: `postman/README.md`

### Quick facts
- Default page size is 20; `?page_size=` up to 100.
- Most endpoints require authentication and return 401 if missing/invalid.
- Include an `X-Request-ID` header to correlate frontend requests with backend logs; the API echoes it back.
- Use `/api/v1/…` routes only; legacy `/api/…` is kept for backward compatibility but not documented.
