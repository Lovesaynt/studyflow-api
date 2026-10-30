"""Subjects service."""

from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.subject import Subject
from app.schemas.subject import SubjectCreate, SubjectListResponse, SubjectResponse, SubjectUpdate


class SubjectService:
    """Service for subject operations."""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def create(self, user_id: UUID, subject_data: SubjectCreate) -> SubjectResponse:
        """
        Create a new subject for the user.

        Args:
            user_id: Owner's user ID
            subject_data: Subject creation data

        Returns:
            Created subject response

        Raises:
            ValueError: If subject name already exists for this user
        """
        subject = Subject(
            user_id=user_id,
            name=subject_data.name.strip(),
        )

        self.db.add(subject)
        try:
            await self.db.commit()
            await self.db.refresh(subject)
        except IntegrityError as e:
            await self.db.rollback()
            raise ValueError("Subject with this name already exists") from e

        return SubjectResponse.model_validate(subject)

    async def get_list(
        self,
        user_id: UUID,
        limit: int = 50,
        offset: int = 0,
    ) -> SubjectListResponse:
        """
        Get list of subjects for the user with pagination.

        Args:
            user_id: Owner's user ID
            limit: Maximum number of subjects to return
            offset: Number of subjects to skip

        Returns:
            Paginated subject list response
        """
        # Get total count
        count_result = await self.db.execute(
            select(func.count(Subject.id)).where(Subject.user_id == user_id)
        )
        total = count_result.scalar() or 0

        # Get paginated subjects
        result = await self.db.execute(
            select(Subject)
            .where(Subject.user_id == user_id)
            .order_by(Subject.created_at.desc())
            .limit(limit)
            .offset(offset)
        )
        subjects = result.scalars().all()

        return SubjectListResponse(
            items=[SubjectResponse.model_validate(s) for s in subjects],
            total=total,
            limit=limit,
            offset=offset,
        )

    async def get_by_id(self, user_id: UUID, subject_id: UUID) -> SubjectResponse:
        """
        Get a subject by ID (only if owned by user).

        Args:
            user_id: Owner's user ID
            subject_id: Subject's UUID

        Returns:
            Subject response

        Raises:
            ValueError: If subject not found or not owned by user
        """
        result = await self.db.execute(
            select(Subject).where(Subject.id == subject_id, Subject.user_id == user_id)
        )
        subject = result.scalar_one_or_none()

        if subject is None:
            raise ValueError("Subject not found")

        return SubjectResponse.model_validate(subject)

    async def update(
        self,
        user_id: UUID,
        subject_id: UUID,
        subject_data: SubjectUpdate,
    ) -> SubjectResponse:
        """
        Update a subject (partial update).

        Args:
            user_id: Owner's user ID
            subject_id: Subject's UUID
            subject_data: Subject update data

        Returns:
            Updated subject response

        Raises:
            ValueError: If subject not found, not owned by user, or name conflicts
        """
        result = await self.db.execute(
            select(Subject).where(Subject.id == subject_id, Subject.user_id == user_id)
        )
        subject = result.scalar_one_or_none()

        if subject is None:
            raise ValueError("Subject not found")

        # Update only provided fields
        update_data = subject_data.model_dump(exclude_unset=True)

        if "name" in update_data and update_data["name"] is not None:
            subject.name = update_data["name"].strip()

        try:
            await self.db.commit()
            await self.db.refresh(subject)
        except IntegrityError as e:
            await self.db.rollback()
            raise ValueError("Subject with this name already exists") from e

        return SubjectResponse.model_validate(subject)

    async def delete(self, user_id: UUID, subject_id: UUID) -> None:
        """
        Delete a subject (only if owned by user).

        Args:
            user_id: Owner's user ID
            subject_id: Subject's UUID

        Raises:
            ValueError: If subject not found or not owned by user
        """
        result = await self.db.execute(
            select(Subject).where(Subject.id == subject_id, Subject.user_id == user_id)
        )
        subject = result.scalar_one_or_none()

        if subject is None:
            raise ValueError("Subject not found")

        await self.db.delete(subject)
        await self.db.commit()
