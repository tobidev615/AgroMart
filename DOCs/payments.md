## Payments & Wallets

Payments are processed via Stripe Checkout; a simple wallet system is also available.

### Endpoints
- `POST /api/v1/payments/checkout-session/` → `{ order_id }` → `{ checkout_session_id, checkout_url }`
- `POST /api/v1/payments/stripe/webhook/` (no auth)
- `GET /api/v1/payments/wallet/`
- `POST /api/v1/payments/wallet/deposit/`
- `POST /api/v1/payments/wallet/pay/` → `{ order_id }`

### Flow: Stripe Checkout
1. Client requests a checkout session for an order
2. User completes payment on Stripe-hosted page
3. Webhook marks the `Payment` as `SUCCEEDED`

### Wallet
- Deposit funds, then pay orders from wallet balance

### Examples
```bash
# Create checkout session
curl -X POST -H "Authorization: Bearer <ACCESS>" -H "Content-Type: application/json" \
  -d '{"order_id": 123}' http://127.0.0.1:8000/api/v1/payments/checkout-session/

# Wallet detail
curl -H "Authorization: Bearer <ACCESS>" http://127.0.0.1:8000/api/v1/payments/wallet/

# Wallet deposit
curl -X POST -H "Authorization: Bearer <ACCESS>" -H "Content-Type: application/json" \
  -d '{"amount":"25.00","reference":"test-deposit"}' \
  http://127.0.0.1:8000/api/v1/payments/wallet/deposit/
```
