# API Examples

Base URL: `http://localhost:8000`

All authenticated requests require the header:
```
Authorization: Bearer <access_token>
```

---

## Auth

### Register a new client

```http
POST /auth/register
Content-Type: application/json

{
  "email": "alice@example.com",
  "full_name": "Alice Dupont",
  "password": "Str0ngP@ss!",
  "role": "CLIENT"
}
```

**Response 201**
```json
{
  "id": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
  "email": "alice@example.com",
  "full_name": "Alice Dupont",
  "role": "CLIENT",
  "created_at": "2026-05-08T10:00:00Z",
  "updated_at": "2026-05-08T10:00:00Z"
}
```

### Register a provider

```http
POST /auth/register
Content-Type: application/json

{
  "email": "bob@example.com",
  "full_name": "Bob Martin",
  "password": "Str0ngP@ss!",
  "role": "PROVIDER"
}
```

### Login

```http
POST /auth/login
Content-Type: application/json

{
  "email": "alice@example.com",
  "password": "Str0ngP@ss!"
}
```

**Response 200**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
}
```

### Refresh access token

```http
POST /auth/refresh
Content-Type: application/json

{
  "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
}
```

---

## Users

### Get current user profile

```http
GET /users/me
Authorization: Bearer <access_token>
```

**Response 200**
```json
{
  "id": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
  "email": "alice@example.com",
  "full_name": "Alice Dupont",
  "role": "CLIENT",
  "created_at": "2026-05-08T10:00:00Z",
  "updated_at": "2026-05-08T10:00:00Z"
}
```

### Get user by ID

```http
GET /users/3fa85f64-5717-4562-b3fc-2c963f66afa6
Authorization: Bearer <access_token>
```

---

## Services

### Create a service (PROVIDER role required)

```http
POST /services/
Authorization: Bearer <provider_access_token>
Content-Type: application/json

{
  "title": "Home Plumbing Repair",
  "description": "Full plumbing inspection and repair for residential properties.",
  "price": 85.00
}
```

**Response 201**
```json
{
  "id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
  "title": "Home Plumbing Repair",
  "description": "Full plumbing inspection and repair for residential properties.",
  "price": 85.0,
  "provider_id": "...",
  "created_at": "2026-05-08T10:05:00Z",
  "updated_at": "2026-05-08T10:05:00Z"
}
```

### List services (paginated, cached)

```http
GET /services/?page=1&size=10
```

**Response 200**
```json
{
  "items": [...],
  "page": 1,
  "size": 10,
  "has_next": true
}
```

### Get a specific service

```http
GET /services/a1b2c3d4-e5f6-7890-abcd-ef1234567890
```

### Update a service (owner or ADMIN)

```http
PUT /services/a1b2c3d4-e5f6-7890-abcd-ef1234567890
Authorization: Bearer <provider_access_token>
Content-Type: application/json

{
  "price": 90.00
}
```

### Delete a service (owner or ADMIN)

```http
DELETE /services/a1b2c3d4-e5f6-7890-abcd-ef1234567890
Authorization: Bearer <provider_access_token>
```

**Response 204 No Content**

---

## Bookings

### Create a booking (CLIENT role required)

```http
POST /bookings/
Authorization: Bearer <client_access_token>
Content-Type: application/json

{
  "service_id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
  "provider_id": "...",
  "scheduled_at": "2026-05-15T14:00:00Z"
}
```

**Response 201**
```json
{
  "id": "b2c3d4e5-f6a7-8901-bcde-f12345678901",
  "service_id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
  "client_id": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
  "provider_id": "...",
  "status": "PENDING",
  "scheduled_at": "2026-05-15T14:00:00Z",
  "created_at": "2026-05-08T10:10:00Z",
  "updated_at": "2026-05-08T10:10:00Z"
}
```

### List my bookings (CLIENT sees own, PROVIDER sees received)

```http
GET /bookings/?page=1&size=10
Authorization: Bearer <access_token>
```

### Accept a booking (PROVIDER role required)

```http
POST /bookings/b2c3d4e5-f6a7-8901-bcde-f12345678901/accept
Authorization: Bearer <provider_access_token>
```

**Response 200** — booking status becomes `ACCEPTED`

### Cancel a booking (CLIENT or PROVIDER)

```http
POST /bookings/b2c3d4e5-f6a7-8901-bcde-f12345678901/cancel
Authorization: Bearer <access_token>
```

**Response 200** — booking status becomes `CANCELLED`

---

## File Upload

```http
POST /files/upload
Authorization: Bearer <access_token>
Content-Type: multipart/form-data

file=@/path/to/photo.jpg
```

**Response 200**
```json
{
  "id": "c3d4e5f6-a7b8-9012-cdef-123456789012",
  "filename": "photo.jpg",
  "content_type": "image/jpeg",
  "url": "/uploads/photo.jpg",
  "created_at": "2026-05-08T10:15:00Z"
}
```

Validation rules:
- Allowed MIME types: `image/jpeg`, `image/png`, `image/webp`, `application/pdf`
- Maximum size: 5 MB

---

## Admin

### Get platform statistics (ADMIN role required)

```http
GET /admin/stats
Authorization: Bearer <admin_access_token>
```

**Response 200**
```json
{
  "total_users": 120,
  "total_services": 45,
  "total_bookings": 312
}
```

### Delete a user (ADMIN role required)

```http
DELETE /admin/users/3fa85f64-5717-4562-b3fc-2c963f66afa6
Authorization: Bearer <admin_access_token>
```

**Response 204 No Content**

---

## Health check

```http
GET /health
```

**Response 200**
```json
{"status": "ok"}
```

---

## Error responses

All domain errors return a consistent envelope:

```json
{
  "detail": "User not found"
}
```

| HTTP code | Meaning |
|-----------|---------|
| 400 | Validation error |
| 401 | Missing or invalid JWT |
| 403 | Insufficient role |
| 404 | Resource not found |
| 409 | Booking conflict |
| 429 | Rate limit exceeded (auth routes: 5 req/min) |
| 500 | Unexpected server error |
