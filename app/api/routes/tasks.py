"""Tasks routes."""

from datetime import datetime
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user_id
from app.db.session import get_db
from app.models.task import TaskPriority, TaskStatus
from app.schemas.task import TaskCreate, TaskListResponse, TaskResponse, TaskUpdate
from app.services.tasks import TaskService

router = APIRouter(prefix="/tasks", tags=["Tasks"])


@router.post(
    "",
    response_model=TaskResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new task",
)
async def create_task(
    task_data: TaskCreate,
    user_id: UUID = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
) -> TaskResponse:
    """
    Create a new task for the authenticated user.

    - **title**: Task title (required, max 150 chars)
    - **description**: Task description (optional)
    - **priority**: Task priority - low, medium, high (default: medium)
    - **status**: Task status - pending, in_progress, completed (default: pending)
    - **due_date**: Task due date (optional, ISO 8601 format)
    - **subject_id**: Subject UUID (optional, must belong to user)
    """
    task_service = TaskService(db)
    try:
        return await task_service.create(user_id, task_data)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e)) from e


@router.get(
    "",
    response_model=TaskListResponse,
    summary="List tasks with filtering and pagination",
)
async def list_tasks(
    status: str | None = Query(
        default=None, description="Filter by status (pending, in_progress, completed)"
    ),
    priority: str | None = Query(
        default=None, description="Filter by priority (low, medium, high)"
    ),
    subject_id: UUID | None = Query(default=None, description="Filter by subject"),
    due_before: datetime | None = Query(
        default=None, description="Filter tasks due before this date"
    ),
    due_after: datetime | None = Query(
        default=None, description="Filter tasks due after this date"
    ),
    limit: int = Query(default=20, ge=1, le=100, description="Page size (1-100)"),
    offset: int = Query(default=0, ge=0, description="Page offset"),
    user_id: UUID = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
) -> TaskListResponse:
    """
    List tasks for the authenticated user with filtering and pagination.

    Filters (all optional):
    - **status**: pending, in_progress, completed
    - **priority**: low, medium, high
    - **subject_id**: UUID of subject
    - **due_before**: ISO 8601 datetime (e.g., 2024-01-20T23:59:00Z)
    - **due_after**: ISO 8601 datetime

    Pagination:
    - **limit**: Page size (1-100, default 20)
    - **offset**: Page offset (default 0)
    """
    task_service = TaskService(db)

    # Convert string filters to enums if provided
    status_enum = TaskStatus(status) if status else None
    priority_enum = TaskPriority(priority) if priority else None

    return await task_service.get_list(
        user_id,
        status=status_enum,
        priority=priority_enum,
        subject_id=subject_id,
        due_before=due_before,
        due_after=due_after,
        limit=limit,
        offset=offset,
    )


@router.get(
    "/{task_id}",
    response_model=TaskResponse,
    summary="Get a task by ID",
)
async def get_task(
    task_id: UUID,
    user_id: UUID = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
) -> TaskResponse:
    """
    Get a specific task by ID (only if owned by the authenticated user).
    """
    task_service = TaskService(db)
    try:
        return await task_service.get_by_id(user_id, task_id)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e)) from e


@router.patch(
    "/{task_id}",
    response_model=TaskResponse,
    summary="Update a task (partial update)",
)
async def update_task(
    task_id: UUID,
    task_data: TaskUpdate,
    user_id: UUID = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
) -> TaskResponse:
    """
    Update a task (partial update - only provided fields are updated).

    - **title**: Task title (optional, max 150 chars)
    - **description**: Task description (optional)
    - **priority**: Task priority - low, medium, high (optional)
    - **status**: Task status - pending, in_progress, completed (optional)
    - **due_date**: Task due date (optional, ISO 8601 format)
    - **subject_id**: Subject UUID (optional, must belong to user; null to remove)
    """
    task_service = TaskService(db)
    try:
        return await task_service.update(user_id, task_id, task_data)
    except ValueError as e:
        if "Subject not found" in str(e):
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e)) from e
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e)) from e


@router.delete(
    "/{task_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete a task",
)
async def delete_task(
    task_id: UUID,
    user_id: UUID = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
) -> None:
    """
    Delete a task (only if owned by the authenticated user).
    """
    task_service = TaskService(db)
    try:
        await task_service.delete(user_id, task_id)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e)) from e
