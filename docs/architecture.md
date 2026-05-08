# Architecture

ServiceHub follows **Clean Architecture** with four strict layers. Each layer can only depend on the layer directly below it; outer layers depend on inner ones, never the reverse.

```
┌─────────────────────────────────────────────────┐
│                    API Layer                     │
│   FastAPI routers · schemas · dependencies       │
├─────────────────────────────────────────────────┤
│               Application Layer                  │
│   Use cases · DTOs · mappers · interfaces        │
├─────────────────────────────────────────────────┤
│                 Domain Layer                     │
│   Entities · value objects · repo interfaces     │
├─────────────────────────────────────────────────┤
│              Infrastructure Layer                │
│  SQLAlchemy · Redis · JWT · storage · bg tasks   │
└─────────────────────────────────────────────────┘
         ↕ Core (config · logging · middleware)
```

## Layer Responsibilities

### Domain (`app/domain/`)
Pure Python — zero framework imports. Contains:
- **Entities**: `User`, `Service`, `Booking`, `Review`, `FileUpload` with `BaseEntity` (id, created_at, updated_at).
- **Value objects**: `Email`, `Role` (CLIENT / PROVIDER / ADMIN), `BookingStatus`.
- **Repository interfaces**: Abstract Base Classes defining the contract for persistence — `UserRepository`, `ServiceRepository`, `BookingRepository`.
- **Exceptions**: `UserNotFound`, `ServiceNotFound`, `BookingConflict`, `PermissionDenied`, etc.

### Application (`app/application/`)
Orchestrates domain objects. Contains:
- **Use cases**: one class per business action (`CreateUser`, `Login`, `Register`, `CreateService`, `ListServices`, `CreateBooking`, `AcceptBooking`, `CancelBooking`, `UploadFile`).
- **DTOs**: Pydantic models for input/output (`UserCreateDTO`, `ServiceReadDTO`, etc.) with separate Create / Read / Update variants.
- **Mappers**: `user_to_dto()`, `dto_to_user()`, etc.
- **Interfaces**: `UnitOfWork` ABC, `StorageInterface` ABC, `NotificationService` ABC.

### Infrastructure (`app/infrastructure/`)
Implements the interfaces defined in domain and application:
- **Database**: async SQLAlchemy engine, session factory, ORM models, Alembic migrations, concrete repositories, `SQLAlchemyUnitOfWork`.
- **Auth**: `PasswordService` (bcrypt via passlib), `JWTService` (python-jose: access + refresh tokens).
- **Cache**: Redis factory (async connection pool), `CacheService` (get/set/delete/invalidate_pattern), `@cached` decorator with TTL.
- **Storage**: `LocalStorage` for file uploads, extensible via `StorageInterface`.
- **Background tasks**: email notifications, booking notifications, provider stats recalculation.

### API (`app/api/`)
Thin FastAPI adapters:
- **Routers**: `/auth`, `/users`, `/services`, `/bookings`, `/admin`, `/files`.
- **Schemas**: Pydantic request/response models, `PaginatedResponse[T]`, `PageParams`.
- **Dependencies**: `get_session` (DB), `get_current_user` / `require_role` (JWT auth).
- **Exception handlers**: maps `DomainException` subclasses to HTTP 4xx responses.

### Core (`app/core/`)
Cross-cutting concerns shared by all layers:
- **Config**: `Settings` via Pydantic Settings (reads `.env`), production overrides.
- **Logging**: structlog with JSON renderer, timestamp, log level, bound context.
- **Middleware**: `CorrelationIdMiddleware` (generates / propagates `X-Request-ID`), `RateLimiter` (Redis sliding window, configurable per-route).
- **Security**: `PermissionStrategy` interface + `AdminStrategy`, `ProviderStrategy`, `ClientStrategy`.

## Key Patterns

| Pattern | Where |
|---------|-------|
| Repository | `app/domain/repositories/` (interface) + `app/infrastructure/repositories/` (impl) |
| Unit of Work | `app/application/interfaces/unit_of_work.py` + `app/infrastructure/database/unit_of_work.py` |
| Factory | `app/infrastructure/cache/redis_factory.py`, `app/infrastructure/database/session.py` |
| Strategy | `app/core/security/permissions.py` + strategies/ |
| Decorator | `app/infrastructure/cache/cache_decorator.py` |

## Data Flow — typical request

```
Client request
    │
    ▼
CorrelationIdMiddleware  (attaches X-Request-ID)
    │
    ▼
RateLimiter  (Redis sliding window — auth routes only)
    │
    ▼
FastAPI Router  (validates schema, resolves Depends)
    │
    ├── get_current_user → JWTService.decode_token → UserRepository.get_by_id
    │
    ▼
Use Case  (pure business logic, uses UnitOfWork)
    │
    ├── Repository  →  SQLAlchemy async session
    ├── CacheService  →  Redis async pool
    └── BackgroundTask  (fire-and-forget notifications)
    │
    ▼
DTO / mapper  →  JSON response
```

## Database Schema (high level)

```
users
  id · email · full_name · hashed_password · role · created_at · updated_at

services
  id · provider_id(FK users) · title · description · price · created_at · updated_at

bookings
  id · client_id(FK users) · provider_id(FK users) · service_id(FK services)
    · status · scheduled_at · created_at · updated_at

reviews
  id · booking_id(FK bookings) · rating · comment · created_at · updated_at

file_uploads
  id · owner_id(FK users) · filename · content_type · path · created_at · updated_at
```

## CI/CD

```
push / PR
    │
    ├── lint.yml    →  ruff check + ruff format --check
    ├── tests.yml   →  pytest + coverage (≥65 %) + badge
    └── docker.yml  →  docker build (smoke test)
```
