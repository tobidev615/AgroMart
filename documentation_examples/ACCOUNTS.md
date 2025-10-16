# Accounts API Examples (v1)

## Register
Request
```http
POST /api/v1/accounts/register/
Content-Type: application/json

{
  "username": "alice",
  "email": "alice@example.com",
  "first_name": "Alice",
  "last_name": "Smith",
  "password": "passw0rd123",
  "role": "CONSUMER"
}
```

Response 201
```json
{
  "token": "<token-or-jwt>",
  "user": {"id": 1, "username": "alice", "email": "alice@example.com"},
  "profile": {"role": "CONSUMER"}
}
```

## JWT Login
Request
```http
POST /api/v1/accounts/jwt/login/
Content-Type: application/json

{ "username": "alice", "password": "passw0rd123" }
```

Response 200
```json
{ "access": "<jwt>", "refresh": "<jwt>" }
```

## Me
Request
```http
GET /api/v1/accounts/me/
Authorization: Bearer <access>
```

Response 200
```json
{ "id": 1, "username": "alice", "email": "alice@example.com", "profile": {"role": "CONSUMER"}}
```
