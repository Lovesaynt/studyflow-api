"""Dashboard tests."""

from datetime import UTC, datetime, timedelta

from httpx import AsyncClient

from app.models.subject import Subject
from app.models.task import Task, TaskStatus


class TestDashboardSummary:
    """Tests for dashboard summary endpoint."""

    async def test_dashboard_empty(self, auth_client: AsyncClient):
        """Test dashboard with no tasks or subjects."""
        response = await auth_client.get("/api/v1/dashboard/summary")
        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 0
        assert data["pending"] == 0
        assert data["in_progress"] == 0
        assert data["completed"] == 0
        assert data["overdue"] == 0
        assert data["subjects"] == 0

    async def test_dashboard_with_tasks(self, auth_client: AsyncClient, test_user, db_session):
        """Test dashboard with various task statuses."""

        # Create tasks with different statuses
        tasks = [
            Task(user_id=test_user.id, title="Pending 1", status=TaskStatus.PENDING),
            Task(user_id=test_user.id, title="Pending 2", status=TaskStatus.PENDING),
            Task(user_id=test_user.id, title="In Progress", status=TaskStatus.IN_PROGRESS),
            Task(user_id=test_user.id, title="Completed 1", status=TaskStatus.COMPLETED),
            Task(user_id=test_user.id, title="Completed 2", status=TaskStatus.COMPLETED),
        ]
        db_session.add_all(tasks)
        await db_session.commit()

        response = await auth_client.get("/api/v1/dashboard/summary")
        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 5
        assert data["pending"] == 2
        assert data["in_progress"] == 1
        assert data["completed"] == 2
        assert data["overdue"] == 0

    async def test_dashboard_with_subjects(self, auth_client: AsyncClient, test_user, db_session):
        """Test dashboard with subjects."""

        for i in range(3):
            subject = Subject(user_id=test_user.id, name=f"Subject {i}")
            db_session.add(subject)
        await db_session.commit()

        response = await auth_client.get("/api/v1/dashboard/summary")
        assert response.status_code == 200
        data = response.json()
        assert data["subjects"] == 3

    async def test_dashboard_overdue_tasks(self, auth_client: AsyncClient, test_user, db_session):
        """Test dashboard overdue calculation."""

        now = datetime.now(UTC)
        past = now - timedelta(days=1)
        future = now + timedelta(days=1)

        tasks = [
            Task(
                user_id=test_user.id,
                title="Overdue pending",
                due_date=past,
                status=TaskStatus.PENDING,
            ),
            Task(
                user_id=test_user.id,
                title="Overdue in_progress",
                due_date=past,
                status=TaskStatus.IN_PROGRESS,
            ),
            Task(
                user_id=test_user.id, title="Future due", due_date=future, status=TaskStatus.PENDING
            ),
            Task(
                user_id=test_user.id,
                title="Completed overdue",
                due_date=past,
                status=TaskStatus.COMPLETED,
            ),
            Task(
                user_id=test_user.id, title="No due date", due_date=None, status=TaskStatus.PENDING
            ),
        ]
        db_session.add_all(tasks)
        await db_session.commit()

        response = await auth_client.get("/api/v1/dashboard/summary")
        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 5
        # Overdue = past due AND not completed
        assert data["overdue"] == 2  # pending + in_progress with past due date

    async def test_dashboard_completed_overdue_not_counted(
        self, auth_client: AsyncClient, test_user, db_session
    ):
        """Test that completed tasks with past due dates are not counted as overdue."""

        past = datetime.now(UTC) - timedelta(days=1)

        tasks = [
            Task(
                user_id=test_user.id,
                title="Completed overdue",
                due_date=past,
                status=TaskStatus.COMPLETED,
            ),
            Task(
                user_id=test_user.id,
                title="Another completed overdue",
                due_date=past,
                status=TaskStatus.COMPLETED,
            ),
        ]
        db_session.add_all(tasks)
        await db_session.commit()

        response = await auth_client.get("/api/v1/dashboard/summary")
        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 2
        assert data["completed"] == 2
        assert data["overdue"] == 0  # Completed tasks should not be overdue

    async def test_dashboard_isolation(self, auth_client: AsyncClient, test_user2, db_session):
        """Test dashboard only shows current user's data."""
        from app.models.subject import Subject

        # Create data for other user
        subject = Subject(user_id=test_user2.id, name="Other subject")
        task = Task(user_id=test_user2.id, title="Other task", status=TaskStatus.PENDING)
        db_session.add_all([subject, task])
        await db_session.commit()

        response = await auth_client.get("/api/v1/dashboard/summary")
        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 0
        assert data["subjects"] == 0

    async def test_dashboard_without_auth(self, client: AsyncClient):
        """Test dashboard without authentication fails."""
        response = await client.get("/api/v1/dashboard/summary")
        assert response.status_code == 401

    async def test_dashboard_combined(
        self, auth_client: AsyncClient, test_user, test_subject, db_session
    ):
        """Test dashboard with combined tasks and subjects."""

        # Create tasks with various statuses and due dates
        now = datetime.now(UTC)
        past = now - timedelta(hours=2)
        future = now + timedelta(days=1)

        tasks = [
            Task(
                user_id=test_user.id,
                title="Pending overdue",
                due_date=past,
                status=TaskStatus.PENDING,
            ),
            Task(
                user_id=test_user.id,
                title="In progress",
                due_date=future,
                status=TaskStatus.IN_PROGRESS,
            ),
            Task(
                user_id=test_user.id, title="Completed", due_date=past, status=TaskStatus.COMPLETED
            ),
            Task(
                user_id=test_user.id,
                title="Pending future",
                due_date=future,
                status=TaskStatus.PENDING,
            ),
        ]
        db_session.add_all(tasks)
        await db_session.commit()

        response = await auth_client.get("/api/v1/dashboard/summary")
        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 4
        assert data["pending"] == 2
        assert data["in_progress"] == 1
        assert data["completed"] == 1
        assert data["overdue"] == 1  # Only "Pending overdue"
        assert data["subjects"] == 1
