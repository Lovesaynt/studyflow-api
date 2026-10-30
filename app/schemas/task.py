"""Task schemas."""

import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field, field_validator


class TaskBase(BaseModel):
    """Base schema for task."""

    title: str = Field(..., min_length=1, max_length=150, description="Task title")
    description: str | None = Field(default=None, description="Task description")
    priority: str = Field(
        default="medium",
        pattern="^(low|medium|high)$",
        description="Task priority",
    )
    status: str = Field(
        default="pending",
        pattern="^(pending|in_progress|completed)$",
        description="Task status",
    )
    due_date: datetime | None = Field(default=None, description="Task due date")
    subject_id: uuid.UUID | None = Field(default=None, description="Subject UUID")

    @field_validator("title")
    @classmethod
    def title_not_empty(cls, v: str) -> str:
        stripped = v.strip()
        if not stripped:
            raise ValueError("Task title cannot be empty or whitespace only")
        return stripped

    @field_validator("description")
    @classmethod
    def description_strip(cls, v: str | None) -> str | None:
        if v is not None:
            return v.strip() or None
        return v


class TaskCreate(TaskBase):
    """Schema for creating a task."""

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "title": "Complete calculus homework",
                "description": "Solve problems 1-10 from chapter 3",
                "priority": "high",
                "status": "pending",
                "due_date": "2024-01-20T23:59:00Z",
                "subject_id": "550e8400-e29b-41d4-a716-446655440000",
            }
        }
    )


class TaskUpdate(BaseModel):
    """Schema for updating a task (partial update - all fields optional)."""

    title: str | None = Field(default=None, min_length=1, max_length=150, description="Task title")
    description: str | None = Field(default=None, description="Task description")
    priority: str | None = Field(
        default=None,
        pattern="^(low|medium|high)$",
        description="Task priority",
    )
    status: str | None = Field(
        default=None,
        pattern="^(pending|in_progress|completed)$",
        description="Task status",
    )
    due_date: datetime | None = Field(default=None, description="Task due date")
    subject_id: uuid.UUID | None = Field(default=None, description="Subject UUID")

    @field_validator("title")
    @classmethod
    def title_not_empty(cls, v: str | None) -> str | None:
        if v is not None:
            stripped = v.strip()
            if not stripped:
                raise ValueError("Task title cannot be empty or whitespace only")
            return stripped
        return v

    @field_validator("description")
    @classmethod
    def description_strip(cls, v: str | None) -> str | None:
        if v is not None:
            return v.strip() or None
        return v

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "status": "in_progress",
                "priority": "high",
            }
        }
    )


class TaskResponse(TaskBase):
    """Schema for task response."""

    id: uuid.UUID = Field(..., description="Task's unique identifier")
    user_id: uuid.UUID = Field(..., description="Owner's user ID")
    created_at: datetime = Field(..., description="Creation timestamp")
    updated_at: datetime = Field(..., description="Last update timestamp")

    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            "example": {
                "id": "550e8400-e29b-41d4-a716-446655440000",
                "user_id": "550e8400-e29b-41d4-a716-446655440001",
                "title": "Complete calculus homework",
                "description": "Solve problems 1-10 from chapter 3",
                "priority": "high",
                "status": "pending",
                "due_date": "2024-01-20T23:59:00Z",
                "subject_id": "550e8400-e29b-41d4-a716-446655440002",
                "created_at": "2024-01-15T10:30:00Z",
                "updated_at": "2024-01-15T10:30:00Z",
            }
        },
    )


class TaskListResponse(BaseModel):
    """Schema for paginated task list response."""

    items: list[TaskResponse]
    total: int = Field(..., description="Total number of tasks")
    limit: int = Field(..., description="Page size limit")
    offset: int = Field(..., description="Page offset")

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "items": [],
                "total": 0,
                "limit": 10,
                "offset": 0,
            }
        }
    )
