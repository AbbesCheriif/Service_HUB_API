# ServiceHub API

## Overview

ServiceHub allows clients to discover and book services from providers (plumbers, tutors, cleaners, etc.), with a full admin back-office. The codebase is structured around Domain-Driven Design with strict separation between domain, application, infrastructure, and API layers.

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

## Architecture

```
app/
├── domain/          # Entities, value objects, repository interfaces (no external deps)
├── application/     # Use cases, DTOs, mappers, service interfaces
├── infrastructure/  # SQLAlchemy repos, Redis, JWT, storage, background tasks
├── api/             # FastAPI routers, schemas, dependencies, exception handlers
└── core/            # Config, logging, middleware, security strategies
tests/
├── unit/
├── integration/
└── api/
```

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
# Edit .env with your database URL, Redis URL, and secret key
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

The API will be available at `http://localhost:8000`.
Interactive docs: `http://localhost:8000/docs`

### Running Tests

```bash
pytest --cov=app --cov-report=term-missing
```

### Docker

```bash
docker-compose up --build
```

## API Highlights

- `POST /auth/register` — Register as client or provider
- `POST /auth/login` — Obtain JWT access + refresh tokens
- `GET /services` — Browse available services (paginated, cached)
- `POST /bookings` — Book a service
- `GET /admin/stats` — Admin dashboard stats (admin role required)
- `POST /files/upload` — Upload a file (MIME + size validated)

## Branch Strategy

```
main        ← production only
develop     ← integration branch
feat/*      ← feature branches
test/*      ← test branches
ci/*        ← CI/CD branches
```

## License

MIT
