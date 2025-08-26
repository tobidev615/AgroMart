# Business (Corporate Buyers) API Documentation

This document covers corporate/enterprise purchasing features for restaurants, caterers, hotels, supermarkets, and large buyers.

- Bulk orders with crates/sacks/kg
- Volume-based pricing tiers
- Contract (standing) orders with scheduled deliveries
- Credit terms & invoicing
- Account-manager and support contacts
- Logistics dashboard (orders + deliveries)
- Analytics and reports
- Branding/packaging preferences

All endpoints are prefixed by:
- API v1: `/api/v1/business/`

Authentication: use JWT or Token
- Header: `Authorization: Bearer <access_token>` OR `Authorization: Token <token>`

---

## Profile & Business Types

### Model: BusinessProfile
- `user` (one-to-one)
- `name`, `company`, `business_type` (RESTAURANT, CATERER, HOTEL, SUPERMARKET, LARGE_BUYER), `tax_id`
- Address: `address`, `city`, `country`
- Account manager/support: `account_manager_name`, `account_manager_email`, `account_manager_phone`, `support_whatsapp`, `support_phone`
- Credit: `credit_terms_days` (0=prepaid, 7, 30), `credit_limit`
- Branding: `branding_enabled`, `brand_name`, `packaging_preferences` (JSON)

### Get/Update My Business Profile
GET/PATCH `/api/v1/business/me/`

Request (PATCH):
```http
PATCH /api/v1/business/me/
Authorization: Bearer <token>
Content-Type: application/json

{
  "company": "Blue Harbor Hotel",
  "business_type": "HOTEL",
  "tax_id": "BH-99283",
  "credit_terms_days": 30,
  "credit_limit": "500000.00",
  "branding_enabled": true,
  "brand_name": "Blue Harbor",
  "packaging_preferences": {"tomatoes": {"unit": "crate", "label": "BH"}},
  "account_manager_name": "Chris Daniels",
  "account_manager_email": "chris@agromart.example",
  "account_manager_phone": "+1-555-0109",
  "support_whatsapp": "+1-555-0199"
}
```

Response (200):
```json
{
  "id": 4,
  "user": 21,
  "name": "Blue Harbor",
  "company": "Blue Harbor Hotel",
  "business_type": "HOTEL",
  "tax_id": "BH-99283",
  "address": "",
  "city": "",
  "country": "",
  "account_manager_name": "Chris Daniels",
  "account_manager_email": "chris@agromart.example",
  "account_manager_phone": "+1-555-0109",
  "support_whatsapp": "+1-555-0199",
  "support_phone": "",
  "credit_terms_days": 30,
  "credit_limit": "500000.00",
  "branding_enabled": true,
  "brand_name": "Blue Harbor",
  "packaging_preferences": {"tomatoes": {"unit": "crate", "label": "BH"}},
  "created_at": "2025-01-01T10:00:00Z",
  "updated_at": "2025-01-01T10:05:00Z"
}
```

Permissions: Business users or staff.

---

## Orders & Bulk Ordering

### View My Orders
GET `/api/v1/business/orders/`
- Lists orders for the business user (includes items via prefetch)

Response (200):
```json
{
  "count": 2, "next": null, "previous": null,
  "results": [
    {
      "id": 101,
      "total_amount": "120000.00",
      "status": "PENDING",
      "created_at": "2025-01-02T09:30:00Z",
      "items": [
        {"product_name": "Tomatoes", "unit": "crate", "quantity": 50, "price_per_unit": "2000.00", "subtotal": "100000.00"},
        {"product_name": "Onions", "unit": "sack", "quantity": 10, "price_per_unit": "2000.00", "subtotal": "20000.00"}
      ]
    }
  ]
}
```

### Create a Bulk Order (Volume Pricing)
POST `/api/v1/business/bulk-orders/`

- Units can be any string like `kg`, `crate`, `sack` (aligned with your catalog)
- Pricing tiers are applied automatically (business-specific first, then global)

Request:
```http
POST /api/v1/business/bulk-orders/
Authorization: Bearer <token>
Content-Type: application/json

{
  "items": [
    {"produce_id": 1, "quantity": 50, "unit": "crate"},
    {"produce_id": 7, "quantity": 200, "unit": "kg"}
  ]
}
```

Response (201): standard Order payload
```json
{
  "id": 123,
  "status": "PENDING",
  "total_amount": "345000.00",
  "items": [
    {"product_name": "Tomatoes", "unit": "crate", "quantity": 50, "price_per_unit": "2000.00", "subtotal": "100000.00"},
    {"product_name": "Potatoes", "unit": "kg", "quantity": 200, "price_per_unit": "1225.00", "subtotal": "245000.00"}
  ]
}
```

Errors:
```json
{"detail": "Insufficient stock for Tomatoes", "available": 30}
```

---

## Volume Pricing Tiers (Admin)

Business or global tiers used for discounting by quantity.

Model: BusinessPricingTier
- `business` (nullable = global tier)
- `produce`, `min_quantity`, `unit`, `unit_price`, `active`

Endpoints (admin only):
- GET/POST `/api/v1/business/pricing-tiers/`
- GET/PATCH/DELETE `/api/v1/business/pricing-tiers/<id>/`

Example tier:
```json
{
  "business": null,         // global tier
  "produce": 1,             // Tomatoes
  "min_quantity": 100,
  "unit": "kg",
  "unit_price": "1100.00",
  "active": true
}
```

---

## Contract (Standing) Orders

Create recurring standing orders with frequency and priority.

Model: ContractOrder (+ ContractOrderItem)
- `business`, `name`, `frequency` (WEEKLY|BIWEEKLY|MONTHLY), `next_delivery_date`, `priority`, `is_active`, `notes`
- Items: `produce`, `quantity`, `unit`, `agreed_unit_price`

Endpoints:
- GET/POST `/api/v1/business/contracts/`
- GET/PATCH/DELETE `/api/v1/business/contracts/<id>/`
- POST `/api/v1/business/contracts/run-cycle/` (admin) — processes due contracts: creates Orders + Deliveries and advances `next_delivery_date`

Create request:
```http
POST /api/v1/business/contracts/
Authorization: Bearer <token>
Content-Type: application/json

{
  "name": "Weekly tomatoes",
  "frequency": "WEEKLY",
  "next_delivery_date": "2025-01-06",
  "priority": true,
  "is_active": true,
  "notes": "Priority supply",
  "items": [
    {"produce": 1, "quantity": 50, "unit": "kg", "agreed_unit_price": "1200.00"}
  ]
}
```

Response (201): contract with items

---

## Credit & Invoicing

Invoices are generated per order (integration point for automated issuance). Fields include `payment_terms_days`, `due_date`, `status` (DRAFT|ISSUED|PAID|OVERDUE), `total_amount`, `pdf_path` (WeasyPrint integration).

Endpoints:
- GET `/api/v1/business/invoices/`
- GET `/api/v1/business/invoices/<id>/`

Example (list):
```json
{
  "count": 1, "next": null, "previous": null,
  "results": [
    {
      "id": 55,
      "business": 4,
      "order": 123,
      "payment_terms_days": 30,
      "issued_at": "2025-01-02T10:00:00Z",
      "due_date": "2025-02-01",
      "status": "ISSUED",
      "total_amount": "345000.00",
      "pdf_path": "/media/invoices/invoice-55.pdf"
    }
  ]
}
```

Business profile’s `credit_terms_days` typically informs invoice terms; `due_date` should be set when issuing an invoice.

---

## Logistics Dashboard

GET `/api/v1/business/logistics/`
- Returns current user’s orders and deliveries (basic status view)

Response (200):
```json
{
  "orders": [{"id": 123, "status": "PENDING", "created_at": "2025-01-02T09:30:00Z"}],
  "deliveries": [{"id": 77, "order_id": 123, "status": "PENDING", "scheduled_date": "2025-01-03", "notes": "AM slot"}]
}
```

---

## Analytics & Reports

GET `/api/v1/business/analytics/`
- Totals and top items for the business user

Response (200):
```json
{
  "total_spent": "1234500.00",
  "total_orders": 42,
  "top_items": [
    {"product_name": "Tomatoes", "total_qty": 1200},
    {"product_name": "Onions", "total_qty": 800}
  ]
}
```

Planned extensions:
- Monthly PDF/CSV reports (Celery) to email
- Seasonal price trend charts
- Waste-reduction metrics

---

## Permissions
- Business endpoints: `IsBusinessOrStaff`
- Pricing tiers & contract cycle trigger: `IsAdminUser`

## Rate Limiting
- Uses global DRF throttles (configurable). Recommend custom tiers for bulk/contract endpoints.

## Errors (examples)
- 400 stock/validation: `{ "detail": "Insufficient stock for Tomatoes", "available": 30 }`
- 403 permission: `{ "detail": "You do not have permission to perform this action." }`
- 404 not found: `{ "detail": "Not found." }`

---

## Implementation Notes
- Volume pricing resolution: business-specific tier wins; fallback to global tier; otherwise base `price_per_unit`.
- Units are free-form strings and should correspond to produce’s merchandising (e.g., `kg`, `crate`, `sack`).
- Deliveries are created as placeholders; scheduling/assignment flows live in the `deliveries` app.
- Invoicing integrates with WeasyPrint for PDFs; set `pdf_path` after generation.
- Standing orders advanced by frequency after each run.

## Postman Quickstart (snippets)

- Bulk order
```bash
curl -X POST "$API_BASE/api/v1/business/bulk-orders/" \
 -H "Authorization: Bearer $TOKEN" -H "Content-Type: application/json" \
 -d '{"items":[{"produce_id":1,"quantity":50,"unit":"crate"}]}'
```

- Create contract
```bash
curl -X POST "$API_BASE/api/v1/business/contracts/" \
 -H "Authorization: Bearer $TOKEN" -H "Content-Type: application/json" \
 -d '{"name":"Weekly tomatoes","frequency":"WEEKLY","next_delivery_date":"2025-01-06","priority":true,"is_active":true,"items":[{"produce":1,"quantity":50,"unit":"kg","agreed_unit_price":"1200.00"}]}'
```

- List invoices
```bash
curl -H "Authorization: Bearer $TOKEN" "$API_BASE/api/v1/business/invoices/"
```


