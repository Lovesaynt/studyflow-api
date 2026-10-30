"""Subject schemas."""

import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field, field_validator


class SubjectBase(BaseModel):
    """Base schema for subject."""

    name: str = Field(..., min_length=1, max_length=100, description="Subject name")

    @field_validator("name")
    @classmethod
    def name_not_empty(cls, v: str) -> str:
        stripped = v.strip()
        if not stripped:
            raise ValueError("Subject name cannot be empty or whitespace only")
        return stripped


class SubjectCreate(SubjectBase):
    """Schema for creating a subject."""

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "name": "Calculus I",
            }
        }
    )


class SubjectUpdate(BaseModel):
    """Schema for updating a subject (partial update)."""

    name: str | None = Field(default=None, min_length=1, max_length=100, description="Subject name")

    @field_validator("name")
    @classmethod
    def name_not_empty(cls, v: str | None) -> str | None:
        if v is not None:
            stripped = v.strip()
            if not stripped:
                raise ValueError("Subject name cannot be empty or whitespace only")
            return stripped
        return v

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "name": "Calculus II",
            }
        }
    )


class SubjectResponse(SubjectBase):
    """Schema for subject response."""

    id: uuid.UUID = Field(..., description="Subject's unique identifier")
    user_id: uuid.UUID = Field(..., description="Owner's user ID")
    created_at: datetime = Field(..., description="Creation timestamp")
    updated_at: datetime = Field(..., description="Last update timestamp")

    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            "example": {
                "id": "550e8400-e29b-41d4-a716-446655440000",
                "user_id": "550e8400-e29b-41d4-a716-446655440001",
                "name": "Calculus I",
                "created_at": "2024-01-15T10:30:00Z",
                "updated_at": "2024-01-15T10:30:00Z",
            }
        },
    )


class SubjectListResponse(BaseModel):
    """Schema for subject list response."""

    items: list[SubjectResponse]
    total: int = Field(..., description="Total number of subjects")
    limit: int = Field(..., description="Page size limit")
    offset: int = Field(..., description="Page offset")

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "items": [],
                "total": 0,
                "limit": 50,
                "offset": 0,
            }
        }
    )
