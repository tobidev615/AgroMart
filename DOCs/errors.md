## Error Handling

The API returns structured errors. Always read `code` and display/record `request_id` for support.

### Shape
```json
{
  "detail": "Human-readable message",
  "code": "error_code",
  "request_id": "uuid-...",
  "field_errors": { "field": ["msg", "msg2"] } // present on 400 when relevant
}
```

### Common statuses
- 400 validation: `code=validation_error`, optional `field_errors`
- 401 unauthorized: `code=authentication_failed` or `not_authenticated`
- 403 forbidden: `code=permission_denied`
- 404 not found: `code=not_found`
- 429 rate limited: `code=rate_limit_exceeded`, may include `retry_after`
- 500 server error: `code=server_error`

### Examples
```json
{
  "detail": "Invalid credentials",
  "code": "authentication_failed",
  "request_id": "2c8f..."
}
```

```json
{
  "detail": "Validation error occurred.",
  "code": "validation_error",
  "field_errors": { "email": ["This field is required."] },
  "request_id": "8bf3..."
}
```

### Client guidance
- Surface `detail` to users where appropriate; map `field_errors` to form UI.
- On 401 with expired access token, attempt refresh then retry once.
- On 429, respect backoff and retry after a delay.
- Log `request_id` along with user actions to aid support.