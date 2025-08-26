## Frontend Integration Guide

### Base setup (fetch/axios)
```javascript
import axios from 'axios';

const api = axios.create({
  baseURL: 'http://127.0.0.1:8000/api/v1/',
  headers: { 'Accept': 'application/json', 'Content-Type': 'application/json' }
});

api.interceptors.request.use((config) => {
  const token = localStorage.getItem('access');
  if (token) config.headers.Authorization = `Bearer ${token}`;
  const requestId = crypto.randomUUID();
  config.headers['X-Request-ID'] = requestId;
  return config;
});

export default api;
```

### JWT auth flow
1. Login: `POST /accounts/jwt/login/` with `{ username, password }` → `{ access, refresh }`
2. Store `access` (short-lived) and `refresh` (longer-lived)
3. Attach `Authorization: Bearer <access>` to requests
4. On 401 due to expiry, refresh: `POST /accounts/jwt/refresh/` with `{ refresh }`

```javascript
async function login(username, password) {
  const { data } = await api.post('/accounts/jwt/login/', { username, password });
  localStorage.setItem('access', data.access);
  localStorage.setItem('refresh', data.refresh);
}

async function refreshAccess() {
  const refresh = localStorage.getItem('refresh');
  if (!refresh) return;
  const { data } = await api.post('/accounts/jwt/refresh/', { refresh });
  localStorage.setItem('access', data.access);
}
```

### Example: list produce with pagination, search, ordering
```javascript
async function listPublicProduce({ page = 1, pageSize = 20, search = '', ordering = '-created_at' } = {}) {
  const params = { page, page_size: pageSize, search, ordering };
  const { data } = await api.get('/farmers/public/produce/', { params });
  // DRF pagination shape: { count, next, previous, results }
  return data;
}
```

### Handling errors
- Error responses include `detail` (string), `code` (string), and `request_id`.
- 400 may include `field_errors` (object of field → [errors]).

```javascript
function toUserMessage(error) {
  if (!error.response) return 'Network error';
  const { status, data } = error.response;
  if (data.field_errors) return 'Please correct highlighted fields.';
  return data.detail || `Request failed (${status})`;
}
```

### Notifications via SSE
EventSource cannot set custom headers; pass `access` (JWT) or `token` (DRF token) as query parameters. Optionally pass `last_id` to resume.

```javascript
function connectNotificationsSSE() {
  const access = localStorage.getItem('access');
  const url = new URL('http://127.0.0.1:8000/api/v1/notifications/stream/');
  if (access) url.searchParams.set('access', access);
  const es = new EventSource(url.toString());
  es.onmessage = (evt) => {
    const payload = JSON.parse(evt.data);
    // handle notification
    console.log('notification', payload);
  };
  es.onerror = () => {
    // reconnect strategy handled by browser; consider exponential backoff on close
  };
  return es;
}
```

### Common tips
- Respect throttle limits: back off on 429; use `errors.md` guidance.
- Prefer server-side filtering/search; avoid fetching massive lists.
- Send `X-Request-ID` to trace requests; surface `request_id` in UI on failures for faster support.
