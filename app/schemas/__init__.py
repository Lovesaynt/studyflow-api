"""Schemas module."""

from app.schemas.auth import TokenResponse, UserLogin, UserRegister, UserResponse
from app.schemas.dashboard import DashboardSummary
from app.schemas.subject import (
    SubjectCreate,
    SubjectListResponse,
    SubjectResponse,
    SubjectUpdate,
)
from app.schemas.task import (
    TaskCreate,
    TaskListResponse,
    TaskResponse,
    TaskUpdate,
)

__all__ = [
    # Auth
    "UserRegister",
    "UserLogin",
    "TokenResponse",
    "UserResponse",
    # Subject
    "SubjectCreate",
    "SubjectUpdate",
    "SubjectResponse",
    "SubjectListResponse",
    # Task
    "TaskCreate",
    "TaskUpdate",
    "TaskResponse",
    "TaskListResponse",
    # Dashboard
    "DashboardSummary",
]
