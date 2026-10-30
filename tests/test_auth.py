"""Authentication tests."""

from datetime import UTC

from httpx import AsyncClient


class TestRegistration:
    """Tests for user registration."""

    async def test_register_success(self, client: AsyncClient):
        """Test successful user registration."""
        response = await client.post(
            "/api/v1/auth/register",
            json={
                "name": "John Doe",
                "email": "john@example.com",
                "password": "securepassword123",
            },
        )
        assert response.status_code == 201
        data = response.json()
        assert data["name"] == "John Doe"
        assert data["email"] == "john@example.com"
        assert "id" in data
        assert "created_at" in data
        assert "password" not in data

    async def test_register_duplicate_email(self, client: AsyncClient, test_user):
        """Test registration with duplicate email fails."""
        response = await client.post(
            "/api/v1/auth/register",
            json={
                "name": "Another User",
                "email": test_user.email,
                "password": "password123",
            },
        )
        assert response.status_code == 409
        assert "already registered" in response.json()["detail"].lower()

    async def test_register_invalid_email(self, client: AsyncClient):
        """Test registration with invalid email fails."""
        response = await client.post(
            "/api/v1/auth/register",
            json={
                "name": "John Doe",
                "email": "invalid-email",
                "password": "password123",
            },
        )
        assert response.status_code == 422

    async def test_register_short_password(self, client: AsyncClient):
        """Test registration with short password fails."""
        response = await client.post(
            "/api/v1/auth/register",
            json={
                "name": "John Doe",
                "email": "john@example.com",
                "password": "short",
            },
        )
        assert response.status_code == 422

    async def test_register_empty_name(self, client: AsyncClient):
        """Test registration with empty name fails."""
        response = await client.post(
            "/api/v1/auth/register",
            json={
                "name": "   ",
                "email": "john@example.com",
                "password": "password123",
            },
        )
        assert response.status_code == 422

    async def test_register_whitespace_only_name(self, client: AsyncClient):
        """Test registration with whitespace-only name fails."""
        response = await client.post(
            "/api/v1/auth/register",
            json={
                "name": "  \t\n  ",
                "email": "john@example.com",
                "password": "password123",
            },
        )
        assert response.status_code == 422

    async def test_register_empty_password(self, client: AsyncClient):
        """Test registration with empty password fails."""
        response = await client.post(
            "/api/v1/auth/register",
            json={
                "name": "John Doe",
                "email": "john@example.com",
                "password": "   ",
            },
        )
        assert response.status_code == 422

    async def test_register_missing_fields(self, client: AsyncClient):
        """Test registration with missing fields fails."""
        response = await client.post(
            "/api/v1/auth/register",
            json={
                "email": "john@example.com",
            },
        )
        assert response.status_code == 422


class TestLogin:
    """Tests for user login."""

    async def test_login_success(self, client: AsyncClient, test_user):
        """Test successful login."""
        response = await client.post(
            "/api/v1/auth/login",
            json={
                "email": test_user.email,
                "password": "password123",
            },
        )
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert data["token_type"] == "bearer"

    async def test_login_wrong_password(self, client: AsyncClient, test_user):
        """Test login with wrong password fails."""
        response = await client.post(
            "/api/v1/auth/login",
            json={
                "email": test_user.email,
                "password": "wrongpassword",
            },
        )
        assert response.status_code == 401
        assert "invalid credentials" in response.json()["detail"].lower()

    async def test_login_nonexistent_user(self, client: AsyncClient):
        """Test login with nonexistent user fails."""
        response = await client.post(
            "/api/v1/auth/login",
            json={
                "email": "nonexistent@example.com",
                "password": "password123",
            },
        )
        assert response.status_code == 401

    async def test_login_invalid_email(self, client: AsyncClient):
        """Test login with invalid email format fails."""
        response = await client.post(
            "/api/v1/auth/login",
            json={
                "email": "invalid-email",
                "password": "password123",
            },
        )
        assert response.status_code == 422

    async def test_login_missing_fields(self, client: AsyncClient):
        """Test login with missing fields fails."""
        response = await client.post(
            "/api/v1/auth/login",
            json={"email": "test@example.com"},
        )
        assert response.status_code == 422


class TestCurrentUser:
    """Tests for getting current user profile."""

    async def test_get_me_success(self, auth_client: AsyncClient, test_user):
        """Test getting current user profile."""
        response = await auth_client.get("/api/v1/auth/me")
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == str(test_user.id)
        assert data["name"] == test_user.name
        assert data["email"] == test_user.email
        assert "created_at" in data

    async def test_get_me_without_token(self, client: AsyncClient):
        """Test getting current user without token fails."""
        response = await client.get("/api/v1/auth/me")
        assert response.status_code == 401

    async def test_get_me_invalid_token(self, client: AsyncClient):
        """Test getting current user with invalid token fails."""
        client.headers["Authorization"] = "Bearer invalid-token"
        response = await client.get("/api/v1/auth/me")
        assert response.status_code == 401

    async def test_get_me_expired_token(self, client: AsyncClient):
        """Test getting current user with expired token fails."""
        from datetime import datetime, timedelta

        import jwt

        from app.core.config import get_settings

        settings = get_settings()
        expired_token = jwt.encode(
            {
                "sub": "00000000-0000-0000-0000-000000000000",
                "exp": datetime.now(UTC) - timedelta(hours=1),
            },
            settings.JWT_SECRET_KEY,
            algorithm=settings.JWT_ALGORITHM,
        )
        client.headers["Authorization"] = f"Bearer {expired_token}"
        response = await client.get("/api/v1/auth/me")
        assert response.status_code == 401


class TestPasswordHashing:
    """Tests for password security."""

    async def test_password_not_stored_in_plaintext(self, test_user, db_session):
        """Test that password is not stored in plaintext."""
        from sqlalchemy import select

        from app.models.user import User

        result = await db_session.execute(select(User).where(User.id == test_user.id))
        user = result.scalar_one()
        assert user.password_hash != "password123"
        assert "$argon2" in user.password_hash

    async def test_password_verification(self, test_user):
        """Test password verification works."""
        from app.core.security import verify_password

        assert verify_password("password123", test_user.password_hash)
        assert not verify_password("wrongpassword", test_user.password_hash)
