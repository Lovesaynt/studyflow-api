"""Subjects routes."""

from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user_id
from app.db.session import get_db
from app.schemas.subject import SubjectCreate, SubjectListResponse, SubjectResponse, SubjectUpdate
from app.services.subjects import SubjectService

router = APIRouter(prefix="/subjects", tags=["Subjects"])


@router.post(
    "",
    response_model=SubjectResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new subject",
)
async def create_subject(
    subject_data: SubjectCreate,
    user_id: UUID = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
) -> SubjectResponse:
    """
    Create a new subject for the authenticated user.

    - **name**: Subject name (required, max 100 chars, unique per user)
    """
    subject_service = SubjectService(db)
    try:
        return await subject_service.create(user_id, subject_data)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(e)) from e


@router.get(
    "",
    response_model=SubjectListResponse,
    summary="List all subjects for the authenticated user",
)
async def list_subjects(
    limit: int = 50,
    offset: int = 0,
    user_id: UUID = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
) -> SubjectListResponse:
    """
    List all subjects for the authenticated user with pagination.

    - **limit**: Maximum number of subjects to return (default 50)
    - **offset**: Number of subjects to skip (default 0)
    """
    subject_service = SubjectService(db)
    return await subject_service.get_list(user_id, limit=limit, offset=offset)


@router.get(
    "/{subject_id}",
    response_model=SubjectResponse,
    summary="Get a subject by ID",
)
async def get_subject(
    subject_id: UUID,
    user_id: UUID = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
) -> SubjectResponse:
    """
    Get a specific subject by ID (only if owned by the authenticated user).
    """
    subject_service = SubjectService(db)
    try:
        return await subject_service.get_by_id(user_id, subject_id)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e)) from e


@router.patch(
    "/{subject_id}",
    response_model=SubjectResponse,
    summary="Update a subject (partial update)",
)
async def update_subject(
    subject_id: UUID,
    subject_data: SubjectUpdate,
    user_id: UUID = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
) -> SubjectResponse:
    """
    Update a subject (partial update - only provided fields are updated).

    - **name**: Subject name (optional, max 100 chars, unique per user)
    """
    subject_service = SubjectService(db)
    try:
        return await subject_service.update(user_id, subject_id, subject_data)
    except ValueError as e:
        if "already exists" in str(e):
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(e)) from e
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e)) from e


@router.delete(
    "/{subject_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete a subject",
)
async def delete_subject(
    subject_id: UUID,
    user_id: UUID = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
) -> None:
    """
    Delete a subject (only if owned by the authenticated user).
    """
    subject_service = SubjectService(db)
    try:
        await subject_service.delete(user_id, subject_id)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e)) from e
