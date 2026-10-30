"""Subject model."""

import uuid
from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey, String, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, TimestampMixin

if TYPE_CHECKING:
    from app.models.task import Task
    from app.models.user import User


class Subject(Base, TimestampMixin):
    """Subject (discipline) model."""

    __tablename__ = "subjects"

    __table_args__ = (UniqueConstraint("user_id", "name", name="uq_user_subject_name"),)

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
    name: Mapped[str] = mapped_column(String(100), nullable=False)

    # Relationships
    user: Mapped["User"] = relationship(
        "User",
        back_populates="subjects",
        lazy="selectin",
    )
    tasks: Mapped[list["Task"]] = relationship(
        "Task",
        back_populates="subject",
        lazy="selectin",
        viewonly=True,
        primaryjoin="Subject.id == Task.subject_id",
        foreign_keys="Task.subject_id",
    )

    def __repr__(self) -> str:
        return f"<Subject(id={self.id}, name={self.name})>"
