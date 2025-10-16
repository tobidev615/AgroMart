## Orders & Cart

### Endpoints
- `GET|POST|PUT|DELETE /api/v1/cart/`
- `GET|POST|PATCH|DELETE /api/v1/cart/items/`
- `GET|PATCH|DELETE /api/v1/cart/items/<id>/`
- `POST /api/v1/checkout/`
- `GET /api/v1/orders/`
- `GET /api/v1/orders/<id>/`

### Examples
```bash
# Add to cart
curl -X POST -H "Authorization: Bearer <ACCESS>" -H "Content-Type: application/json" \
  -d '{"produce_id": 10, "quantity": 2}' \
  http://127.0.0.1:8000/api/v1/cart/items/

# Checkout
curl -X POST -H "Authorization: Bearer <ACCESS>" \
  http://127.0.0.1:8000/api/v1/checkout/
```
