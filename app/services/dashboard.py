"""Dashboard service."""

from datetime import UTC, datetime
from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.subject import Subject
from app.models.task import Task, TaskStatus
from app.schemas.dashboard import DashboardSummary


class DashboardService:
    """Service for dashboard operations."""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_summary(self, user_id: UUID) -> DashboardSummary:
        """
        Get productivity dashboard summary for the user.

        Args:
            user_id: Owner's user ID

        Returns:
            Dashboard summary with task counts
        """
        now = datetime.now(UTC)

        # Total tasks
        total_result = await self.db.execute(
            select(func.count(Task.id)).where(Task.user_id == user_id)
        )
        total = total_result.scalar() or 0

        # Pending tasks
        pending_result = await self.db.execute(
            select(func.count(Task.id)).where(
                Task.user_id == user_id, Task.status == TaskStatus.PENDING
            )
        )
        pending = pending_result.scalar() or 0

        # In progress tasks
        in_progress_result = await self.db.execute(
            select(func.count(Task.id)).where(
                Task.user_id == user_id, Task.status == TaskStatus.IN_PROGRESS
            )
        )
        in_progress = in_progress_result.scalar() or 0

        # Completed tasks
        completed_result = await self.db.execute(
            select(func.count(Task.id)).where(
                Task.user_id == user_id, Task.status == TaskStatus.COMPLETED
            )
        )
        completed = completed_result.scalar() or 0

        # Overdue tasks (due date < now AND status != completed)
        overdue_result = await self.db.execute(
            select(func.count(Task.id)).where(
                Task.user_id == user_id,
                Task.due_date < now,
                Task.status != TaskStatus.COMPLETED,
            )
        )
        overdue = overdue_result.scalar() or 0

        # Number of subjects
        subjects_result = await self.db.execute(
            select(func.count(Subject.id)).where(Subject.user_id == user_id)
        )
        subjects = subjects_result.scalar() or 0

        return DashboardSummary(
            total=total,
            pending=pending,
            in_progress=in_progress,
            completed=completed,
            overdue=overdue,
            subjects=subjects,
        )
