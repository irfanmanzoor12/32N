from datetime import date, datetime, timezone
from typing import Any, Optional
import uuid

from tasks_mcp.models import Priority, Status, Task


class TaskNotFound(Exception):
    pass


class TaskStore:
    def __init__(self) -> None:
        self._tasks: dict[str, Task] = {}

    def _now(self) -> datetime:
        return datetime.now(timezone.utc)

    def add(
        self,
        user_id: str,
        title: str,
        notes: Optional[str] = None,
        due_date: Optional[date] = None,
        priority: Priority = Priority.medium,
    ) -> Task:
        now = self._now()
        task = Task(
            id=str(uuid.uuid4()),
            user_id=user_id,
            title=title,
            notes=notes,
            due_date=due_date,
            priority=priority,
            status=Status.active,
            created_at=now,
            updated_at=now,
        )
        self._tasks[task.id] = task
        return task

    def get_for_user(self, task_id: str, user_id: str) -> Task:
        task = self._tasks.get(task_id)
        if task is None or task.user_id != user_id:
            raise TaskNotFound(task_id)
        return task

    def list(
        self,
        user_id: str,
        status: Optional[Status | str] = None,
        priority: Optional[Priority] = None,
        due_before: Optional[date] = None,
    ) -> list[Task]:
        results = [t for t in self._tasks.values() if t.user_id == user_id]
        if status and status != "all":
            results = [t for t in results if t.status == status]
        if priority:
            results = [t for t in results if t.priority == priority]
        if due_before:
            results = [t for t in results if t.due_date is not None and t.due_date <= due_before]
        return results

    def update(self, task_id: str, **kwargs: Any) -> Task:
        task = self._tasks[task_id]
        for key, value in kwargs.items():
            setattr(task, key, value)
        task.updated_at = self._now()
        return task

    def clear(self) -> None:
        self._tasks.clear()


store = TaskStore()
