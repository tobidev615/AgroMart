## Notifications – Server-Sent Events (SSE)

Stream real-time notifications to the browser via SSE.

### Endpoint
- `GET /api/v1/notifications/stream/`
- Content-Type: `text/event-stream`

### Auth options (priority)
1. Existing session/header auth if present
2. `?access=<JWT_ACCESS>` query parameter
3. `?token=<DRF_TOKEN>` query parameter

Optional: `?last_id=<int>` to only receive notifications newer than the last processed ID.

### Client example
```javascript
function connectNotificationsSSE() {
  const access = localStorage.getItem('access');
  const url = new URL('http://127.0.0.1:8000/api/v1/notifications/stream/');
  if (access) url.searchParams.set('access', access);
  const es = new EventSource(url.toString());

  es.onmessage = (event) => {
    const notification = JSON.parse(event.data);
    // e.g., show toast, update badge, etc.
  };

  es.onerror = () => {
    // Browser will auto-reconnect; consider closing on auth errors and relogin
  };

  return es;
}
```

### Notes
- Browsers do not allow custom headers in EventSource; use query param auth above.
- The backend batches newly created notifications every second for the connected user.
- For production, consider exponential backoff and handling of 401 events in `onerror`.
