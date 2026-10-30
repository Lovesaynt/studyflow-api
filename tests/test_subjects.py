"""Subjects tests."""

from uuid import uuid4

from httpx import AsyncClient

from app.models.subject import Subject
from app.models.task import Task, TaskPriority, TaskStatus


class TestSubjectCreation:
    """Tests for subject creation."""

    async def test_create_subject_success(self, auth_client: AsyncClient):
        """Test creating a subject."""
        response = await auth_client.post(
            "/api/v1/subjects",
            json={"name": "Mathematics"},
        )
        assert response.status_code == 201
        data = response.json()
        assert data["name"] == "Mathematics"
        assert "id" in data
        assert "user_id" in data
        assert "created_at" in data
        assert "updated_at" in data

    async def test_create_subject_duplicate_name(self, auth_client: AsyncClient, test_subject):
        """Test creating a subject with duplicate name fails."""
        response = await auth_client.post(
            "/api/v1/subjects",
            json={"name": test_subject.name},
        )
        assert response.status_code == 409
        assert "already exists" in response.json()["detail"].lower()

    async def test_create_subject_empty_name(self, auth_client: AsyncClient):
        """Test creating a subject with empty name fails."""
        response = await auth_client.post(
            "/api/v1/subjects",
            json={"name": "   "},
        )
        assert response.status_code == 422

    async def test_create_subject_too_long_name(self, auth_client: AsyncClient):
        """Test creating a subject with too long name fails."""
        response = await auth_client.post(
            "/api/v1/subjects",
            json={"name": "A" * 101},
        )
        assert response.status_code == 422

    async def test_create_subject_without_auth(self, client: AsyncClient):
        """Test creating a subject without authentication fails."""
        response = await client.post(
            "/api/v1/subjects",
            json={"name": "Mathematics"},
        )
        assert response.status_code == 401

    async def test_create_subject_same_name_different_user(
        self, auth_client: AsyncClient, test_user2, db_session, test_subject
    ):
        """Test different users can have subjects with same name."""
        # test_subject already exists for test_user with name "Test Subject"
        # Create subject for user2 with the same name - should succeed
        subject = Subject(user_id=test_user2.id, name=test_subject.name)
        db_session.add(subject)
        await db_session.commit()
        assert subject.id is not None

        # Now create a NEW subject for test_user with a DIFFERENT name
        # (test_user already has "Test Subject" from test_subject fixture)
        response = await auth_client.post(
            "/api/v1/subjects",
            json={"name": "Another Subject"},
        )
        assert response.status_code == 201
        data = response.json()
        assert data["name"] == "Another Subject"


class TestSubjectListing:
    """Tests for subject listing."""

    async def test_list_subjects_empty(self, auth_client: AsyncClient):
        """Test listing subjects when none exist."""
        response = await auth_client.get("/api/v1/subjects")
        assert response.status_code == 200
        data = response.json()
        assert data["items"] == []
        assert data["total"] == 0

    async def test_list_subjects_with_data(self, auth_client: AsyncClient, test_subject):
        """Test listing subjects with data."""
        response = await auth_client.get("/api/v1/subjects")
        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 1
        assert len(data["items"]) == 1
        assert data["items"][0]["name"] == test_subject.name

    async def test_list_subjects_pagination(self, auth_client: AsyncClient, test_user, db_session):
        """Test subject pagination."""
        for i in range(5):
            subject = Subject(user_id=test_user.id, name=f"Subject {i}")
            db_session.add(subject)
        await db_session.commit()

        response = await auth_client.get("/api/v1/subjects?limit=2&offset=0")
        assert response.status_code == 200
        data = response.json()
        assert len(data["items"]) == 2
        assert data["total"] == 5
        assert data["limit"] == 2
        assert data["offset"] == 0

    async def test_list_subjects_isolation(self, auth_client: AsyncClient, test_user2, db_session):
        """Test subjects are isolated between users."""
        subject = Subject(user_id=test_user2.id, name="Other user subject")
        db_session.add(subject)
        await db_session.commit()

        response = await auth_client.get("/api/v1/subjects")
        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 0


class TestSubjectRetrieval:
    """Tests for getting a single subject."""

    async def test_get_subject_success(self, auth_client: AsyncClient, test_subject):
        """Test getting a subject by ID."""
        response = await auth_client.get(f"/api/v1/subjects/{test_subject.id}")
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == str(test_subject.id)
        assert data["name"] == test_subject.name

    async def test_get_subject_not_found(self, auth_client: AsyncClient):
        """Test getting a nonexistent subject fails."""
        fake_id = str(uuid4())
        response = await auth_client.get(f"/api/v1/subjects/{fake_id}")
        assert response.status_code == 404

    async def test_get_subject_other_user(self, auth_client: AsyncClient, test_user2, db_session):
        """Test getting another user's subject fails."""
        subject = Subject(user_id=test_user2.id, name="Other user subject")
        db_session.add(subject)
        await db_session.commit()
        await db_session.refresh(subject)

        response = await auth_client.get(f"/api/v1/subjects/{subject.id}")
        assert response.status_code == 404


class TestSubjectUpdate:
    """Tests for subject updates."""

    async def test_update_subject_name(self, auth_client: AsyncClient, test_subject):
        """Test updating subject name."""
        response = await auth_client.patch(
            f"/api/v1/subjects/{test_subject.id}",
            json={"name": "Advanced Mathematics"},
        )
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "Advanced Mathematics"
        assert data["id"] == str(test_subject.id)

    async def test_update_subject_duplicate_name(
        self, auth_client: AsyncClient, test_user, db_session, test_subject
    ):
        """Test updating subject to duplicate name fails."""
        # Create another subject
        other = Subject(user_id=test_user.id, name="Physics")
        db_session.add(other)
        await db_session.commit()

        # Try to rename test_subject to Physics
        response = await auth_client.patch(
            f"/api/v1/subjects/{test_subject.id}",
            json={"name": "Physics"},
        )
        assert response.status_code == 409

    async def test_update_subject_not_found(self, auth_client: AsyncClient):
        """Test updating a nonexistent subject fails."""
        fake_id = str(uuid4())
        response = await auth_client.patch(
            f"/api/v1/subjects/{fake_id}",
            json={"name": "New Name"},
        )
        assert response.status_code == 404

    async def test_update_subject_other_user(
        self, auth_client: AsyncClient, test_user2, db_session
    ):
        """Test updating another user's subject fails."""
        subject = Subject(user_id=test_user2.id, name="Other user subject")
        db_session.add(subject)
        await db_session.commit()
        await db_session.refresh(subject)

        response = await auth_client.patch(
            f"/api/v1/subjects/{subject.id}",
            json={"name": "Hacked"},
        )
        assert response.status_code == 404

    async def test_update_subject_empty_name(self, auth_client: AsyncClient, test_subject):
        """Test updating subject with empty name fails."""
        response = await auth_client.patch(
            f"/api/v1/subjects/{test_subject.id}",
            json={"name": "   "},
        )
        assert response.status_code == 422


class TestSubjectDeletion:
    """Tests for subject deletion."""

    async def test_delete_subject_success(self, auth_client: AsyncClient, test_subject):
        """Test deleting a subject."""
        response = await auth_client.delete(f"/api/v1/subjects/{test_subject.id}")
        assert response.status_code == 204

        # Verify it's gone
        response = await auth_client.get(f"/api/v1/subjects/{test_subject.id}")
        assert response.status_code == 404

    async def test_delete_subject_not_found(self, auth_client: AsyncClient):
        """Test deleting a nonexistent subject fails."""
        fake_id = str(uuid4())
        response = await auth_client.delete(f"/api/v1/subjects/{fake_id}")
        assert response.status_code == 404

    async def test_delete_subject_other_user(
        self, auth_client: AsyncClient, test_user2, db_session
    ):
        """Test deleting another user's subject fails."""
        subject = Subject(user_id=test_user2.id, name="Other user subject")
        db_session.add(subject)
        await db_session.commit()
        await db_session.refresh(subject)

        response = await auth_client.delete(f"/api/v1/subjects/{subject.id}")
        assert response.status_code == 404

    async def test_delete_subject_with_associated_tasks(
        self, auth_client: AsyncClient, test_user, test_subject, db_session
    ):
        """Test deleting a subject that has associated tasks."""
        # Create a task with this subject
        task = Task(
            user_id=test_user.id,
            subject_id=test_subject.id,
            title="Task with subject",
            priority=TaskPriority.MEDIUM,
            status=TaskStatus.PENDING,
        )
        db_session.add(task)
        await db_session.commit()

        # Delete the subject - should succeed but leave task with orphaned subject_id
        response = await auth_client.delete(f"/api/v1/subjects/{test_subject.id}")
        assert response.status_code == 204

        # Verify subject is deleted
        response = await auth_client.get("/api/v1/subjects")
        assert response.status_code == 200
        assert response.json()["total"] == 0

        # Verify task still exists but subject_id remains
        response = await auth_client.get("/api/v1/tasks")
        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 1
        assert data["items"][0]["subject_id"] == str(test_subject.id)


class TestDataIsolation:
    """Tests for user data isolation for subjects."""

    async def test_user_cannot_see_other_user_subjects(
        self, auth_client: AsyncClient, test_user2, db_session
    ):
        """Test user cannot see another user's subjects."""
        subject = Subject(user_id=test_user2.id, name="Other user subject")
        db_session.add(subject)
        await db_session.commit()

        response = await auth_client.get("/api/v1/subjects")
        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 0

    async def test_user_cannot_access_other_user_subject(
        self, auth_client: AsyncClient, test_user2, db_session
    ):
        """Test user cannot access another user's subject by ID."""
        subject = Subject(user_id=test_user2.id, name="Other user subject")
        db_session.add(subject)
        await db_session.commit()
        await db_session.refresh(subject)

        # Try to get
        response = await auth_client.get(f"/api/v1/subjects/{subject.id}")
        assert response.status_code == 404

        # Try to update
        response = await auth_client.patch(
            f"/api/v1/subjects/{subject.id}",
            json={"name": "Hacked"},
        )
        assert response.status_code == 404

        # Try to delete
        response = await auth_client.delete(f"/api/v1/subjects/{subject.id}")
        assert response.status_code == 404
