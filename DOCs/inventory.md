## Inventory (Catalog)

Public, read-only catalog endpoints for categories, products, and variants.

### Endpoints
- `GET /api/v1/inventory/categories/`
- `GET /api/v1/inventory/products/`
- `GET /api/v1/inventory/variants/`

### Query params
- Common: `page`, `page_size`, `search`, `ordering`
- Products filters: `category`, `category__slug`
- Variants filters: `product`, `product__slug`, `sku`

### Examples
```bash
# List categories
curl "http://127.0.0.1:8000/api/v1/inventory/categories/?ordering=name"

# Search products
curl "http://127.0.0.1:8000/api/v1/inventory/products/?search=tomato"

# Filter variants by SKU
curl "http://127.0.0.1:8000/api/v1/inventory/variants/?sku=SKU-123"
```
