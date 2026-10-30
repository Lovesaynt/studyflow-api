"""Task model."""

import enum
import uuid
from datetime import datetime
from typing import TYPE_CHECKING, Union

from sqlalchemy import CheckConstraint, DateTime, ForeignKey, Index, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, TimestampMixin

if TYPE_CHECKING:
    from app.models.subject import Subject
    from app.models.user import User


class TaskPriority(enum.StrEnum):
    """Task priority levels."""

    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


class TaskStatus(enum.StrEnum):
    """Task status levels."""

    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"


class Task(Base, TimestampMixin):
    """Task model for academic tasks."""

    __tablename__ = "tasks"

    __table_args__ = (
        CheckConstraint(
            "priority IN ('low', 'medium', 'high')",
            name="ck_task_priority",
        ),
        CheckConstraint(
            "status IN ('pending', 'in_progress', 'completed')",
            name="ck_task_status",
        ),
        Index("ix_tasks_user_id_status", "user_id", "status"),
        Index("ix_tasks_user_id_priority", "user_id", "priority"),
        Index("ix_tasks_user_id_due_date", "user_id", "due_date"),
    )

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
    )
    subject_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("subjects.id", ondelete="SET NULL"),
        nullable=True,
    )
    title: Mapped[str] = mapped_column(String(150), nullable=False)
    description: Mapped[str | None] = mapped_column(String, nullable=True)
    priority: Mapped[str] = mapped_column(
        String(10),
        default=TaskPriority.MEDIUM,
        nullable=False,
    )
    status: Mapped[str] = mapped_column(
        String(20),
        default=TaskStatus.PENDING,
        nullable=False,
    )
    due_date: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    # Relationships
    user: Mapped["User"] = relationship(
        "User",
        back_populates="tasks",
        lazy="selectin",
    )
    subject: Mapped[Union["Subject", None]] = relationship(
        "Subject",
        back_populates="tasks",
        lazy="selectin",
        primaryjoin="Task.subject_id == Subject.id",
        foreign_keys="Task.subject_id",
    )

    def __repr__(self) -> str:
        return f"<Task(id={self.id}, title={self.title}, status={self.status})>"
