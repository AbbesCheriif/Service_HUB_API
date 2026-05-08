# Endpoint Reference

## Authentication (`/auth`)

| Method | Path | Auth | Role | Description |
|--------|------|------|------|-------------|
| POST | `/auth/register` | No | — | Register a new user (CLIENT or PROVIDER) |
| POST | `/auth/login` | No | — | Login and receive access + refresh JWT tokens |
| POST | `/auth/refresh` | No | — | Exchange a refresh token for a new access token |

Rate limit: 5 requests / minute on `/auth/login` and `/auth/register`.

### Request schemas

**RegisterRequest**
```json
{
  "email": "string (EmailStr)",
  "full_name": "string",
  "password": "string (min 8 chars)",
  "role": "CLIENT | PROVIDER"
}
```

**LoginRequest**
```json
{
  "email": "string",
  "password": "string"
}
```

**RefreshRequest**
```json
{
  "refresh_token": "string"
}
```

**TokenResponse**
```json
{
  "access_token": "string",
  "refresh_token": "string"
}
```

---

## Users (`/users`)

| Method | Path | Auth | Role | Description |
|--------|------|------|------|-------------|
| GET | `/users/me` | JWT | any | Get current user profile |
| GET | `/users/{id}` | JWT | any | Get user by UUID |

### Response schema — UserReadDTO

```json
{
  "id": "uuid",
  "email": "string",
  "full_name": "string",
  "role": "CLIENT | PROVIDER | ADMIN",
  "created_at": "datetime",
  "updated_at": "datetime"
}
```

---

## Services (`/services`)

| Method | Path | Auth | Role | Description |
|--------|------|------|------|-------------|
| POST | `/services/` | JWT | PROVIDER, ADMIN | Create a new service |
| GET | `/services/` | No | — | List services (paginated, Redis-cached) |
| GET | `/services/{id}` | No | — | Get service by UUID |
| PUT | `/services/{id}` | JWT | PROVIDER (owner), ADMIN | Update a service |
| DELETE | `/services/{id}` | JWT | PROVIDER (owner), ADMIN | Delete a service |

### Query parameters — list endpoint

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `page` | int | 1 | Page number (1-based) |
| `size` | int | 10 | Items per page |

### Request schema — ServiceCreateRequest / ServiceUpdateRequest

```json
{
  "title": "string",
  "description": "string",
  "price": "float (≥ 0)"
}
```

`ServiceUpdateRequest` accepts any subset of the above fields (`exclude_none=True`).

### Response schema — ServiceResponse

```json
{
  "id": "uuid",
  "title": "string",
  "description": "string",
  "price": "float",
  "provider_id": "uuid",
  "created_at": "datetime",
  "updated_at": "datetime"
}
```

### Paginated response envelope

```json
{
  "items": [...],
  "page": 1,
  "size": 10,
  "has_next": true
}
```

---

## Bookings (`/bookings`)

| Method | Path | Auth | Role | Description |
|--------|------|------|------|-------------|
| POST | `/bookings/` | JWT | CLIENT | Create a booking |
| GET | `/bookings/` | JWT | any | List own bookings (CLIENT → by client, PROVIDER → by provider) |
| GET | `/bookings/{id}` | JWT | owner or ADMIN | Get booking by UUID |
| POST | `/bookings/{id}/accept` | JWT | PROVIDER (owner), ADMIN | Accept a pending booking |
| POST | `/bookings/{id}/cancel` | JWT | CLIENT or PROVIDER (owner), ADMIN | Cancel a booking |

### Request schema — BookingCreateRequest

```json
{
  "service_id": "uuid",
  "provider_id": "uuid",
  "scheduled_at": "datetime (ISO 8601)"
}
```

### Response schema — BookingResponse

```json
{
  "id": "uuid",
  "service_id": "uuid",
  "client_id": "uuid",
  "provider_id": "uuid",
  "status": "PENDING | ACCEPTED | CANCELLED",
  "scheduled_at": "datetime",
  "created_at": "datetime",
  "updated_at": "datetime"
}
```

Booking status transitions:
```
PENDING → ACCEPTED  (via /accept)
PENDING → CANCELLED (via /cancel)
ACCEPTED → CANCELLED (via /cancel)
```

Background tasks triggered on booking creation:
- Email notification to provider
- Booking notification task
- Provider stats recalculation

---

## File Upload (`/files`)

| Method | Path | Auth | Role | Description |
|--------|------|------|------|-------------|
| POST | `/files/upload` | JWT | any | Upload a file |

Content-Type: `multipart/form-data`

**Validation**
- Allowed MIME types: `image/jpeg`, `image/png`, `image/webp`, `application/pdf`
- Maximum size: 5 MB

### Response schema

```json
{
  "id": "uuid",
  "filename": "string",
  "content_type": "string",
  "url": "string",
  "created_at": "datetime"
}
```

---

## Admin (`/admin`)

| Method | Path | Auth | Role | Description |
|--------|------|------|------|-------------|
| GET | `/admin/stats` | JWT | ADMIN | Platform statistics |
| DELETE | `/admin/users/{id}` | JWT | ADMIN | Delete a user account |

### Response schema — stats

```json
{
  "total_users": "int",
  "total_services": "int",
  "total_bookings": "int"
}
```

---

## Health

| Method | Path | Auth | Description |
|--------|------|------|-------------|
| GET | `/health` | No | Liveness check |

```json
{"status": "ok"}
```

---

## Global headers

| Header | Direction | Description |
|--------|-----------|-------------|
| `Authorization: Bearer <token>` | Request | JWT access token |
| `X-Request-ID` | Response | Correlation ID generated per request |

## HTTP status codes used

| Code | Meaning |
|------|---------|
| 200 | OK |
| 201 | Created |
| 204 | No Content (DELETE success) |
| 400 | Bad Request / Validation error |
| 401 | Unauthorized (missing or invalid JWT) |
| 403 | Forbidden (insufficient role) |
| 404 | Not Found |
| 409 | Conflict (e.g. booking overlap) |
| 429 | Too Many Requests (rate limit) |
| 500 | Internal Server Error |
