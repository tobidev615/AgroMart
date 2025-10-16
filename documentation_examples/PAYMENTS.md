# Payments API Examples (v1)

## Create Checkout Session
```http
POST /api/v1/payments/checkout-session/
Authorization: Bearer <access>
Content-Type: application/json

{ "order_id": 42 }
```

Response 200
```json
{ "checkout_url": "https://checkout.stripe.com/c/pay_..." }
```

## Stripe Webhook
```http
POST /api/v1/payments/stripe/webhook/
Stripe-Signature: <signature>
```

Response 200
```json
{ "status": "received" }
```

## Wallet
```http
GET /api/v1/payments/wallet/
Authorization: Bearer <access>
```

```http
POST /api/v1/payments/wallet/deposit/
Authorization: Bearer <access>
Content-Type: application/json

{ "amount": "25.00", "reference": "test-deposit" }
```

```http
POST /api/v1/payments/wallet/pay/
Authorization: Bearer <access>
Content-Type: application/json

{ "order_id": 1 }
```
