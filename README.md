# StudyFlow API

A REST API for academic task management built with FastAPI, SQLAlchemy 2.0, and PostgreSQL.

[![Python Version](https://img.shields.io/badge/python-3.11%2B-blue.svg)](https://www.python.org/downloads/)
[![FastAPI Version](https://img.shields.io/badge/FastAPI-0.162.0-009688.svg?logo=fastapi)](https://fastapi.tiangolo.com/)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)
[![Code Style](https://img.shields.io/badge/code%20style-ruff-000000.svg)](https://github.com/astral-sh/ruff)
[![Type Checking](https://img.shields.io/badge/type%20checking-mypy-blue.svg)](https://github.com/mypyc/mypy)

---

## 📖 Overview

StudyFlow API is a backend service designed to help students and lifelong learners organize their academic workload. It provides secure, user-scoped management of tasks and subjects with a clean REST interface, built on a modern Python async stack.

---

## ✨ Key Features

- 🔐 **Authentication** — JWT-based access tokens with Argon2 password hashing
- 📋 **Task Management** — Full CRUD with priorities, statuses, due dates, and rich filtering
- 📚 **Subject Organization** — Group tasks by subject with per-user unique names
- 🔍 **Filtering & Pagination** — Filter by status, priority, subject, and date ranges
- 📊 **Dashboard** — Productivity summary with counts, overdue tracking, and completion rates
- 🔒 **Data Isolation** — All resources scoped to the authenticated user at the database level
- ⚡ **Async Architecture** — Fully asynchronous with SQLAlchemy 2.0 and asyncpg/aiosqlite

---

## 🛠 Technology Stack

| Category | Technology | Version |
|----------|------------|---------|
| **Framework** | FastAPI | 0.162.0 |
| **ASGI Server** | Uvicorn | 0.30.6 |
| **Database (Prod)** | PostgreSQL | 16 (via psycopg 3) |
| **Database (Test)** | SQLite | aiosqlite |
| **ORM** | SQLAlchemy | 2.1.6 (async) |
| **Migrations** | Alembic | 1.13.1 |
| **Validation** | Pydantic | 2.14.1 |
| **Settings** | Pydantic Settings | 2.9.1 |
| **Auth** | PyJWT | 2.15.1 |
| **Password Hashing** | Argon2 (passlib) | 1.7.4 / 25.1.0 |
| **Rate Limiting** | SlowAPI | 0.1.10 |
| **Testing** | pytest / pytest-asyncio / httpx | 9.2.0 / 1.4.1 / 0.27.2 |
| **Linting** | Ruff | 0.9.0 |
| **Type Checking** | mypy | 1.14.0 |

---

## 🏗 Architecture & Project Structure

```
studyflow-api/
├── app/
│   ├── api/
│   │   ├── routes/          # API route handlers (auth, subjects, tasks, dashboard)
│   │   └── deps.py          # FastAPI dependencies (auth, DB session)
│   ├── core/
│   │   ├── config.py        # Settings management (Pydantic Settings)
│   │   └── security.py      # Auth utilities (hashing, JWT)
│   ├── db/
│   │   ├── base.py          # SQLAlchemy declarative base & mixins
│   │   └── session.py       # Async session management & engine config
│   ├── models/              # SQLAlchemy ORM models (User, Subject, Task)
│   ├── schemas/             # Pydantic schemas (request/response)
│   ├── services/            # Business logic layer
│   └── main.py              # FastAPI application factory
├── alembic/                 # Database migrations
├── tests/                   # Test suite (unit & integration)
├── Dockerfile               # Container image definition
├── compose.yaml             # Docker Compose for local development
├── pyproject.toml           # Project metadata & tool configuration
├── requirements.txt         # Pinned dependencies
└── .env.example             # Environment variable template
```

---

## 📋 Requirements

- **Python** ≥ 3.11
- **PostgreSQL** ≥ 16 (production)
- **Docker & Docker Compose** (optional, for containerized development)

---

## 🚀 Installation & Setup

### Local Development (venv)

```bash
# 1. Clone the repository
git clone <repository-url>
cd studyflow-api

# 2. Create and activate virtual environment
python -m venv .venv

# Linux / macOS:
source .venv/bin/activate

# Windows PowerShell:
.venv\Scripts\Activate.ps1

# 3. Install dependencies (including dev tools)
pip install -e ".[dev]"

# 4. Configure environment variables
cp .env.example .env
# Edit .env with your settings (see Configuration section)

# 5. Run database migrations
alembic upgrade head

# 6. Start the development server
uvicorn app.main:app --reload
```

The API will be available at `http://localhost:8000`.

### Using Docker Compose

```bash
# Build and start all services
docker compose up --build

# Run in background
docker compose up --build -d

# View logs
docker compose logs -f api

# Stop services
docker compose down
```

This starts:
- **PostgreSQL 16** on port `5432`
- **StudyFlow API** on port `8000`

> **Note:** The `compose.yaml` uses a development JWT secret by default. Override with `JWT_SECRET_KEY` environment variable for production use.

---

## ⚙️ Configuration

All configuration is loaded from environment variables (see `.env.example` for the template).

| Variable | Description | Default | Required |
|----------|-------------|---------|----------|
| `APP_NAME` | Application display name | `StudyFlow API` | No |
| `APP_ENV` | Environment name (`development`, `production`) | `development` | No |
| `DEBUG` | Enable debug mode (auto-reload, verbose errors) | `false` | No |
| `DATABASE_URL` | PostgreSQL connection string | — | **Yes** |
| `JWT_SECRET_KEY` | Secret key for JWT signing (min 32 chars) | — | **Yes** |
| `JWT_ALGORITHM` | JWT signing algorithm | `HS256` | No |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | Access token lifetime | `30` | No |
| `BCRYPT_ROUNDS` | Argon2 time cost (iterations) | `12` | No |
| `CORS_ORIGINS` | Comma-separated list of allowed origins | *(empty = disabled)* | No |

### Example `.env` for Local Development

```ini
APP_NAME=StudyFlow API
APP_ENV=development
DEBUG=true
DATABASE_URL=postgresql+psycopg://studyflow:studyflow_dev@localhost:5432/studyflow
JWT_SECRET_KEY=your-secure-random-secret-key-here
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
BCRYPT_ROUNDS=12
CORS_ORIGINS=http://localhost:3000,http://localhost:5173
```

> ⚠️ **Security:** Never commit `.env` files. Use strong, unique `JWT_SECRET_KEY` values in production (min 32 random characters). Rotate periodically.

---

## 📚 API Documentation

Interactive documentation is available when the server is running:

- **Swagger UI:** `http://localhost:8000/docs`
- **ReDoc:** `http://localhost:8000/redoc`
- **OpenAPI JSON:** `http://localhost:8000/openapi.json`

### Endpoints Summary

#### Authentication (`/api/v1/auth`)

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/register` | Register a new user |
| `POST` | `/login` | Authenticate and receive access token |
| `GET` | `/me` | Get current user profile |

#### Subjects (`/api/v1/subjects`)

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/` | Create a new subject |
| `GET` | `/` | List subjects (paginated) |
| `GET` | `/{subject_id}` | Get subject by ID |
| `PATCH` | `/{subject_id}` | Update subject |
| `DELETE` | `/{subject_id}` | Delete subject |

#### Tasks (`/api/v1/tasks`)

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/` | Create a new task |
| `GET` | `/` | List tasks (with filtering & pagination) |
| `GET` | `/{task_id}` | Get task by ID |
| `PATCH` | `/{task_id}` | Update task |
| `DELETE` | `/{task_id}` | Delete task |

**Task Filters (query parameters):**

| Parameter | Type | Description |
|-----------|------|-------------|
| `status` | enum | `pending`, `in_progress`, `completed` |
| `priority` | enum | `low`, `medium`, `high` |
| `subject_id` | UUID | Filter by subject |
| `due_before` | datetime | ISO 8601 upper bound |
| `due_after` | datetime | ISO 8601 lower bound |
| `limit` | int | Page size (1–100, default: 20) |
| `offset` | int | Page offset (default: 0) |

#### Dashboard (`/api/v1/dashboard`)

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/summary` | Productivity summary (counts, overdue, completion rate) |

---

## 🧪 Testing & Code Quality

### Run Tests

```bash
# Run all tests
pytest

# Run with coverage report
pytest --cov=app --cov-report=html

# Run specific test module
pytest tests/test_tasks.py -v

# Run with verbose output
pytest -v
```

### Linting & Formatting

```bash
# Check for lint errors
ruff check app/ tests/

# Auto-fix lint errors (where safe)
ruff check --fix app/ tests/

# Format code
ruff format app/ tests/
```

### Type Checking

```bash
# Static type analysis
mypy app/
```

### CI Pipeline

The GitHub Actions workflow (`.github/workflows/ci.yml`) runs on every push and PR:

1. **Lint & Type Check** — Ruff + mypy
2. **Tests** — pytest with PostgreSQL 16 service, coverage upload to Codecov

---

## 🔐 Security

### Implemented Protections

| Area | Implementation |
|------|----------------|
| **Password Hashing** | Argon2id via passlib (memory-hard, configurable cost) |
| **Token Auth** | JWT (HS256), 30-min expiry, configurable |
| **Data Isolation** | All queries filter by `user_id` at ORM level |
| **SQL Injection** | SQLAlchemy ORM — no raw SQL in application code |
| **Input Validation** | Pydantic v2 schemas on all request bodies |
| **Rate Limiting** | Global: 100 req/min/IP; Auth: 5/min register, 10/min login |
| **Security Headers** | `X-Content-Type-Options: nosniff`, `X-Frame-Options: DENY`, `Referrer-Policy: strict-origin-when-cross-origin`, `Strict-Transport-Security` (production only) |
| **CORS** | Disabled by default; explicit origins via `CORS_ORIGINS` |
| **Secrets Management** | Environment variables only; `.env` gitignored; `.env.example` contains placeholders |

### Security Policy

See [SECURITY.md](SECURITY.md) for vulnerability reporting, supported versions, and disclosure policy.

---

## 📦 Database Migrations

```bash
# Generate a new migration (auto-detect model changes)
alembic revision --autogenerate -m "description of changes"

# Apply all pending migrations
alembic upgrade head

# Rollback one migration
alembic downgrade -1

# Show current migration head
alembic current

# Show migration history
alembic history
```

---

## 🤖 AI-Assisted Development

This project was developed with assistance from:

- **Claude Code** (Anthropic's official CLI for Claude)
- **Claude Opus 5.5**
- **Fable 5**

These AI tools assisted with various development activities including code generation, implementation support, debugging, refactoring, and documentation.

**Important clarifications:**

- The project received personal human review and revisions throughout development.
- AI-generated suggestions and implementations were reviewed and adjusted as appropriate.
- The project is not presented as entirely AI-generated or as the autonomous work of an AI agent.
- Final development decisions and project direction involved personal judgment and oversight.

---

## 🤝 Contributing

Contributions are welcome. Please read [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines on:

- Code style and standards
- Pull request process
- Testing requirements
- Issue reporting

---

## 📜 License

This project is licensed under the **MIT License** — see the [LICENSE](LICENSE) file for details.

---

## 📌 Project Status & Limitations

| Aspect | Status |
|--------|--------|
| Core API | ✅ Stable |
| Authentication | ✅ Implemented (access tokens only) |
| Refresh Tokens | 📋 Planned (not yet implemented) |
| Test Coverage | ✅ 91 tests passing |
| CI/CD | ✅ Configured (GitHub Actions) |
| Production Hardening | ⚠️ Basic (add WAF, monitoring, secrets rotation for prod) |

> **Note:** This is a backend API only. A frontend client is not included.

---

*Generated with transparency. Last updated: 2026.*