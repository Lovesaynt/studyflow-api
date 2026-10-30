"""Dashboard routes."""

from uuid import UUID

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user_id
from app.db.session import get_db
from app.schemas.dashboard import DashboardSummary
from app.services.dashboard import DashboardService

router = APIRouter(prefix="/dashboard", tags=["Dashboard"])


@router.get(
    "/summary",
    response_model=DashboardSummary,
    summary="Get productivity dashboard summary",
)
async def get_dashboard_summary(
    user_id: UUID = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
) -> DashboardSummary:
    """
    Get productivity dashboard summary for the authenticated user.

    Returns:
    - **total**: Total number of tasks
    - **pending**: Number of pending tasks
    - **in_progress**: Number of tasks in progress
    - **completed**: Number of completed tasks
    - **overdue**: Number of overdue tasks (due date < now AND not completed)
    """
    dashboard_service = DashboardService(db)
    return await dashboard_service.get_summary(user_id)
