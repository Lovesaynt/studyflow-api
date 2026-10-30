"""Tasks tests."""

from datetime import UTC, datetime, timedelta
from uuid import uuid4

from httpx import AsyncClient

from app.models.subject import Subject
from app.models.task import Task


class TestTaskCreation:
    """Tests for task creation."""

    async def test_create_task_minimal(self, auth_client: AsyncClient):
        """Test creating a task with minimal required fields."""
        response = await auth_client.post(
            "/api/v1/tasks",
            json={"title": "Test Task"},
        )
        assert response.status_code == 201
        data = response.json()
        assert data["title"] == "Test Task"
        assert data["description"] is None
        assert data["priority"] == "medium"
        assert data["status"] == "pending"
        assert data["due_date"] is None
        assert data["subject_id"] is None
        assert "id" in data
        assert "user_id" in data
        assert "created_at" in data
        assert "updated_at" in data

    async def test_create_task_full(self, auth_client: AsyncClient, test_subject):
        """Test creating a task with all fields."""
        response = await auth_client.post(
            "/api/v1/tasks",
            json={
                "title": "Complete homework",
                "description": "Solve problems 1-10",
                "priority": "high",
                "status": "in_progress",
                "due_date": "2024-12-31T23:59:00Z",
                "subject_id": str(test_subject.id),
            },
        )
        assert response.status_code == 201
        data = response.json()
        assert data["title"] == "Complete homework"
        assert data["description"] == "Solve problems 1-10"
        assert data["priority"] == "high"
        assert data["status"] == "in_progress"
        assert data["subject_id"] == str(test_subject.id)

    async def test_create_task_with_subject_id(self, auth_client: AsyncClient, test_subject):
        """Test creating a task with a valid subject."""
        response = await auth_client.post(
            "/api/v1/tasks",
            json={
                "title": "Task with subject",
                "subject_id": str(test_subject.id),
            },
        )
        assert response.status_code == 201
        assert response.json()["subject_id"] == str(test_subject.id)

    async def test_create_task_with_invalid_subject_id(self, auth_client: AsyncClient):
        """Test creating a task with invalid subject ID fails."""
        fake_id = str(uuid4())
        response = await auth_client.post(
            "/api/v1/tasks",
            json={
                "title": "Task with invalid subject",
                "subject_id": fake_id,
            },
        )
        assert response.status_code == 404
        assert "subject not found" in response.json()["detail"].lower()

    async def test_create_task_with_other_user_subject(
        self, auth_client: AsyncClient, test_user2, db_session
    ):
        """Test creating a task with another user's subject fails."""
        # Create a subject for user2
        subject = Subject(user_id=test_user2.id, name="Other User Subject")
        db_session.add(subject)
        await db_session.commit()
        await db_session.refresh(subject)

        response = await auth_client.post(
            "/api/v1/tasks",
            json={
                "title": "Task with other user subject",
                "subject_id": str(subject.id),
            },
        )
        assert response.status_code == 404

    async def test_create_task_invalid_priority(self, auth_client: AsyncClient):
        """Test creating a task with invalid priority fails."""
        response = await auth_client.post(
            "/api/v1/tasks",
            json={"title": "Test", "priority": "urgent"},
        )
        assert response.status_code == 422

    async def test_create_task_invalid_status(self, auth_client: AsyncClient):
        """Test creating a task with invalid status fails."""
        response = await auth_client.post(
            "/api/v1/tasks",
            json={"title": "Test", "status": "done"},
        )
        assert response.status_code == 422

    async def test_create_task_empty_title(self, auth_client: AsyncClient):
        """Test creating a task with empty title fails."""
        response = await auth_client.post(
            "/api/v1/tasks",
            json={"title": "   "},
        )
        assert response.status_code == 422

    async def test_create_task_without_auth(self, client: AsyncClient):
        """Test creating a task without authentication fails."""
        response = await client.post(
            "/api/v1/tasks",
            json={"title": "Test Task"},
        )
        assert response.status_code == 401

    async def test_create_task_with_subject_id_null(self, auth_client: AsyncClient):
        """Test creating a task with explicit null subject_id."""
        response = await auth_client.post(
            "/api/v1/tasks",
            json={"title": "Test", "subject_id": None},
        )
        assert response.status_code == 201
        assert response.json()["subject_id"] is None


class TestTaskListing:
    """Tests for task listing."""

    async def test_list_tasks_empty(self, auth_client: AsyncClient):
        """Test listing tasks when none exist."""
        response = await auth_client.get("/api/v1/tasks")
        assert response.status_code == 200
        data = response.json()
        assert data["items"] == []
        assert data["total"] == 0
        assert data["limit"] == 20
        assert data["offset"] == 0

    async def test_list_tasks_with_data(self, auth_client: AsyncClient, test_task):
        """Test listing tasks with data."""
        response = await auth_client.get("/api/v1/tasks")
        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 1
        assert len(data["items"]) == 1
        assert data["items"][0]["title"] == test_task.title

    async def test_list_tasks_pagination(self, auth_client: AsyncClient, test_user, db_session):
        """Test task pagination."""
        # Create multiple tasks
        for i in range(5):
            task = Task(
                user_id=test_user.id,
                title=f"Task {i}",
                priority="medium",
                status="pending",
            )
            db_session.add(task)
        await db_session.commit()

        # Test first page
        response = await auth_client.get("/api/v1/tasks?limit=2&offset=0")
        assert response.status_code == 200
        data = response.json()
        assert len(data["items"]) == 2
        assert data["total"] == 5
        assert data["limit"] == 2
        assert data["offset"] == 0

        # Test second page
        response = await auth_client.get("/api/v1/tasks?limit=2&offset=2")
        assert response.status_code == 200
        data = response.json()
        assert len(data["items"]) == 2
        assert data["offset"] == 2

        # Test third page (only 1 item)
        response = await auth_client.get("/api/v1/tasks?limit=2&offset=4")
        assert response.status_code == 200
        data = response.json()
        assert len(data["items"]) == 1
        assert data["offset"] == 4

    async def test_list_tasks_limit_validation(self, auth_client: AsyncClient):
        """Test limit validation."""
        response = await auth_client.get("/api/v1/tasks?limit=0")
        assert response.status_code == 422

        response = await auth_client.get("/api/v1/tasks?limit=101")
        assert response.status_code == 422

    async def test_list_tasks_offset_validation(self, auth_client: AsyncClient):
        """Test offset validation."""
        response = await auth_client.get("/api/v1/tasks?offset=-1")
        assert response.status_code == 422


class TestTaskFiltering:
    """Tests for task filtering."""

    async def test_filter_by_status(self, auth_client: AsyncClient, test_user, db_session):
        """Test filtering tasks by status."""
        # Create tasks with different statuses
        for status in ["pending", "in_progress", "completed"]:
            task = Task(
                user_id=test_user.id,
                title=f"{status} task",
                status=status,
            )
            db_session.add(task)
        await db_session.commit()

        # Filter by pending
        response = await auth_client.get("/api/v1/tasks?status=pending")
        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 1
        assert data["items"][0]["status"] == "pending"

        # Filter by completed
        response = await auth_client.get("/api/v1/tasks?status=completed")
        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 1
        assert data["items"][0]["status"] == "completed"

    async def test_filter_by_priority(self, auth_client: AsyncClient, test_user, db_session):
        """Test filtering tasks by priority."""
        for priority in ["low", "medium", "high"]:
            task = Task(
                user_id=test_user.id,
                title=f"{priority} priority task",
                priority=priority,
            )
            db_session.add(task)
        await db_session.commit()

        response = await auth_client.get("/api/v1/tasks?priority=high")
        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 1
        assert data["items"][0]["priority"] == "high"

    async def test_filter_by_subject_id(
        self, auth_client: AsyncClient, test_user, test_subject, db_session
    ):
        """Test filtering tasks by subject."""
        # Create task with subject
        task1 = Task(user_id=test_user.id, title="With subject", subject_id=test_subject.id)
        # Create task without subject
        task2 = Task(user_id=test_user.id, title="Without subject", subject_id=None)
        db_session.add_all([task1, task2])
        await db_session.commit()

        response = await auth_client.get(f"/api/v1/tasks?subject_id={test_subject.id}")
        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 1
        assert data["items"][0]["subject_id"] == str(test_subject.id)

    async def test_filter_by_due_before(self, auth_client: AsyncClient, test_user, db_session):
        """Test filtering tasks by due_before."""
        now = datetime.now(UTC).replace(microsecond=0)
        past = now - timedelta(days=1)
        future = now + timedelta(days=1)

        task1 = Task(user_id=test_user.id, title="Past due", due_date=past)
        task2 = Task(user_id=test_user.id, title="Future due", due_date=future)
        task3 = Task(user_id=test_user.id, title="No due date", due_date=None)
        db_session.add_all([task1, task2, task3])
        await db_session.commit()

        # Should include past due and no due date? No, only past due and future due
        # due_before filters tasks due before the given date
        # Use Z format for URL compatibility (FastAPI doesn't parse +00:00 in query params)
        future_iso = future.strftime("%Y-%m-%dT%H:%M:%SZ")
        response = await auth_client.get(f"/api/v1/tasks?due_before={future_iso}")
        assert response.status_code == 200
        data = response.json()
        # Should include both past due and future due (both are <= future)
        # Note: future due task has due_date == future, so it's <= future (inclusive)
        assert data["total"] == 2
        titles = {item["title"] for item in data["items"]}
        assert titles == {"Past due", "Future due"}

    async def test_filter_by_due_after(self, auth_client: AsyncClient, test_user, db_session):
        """Test filtering tasks by due_after."""
        now = datetime.now(UTC).replace(microsecond=0)
        past = now - timedelta(days=1)
        future = now + timedelta(days=1)

        task1 = Task(user_id=test_user.id, title="Past due", due_date=past)
        task2 = Task(user_id=test_user.id, title="Future due", due_date=future)
        task3 = Task(user_id=test_user.id, title="No due date", due_date=None)
        db_session.add_all([task1, task2, task3])
        await db_session.commit()

        # Use Z format for URL compatibility
        past_iso = past.strftime("%Y-%m-%dT%H:%M:%SZ")
        response = await auth_client.get(f"/api/v1/tasks?due_after={past_iso}")
        assert response.status_code == 200
        data = response.json()
        # Should include future due task only (past due is exactly at boundary, not after)
        assert data["total"] == 1
        assert data["items"][0]["title"] == "Future due"

    async def test_filter_combined(
        self, auth_client: AsyncClient, test_user, test_subject, db_session
    ):
        """Test combined filtering."""
        # Create various tasks
        tasks = [
            Task(
                user_id=test_user.id,
                title="High priority pending",
                priority="high",
                status="pending",
                subject_id=test_subject.id,
            ),
            Task(
                user_id=test_user.id,
                title="Low priority completed",
                priority="low",
                status="completed",
                subject_id=test_subject.id,
            ),
            Task(
                user_id=test_user.id,
                title="Medium priority in_progress",
                priority="medium",
                status="in_progress",
                subject_id=None,
            ),
        ]
        db_session.add_all(tasks)
        await db_session.commit()

        response = await auth_client.get("/api/v1/tasks?priority=high&status=pending")
        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 1
        assert data["items"][0]["title"] == "High priority pending"


class TestTaskRetrieval:
    """Tests for getting a single task."""

    async def test_get_task_success(self, auth_client: AsyncClient, test_task):
        """Test getting a task by ID."""
        response = await auth_client.get(f"/api/v1/tasks/{test_task.id}")
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == str(test_task.id)
        assert data["title"] == test_task.title

    async def test_get_task_not_found(self, auth_client: AsyncClient):
        """Test getting a nonexistent task fails."""
        fake_id = str(uuid4())
        response = await auth_client.get(f"/api/v1/tasks/{fake_id}")
        assert response.status_code == 404

    async def test_get_task_other_user(self, auth_client: AsyncClient, test_user2, db_session):
        """Test getting another user's task fails."""
        task = Task(user_id=test_user2.id, title="Other user task")
        db_session.add(task)
        await db_session.commit()
        await db_session.refresh(task)

        response = await auth_client.get(f"/api/v1/tasks/{task.id}")
        assert response.status_code == 404


class TestTaskUpdate:
    """Tests for task updates."""

    async def test_update_task_status(self, auth_client: AsyncClient, test_task):
        """Test updating task status."""
        response = await auth_client.patch(
            f"/api/v1/tasks/{test_task.id}",
            json={"status": "completed"},
        )
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "completed"
        assert data["title"] == test_task.title  # Unchanged

    async def test_update_task_priority(self, auth_client: AsyncClient, test_task):
        """Test updating task priority."""
        response = await auth_client.patch(
            f"/api/v1/tasks/{test_task.id}",
            json={"priority": "high"},
        )
        assert response.status_code == 200
        assert response.json()["priority"] == "high"

    async def test_update_task_title(self, auth_client: AsyncClient, test_task):
        """Test updating task title."""
        response = await auth_client.patch(
            f"/api/v1/tasks/{test_task.id}",
            json={"title": "Updated Title"},
        )
        assert response.status_code == 200
        assert response.json()["title"] == "Updated Title"

    async def test_update_task_description(self, auth_client: AsyncClient, test_task):
        """Test updating task description."""
        response = await auth_client.patch(
            f"/api/v1/tasks/{test_task.id}",
            json={"description": "New description"},
        )
        assert response.status_code == 200
        assert response.json()["description"] == "New description"

    async def test_update_task_due_date(self, auth_client: AsyncClient, test_task):
        """Test updating task due date."""
        new_date = "2025-01-01T12:00:00Z"
        response = await auth_client.patch(
            f"/api/v1/tasks/{test_task.id}",
            json={"due_date": new_date},
        )
        assert response.status_code == 200
        # Response may not include 'Z' suffix, compare as datetime
        assert response.json()["due_date"].startswith("2025-01-01T12:00:00")

    async def test_update_task_subject_id(self, auth_client: AsyncClient, test_task, test_subject):
        """Test updating task subject."""
        response = await auth_client.patch(
            f"/api/v1/tasks/{test_task.id}",
            json={"subject_id": str(test_subject.id)},
        )
        assert response.status_code == 200
        assert response.json()["subject_id"] == str(test_subject.id)

    async def test_update_task_remove_subject(self, auth_client: AsyncClient, test_task):
        """Test removing subject from task."""
        response = await auth_client.patch(
            f"/api/v1/tasks/{test_task.id}",
            json={"subject_id": None},
        )
        assert response.status_code == 200
        assert response.json()["subject_id"] is None

    async def test_update_task_invalid_subject(self, auth_client: AsyncClient, test_task):
        """Test updating task with invalid subject fails."""
        fake_id = str(uuid4())
        response = await auth_client.patch(
            f"/api/v1/tasks/{test_task.id}",
            json={"subject_id": fake_id},
        )
        assert response.status_code == 404

    async def test_update_task_other_user(self, auth_client: AsyncClient, test_user2, db_session):
        """Test updating another user's task fails."""
        task = Task(user_id=test_user2.id, title="Other user task")
        db_session.add(task)
        await db_session.commit()
        await db_session.refresh(task)

        response = await auth_client.patch(
            f"/api/v1/tasks/{task.id}",
            json={"title": "Hacked"},
        )
        assert response.status_code == 404

    async def test_update_task_partial(self, auth_client: AsyncClient, test_task):
        """Test partial update preserves other fields."""
        original_priority = test_task.priority
        original_status = test_task.status

        response = await auth_client.patch(
            f"/api/v1/tasks/{test_task.id}",
            json={"title": "New Title"},
        )
        assert response.status_code == 200
        data = response.json()
        assert data["title"] == "New Title"
        assert data["priority"] == original_priority
        assert data["status"] == original_status


class TestTaskDeletion:
    """Tests for task deletion."""

    async def test_delete_task_success(self, auth_client: AsyncClient, test_task):
        """Test deleting a task."""
        response = await auth_client.delete(f"/api/v1/tasks/{test_task.id}")
        assert response.status_code == 204

        # Verify it's gone
        response = await auth_client.get(f"/api/v1/tasks/{test_task.id}")
        assert response.status_code == 404

    async def test_delete_task_not_found(self, auth_client: AsyncClient):
        """Test deleting a nonexistent task fails."""
        fake_id = str(uuid4())
        response = await auth_client.delete(f"/api/v1/tasks/{fake_id}")
        assert response.status_code == 404

    async def test_delete_task_other_user(self, auth_client: AsyncClient, test_user2, db_session):
        """Test deleting another user's task fails."""
        task = Task(user_id=test_user2.id, title="Other user task")
        db_session.add(task)
        await db_session.commit()
        await db_session.refresh(task)

        response = await auth_client.delete(f"/api/v1/tasks/{task.id}")
        assert response.status_code == 404


class TestDataIsolation:
    """Tests for user data isolation."""

    async def test_user_cannot_see_other_user_tasks(
        self, auth_client: AsyncClient, test_user2, db_session
    ):
        """Test user cannot see another user's tasks."""
        task = Task(user_id=test_user2.id, title="Other user task")
        db_session.add(task)
        await db_session.commit()

        response = await auth_client.get("/api/v1/tasks")
        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 0

    async def test_user_cannot_create_task_with_other_user_subject(
        self, auth_client: AsyncClient, test_user2, db_session
    ):
        """Test user cannot create task with another user's subject."""
        subject = Subject(user_id=test_user2.id, name="Other user subject")
        db_session.add(subject)
        await db_session.commit()
        await db_session.refresh(subject)

        response = await auth_client.post(
            "/api/v1/tasks",
            json={"title": "Test", "subject_id": str(subject.id)},
        )
        assert response.status_code == 404

    async def test_user_cannot_update_task_with_other_user_subject(
        self, auth_client: AsyncClient, test_task, test_user2, db_session
    ):
        """Test user cannot update task with another user's subject."""
        subject = Subject(user_id=test_user2.id, name="Other user subject")
        db_session.add(subject)
        await db_session.commit()
        await db_session.refresh(subject)

        response = await auth_client.patch(
            f"/api/v1/tasks/{test_task.id}",
            json={"subject_id": str(subject.id)},
        )
        assert response.status_code == 404
