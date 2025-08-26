# Payments API Examples

## Create Checkout Session
```http
POST /api/payments/checkout-session/
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
POST /api/payments/stripe/webhook/
Stripe-Signature: <signature>
```

Response 200
```json
{ "status": "received" }
```


