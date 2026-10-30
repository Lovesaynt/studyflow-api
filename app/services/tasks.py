"""Tasks service."""

from datetime import datetime
from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.subject import Subject
from app.models.task import Task, TaskPriority, TaskStatus
from app.schemas.task import TaskCreate, TaskListResponse, TaskResponse, TaskUpdate


class TaskService:
    """Service for task operations."""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def create(self, user_id: UUID, task_data: TaskCreate) -> TaskResponse:
        """
        Create a new task for the user.

        Args:
            user_id: Owner's user ID
            task_data: Task creation data

        Returns:
            Created task response

        Raises:
            ValueError: If subject doesn't exist or doesn't belong to user
        """
        # Verify subject exists and belongs to user if provided
        if task_data.subject_id is not None:
            result = await self.db.execute(
                select(Subject).where(
                    Subject.id == task_data.subject_id, Subject.user_id == user_id
                )
            )
            subject = result.scalar_one_or_none()
            if subject is None:
                raise ValueError("Subject not found")

        task = Task(
            user_id=user_id,
            subject_id=task_data.subject_id,
            title=task_data.title.strip(),
            description=task_data.description,
            priority=task_data.priority,
            status=task_data.status,
            due_date=task_data.due_date,
        )

        self.db.add(task)
        try:
            await self.db.commit()
            await self.db.refresh(task)
        except IntegrityError as e:
            await self.db.rollback()
            raise ValueError("Failed to create task") from e

        return TaskResponse.model_validate(task)

    async def get_list(
        self,
        user_id: UUID,
        status: TaskStatus | None = None,
        priority: TaskPriority | None = None,
        subject_id: UUID | None = None,
        due_before: datetime | None = None,
        due_after: datetime | None = None,
        limit: int = 20,
        offset: int = 0,
    ) -> TaskListResponse:
        """
        Get list of tasks for the user with filtering and pagination.

        Args:
            user_id: Owner's user ID
            status: Filter by status
            priority: Filter by priority
            subject_id: Filter by subject
            due_before: Filter tasks due before this date
            due_after: Filter tasks due after this date
            limit: Maximum number of tasks to return
            offset: Number of tasks to skip

        Returns:
            Paginated task list response
        """
        # Build base query
        query = select(Task).where(Task.user_id == user_id)

        # Apply filters
        if status is not None:
            query = query.where(Task.status == status)
        if priority is not None:
            query = query.where(Task.priority == priority)
        if subject_id is not None:
            query = query.where(Task.subject_id == subject_id)
        if due_before is not None:
            query = query.where(Task.due_date <= due_before)
        if due_after is not None:
            query = query.where(Task.due_date > due_after)

        # Get total count
        count_query = select(func.count(Task.id)).where(Task.user_id == user_id)
        if status is not None:
            count_query = count_query.where(Task.status == status)
        if priority is not None:
            count_query = count_query.where(Task.priority == priority)
        if subject_id is not None:
            count_query = count_query.where(Task.subject_id == subject_id)
        if due_before is not None:
            count_query = count_query.where(Task.due_date <= due_before)
        if due_after is not None:
            count_query = count_query.where(Task.due_date > due_after)

        count_result = await self.db.execute(count_query)
        total = count_result.scalar() or 0

        # Get paginated tasks
        query = (
            query.options(selectinload(Task.subject))
            .order_by(Task.due_date.asc().nullslast(), Task.created_at.desc())
            .limit(limit)
            .offset(offset)
        )
        result = await self.db.execute(query)
        tasks = result.scalars().all()

        return TaskListResponse(
            items=[TaskResponse.model_validate(t) for t in tasks],
            total=total,
            limit=limit,
            offset=offset,
        )

    async def get_by_id(self, user_id: UUID, task_id: UUID) -> TaskResponse:
        """
        Get a task by ID (only if owned by user).

        Args:
            user_id: Owner's user ID
            task_id: Task's UUID

        Returns:
            Task response

        Raises:
            ValueError: If task not found or not owned by user
        """
        result = await self.db.execute(
            select(Task)
            .options(selectinload(Task.subject))
            .where(Task.id == task_id, Task.user_id == user_id)
        )
        task = result.scalar_one_or_none()

        if task is None:
            raise ValueError("Task not found")

        return TaskResponse.model_validate(task)

    async def update(
        self,
        user_id: UUID,
        task_id: UUID,
        task_data: TaskUpdate,
    ) -> TaskResponse:
        """
        Update a task (partial update).

        Args:
            user_id: Owner's user ID
            task_id: Task's UUID
            task_data: Task update data

        Returns:
            Updated task response

        Raises:
            ValueError: If task not found, not owned by user, or subject invalid
        """
        result = await self.db.execute(
            select(Task).where(Task.id == task_id, Task.user_id == user_id)
        )
        task = result.scalar_one_or_none()

        if task is None:
            raise ValueError("Task not found")

        # Update only provided fields
        update_data = task_data.model_dump(exclude_unset=True)

        if "title" in update_data and update_data["title"] is not None:
            task.title = update_data["title"].strip()
        if "description" in update_data:
            task.description = update_data["description"]
        if "priority" in update_data and update_data["priority"] is not None:
            task.priority = update_data["priority"]
        if "status" in update_data and update_data["status"] is not None:
            task.status = update_data["status"]
        if "due_date" in update_data:
            task.due_date = update_data["due_date"]
        if "subject_id" in update_data:
            if update_data["subject_id"] is not None:
                # Verify subject exists and belongs to user
                subject_result = await self.db.execute(
                    select(Subject).where(
                        Subject.id == update_data["subject_id"], Subject.user_id == user_id
                    )
                )
                subject = subject_result.scalar_one_or_none()
                if subject is None:
                    raise ValueError("Subject not found")
                task.subject_id = update_data["subject_id"]
            else:
                task.subject_id = None

        try:
            await self.db.commit()
            # Refresh with subject relationship loaded
            result = await self.db.execute(
                select(Task)
                .options(selectinload(Task.subject))
                .where(Task.id == task_id)
            )
            task = result.scalar_one()
        except IntegrityError as e:
            await self.db.rollback()
            raise ValueError("Failed to update task") from e

        return TaskResponse.model_validate(task)

    async def delete(self, user_id: UUID, task_id: UUID) -> None:
        """
        Delete a task (only if owned by user).

        Args:
            user_id: Owner's user ID
            task_id: Task's UUID

        Raises:
            ValueError: If task not found or not owned by user
        """
        result = await self.db.execute(
            select(Task).where(Task.id == task_id, Task.user_id == user_id)
        )
        task = result.scalar_one_or_none()

        if task is None:
            raise ValueError("Task not found")

        await self.db.delete(task)
        await self.db.commit()
