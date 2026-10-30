# StudyFlow API

A REST API for academic task management built with FastAPI, SQLAlchemy 2.0, and PostgreSQL.

## Features

- **User Authentication**: JWT-based authentication with Argon2 password hashing
- **Task Management**: Create, read, update, delete tasks with priorities, statuses, and due dates
- **Subject Management**: Organize tasks by subjects with unique names per user
- **Filtering & Pagination**: Filter tasks by status, priority, subject, and due dates
- **Dashboard**: Productivity summary with task counts and overdue tracking
- **Data Isolation**: All data scoped to authenticated user
- **Async Architecture**: Fully async with SQLAlchemy 2.0 and asyncpg

## Tech Stack

- **Framework**: FastAPI 0.115
- **Database**: PostgreSQL 16 (production) / SQLite (testing)
- **ORM**: SQLAlchemy 2.0 with async support
- **Migrations**: Alembic
- **Validation**: Pydantic v2
- **Authentication**: PyJWT + Argon2 (via passlib)
- **Testing**: pytest + pytest-asyncio + httpx
- **Linting**: Ruff
- **Type Checking**: mypy

## Quick Start

### Prerequisites

- Python 3.11+
- PostgreSQL 16+ (for production)
- Docker & Docker Compose (optional)

### Local Development

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd studyflow-api
   ```

2. **Create virtual environment and install dependencies**
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   pip install -e ".[dev]"
   ```

3. **Configure environment**
   ```bash
   cp .env.example .env
   # Edit .env with your settings
   ```

4. **Run database migrations**
   ```bash
   alembic upgrade head
   ```

5. **Start the development server**
   ```bash
   uvicorn app.main:app --reload
   ```

   API will be available at `http://localhost:8000`

6. **View API documentation**
   - Swagger UI: `http://localhost:8000/docs`
   - ReDoc: `http://localhost:8000/redoc`

### Using Docker Compose

```bash
docker compose up --build
```

This starts:
- PostgreSQL database on port 5432
- API server on port 8000

## API Endpoints

### Authentication
- `POST /api/v1/auth/register` - Register new user
- `POST /api/v1/auth/login` - Login and get access token
- `GET /api/v1/auth/me` - Get current user profile

### Subjects
- `POST /api/v1/subjects` - Create subject
- `GET /api/v1/subjects` - List subjects (paginated)
- `GET /api/v1/subjects/{subject_id}` - Get subject by ID
- `PATCH /api/v1/subjects/{subject_id}` - Update subject
- `DELETE /api/v1/subjects/{subject_id}` - Delete subject

### Tasks
- `POST /api/v1/tasks` - Create task
- `GET /api/v1/tasks` - List tasks (with filtering & pagination)
- `GET /api/v1/tasks/{task_id}` - Get task by ID
- `PATCH /api/v1/tasks/{task_id}` - Update task
- `DELETE /api/v1/tasks/{task_id}` - Delete task

**Task Filters:**
- `status`: pending, in_progress, completed
- `priority`: low, medium, high
- `subject_id`: UUID
- `due_before`: ISO 8601 datetime
- `due_after`: ISO 8601 datetime
- `limit`: Page size (1-100, default 20)
- `offset`: Page offset (default 0)

### Dashboard
- `GET /api/v1/dashboard/summary` - Get productivity summary

## Project Structure

```
studyflow-api/
├── app/
│   ├── api/
│   │   ├── routes/        # API route handlers
│   │   └── deps.py        # FastAPI dependencies
│   ├── core/
│   │   ├── config.py      # Settings management
│   │   └── security.py    # Auth utilities
│   ├── db/
│   │   ├── base.py        # SQLAlchemy base models
│   │   └── session.py     # Database session management
│   ├── models/            # SQLAlchemy models
│   ├── schemas/           # Pydantic schemas
│   ├── services/          # Business logic
│   └── main.py            # FastAPI application
├── alembic/               # Database migrations
├── tests/                 # Test suite
├── Dockerfile
├── compose.yaml
├── pyproject.toml
├── requirements.txt
└── .env.example
```

## Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=app --cov-report=html

# Run specific test file
pytest tests/test_tasks.py -v
```

## Code Quality

```bash
# Linting
ruff check .

# Format code
ruff format .

# Type checking
mypy app/
```

## Configuration

Key environment variables (see `.env.example`):

| Variable | Description | Default |
|----------|-------------|---------|
| `DATABASE_URL` | PostgreSQL connection string | Required |
| `JWT_SECRET_KEY` | Secret key for JWT signing | Required |
| `JWT_ALGORITHM` | JWT algorithm | `HS256` |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | Token expiry | `30` |
| `DEBUG` | Enable debug mode | `false` |

## Database Migrations

```bash
# Create new migration
alembic revision --autogenerate -m "description"

# Apply migrations
alembic upgrade head

# Rollback
alembic downgrade -1
```

## Security

- Passwords hashed with Argon2 (via passlib)
- JWT tokens with configurable expiry
- User data isolation at database level
- SQL injection prevention via SQLAlchemy ORM
- Input validation via Pydantic

## License

MIT License - see LICENSE file for details.