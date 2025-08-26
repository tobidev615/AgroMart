## Pagination

All list endpoints use page-number pagination.

### Query parameters
- `page`: 1-based page number (default: 1)
- `page_size`: items per page (default: 20, max: 100)

### Response shape
```json
{
  "count": 123,
  "next": "http://127.0.0.1:8000/api/v1/resource/?page=3&page_size=20",
  "previous": null,
  "results": [ /* array of items */ ]
}
```

### Client tips
- Use `next` and `previous` URLs when convenient to avoid manual param building.
- Keep `page_size` modest to reduce latency; prefer infinite scroll with `page` increments.
- Combine with `search`, `ordering`, and filter params where supported.
