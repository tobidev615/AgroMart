# FarmFresh REST API

A comprehensive Django REST API for farm management, order processing, and delivery coordination.

## Quick Start

```bash
# Create virtual environment
python -m venv farmfresh_env
source farmfresh_env/bin/activate  # On Windows: farmfresh_env\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Set up environment variables
cp .env.example .env
# Edit .env with your settings

# Run migrations
python manage.py migrate

# Seed demo data
# Option A: Seed EVERYTHING (users, profiles, produce, orders, deliveries, subscriptions, etc.)
python manage.py seed_all
# Option B: Only seed subscription plans
python manage.py seed_plans

# Start development server
python manage.py runserver
```

## Authentication
- Token-based or JWT.
- Include header: `Authorization: Token <token>` or `Authorization: Bearer <access>`
- Obtain token/JWT via endpoints below.

## Global Pagination
- All list endpoints use `PageNumberPagination`
- Default: 20 items per page
- Customizable via `?page_size=<number>` (max 100)

## API Endpoints

### Accounts (`userprofiles`)

**Endpoints**
- POST `'/api/accounts/register/'` → `{ username, email, password, first_name, last_name, role }`
- POST `'/api/accounts/login/'` (DRF authtoken) → `{ "token": "..." }`
- POST `'/api/accounts/jwt/login/'` (SimpleJWT) → `{ "access": "...", "refresh": "..." }`
- POST `'/api/accounts/jwt/refresh/'` (SimpleJWT) → `{ "access": "..." }`
- GET/PATCH `'/api/accounts/me/'` → returns/updates current user's profile
- GET `'/api/accounts/verify-email/?uid=...&token=...'` → verify user email
- POST `'/api/accounts/password-reset-request/'` → `{ email }` (always 200)
- POST `'/api/accounts/password-reset-confirm/'` → `{ uid, token, new_password }`

**Validation**
- Role is enforced via choices: sending invalid role returns `400` with `{"role": ["... is not a valid choice."]}`.
- `email_verified` added to profile and set via verification link.

**User Types**
- `FARMER`: Can manage farm profiles and produce
- `CONSUMER`: Can place orders, manage subscriptions, and use consumer features
- `BUSINESS`: Business-specific features
- `DISTRIBUTOR`: Delivery coordination
- `OTHERS`: Basic access

### Farmers (`farmers`)

**Models**
- `FarmerProfile`: Extended user profile for farmers
- `FarmCluster`: Group of farmers working together
- `Produce`: Products offered by farmers

**Endpoints**
- GET/POST/PUT/PATCH/DELETE `'/api/farmers/me/'` → manage own farmer profile
- GET/POST/PUT/PATCH/DELETE `'/api/farmers/produce/'` → manage own produce
- GET `'/api/farmers/public/produce/'` → browse all available produce (public)
- GET `'/api/farmers/public/produce/<id>/'` → view specific produce (public)
- GET/POST/PUT/PATCH/DELETE `'/api/farmers/clusters/'` → manage farm clusters

**Permissions**
- Farmers can only manage their own profiles and produce
- Staff can manage all farmer data
- Public produce browsing is open to all

**Features**
- Search and filter produce by name, variety, farmer, location
- Order by price, date, name
- Stock validation and automatic availability updates

### Consumers (`consumers`)

**Models**
- `ConsumerProfile`: Extended profile for consumers with preferences and analytics
- `ConsumerWishlist`: Wishlist items for consumers
- `ConsumerReview`: Reviews and ratings for produce
- `ConsumerAnalytics`: Detailed analytics for consumer behavior
- `ConsumerPreference`: Detailed preferences for consumers

**Endpoints**
- GET/PATCH `'/api/consumers/me/'` → manage consumer profile
- GET `'/api/consumers/dashboard/'` → comprehensive consumer dashboard
- GET/POST/PUT/PATCH/DELETE `'/api/consumers/wishlist/'` → manage wishlist
- GET/POST/PUT/PATCH/DELETE `'/api/consumers/reviews/'` → manage reviews
- GET `'/api/consumers/analytics/'` → view consumer analytics
- GET/PATCH `'/api/consumers/preferences/'` → manage preferences
- POST `'/api/consumers/favorites/toggle-farmer/'` → manage favorite farmers
- GET `'/api/consumers/recommendations/'` → get personalized recommendations
- GET `'/api/consumers/order-history/'` → view detailed order history

**Features**
- Comprehensive consumer profile with delivery and dietary preferences
- Wishlist functionality with availability tracking
- Review and rating system with verified purchase badges
- Detailed analytics including spending patterns and preferences
- Personalized recommendations based on order history
- Favorite farmers management
- Order history with statistics
- Preference management for produce types, quantities, and notifications

**Permissions**
- Consumers can only manage their own profiles, wishlists, and reviews
- Staff can manage all consumer data
- Automatic profile creation for users with CONSUMER role

### Orders (`orders`)

**Models**
- `Cart`: Shopping cart for users
- `CartItem`: Items in cart
- `Order`: Completed orders
- `OrderItem`: Items in orders

**Endpoints**
- GET/POST/PUT/PATCH/DELETE `'/api/cart/'` → manage cart
- GET/POST/PUT/PATCH/DELETE `'/api/cart/items/'` → manage cart items
- POST `'/api/checkout/'` → convert cart to order
- GET/PUT/PATCH `'/api/orders/'` → view/update own orders
- GET `'/api/farmers/orders/'` → farmers view orders containing their produce

**Order Status**
- `PENDING`: Order placed, awaiting confirmation
- `CONFIRMED`: Order confirmed by farmer
- `DELIVERED`: Order delivered to customer

**Features**
- Automatic stock deduction on checkout
- Produce marked unavailable when stock hits zero
- Order history for farmers and consumers
- Validation prevents over-ordering

### Subscriptions (`subscriptions`)

**Models**
- `SubscriptionPlan`: Available subscription plans
- `Subscription`: User's active subscriptions
- `SubscriptionItem`: Items in subscriptions

**Endpoints**
- GET `'/api/subscriptions/plans/'` → view available plans
- GET/POST `'/api/subscriptions/'` → manage user subscriptions
- GET `'/api/subscriptions/suggestions/'` → get personalized suggestions
- POST `'/api/subscriptions/run-cycle/'` → staff-only, process subscription cycles

**Features**
- Weekly/monthly billing periods
- Auto-suggestions based on order history
- Background processing with Celery
- Default plans seeded automatically

### Notifications (`notifications`)

**Models**
- `Notification`: In-app notifications

**Endpoints**
- GET `'/api/notifications/'` → list user notifications
- PATCH `'/api/notifications/<id>/'` → mark as read
- GET `'/api/notifications/stream/'` → Server-Sent Events stream

**Features**
- Real-time notifications via SSE
- Email and SMS integration (Twilio)
- Automatic notifications for:
  - Order status changes
  - New produce availability
  - Subscription reminders
- Daily/weekly digest emails

### Business (`business`)

See full guide: documentation_examples/BUSINESS.md

**Models**
- `BusinessProfile`: Corporate buyer profile with type, credit terms, branding/packaging, account manager/support contacts
- `BusinessPricingTier`: Global or per-business volume pricing by unit and min quantity
- `ContractOrder` + `ContractOrderItem`: Standing/recurring orders with frequency and priority
- `BusinessInvoice`: Per-order invoice with payment terms, due date, status, PDF path

**Key Endpoints (prefix: `/api/v1/business/`)**
- Profile: GET/PATCH `me/`
- My orders: GET `orders/`
- Bulk orders: POST `bulk-orders/`
- Pricing tiers (admin): GET/POST `pricing-tiers/`, GET/PATCH/DELETE `pricing-tiers/<id>/`
- Contracts: GET/POST `contracts/`, GET/PATCH/DELETE `contracts/<id>/`, POST `contracts/run-cycle/` (admin)
- Invoices: GET `invoices/`, GET `invoices/<id>/`
- Logistics dashboard: GET `logistics/`
- Analytics: GET `analytics/`

**Features**
- Bulk ordering in crates/sacks/kg with automatic volume-based pricing
- Standing orders with scheduled deliveries and priority supply
- Credit terms and downloadable invoices (PDF integration)
- Dedicated account manager + WhatsApp/phone support fields
- Logistics snapshot (orders + deliveries) and purchase analytics

**Permissions**
- Business endpoints: authenticated users with role `BUSINESS` or staff
- Pricing tiers and run-cycle: admin only

### Distributors (`distributors`)

**Models**
- `DistributorProfile`: Extended profile for distributors

**Endpoints**
- GET/POST/PUT/PATCH/DELETE `'/api/distributors/me/'` → manage distributor profile

**Permissions**
- Distributors can only manage their own profiles
- Staff can manage all distributor data

### Deliveries (`deliveries`)

**Models**
- `Delivery`: Delivery records with status tracking

**Endpoints**
- GET/PUT/PATCH `'/api/deliveries/'` → view/update deliveries
- GET `'/api/deliveries/assigned/'` → distributors view assigned deliveries
- POST `'/api/deliveries/<id>/mark-delivered/'` → mark delivery as complete

**Delivery Status**
- `PENDING`: Delivery created
- `SCHEDULED`: Delivery scheduled
- `OUT_FOR_DELIVERY`: En route to customer
- `DELIVERED`: Successfully delivered

**Permissions**
- Distributors see only their assigned deliveries
- Distributors can update status and notes
- Staff can manage all deliveries

### Deliveries – implementation notes
- Permissions:
  - Staff: full access to all deliveries
  - Distributor: only deliveries assigned to them; can update only `status` and `notes`
  - Customer: only deliveries for their own orders; read-only
- Query optimization:
  - Uses `select_related("order", "order__user", "distributor", "distributor__user")` across list/detail views
  - Filters distributors with `distributor__user=<request.user>`
- Status flow: `PENDING` → `SCHEDULED` → `OUT_FOR_DELIVERY` → `DELIVERED`
- Endpoints:
  - GET `/api/deliveries/assigned/` (distributor): only `OUT_FOR_DELIVERY`
  - POST `/api/deliveries/<id>/mark-delivered/` (distributor or staff)

Examples
```bash
# Distributor: list assigned and out-for-delivery
curl -H "Authorization: Bearer <ACCESS>" \
  http://127.0.0.1:8000/api/deliveries/assigned/

# Distributor: mark delivered
curl -X POST -H "Authorization: Bearer <ACCESS>" \
  http://127.0.0.1:8000/api/deliveries/123/mark-delivered/
```

### Orders – implementation notes
- Totals: all endpoints use `total_amount` (not `total_price`).
- Validation: prevents empty cart, negative/zero quantities, and ordering beyond stock.
- Stock handling: decrements `quantity_available`; auto-sets `available=false` when stock hits 0.
- Query optimization: `select_related('user')` and `prefetch_related('items', 'items__produce', 'items__produce__farmer')`.
- Delivery linkage: a `Delivery` record is created (if missing) on checkout and on order confirmation.

### Readiness – implementation notes
- Health: `GET /api/health/` returns `{ status: 'ok' }`.
- Readiness: `GET /api/readiness/` checks database, cache, and Redis.
- Redis target: uses `settings.CELERY_BROKER_URL` (no hardcoded URL).
- Response: `200` healthy, `503` if any check fails.

### Logging – implementation notes
- Structured logs to console and `logs/app.log` with timestamps.
- Request ID propagation via `RequestIdMiddleware` and `RequestIdFilter`.
- Header: send `X-Request-ID: <uuid>` to trace a request across logs; response echoes `X-Request-ID`.
- Format includes `request_id` for easier correlation.

## Observability & Reliability

### Health & Readiness Probes
- `GET /api/health/` → Basic health check
- `GET /api/readiness/` → Comprehensive readiness check (database, cache, Redis)

### Structured Logging
- Console and file logging
- Request IDs for tracing
- Structured format with timestamps
- Log files in `logs/app.log`

### Error Tracking (Sentry)
- Automatic error capture and reporting
- Performance monitoring
- Environment-specific configuration
- Set `SENTRY_DSN` in environment

### Background Jobs (Celery + Redis)
- Asynchronous notification sending
- Subscription cycle processing
- Digest email generation
- Scheduled tasks with Celery Beat

## Security & Limits

### HTTPS & Security Headers
- `SECURE_SSL_REDIRECT`: Force HTTPS in production
- `SECURE_HSTS_SECONDS`: HTTP Strict Transport Security
- `SECURE_CONTENT_TYPE_NOSNIFF`: Prevent MIME sniffing
- `SECURE_BROWSER_XSS_FILTER`: XSS protection
- `X_FRAME_OPTIONS`: Clickjacking protection

### Rate Limiting
- Anonymous users: 100 requests/hour
- Authenticated users: 1000 requests/hour
- Configurable via `DEFAULT_THROTTLE_RATES`

### CORS Configuration
- `CORS_ALLOW_ALL_ORIGINS`: Development only
- `CORS_ALLOWED_ORIGINS`: Production whitelist
- `CSRF_TRUSTED_ORIGINS`: CSRF protection

### Secret Management
- Environment variables for all secrets
- `.env` file for local development
- Production secrets via environment

## Data & Performance

### Database Indexes
- **Orders**: `status`, `created_at`, `user+status`
- **Produce**: `available`, `created_at`, `farmer+available`
- **Deliveries**: `status`, `distributor`, `scheduled_date`, `distributor+status`

### Query Optimization
- `select_related()` for foreign key relationships
- `prefetch_related()` for many-to-many relationships
- Optimized querysets in all ViewSets

### Filtering & Search
- Django Filter backend for complex filtering
- Search across multiple fields
- Ordering by any field
- Public produce browsing with advanced filters

### Seed Data
- Full demo dataset: `python manage.py seed_all` (idempotent)
  - Creates: staff, farmers, consumers, business, distributor; farmer/distributor/business profiles; produce inventory; orders + items; deliveries; payments; notifications; subscriptions; pricing tiers; business contracts + invoices
  - Default credentials:
    - Staff: `staff / password123`
    - Farmers: `farmer_ada / password123`, `farmer_kofi / password123`
    - Consumers: `alice / password123`, `bob / password123`
    - Business: `resto_one / password123`
    - Distributor: `distro_max / password123`
- Only subscription plans: `python manage.py seed_plans`

## Project Structure

```
farmfresh-restapi/
├── farmfresh/              # Main project settings
├── api/                    # Health/readiness endpoints
├── userprofiles/           # User management & auth
├── farmers/               # Farmer profiles & produce
├── consumers/             # Consumer profiles & features
├── orders/                # Cart & order management
├── subscriptions/          # Subscription system
├── notifications/          # Notification system
├── business/              # Business user features
├── distributors/          # Distributor features
├── deliveries/            # Delivery coordination
├── logs/                  # Application logs
└── requirements.txt       # Dependencies
```

## Roles & Permissions Summary

| Role | Can Access | Can Edit | Special Features |
|------|------------|----------|------------------|
| **Farmer** | Own profile/produce | Own profile/produce | Order history for their produce |
| **Consumer** | Own orders/cart, profile, wishlist, reviews | Own orders/cart, profile, wishlist, reviews | Place orders, manage subscriptions, wishlist, reviews, analytics |
| **Business** | Own profile/orders | Own profile | Bulk ordering capabilities |
| **Distributor** | Own profile, assigned deliveries | Own profile, delivery status | Update delivery status |
| **Staff** | All data | All data | Admin access, run subscription cycles |
| **Anonymous** | Public produce browsing | None | Browse available produce |

## Error Responses

```json
{
  "detail": "Error message",
  "field_name": ["Field-specific error"],
  "non_field_errors": ["General form errors"]
}
```

Common HTTP status codes:
- `200`: Success
- `201`: Created
- `400`: Bad Request (validation errors)
- `401`: Unauthorized (missing/invalid token)
- `403`: Forbidden (insufficient permissions)
- `404`: Not Found
- `429`: Too Many Requests (rate limited)
- `503`: Service Unavailable (readiness check failed)

## Realtime Notifications (SSE)

Frontend example for Server-Sent Events:

```javascript
const eventSource = new EventSource('/api/notifications/stream/?last_id=0');

eventSource.onmessage = function(event) {
    const notification = JSON.parse(event.data);
    console.log('New notification:', notification);
};

eventSource.onerror = function(error) {
    console.error('SSE error:', error);
    eventSource.close();
};
```

## API Base URL

- Development: `http://localhost:8000/api/`
- Production: Configure via environment variables

## Useful Commands

```bash
# Database
python manage.py makemigrations
python manage.py migrate
python manage.py seed_all
python manage.py seed_plans

# Development
python manage.py runserver
python manage.py check

# Background tasks
celery -A farmfresh worker --loglevel=info
celery -A farmfresh beat --loglevel=info

# Logs
tail -f logs/app.log

# Health checks
curl http://localhost:8000/api/health/
curl http://localhost:8000/api/readiness/
```

## Environment Variables

Required environment variables (see `.env.example`):
- `DEBUG`: Development mode
- `SECRET_KEY`: Django secret key
- `DATABASE_URL`: Database connection
- `CELERY_BROKER_URL`: Redis connection
- `SENTRY_DSN`: Error tracking (optional)
- `TWILIO_ACCOUNT_SID`: SMS notifications (optional)
- `TWILIO_AUTH_TOKEN`: SMS notifications (optional)
- `TWILIO_FROM_NUMBER`: SMS notifications (optional)
- `EMAIL_HOST`: Email configuration
- `EMAIL_PORT`: Email configuration
- `EMAIL_HOST_USER`: Email configuration
- `EMAIL_HOST_PASSWORD`: Email configuration

## Performance Monitoring

- Database query optimization with indexes
- Redis caching for session and Celery
- Background task processing
- Rate limiting to prevent abuse
- Structured logging for debugging
- Health checks for monitoring

## Security Features

- JWT and token authentication
- Role-based access control
- Input validation and sanitization
- Rate limiting and throttling
- HTTPS enforcement in production
- Security headers configuration
- CORS protection
- CSRF protection

This API provides a complete farm management system with real-time notifications, secure authentication, comprehensive logging, and performance optimizations for production deployment.

### Payments & Invoicing (payments)
- Provider: Stripe Checkout
- Env vars: `STRIPE_API_KEY`, `STRIPE_WEBHOOK_SECRET`
- Flow:
  1) Client requests checkout session
  2) User pays on Stripe-hosted page
  3) Webhook confirms payment, marks Payment as SUCCEEDED, generates PDF invoice
- Endpoints
  - POST `/api/payments/checkout-session/` → `{ order_id }` → `{ checkout_session_id, checkout_url }`
  - POST `/api/payments/stripe/webhook/` (Stripe calls this)
- Models
  - `Payment(user, order, amount, currency, provider_payment_id, status)`
  - `Invoice(user, order, file)` (PDF under `MEDIA_URL/invoices/`)

Example (create checkout session)
```bash
curl -X POST -H "Authorization: Bearer <ACCESS>" -H "Content-Type: application/json" \
  -d '{"order_id": 123}' http://127.0.0.1:8000/api/payments/checkout-session/
```

### Produce Images & CDN
- Field: `Produce.image` (optional)
- Upload method: multipart form with `image` on create/update of produce
- Dev serving: `/media/` (Django) → added via `static()`
- Production (optional): S3 with `django-storages`
  - Env: `USE_S3=true`, `AWS_ACCESS_KEY_ID`, `AWS_SECRET_ACCESS_KEY`, `AWS_STORAGE_BUCKET_NAME`, `AWS_S3_REGION_NAME`

Example (upload/update)
```bash
curl -X PATCH -H "Authorization: Bearer <ACCESS>" \
  -F image=@/path/to/picture.jpg \
  http://127.0.0.1:8000/api/farmers/produce/1/
```

### Audit Trails, Webhooks & Analytics (audit)
- `AuditLog` captures key changes via signals:
  - Order status changes → `order.status.changed`
  - Delivery status changes → `delivery.status.changed`
- Extensible:
  - Add outbound webhooks on these events (sign payloads, retry/backoff)
  - Emit analytics events to PostHog/Segment from the same signal hooks

### i18n & Timezone
- i18n enabled (`LocaleMiddleware`); default language: English
- Timezone: UTC by default; recommend storing per-user `timezone` on profile and activating per-request
- To add localized strings: wrap user-facing text with Django i18n (`gettext`)

### Postman / Insomnia Collection
- Export OpenAPI schema and import:
  - Schema: `GET /api/schema/`
  - Swagger UI: `GET /api/docs/`
  - Redoc: `GET /api/redoc/`
- Most API clients can import the JSON from `/api/schema/` directly

## CI – Continuous Integration (GitHub Actions)
- Tests run automatically on every push and pull request.
- Workflow file: `.github/workflows/ci.yml`
- Pipeline steps: install deps, Django check, run pytest with coverage, upload coverage artifact.

## Docker & Compose – How to run

Build and run the API + Redis + Celery worker/beat:
```bash
docker compose up --build
```
- App: http://localhost:8000/
- Redis: internal to the network
- Celery worker/beat: background processing and schedules

Environment (override with a `.env` file or inline):
- `SECRET_KEY` (required)
- `ALLOWED_HOSTS` (e.g., `example.com,localhost`)
- `CELERY_BROKER_URL` / `CELERY_RESULT_BACKEND` (set for Redis in compose)
- `SENTRY_DSN` (optional)

Production notes:
- Put a reverse proxy (Nginx/Traefik) in front of the app container for HTTPS/HTTP2.
- Configure database (Postgres) and update `DATABASES` in settings via env.
- Enable `SECURE_SSL_REDIRECT` and HSTS env toggles.
- Add a backup job (e.g., `pg_dump` to S3) in your infrastructure or as a scheduled container.

## Testing
- See `TESTREADME.md` for a non‑coder friendly step‑by‑step guide.
- Quick start:
  ```bash
  pip install -r requirements.txt -r requirements-dev.txt
  pytest -q
  ```

## Database (production vs. testing)
- Default (dev/testing): sqlite at `db.sqlite3` (no extra setup needed)
- Production: set `DATABASE_URL` for MySQL, example:
  ```
  DATABASE_URL=mysql://dbuser:dbpass@dbhost:3306/agromart
  ```
- Requirements: `mysqlclient` installed (already in requirements.txt)
- If using Docker Compose with MySQL, uncomment the example service in `docker-compose.yml` and set `DATABASE_URL` to point at it (e.g., `mysql://farm:secret@mysql:3306/agromart`).

## Frontend Integration (React/JS)
- CORS: set `CORS_ALLOWED_ORIGINS=http://localhost:3000` (and your prod URLs)
- Auth (recommended): JWT
  - Login: POST `/api/accounts/jwt/login/` → `{ access, refresh }`
  - Refresh: POST `/api/accounts/jwt/refresh/` → `{ access }`
  - Send: `Authorization: Bearer <access>` header
- SSE (notifications):
  - If you use cookies/session, EventSource works with same-origin
  - If you use JWT, you can append `?access=<JWT>` or `?token=<DRF_TOKEN>` to `/api/notifications/stream/`

Example (axios client)
```js
import axios from 'axios';

const api = axios.create({ baseURL: 'http://localhost:8000/api' });

export async function login(username, password) {
  const { data } = await api.post('/accounts/jwt/login/', { username, password });
  api.defaults.headers.common.Authorization = `Bearer ${data.access}`;
  return data;
}

export async function getProfile() {
  const { data } = await api.get('/accounts/me/');
  return data;
}

export function openNotificationsSSE(access) {
  const url = `http://localhost:8000/api/notifications/stream/?last_id=0&access=${access}`;
  const es = new EventSource(url);
  es.onmessage = (evt) => console.log('notification:', JSON.parse(evt.data));
  es.onerror = (e) => console.error('sse error', e);
  return es;
}
```

## Environment (.env.example)
Copy these into a `.env` file and adjust for your environment:

```env
# Core
DEBUG=True
SECRET_KEY=change-me
ALLOWED_HOSTS=localhost,127.0.0.1

# Database (prod)
# DATABASE_URL=mysql://user:password@mysql:3306/farmfresh

# CORS/CSRF
CORS_ALLOW_ALL_ORIGINS=False
CORS_ALLOWED_ORIGINS=http://localhost:3000
CSRF_TRUSTED_ORIGINS=http://localhost:8000

# Email
EMAIL_BACKEND=django.core.mail.backends.console.EmailBackend
EMAIL_HOST=
EMAIL_PORT=587
EMAIL_HOST_USER=
EMAIL_HOST_PASSWORD=
EMAIL_USE_TLS=True
DEFAULT_FROM_EMAIL=no-reply@farmfresh.local

# Celery/Redis
CELERY_BROKER_URL=redis://redis:6379/0
CELERY_RESULT_BACKEND=redis://redis:6379/1

# Sentry
SENTRY_DSN=
SENTRY_TRACES_SAMPLE_RATE=0.1
SENTRY_ENVIRONMENT=development

# Storage (S3 optional)
USE_S3=False
AWS_ACCESS_KEY_ID=
AWS_SECRET_ACCESS_KEY=
AWS_STORAGE_BUCKET_NAME=
AWS_S3_REGION_NAME=

# Stripe
STRIPE_API_KEY=
STRIPE_WEBHOOK_SECRET=

# Twilio
TWILIO_ACCOUNT_SID=
TWILIO_AUTH_TOKEN=
TWILIO_FROM_NUMBER=
```

### Production notes
- Set `DEBUG=False`, strong `SECRET_KEY`, and `ALLOWED_HOSTS` to your domains
- Set `SECURE_SSL_REDIRECT=True`, `SESSION_COOKIE_SECURE=True`, `CSRF_COOKIE_SECURE=True`, and HSTS values
- Provide `DATABASE_URL` for MySQL
- Lock down `CORS_ALLOWED_ORIGINS` to your frontend domains
- Configure email backend (SMTP) and Sentry DSN

## Deploy (docker-compose)

```bash
# 1) Copy .env.example to .env and set values
cp .env.example .env  # or create .env with the values above

# 2) Start services
export DATABASE_URL="mysql://farm:secret@mysql:3306/agromart"
docker compose up -d --build

# 3) Run migrations and seed
docker compose exec app python manage.py migrate
docker compose exec app python manage.py seed_all
docker compose exec app python manage.py seed_plans

# 4) Check health
curl http://localhost/api/health/
curl http://localhost/api/readiness/
```

Nginx listens on port 80 and proxies to the Django `app` container.

### MySQL (production)
- Ensure `mysqlclient` system deps are available (Dockerfile already installs them)
- Example `DATABASE_URL`: `mysql://farm:secret@mysql:3306/agromart`
- For managed cloud DBs, use SSL params as needed, e.g. `?ssl-mode=REQUIRED`

### Reverse proxy (nginx)
- Included `deploy/nginx.conf` proxies to `app:8000`, adds basic security headers and gzip
- Put nginx in front of Django and terminate TLS at nginx in production

## Production hardening (Phase 1)

- Security defaults
  - `SECURE_PROXY_SSL_HEADER` enabled; when `DEBUG=False`, secure cookies and HSTS are enforced
  - Lock down `CORS_ALLOWED_ORIGINS` and set `ALLOWED_HOSTS`
- Environment configuration
  - `.env` template provided in this README under "Environment (.env.example)"
  - Set `DATABASE_URL` for MySQL in production
- Docker & runtime
  - Hardened `Dockerfile`: non-root user, `collectstatic`, healthcheck, mysqlclient deps
  - Compose includes `nginx` reverse proxy and `mysql` service
  - Nginx config: `deploy/nginx.conf` (gzip + security headers)
- Static files
  - `STATIC_URL=/static/` and `STATIC_ROOT=staticfiles` for `collectstatic`
- Health/readiness
  - `/api/health/` basic liveness; `/api/readiness/` checks DB/cache/Redis
  - Example:
    ```bash
    curl http://localhost/api/health/
    curl http://localhost/api/readiness/
    ```
- Start (production-like via compose)
  - See "Deploy (docker-compose)" section for step-by-step commands

Notes
- For TLS in production, terminate HTTPS at nginx and set `SECURE_SSL_REDIRECT=True`
- Ensure strong `SECRET_KEY`, `DEBUG=False`, and restricted `ALLOWED_HOSTS`

## Professional Standards (Phase 2A)

### Code Quality Tools
- **Linting**: `flake8` with 88-char line length, `black` for formatting
- **Type Checking**: `mypy` with strict settings and type hints throughout
- **Pre-commit Hooks**: Automated code quality checks on commit
- **Security Scanning**: `bandit` for security vulnerabilities, `safety` for dependency checks

### Advanced Security
- **Input Sanitization**: Middleware to prevent XSS and injection attacks
- **SQL Injection Protection**: Pattern-based detection beyond Django ORM
- **Advanced Rate Limiting**: Per-endpoint rate limits (register: 5/hour, login: 10/hour)
- **Security Headers**: Comprehensive CSP, XSS protection, clickjacking prevention

### API Versioning
- **Current**: `/api/v1/` for all endpoints
- **Legacy Support**: `/api/` endpoints still work
- **Future**: Easy migration path to `/api/v2/`

### Caching Layer
- **Redis Caching**: View-level caching with automatic invalidation
- **Cache Keys**: Structured keys for produce lists, user profiles, subscriptions
- **Cache Management**: Utilities for cache invalidation and pattern-based clearing

### Comprehensive Testing
- **Test Coverage**: 80%+ coverage with 25+ test cases
- **Integration Tests**: Full order → payment → delivery workflows
- **Security Tests**: Rate limiting, input sanitization, permission checks
- **Error Handling**: Custom exception handlers with structured logging

### Error Handling & Logging
- **Custom Exceptions**: `FarmFreshException`, `ValidationError`, `RateLimitExceededError`
- **Structured Logging**: Request IDs, error codes, detailed context
- **Exception Handler**: Consistent error responses with request tracing

### Documentation
- **Comprehensive API Docs**: Complete with examples, error responses, rate limits
- **Authentication Flow**: JWT and Token authentication diagrams
- **SDK Examples**: JavaScript/TypeScript and Python client examples
- **Testing Guide**: Step-by-step testing instructions for non-coders

### Usage Examples

**Code Quality:**
```bash
# Format code
black .

# Lint code
flake8 .

# Type check
mypy .

# Security scan
bandit -r .
safety check
```

**Testing:**
```bash
# Run all tests
pytest -q

# Run with coverage
pytest --cov=. --cov-report=term-missing

# Run specific test categories
pytest tests/test_comprehensive.py::TestAuthentication -v
pytest tests/test_comprehensive.py::TestSecurity -v
```

**API Usage:**
```bash
# Health check
curl http://localhost:8000/api/v1/health/

# Register user
curl -X POST http://localhost:8000/api/v1/accounts/register/ \
  -H "Content-Type: application/json" \
  -d '{"username": "farmer", "password": "pass123", "role": "FARMER"}'

# Login with JWT
curl -X POST http://localhost:8000/api/v1/accounts/jwt/login/ \
  -H "Content-Type: application/json" \
  -d '{"username": "farmer", "password": "pass123"}'
```

### Configuration Files
- **`.pre-commit-config.yaml`**: Automated code quality checks
- **`pyproject.toml`**: Black, mypy, flake8 configuration
- **`requirements-dev.txt`**: Development and testing dependencies
- **`farmfresh/middleware.py`**: Security and rate limiting middleware
- **`farmfresh/cache.py`**: Caching utilities and decorators
- **`farmfresh/exceptions.py`**: Custom exception handlers

### Security Features
- **Input Sanitization**: Automatic XSS and injection prevention
- **Rate Limiting**: Per-endpoint limits with detailed logging
- **Security Headers**: Comprehensive browser security headers
- **Request Tracing**: Request IDs for debugging and monitoring
- **Error Logging**: Structured error logging with context

### Performance Features
- **Redis Caching**: View-level caching with smart invalidation
- **Database Optimization**: Connection pooling and query optimization
- **Rate Limiting**: Prevents abuse while allowing legitimate traffic
- **Request Tracing**: End-to-end request tracking

### Documentation Features
- **Complete API Docs**: All endpoints with examples
- **Error Documentation**: Detailed error response formats
- **Authentication Guide**: JWT and Token authentication flows
- **SDK Examples**: Ready-to-use client libraries
- **Testing Guide**: Comprehensive testing instructions

This implementation brings the API to enterprise-grade standards with comprehensive security, testing, documentation, and performance optimizations.
