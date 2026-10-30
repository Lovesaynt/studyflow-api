"""Dashboard schemas."""

from pydantic import BaseModel, ConfigDict, Field


class DashboardSummary(BaseModel):
    """Schema for dashboard productivity summary."""

    total: int = Field(..., description="Total number of tasks")
    pending: int = Field(..., description="Number of pending tasks")
    in_progress: int = Field(..., description="Number of tasks in progress")
    completed: int = Field(..., description="Number of completed tasks")
    overdue: int = Field(
        ..., description="Number of overdue tasks (not completed and past due date)"
    )
    subjects: int = Field(..., description="Number of subjects")

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "total": 25,
                "pending": 10,
                "in_progress": 5,
                "completed": 8,
                "overdue": 2,
                "subjects": 4,
            }
        }
    )
