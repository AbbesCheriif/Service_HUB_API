# ServiceHub API

[![CI - Lint](https://github.com/AbbesCheriif/Service_HUB_API/actions/workflows/lint.yml/badge.svg)](https://github.com/AbbesCheriif/Service_HUB_API/actions/workflows/lint.yml)
[![CI - Tests](https://github.com/AbbesCheriif/Service_HUB_API/actions/workflows/tests.yml/badge.svg)](https://github.com/AbbesCheriif/Service_HUB_API/actions/workflows/tests.yml)
[![CI - Docker](https://github.com/AbbesCheriif/Service_HUB_API/actions/workflows/docker.yml/badge.svg)](https://github.com/AbbesCheriif/Service_HUB_API/actions/workflows/docker.yml)

**ServiceHub** is a production-ready REST API for a multi-service booking platform. Clients discover and book services offered by providers (plumbers, tutors, cleaners, …) and an admin back-office manages the whole platform.

Built with **FastAPI**, **PostgreSQL**, and **Redis**, the codebase enforces **Clean Architecture** — domain logic has zero framework dependencies, use cases are fully unit-testable, and infrastructure is swappable behind repository and service interfaces.

---

## Features

- **Auth** — JWT access + refresh tokens, bcrypt password hashing, rate-limited login/register
- **RBAC** — three roles (CLIENT / PROVIDER / ADMIN) enforced via Strategy pattern
- **Services** — CRUD with Redis-cached list, pagination
- **Bookings** — full lifecycle (PENDING → ACCEPTED / CANCELLED), conflict detection, background notifications
- **File upload** — MIME type + size validation, local storage (swappable via interface)
- **Structured logging** — JSON logs via structlog, correlation ID on every request
- **Observability** — `/health` endpoint, `X-Request-ID` header propagated end-to-end
- **CI/CD** — GitHub Actions: ruff lint, pytest + coverage, Docker build

---

## Tech Stack

| Layer            | Technology                              |
|------------------|-----------------------------------------|
| Framework        | FastAPI 0.111+                          |
| Database         | PostgreSQL 16 via SQLAlchemy 2 async    |
| Cache            | Redis 7 (async)                         |
| Auth             | JWT (python-jose) + bcrypt (passlib)    |
| Migrations       | Alembic                                 |
| Logging          | structlog (JSON structured logs)        |
| Testing          | pytest + pytest-asyncio + httpx         |
| Linting          | ruff                                    |
| Containerisation | Docker + docker-compose                 |

---

## Project Structure

```
app/
├── domain/          # Entities, value objects, repository interfaces (no external deps)
├── application/     # Use cases, DTOs, mappers, service interfaces
├── infrastructure/  # SQLAlchemy repos, Redis, JWT, storage, background tasks
├── api/             # FastAPI routers, schemas, dependencies, exception handlers
└── core/            # Config, logging, middleware, security strategies
tests/
├── unit/            # Pure business logic tests (mocked repos)
├── integration/     # Repository tests against real DB
└── api/             # End-to-end route tests with httpx
docs/
├── architecture.md  # Clean Architecture diagram + layer breakdown
├── endpoints.md     # Full endpoint reference
└── api_examples.md  # HTTP request/response examples
```

---

## Getting Started

### Prerequisites

- Python 3.11+
- PostgreSQL 16
- Redis 7
- Docker & docker-compose (optional)

### Installation

```bash
# Clone the repository
git clone https://github.com/AbbesCheriif/Service_HUB_API.git
cd Service_HUB_API

# Create virtual environment
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate

# Install dependencies
pip install -e ".[dev]"

# Copy and configure environment variables
cp .env.example .env
# Edit .env with your DATABASE_URL, REDIS_URL, and SECRET_KEY
```

### Running the API

```bash
# Apply database migrations
alembic upgrade head

# Start the development server
python run.py
# or
uvicorn app.main:app --reload
```

- API: `http://localhost:8000`
- Interactive docs (Swagger UI): `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

### Docker (recommended)

```bash
docker-compose up --build
```

Starts the API, PostgreSQL, and Redis with health checks and persistent volumes.

### Running Tests

```bash
# All tests with coverage report
pytest --cov=app --cov-report=term-missing

# Unit tests only
pytest tests/unit/

# API tests only
pytest tests/api/
```

---

## API Quick Reference

| Method | Path | Auth | Description |
|--------|------|------|-------------|
| POST | `/auth/register` | No | Register (CLIENT or PROVIDER) |
| POST | `/auth/login` | No | Login → access + refresh tokens |
| POST | `/auth/refresh` | No | Refresh access token |
| GET | `/users/me` | JWT | Current user profile |
| POST | `/services/` | PROVIDER | Create a service |
| GET | `/services/` | No | List services (paginated) |
| POST | `/bookings/` | CLIENT | Book a service |
| POST | `/bookings/{id}/accept` | PROVIDER | Accept a booking |
| POST | `/bookings/{id}/cancel` | any | Cancel a booking |
| POST | `/files/upload` | JWT | Upload a file |
| GET | `/admin/stats` | ADMIN | Platform statistics |
| GET | `/health` | No | Health check |

Full documentation:
- [Architecture](docs/architecture.md)
- [Endpoint Reference](docs/endpoints.md)
- [API Examples](docs/api_examples.md)

---

## Branch Strategy

```
main        ← production only (merges from develop at stable milestones)
develop     ← integration branch
feat/*      ← feature branches
test/*      ← test branches
ci/*        ← CI/CD branches
```

---

## License

MIT
