"""Task service layer for managing CRUD operations."""

from datetime import datetime
from typing import Optional
from sqlmodel import Session, select, desc
from app.database import get_session
from app.models import Task, TaskCreate, TaskUpdate


class TaskService:
    """Service class for task management operations."""

    def __init__(self, session: Optional[Session] = None):
        """Initialize with optional session for testing."""
        self.session = session or get_session()

    def create_task(self, task_data: TaskCreate) -> Task:
        """Create a new task."""
        task = Task(**task_data.model_dump())
        self.session.add(task)
        self.session.commit()
        self.session.refresh(task)
        return task

    def get_all_tasks(self) -> list[Task]:
        """Get all tasks ordered by created date (newest first)."""
        statement = select(Task).order_by(desc(Task.created_at))
        tasks = self.session.exec(statement).all()
        return list(tasks)

    def get_task(self, task_id: int) -> Optional[Task]:
        """Get a specific task by ID."""
        return self.session.get(Task, task_id)

    def update_task(self, task_id: int, task_data: TaskUpdate) -> Optional[Task]:
        """Update an existing task."""
        task = self.session.get(Task, task_id)
        if task is None:
            return None

        # Update only provided fields
        update_data = task_data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(task, field, value)

        task.updated_at = datetime.utcnow()
        self.session.add(task)
        self.session.commit()
        self.session.refresh(task)
        return task

    def toggle_completed(self, task_id: int) -> Optional[Task]:
        """Toggle task completion status."""
        task = self.session.get(Task, task_id)
        if task is None:
            return None

        task.completed = not task.completed
        task.updated_at = datetime.utcnow()
        self.session.add(task)
        self.session.commit()
        self.session.refresh(task)
        return task

    def delete_task(self, task_id: int) -> bool:
        """Delete a task. Returns True if successful, False if not found."""
        task = self.session.get(Task, task_id)
        if task is None:
            return False

        self.session.delete(task)
        self.session.commit()
        return True

    def get_completed_tasks(self) -> list[Task]:
        """Get all completed tasks."""
        statement = select(Task).where(Task.completed).order_by(desc(Task.updated_at))
        tasks = self.session.exec(statement).all()
        return list(tasks)

    def get_pending_tasks(self) -> list[Task]:
        """Get all pending (non-completed) tasks."""
        statement = select(Task).where(Task.completed == False).order_by(desc(Task.created_at))  # noqa: E712
        tasks = self.session.exec(statement).all()
        return list(tasks)

    def close(self) -> None:
        """Close the database session."""
        if self.session:
            self.session.close()
