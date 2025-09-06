from sqlmodel import SQLModel, Field
from datetime import datetime, date
from typing import Optional
from enum import Enum


class TaskPriority(str, Enum):
    """Task priority levels."""

    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    URGENT = "urgent"


class Task(SQLModel, table=True):
    """Task model for the todo list application."""

    __tablename__ = "tasks"  # type: ignore[assignment]

    id: Optional[int] = Field(default=None, primary_key=True)
    title: str = Field(max_length=200, min_length=1)
    description: str = Field(default="", max_length=1000)
    completed: bool = Field(default=False)
    priority: TaskPriority = Field(default=TaskPriority.MEDIUM)
    due_date: Optional[date] = Field(default=None)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)


# Non-persistent schemas for validation and API operations
class TaskCreate(SQLModel, table=False):
    """Schema for creating new tasks."""

    title: str = Field(max_length=200, min_length=1)
    description: str = Field(default="", max_length=1000)
    priority: TaskPriority = Field(default=TaskPriority.MEDIUM)
    due_date: Optional[date] = Field(default=None)


class TaskUpdate(SQLModel, table=False):
    """Schema for updating existing tasks."""

    title: Optional[str] = Field(default=None, max_length=200, min_length=1)
    description: Optional[str] = Field(default=None, max_length=1000)
    completed: Optional[bool] = Field(default=None)
    priority: Optional[TaskPriority] = Field(default=None)
    due_date: Optional[date] = Field(default=None)


class TaskResponse(SQLModel, table=False):
    """Schema for task responses."""

    id: int
    title: str
    description: str
    completed: bool
    priority: TaskPriority
    due_date: Optional[date]
    created_at: datetime
    updated_at: datetime
