"""Authentication service."""

from uuid import UUID

from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import create_access_token, hash_password, verify_password
from app.models.user import User
from app.schemas.auth import TokenResponse, UserLogin, UserRegister, UserResponse


class AuthService:
    """Service for authentication operations."""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def register(self, user_data: UserRegister) -> UserResponse:
        """
        Register a new user.

        Args:
            user_data: User registration data

        Returns:
            Created user response

        Raises:
            ValueError: If email already exists
        """
        # Normalize email
        email = user_data.email.lower().strip()

        # Check if user already exists
        result = await self.db.execute(select(User).where(User.email == email))
        existing_user = result.scalar_one_or_none()

        if existing_user:
            raise ValueError("Email already registered")

        # Hash password
        password_hash = hash_password(user_data.password)

        # Create user
        user = User(
            name=user_data.name.strip(),
            email=email,
            password_hash=password_hash,
        )

        self.db.add(user)
        try:
            await self.db.commit()
            await self.db.refresh(user)
        except IntegrityError as e:
            await self.db.rollback()
            raise ValueError("Email already registered") from e

        return UserResponse.model_validate(user)

    async def login(self, credentials: UserLogin) -> TokenResponse:
        """
        Authenticate user and return access token.

        Args:
            credentials: User login credentials

        Returns:
            Token response with access token

        Raises:
            ValueError: If credentials are invalid
        """
        email = credentials.email.lower().strip()

        result = await self.db.execute(select(User).where(User.email == email))
        user = result.scalar_one_or_none()

        if user is None or not verify_password(credentials.password, user.password_hash):
            raise ValueError("Invalid credentials")

        access_token = create_access_token(subject=str(user.id))

        return TokenResponse(access_token=access_token, token_type="bearer")

    async def get_current_user(self, user_id: UUID) -> UserResponse:
        """
        Get current user by ID.

        Args:
            user_id: User's UUID

        Returns:
            User response

        Raises:
            ValueError: If user not found
        """
        result = await self.db.execute(select(User).where(User.id == user_id))
        user = result.scalar_one_or_none()

        if user is None:
            raise ValueError("User not found")

        return UserResponse.model_validate(user)
