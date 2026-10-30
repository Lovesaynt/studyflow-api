# Contributing to StudyFlow

Thank you for your interest in contributing to StudyFlow! This document provides guidelines and instructions for contributing to this project.

## Table of Contents

- [Code of Conduct](#code-of-conduct)
- [Getting Started](#getting-started)
- [Development Environment](#development-environment)
- [Running Tests](#running-tests)
- [Code Style](#code-style)
- [Submitting Changes](#submitting-changes)
- [Pull Request Process](#pull-request-process)

## Code of Conduct

This project adheres to a [Code of Conduct](CODE_OF_CONDUCT.md). By participating, you are expected to uphold this code.

## Getting Started

### Prerequisites

- Python 3.11+
- PostgreSQL 16+ (for production-like testing)
- Docker & Docker Compose (optional, for containerized development)

### Development Environment Setup

1. **Fork and clone the repository**

   ```bash
   git clone https://github.com/your-username/studyflow-api.git
   cd studyflow-api
   ```

2. **Create a virtual environment**

   ```bash
   python -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   ```

3. **Install dependencies**

   ```bash
   pip install -e ".[dev]"
   ```

4. **Configure environment**

   ```bash
   cp .env.example .env
   # Edit .env with your settings
   ```

5. **Run database migrations**

   ```bash
   alembic upgrade head
   ```

6. **Start the development server**

   ```bash
   uvicorn app.main:app --reload
   ```

   The API will be available at `http://localhost:8000`

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

## Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=app --cov-report=html

# Run specific test file
pytest tests/test_tasks.py -v
```

## Code Style

This project uses:

- **Ruff** for linting and formatting
- **MyPy** for type checking
- **Pytest** for testing

### Linting

```bash
# Check for linting issues
ruff check app/ tests/

# Auto-fix issues
ruff check app/ tests/ --fix

# Format code
ruff format app/ tests/
```

### Type Checking

```bash
mypy app/
```

## Submitting Changes

1. Create a new branch for your feature or fix:

   ```bash
   git checkout -b feature/your-feature-name
   # or
   git checkout -b fix/your-bug-fix
   ```

2. Make your changes with clear, focused commits.

3. Ensure all tests pass:

   ```bash
   pytest
   ```

4. Ensure linting and type checking pass:

   ```bash
   ruff check app/ tests/
   mypy app/
   ```

5. Push your branch and open a Pull Request.

## Pull Request Process

1. **Title**: Use a clear, descriptive title following conventional commits format (e.g., `feat: add task filtering by due date`).

2. **Description**: Include:
   - What changes were made
   - Why the changes were needed
   - Any breaking changes
   - Related issue numbers (if applicable)

3. **Tests**: Add tests for new functionality. Ensure existing tests still pass.

4. **Documentation**: Update documentation if your changes affect user-facing features.

5. **Review**: Address review comments promptly. All CI checks must pass before merging.

6. **Merge**: Once approved, your PR will be merged by a maintainer.

## Commit Message Format

This project follows [Conventional Commits](https://www.conventionalcommits.org/):

```
<type>(<scope>): <description>

[optional body]

[optional footer]
```

Types:
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation changes
- `style`: Code style changes (formatting, etc.)
- `refactor`: Code refactoring
- `test`: Test additions or modifications
- `chore`: Maintenance tasks

Examples:
- `feat(auth): add refresh token endpoint`
- `fix(tasks): handle null subject_id in task listing`
- `docs(readme): update Docker Compose instructions`