"""Pytest configuration and fixtures."""

from collections.abc import AsyncGenerator

import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.pool import StaticPool

from app.core.security import hash_password
from app.db.base import Base
from app.db.session import get_db
from app.main import app
from app.models.subject import Subject
from app.models.task import Task, TaskPriority, TaskStatus
from app.models.user import User

# Test database URL - use SQLite in memory for fast tests
TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"

# Create test engine
test_engine = create_async_engine(
    TEST_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)

TestAsyncSessionLocal = async_sessionmaker(
    test_engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autoflush=False,
)


@pytest_asyncio.fixture(scope="function")
async def db_session() -> AsyncGenerator[AsyncSession, None]:
    """Create a fresh database session for each test."""
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    async with TestAsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()

    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


@pytest_asyncio.fixture(scope="function")
async def client(db_session: AsyncSession) -> AsyncGenerator[AsyncClient, None]:
    """Create a test client with overridden dependencies."""

    async def override_get_db() -> AsyncGenerator[AsyncSession, None]:
        yield db_session

    app.dependency_overrides[get_db] = override_get_db

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        yield ac

    app.dependency_overrides.clear()


@pytest_asyncio.fixture(scope="function")
async def test_user(db_session: AsyncSession) -> User:
    """Create a test user."""
    user = User(
        name="Test User",
        email="test@example.com",
        password_hash=hash_password("password123"),
    )
    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)
    return user


@pytest_asyncio.fixture(scope="function")
async def test_user2(db_session: AsyncSession) -> User:
    """Create a second test user for isolation tests."""
    user = User(
        name="Test User 2",
        email="test2@example.com",
        password_hash=hash_password("password123"),
    )
    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)
    return user


@pytest_asyncio.fixture(scope="function")
async def auth_token(test_user: User) -> str:
    """Generate a JWT token for the test user."""
    from app.core.security import create_access_token

    return create_access_token(subject=str(test_user.id))


@pytest_asyncio.fixture(scope="function")
async def auth_headers(auth_token: str) -> dict:
    """Generate authorization headers for the test user."""
    return {"Authorization": f"Bearer {auth_token}"}


@pytest_asyncio.fixture(scope="function")
async def test_subject(db_session: AsyncSession, test_user: User) -> Subject:
    """Create a test subject for the test user."""
    subject = Subject(
        user_id=test_user.id,
        name="Test Subject",
    )
    db_session.add(subject)
    await db_session.commit()
    await db_session.refresh(subject)
    return subject


@pytest_asyncio.fixture(scope="function")
async def test_task(db_session: AsyncSession, test_user: User, test_subject: Subject) -> Task:
    """Create a test task for the test user."""
    task = Task(
        user_id=test_user.id,
        subject_id=test_subject.id,
        title="Test Task",
        description="Test Description",
        priority=TaskPriority.MEDIUM,
        status=TaskStatus.PENDING,
    )
    db_session.add(task)
    await db_session.commit()
    await db_session.refresh(task)
    return task


@pytest_asyncio.fixture(scope="function")
async def auth_client(client: AsyncClient, auth_headers: dict) -> AsyncClient:
    """Create a test client with authentication headers."""
    client.headers.update(auth_headers)
    return client
