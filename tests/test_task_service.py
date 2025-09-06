"""Tests for the task service layer."""

import pytest
from datetime import date, datetime
from app.database import reset_db, get_session
from app.task_service import TaskService
from app.models import TaskCreate, TaskUpdate, TaskPriority


@pytest.fixture()
def new_db():
    """Clean database for each test."""
    reset_db()
    yield
    reset_db()


@pytest.fixture()
def task_service(new_db):
    """Task service with clean database."""
    session = get_session()
    service = TaskService(session)
    yield service
    service.close()


class TestTaskCreation:
    """Test task creation functionality."""

    def test_create_basic_task(self, task_service: TaskService):
        """Test creating a basic task with minimal data."""
        task_data = TaskCreate(title="Test Task")
        task = task_service.create_task(task_data)

        assert task.id is not None
        assert task.title == "Test Task"
        assert task.description == ""
        assert not task.completed
        assert task.priority == TaskPriority.MEDIUM
        assert task.due_date is None
        assert isinstance(task.created_at, datetime)
        assert isinstance(task.updated_at, datetime)

    def test_create_task_with_all_fields(self, task_service: TaskService):
        """Test creating a task with all fields populated."""
        due_date = date.today()
        task_data = TaskCreate(
            title="Complete project",
            description="Finish the todo app implementation",
            priority=TaskPriority.HIGH,
            due_date=due_date,
        )
        task = task_service.create_task(task_data)

        assert task.title == "Complete project"
        assert task.description == "Finish the todo app implementation"
        assert task.priority == TaskPriority.HIGH
        assert task.due_date == due_date

    def test_create_task_with_different_priorities(self, task_service: TaskService):
        """Test creating tasks with different priority levels."""
        priorities = [TaskPriority.LOW, TaskPriority.MEDIUM, TaskPriority.HIGH, TaskPriority.URGENT]

        for priority in priorities:
            task_data = TaskCreate(title=f"Task with {priority.value} priority", priority=priority)
            task = task_service.create_task(task_data)
            assert task.priority == priority


class TestTaskRetrieval:
    """Test task retrieval functionality."""

    def test_get_all_tasks_empty(self, task_service: TaskService):
        """Test getting all tasks when database is empty."""
        tasks = task_service.get_all_tasks()
        assert tasks == []

    def test_get_all_tasks_with_data(self, task_service: TaskService):
        """Test getting all tasks with data."""
        # Create test tasks
        task1_data = TaskCreate(title="First task")
        task2_data = TaskCreate(title="Second task")

        task1 = task_service.create_task(task1_data)
        task2 = task_service.create_task(task2_data)

        tasks = task_service.get_all_tasks()
        assert len(tasks) == 2
        # Should be ordered by created_at desc (newest first)
        assert tasks[0].id == task2.id
        assert tasks[1].id == task1.id

    def test_get_task_by_id_existing(self, task_service: TaskService):
        """Test getting an existing task by ID."""
        task_data = TaskCreate(title="Test task")
        created_task = task_service.create_task(task_data)

        assert created_task.id is not None
        retrieved_task = task_service.get_task(created_task.id)
        assert retrieved_task is not None
        assert retrieved_task.id == created_task.id
        assert retrieved_task.title == "Test task"

    def test_get_task_by_id_nonexistent(self, task_service: TaskService):
        """Test getting a non-existent task by ID."""
        task = task_service.get_task(999)
        assert task is None

    def test_get_completed_tasks(self, task_service: TaskService):
        """Test getting only completed tasks."""
        # Create mix of completed and pending tasks
        task_service.create_task(TaskCreate(title="Pending task"))
        task2 = task_service.create_task(TaskCreate(title="Completed task"))

        # Mark second task as completed
        if task2.id is not None:
            task_service.toggle_completed(task2.id)

        completed_tasks = task_service.get_completed_tasks()
        assert len(completed_tasks) == 1
        assert completed_tasks[0].id == task2.id
        assert completed_tasks[0].completed

    def test_get_pending_tasks(self, task_service: TaskService):
        """Test getting only pending tasks."""
        # Create mix of completed and pending tasks
        task1 = task_service.create_task(TaskCreate(title="Pending task"))
        task2 = task_service.create_task(TaskCreate(title="Completed task"))

        # Mark second task as completed
        if task2.id is not None:
            task_service.toggle_completed(task2.id)

        pending_tasks = task_service.get_pending_tasks()
        assert len(pending_tasks) == 1
        assert pending_tasks[0].id == task1.id
        assert not pending_tasks[0].completed


class TestTaskUpdate:
    """Test task update functionality."""

    def test_update_task_title(self, task_service: TaskService):
        """Test updating task title."""
        task = task_service.create_task(TaskCreate(title="Original title"))
        original_updated_at = task.updated_at

        if task.id is not None:
            updated_task = task_service.update_task(task.id, TaskUpdate(title="Updated title"))

            assert updated_task is not None
            assert updated_task.title == "Updated title"
            assert updated_task.updated_at > original_updated_at

    def test_update_task_multiple_fields(self, task_service: TaskService):
        """Test updating multiple task fields."""
        task = task_service.create_task(TaskCreate(title="Original task"))
        due_date = date.today()

        assert task.id is not None
        update_data = TaskUpdate(
            title="Updated task", description="New description", priority=TaskPriority.URGENT, due_date=due_date
        )
        updated_task = task_service.update_task(task.id, update_data)

        assert updated_task is not None
        assert updated_task.title == "Updated task"
        assert updated_task.description == "New description"
        assert updated_task.priority == TaskPriority.URGENT
        assert updated_task.due_date == due_date

    def test_update_nonexistent_task(self, task_service: TaskService):
        """Test updating a non-existent task."""
        result = task_service.update_task(999, TaskUpdate(title="Won't work"))
        assert result is None

    def test_toggle_completed_status(self, task_service: TaskService):
        """Test toggling task completion status."""
        task = task_service.create_task(TaskCreate(title="Test task"))
        assert not task.completed
        assert task.id is not None

        # Toggle to completed
        updated_task = task_service.toggle_completed(task.id)
        assert updated_task is not None
        assert updated_task.completed

        # Toggle back to pending
        updated_task = task_service.toggle_completed(task.id)
        assert updated_task is not None
        assert not updated_task.completed

    def test_toggle_completed_nonexistent_task(self, task_service: TaskService):
        """Test toggling completion for non-existent task."""
        result = task_service.toggle_completed(999)
        assert result is None


class TestTaskDeletion:
    """Test task deletion functionality."""

    def test_delete_existing_task(self, task_service: TaskService):
        """Test deleting an existing task."""
        task = task_service.create_task(TaskCreate(title="To be deleted"))
        assert task.id is not None
        task_id = task.id

        result = task_service.delete_task(task_id)
        assert result

        # Verify task is gone
        deleted_task = task_service.get_task(task_id)
        assert deleted_task is None

    def test_delete_nonexistent_task(self, task_service: TaskService):
        """Test deleting a non-existent task."""
        result = task_service.delete_task(999)
        assert not result


class TestTaskValidation:
    """Test task validation and edge cases."""

    def test_create_task_with_empty_title_fails(self, task_service: TaskService):
        """Test that creating a task with empty title fails."""
        with pytest.raises(ValueError):
            TaskCreate(title="")

    def test_create_task_with_long_title_fails(self, task_service: TaskService):
        """Test that creating a task with too long title fails."""
        long_title = "x" * 201  # Exceeds 200 char limit
        with pytest.raises(ValueError):
            TaskCreate(title=long_title)

    def test_create_task_with_long_description_fails(self, task_service: TaskService):
        """Test that creating a task with too long description fails."""
        long_description = "x" * 1001  # Exceeds 1000 char limit
        with pytest.raises(ValueError):
            TaskCreate(title="Valid title", description=long_description)


class TestTaskServiceEdgeCases:
    """Test edge cases and error conditions."""

    def test_service_with_none_session_handling(self, new_db):
        """Test service behavior when session is None."""
        # This should create its own session
        service = TaskService(session=None)
        task = service.create_task(TaskCreate(title="Test"))
        assert task.id is not None
        service.close()

    def test_multiple_operations_same_service(self, task_service: TaskService):
        """Test multiple operations with same service instance."""
        # Create
        task = task_service.create_task(TaskCreate(title="Multi-op test"))
        assert task.id is not None

        # Update
        updated_task = task_service.update_task(task.id, TaskUpdate(title="Updated"))
        assert updated_task is not None

        # Toggle completion
        completed_task = task_service.toggle_completed(task.id)
        assert completed_task is not None
        assert completed_task.completed

        # Delete
        result = task_service.delete_task(task.id)
        assert result

        # Verify gone
        final_task = task_service.get_task(task.id)
        assert final_task is None
