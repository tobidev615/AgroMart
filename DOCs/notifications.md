## Notifications

- `GET /api/v1/notifications/`
- `PATCH /api/v1/notifications/<id>/`
- `GET /api/v1/notifications/stream/` (SSE)

SSE auth: append `?access=<JWT>` or `?token=<DRF_TOKEN>`.

See `notifications-sse.md` for client example.
